export type RunningOverrideField = "suction_level" | "water_volume";

type RunningOverrideServiceCall = {
  domain: "ha_dreame";
  service: "update_running_override";
  data: {
    config_entry_id: string;
    field: RunningOverrideField;
    value: number;
  };
};

type SelectConfig = {
  control: "select";
  suffix: "suction_level";
  options: readonly string[];
  optionIndexToOverrideValue: (index: number) => number;
};

type NumberConfig = {
  control: "number";
  suffix: "wetness_level";
  values: readonly number[];
  stateToOverrideValue: (state: unknown) => number | null;
};

type RunningOverrideConfig = SelectConfig | NumberConfig;

const WETNESS_LEVEL_LOW_MAX = 10;
const WETNESS_LEVEL_HIGH_MIN = 22;

const RUNNING_OVERRIDE_CONFIG: Record<RunningOverrideField, RunningOverrideConfig> = {
  suction_level: {
    control: "select",
    suffix: "suction_level",
    options: ["quiet", "standard", "strong", "turbo"],
    optionIndexToOverrideValue: (index) => index,
  },
  water_volume: {
    control: "number",
    suffix: "wetness_level",
    values: [1, 2, 3],
    stateToOverrideValue: (state) => {
      const parsed = Number(String(state ?? "").trim());
      if (!Number.isFinite(parsed)) {
        return null;
      }
      if (parsed <= WETNESS_LEVEL_LOW_MAX) {
        return 1;
      }
      if (parsed >= WETNESS_LEVEL_HIGH_MIN) {
        return 3;
      }
      return 2;
    },
  },
};

export function runningOverrideEntityId(
  vacuumEntityId: string,
  field: RunningOverrideField,
): string | null {
  const normalized = String(vacuumEntityId || "").trim();
  if (!normalized.startsWith("vacuum.")) {
    return null;
  }
  const objectId = normalized.slice("vacuum.".length);
  if (!objectId) {
    return null;
  }

  const config = RUNNING_OVERRIDE_CONFIG[field];
  return `${config.control}.${objectId}_${config.suffix}`;
}

export function runningOverrideValueFromState(
  field: RunningOverrideField,
  entityState: unknown,
): number | null {
  const config = RUNNING_OVERRIDE_CONFIG[field];
  if (config.control === "number") {
    return config.stateToOverrideValue(entityState);
  }

  const normalized = String(entityState ?? "").trim().toLowerCase();
  const index = config.options.indexOf(normalized);
  return index < 0 ? null : config.optionIndexToOverrideValue(index);
}

export function nextRunningOverrideServiceCall(
  configEntryId: string,
  field: RunningOverrideField,
  entityState: unknown,
): RunningOverrideServiceCall {
  return {
    domain: "ha_dreame",
    service: "update_running_override",
    data: {
      config_entry_id: configEntryId,
      field,
      value: nextRunningOverrideValue(field, entityState),
    },
  };
}

function nextRunningOverrideValue(field: RunningOverrideField, entityState: unknown): number {
  const config = RUNNING_OVERRIDE_CONFIG[field];
  if (config.control === "number") {
    const currentValue = config.stateToOverrideValue(entityState);
    const currentIndex = currentValue ? config.values.indexOf(currentValue) : -1;
    const nextIndex = currentIndex < 0 ? 0 : (currentIndex + 1) % config.values.length;
    return config.values[nextIndex];
  }

  const normalized = String(entityState ?? "").trim().toLowerCase();
  const currentIndex = config.options.indexOf(normalized);
  const nextIndex = currentIndex < 0 ? 0 : (currentIndex + 1) % config.options.length;
  return config.optionIndexToOverrideValue(nextIndex);
}
