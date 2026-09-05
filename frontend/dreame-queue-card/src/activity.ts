export type RunActivityPhase =
  | "preparing"
  | "cleaning"
  | "paused"
  | "returning"
  | "finishing"
  | "error"
  | "unknown";

export type RunActivity = {
  phase: RunActivityPhase;
  label: string;
  resumeBlockedReason?: string;
};

export type RobotSignals = {
  queueRunState?: unknown;
  vacuumState?: unknown;
  robotState?: unknown;
  taskStatus?: unknown;
  errorCode?: unknown;
  robotStatus?: unknown;
  paused?: unknown;
  running?: unknown;
  dirtyWaterTankStatus?: unknown;
  cleanWaterTankStatus?: unknown;
};

const PREPARING_ROBOT_STATES = new Set([
  "washing",
  "washing_paused",
  "clean_add_water",
  "charging_completed",
  "returning_to_wash",
  "auto_emptying",
]);

const ACTIVE_CLEANING_ROBOT_STATES = new Set([
  "sweeping_and_mopping",
  "sweeping",
  "vacuuming",
  "mopping",
  "spot_cleaning",
  "room_cleaning",
  "segment_cleaning",
]);

const ERROR_CODE_LABELS: Record<string, string> = {
  water_tank_dry: "clean water tank empty",
  dirty_water_tank: "dirty water tank full",
  remove_mop: "remove mop pads",
  route: "route blocked",
};

function normalize(value: unknown): string {
  return String(value ?? "").trim().toLowerCase();
}

export function waterTankBlockReason(dirty: unknown, clean: unknown): string | null {
  const ready = new Set(["installed", "normal", "ok", "ready", "available"]);
  if (dirty != null && !ready.has(normalize(dirty))) {
    return "Check dirty water tank (full, missing or unavailable)";
  }
  if (clean != null && !ready.has(normalize(clean))) {
    return "Check clean water tank (empty, missing or unavailable)";
  }
  return null;
}

function humanize(value: unknown): string {
  const normalized = normalize(value);
  return normalized ? normalized.replaceAll("_", " ") : "";
}

export function describeDreameError(errorCode: unknown): string | null {
  const normalized = normalize(errorCode);
  if (!normalized || normalized === "no_error" || normalized === "unknown" || normalized === "unavailable") {
    return null;
  }
  return ERROR_CODE_LABELS[normalized] ?? humanize(normalized);
}

function preparingLabel(robotState: string): string {
  switch (robotState) {
    case "washing":
      return "Washing pads";
    case "washing_paused":
      return "Washing paused";
    case "clean_add_water":
      return "Adding water";
    case "returning_to_wash":
      return "Returning to wash";
    case "auto_emptying":
      return "Auto-emptying";
    default:
      return humanize(robotState);
  }
}

export function deriveRunActivity(signals: RobotSignals): RunActivity | null {
  if (normalize(signals.queueRunState) !== "running") {
    return null;
  }

  const vacuumState = normalize(signals.vacuumState);
  const robotState = normalize(signals.robotState);
  const taskStatus = normalize(signals.taskStatus);
  const errorDescription = describeDreameError(signals.errorCode);
  const tankBlock = waterTankBlockReason(signals.dirtyWaterTankStatus, signals.cleanWaterTankStatus);

  if (vacuumState === "error") {
    return { phase: "error", label: tankBlock ?? errorDescription ?? "Error",
      ...(tankBlock ? {resumeBlockedReason: tankBlock} : {}) };
  }

  if (taskStatus === "completed") {
    return { phase: "finishing", label: "Finishing step" };
  }

  if (tankBlock) {
    return { phase: "paused", label: tankBlock, resumeBlockedReason: tankBlock };
  }

  if (vacuumState === "paused" || normalize(signals.robotStatus) === "paused"
      || (signals.paused === true && signals.running === false) || taskStatus.endsWith("_paused")) {
    return {
      phase: "paused",
      label: errorDescription ? `Paused (${errorDescription})` : "Paused",
    };
  }

  if (PREPARING_ROBOT_STATES.has(robotState)) {
    return {
      phase: "preparing",
      label: preparingLabel(robotState),
    };
  }

  if (vacuumState === "returning" && taskStatus === "room_cleaning") {
    return { phase: "returning", label: "Returning to base" };
  }

  if (ACTIVE_CLEANING_ROBOT_STATES.has(robotState)) {
    switch (robotState) {
      case "sweeping":
      case "vacuuming":
        return { phase: "cleaning", label: "Vacuuming" };
      case "mopping":
        return { phase: "cleaning", label: "Mopping" };
      case "sweeping_and_mopping":
        return { phase: "cleaning", label: "Vacuuming + mopping" };
      case "spot_cleaning":
        return { phase: "cleaning", label: "Spot cleaning" };
      default:
        return { phase: "cleaning", label: "Cleaning room" };
    }
  }

  if (vacuumState === "cleaning") {
    return { phase: "cleaning", label: "Cleaning room" };
  }

  if (vacuumState === "returning") {
    return { phase: "returning", label: "Returning to base" };
  }

  return { phase: "unknown", label: "Working" };
}

export function sensorEntityIdForVacuum(
  vacuumEntityId: string,
  suffix: "state" | "status" | "task_status" | "error" | "cleaning_progress" | "dirty_water_tank_status" | "clean_water_tank_status",
): string | null {
  const normalized = String(vacuumEntityId || "").trim();
  if (!normalized.startsWith("vacuum.")) {
    return null;
  }
  const objectId = normalized.slice("vacuum.".length);
  if (!objectId) {
    return null;
  }
  return `sensor.${objectId}_${suffix}`;
}
