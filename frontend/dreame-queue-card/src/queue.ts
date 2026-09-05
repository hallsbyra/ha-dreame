export type QueueItem = {
  itemId: string;
  roomId: number;
  roomName: string;
  status: string;
  overrides: Record<string, unknown>;
  result: string | null;
};

export type QueueSnapshot = {
  runState: string;
  allowRobotCommands: boolean | null;
  autoReconcileEnabled: boolean | null;
  configEntryId: string | null;
  vacuumEntityId: string | null;
  pendingItems: number;
  runningItems: number;
  completedItems: number;
  totalItems: number;
  items: QueueItem[];
};

type HomeAssistantState = {
  state?: unknown;
  attributes?: unknown;
};

const TERMINAL_QUEUE_FAILURE_STATES = new Set(["blocked", "out_of_sync"]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizedString(value: unknown): string {
  return String(value ?? "").trim();
}

function normalizedRunState(value: unknown): string {
  return normalizedString(value).toLowerCase();
}

function nonNegativeInt(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
    return null;
  }
  return Math.trunc(value);
}

function optionalBoolean(value: unknown): boolean | null {
  return typeof value === "boolean" ? value : null;
}

function countByStatus(items: QueueItem[], status: string): number {
  return items.filter((item) => item.status === status).length;
}

function parseQueueItem(value: unknown): QueueItem | null {
  if (!isRecord(value)) {
    return null;
  }

  const itemId = value["item_id"];
  const roomId = value["room_id"];
  const roomName = value["room_name"];
  const status = value["status"];

  if (
    typeof itemId !== "string" ||
    typeof roomId !== "number" ||
    !Number.isFinite(roomId) ||
    typeof roomName !== "string" ||
    typeof status !== "string"
  ) {
    return null;
  }

  return {
    itemId,
    roomId,
    roomName,
    status,
    overrides: isRecord(value["overrides"]) ? { ...value["overrides"] } : {},
    result: typeof value["result"] === "string" ? value["result"] : null,
  };
}

export function isTerminalQueueFailure(runState: unknown): boolean {
  return TERMINAL_QUEUE_FAILURE_STATES.has(normalizedRunState(runState));
}

export function queueRunStateLabel(runState: unknown): string {
  const normalized = normalizedRunState(runState);
  if (!normalized) {
    return "Unknown";
  }
  if (normalized === "blocked") {
    return "Route blocked";
  }
  if (normalized === "out_of_sync") {
    return "Out of sync";
  }
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

export function getQueueItems(attributes: unknown): QueueItem[] {
  if (!isRecord(attributes)) {
    return [];
  }

  const raw = attributes["queue_items"];
  if (!Array.isArray(raw)) {
    return [];
  }

  return raw.flatMap((item) => {
    const parsed = parseQueueItem(item);
    return parsed ? [parsed] : [];
  });
}

export function pendingCount(items: QueueItem[]): number {
  return countByStatus(items, "pending");
}

export function canClearQueue(items: QueueItem[]): boolean {
  return items.length > 0;
}

export function parseQueueSnapshot(stateObject: HomeAssistantState | undefined): QueueSnapshot {
  const attributes = stateObject?.attributes;
  const items = getQueueItems(attributes);
  const attrs = isRecord(attributes) ? attributes : {};

  return {
    runState: normalizedRunState(stateObject?.state) || "unknown",
    allowRobotCommands: optionalBoolean(attrs["allow_robot_commands"]),
    autoReconcileEnabled: optionalBoolean(attrs["auto_reconcile_enabled"]),
    configEntryId:
      typeof attrs["config_entry_id"] === "string" ? attrs["config_entry_id"] : null,
    vacuumEntityId:
      typeof attrs["vacuum_entity_id"] === "string" ? attrs["vacuum_entity_id"] : null,
    pendingItems: nonNegativeInt(attrs["pending_items"]) ?? countByStatus(items, "pending"),
    runningItems: nonNegativeInt(attrs["running_items"]) ?? countByStatus(items, "running"),
    completedItems: nonNegativeInt(attrs["completed_items"]) ?? countByStatus(items, "completed"),
    totalItems: nonNegativeInt(attrs["total_items"]) ?? items.length,
    items,
  };
}
