import { deriveRunActivity, sensorEntityIdForVacuum, type RunActivity } from "./activity";
import { parseQueueSnapshot, queueRunStateLabel, type QueueItem, type QueueSnapshot } from "./queue";
import { overrideLabel, type OverrideField } from "./queue-overrides";
import { extractDreameRooms, type DreameRoom } from "./rooms";

export const CARD_ELEMENT_TAG = "ha-dreame-queue-card";
export const DEFAULT_CARD_TITLE = "HA Dreame Queue";

export type HaDreameQueueCardConfig = {
  entity?: string;
  title?: string;
};

export type HomeAssistantState = {
  state?: unknown;
  attributes?: unknown;
};

export type HomeAssistantLike = {
  states: Record<string, HomeAssistantState | undefined>;
  callService?: (
    domain: string,
    service: string,
    data?: Record<string, unknown>,
  ) => Promise<unknown> | unknown;
};

export type CardViewStatus = "not_configured" | "missing" | "ready";

export type ActiveQueueService = "start_queue" | "cancel_queue" | "skip_current_room";

export type CardActiveControl = {
  ariaLabel: string;
  label: string;
  service: ActiveQueueService;
};

export type CardOverrideControl = {
  field: OverrideField;
  label: string;
  valueLabel: string;
};

export type CardQueueRow = {
  itemId: string;
  queuePosition: number;
  roomName: string;
  status: string;
  statusLabel: string;
  overrides: Record<string, unknown>;
  canRemove: boolean;
  canMoveUp: boolean;
  canMoveDown: boolean;
  overrideControls: CardOverrideControl[];
};

const OVERRIDE_CONTROLS: Array<{ field: OverrideField; label: string }> = [
  { field: "water_volume", label: "Water" },
  { field: "suction_level", label: "Suction" },
  { field: "repeats", label: "Repeats" },
];

export type CardViewModel = {
  title: string;
  status: CardViewStatus;
  entityId: string | null;
  message: string | null;
  snapshot: QueueSnapshot | null;
  activity: RunActivity | null;
  activeControls: CardActiveControl[];
  canClearPending: boolean;
  rooms: DreameRoom[];
  rows: CardQueueRow[];
};

export function buildCardViewModel(
  hass: HomeAssistantLike | undefined,
  config: HaDreameQueueCardConfig,
): CardViewModel {
  const title = normalizedString(config.title) || DEFAULT_CARD_TITLE;
  const entityId = normalizedString(config.entity) || null;

  if (!entityId) {
    return emptyViewModel({
      title,
      status: "not_configured",
      entityId: null,
      message: "Configure a HA Dreame queue status entity.",
    });
  }

  const queueState = hass?.states[entityId];
  if (!queueState) {
    return emptyViewModel({
      title,
      status: "missing",
      entityId,
      message: "Queue entity not found.",
    });
  }

  const snapshot = parseQueueSnapshot(queueState);
  const activity = buildActivity(hass, snapshot);
  const rooms = buildRooms(hass, snapshot);

  return {
    title,
    status: "ready",
    entityId,
    message: null,
    snapshot,
    activity,
    activeControls: buildActiveControls(snapshot),
    canClearPending: snapshot.pendingItems > 0,
    rooms,
    rows: cardQueueRows(snapshot.items),
  };
}

function emptyViewModel({
  title,
  status,
  entityId,
  message,
}: {
  title: string;
  status: CardViewStatus;
  entityId: string | null;
  message: string;
}): CardViewModel {
  return {
    title,
    status,
    entityId,
    message,
    snapshot: null,
    activity: null,
    activeControls: [],
    canClearPending: false,
    rooms: [],
    rows: [],
  };
}

function buildActivity(
  hass: HomeAssistantLike | undefined,
  snapshot: QueueSnapshot,
): RunActivity | null {
  const vacuumEntityId = snapshot.vacuumEntityId;
  if (!hass || !vacuumEntityId) {
    return null;
  }

  return deriveRunActivity({
    queueRunState: snapshot.runState,
    vacuumState: stateValue(hass, vacuumEntityId),
    robotState: stateValue(hass, sensorEntityIdForVacuum(vacuumEntityId, "state")),
    taskStatus: stateValue(hass, sensorEntityIdForVacuum(vacuumEntityId, "task_status")),
    errorCode: stateValue(hass, sensorEntityIdForVacuum(vacuumEntityId, "error")),
  });
}

function cardQueueRows(items: QueueItem[]): CardQueueRow[] {
  const pendingIndexes = items.flatMap((item, index) => (item.status === "pending" ? [index] : []));
  const firstPendingIndex = pendingIndexes[0] ?? null;
  const lastPendingIndex = pendingIndexes[pendingIndexes.length - 1] ?? null;

  return items.map((item, index) => ({
    itemId: item.itemId,
    queuePosition: index,
    roomName: item.roomName,
    status: item.status,
    statusLabel: queueRunStateLabel(item.status),
    overrides: { ...item.overrides },
    canRemove: item.status === "pending",
    canMoveUp: item.status === "pending" && index !== firstPendingIndex,
    canMoveDown: item.status === "pending" && index !== lastPendingIndex,
    overrideControls: item.status === "pending" ? buildOverrideControls(item.overrides) : [],
  }));
}

function buildActiveControls(snapshot: QueueSnapshot): CardActiveControl[] {
  if (snapshot.runState === "running") {
    return [
      {
        ariaLabel: "Cancel queue",
        label: "Cancel",
        service: "cancel_queue",
      },
      {
        ariaLabel: "Skip current room",
        label: "Skip",
        service: "skip_current_room",
      },
    ];
  }

  if (snapshot.pendingItems > 0) {
    return [
      {
        ariaLabel: "Start queue",
        label: "Start",
        service: "start_queue",
      },
    ];
  }

  return [];
}

function buildOverrideControls(overrides: Record<string, unknown>): CardOverrideControl[] {
  return OVERRIDE_CONTROLS.map((control) => ({
    field: control.field,
    label: control.label,
    valueLabel: overrideLabel(control.field, overrides, {}),
  }));
}

function buildRooms(
  hass: HomeAssistantLike | undefined,
  snapshot: QueueSnapshot,
): DreameRoom[] {
  const vacuumEntityId = snapshot.vacuumEntityId;
  if (!hass || !vacuumEntityId) {
    return [];
  }
  const attrs = hass.states[vacuumEntityId]?.attributes;
  return extractDreameRooms(isRecord(attrs) ? attrs["rooms"] : undefined);
}

function stateValue(
  hass: HomeAssistantLike,
  entityId: string | null,
): unknown {
  return entityId ? hass.states[entityId]?.state : undefined;
}

function normalizedString(value: unknown): string {
  return String(value ?? "").trim();
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
