import { deriveRunActivity, sensorEntityIdForVacuum, type RunActivity } from "./activity";
import { parseQueueSnapshot, queueRunStateLabel, type QueueItem, type QueueSnapshot } from "./queue";
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

export type CardQueueRow = {
  itemId: string;
  roomName: string;
  status: string;
  statusLabel: string;
  canRemove: boolean;
};

export type CardViewModel = {
  title: string;
  status: CardViewStatus;
  entityId: string | null;
  message: string | null;
  snapshot: QueueSnapshot | null;
  activity: RunActivity | null;
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
    rooms,
    rows: snapshot.items.map(cardQueueRow),
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

function cardQueueRow(item: QueueItem): CardQueueRow {
  return {
    itemId: item.itemId,
    roomName: item.roomName,
    status: item.status,
    statusLabel: queueRunStateLabel(item.status),
    canRemove: item.status === "pending",
  };
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
