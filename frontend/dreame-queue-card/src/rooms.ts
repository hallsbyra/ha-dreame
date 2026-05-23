export type DreameRoom = {
  roomId: number;
  roomName: string;
};

function toIntOrNull(value: unknown): number | null {
  if (typeof value === "number" && Number.isInteger(value)) {
    return value;
  }
  if (typeof value !== "string") {
    return null;
  }

  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  const parsed = Number(trimmed);
  return Number.isInteger(parsed) ? parsed : null;
}

function collectRooms(node: unknown, out: DreameRoom[]): void {
  if (Array.isArray(node)) {
    for (const value of node) {
      collectRooms(value, out);
    }
    return;
  }

  if (typeof node !== "object" || node === null) {
    return;
  }

  const record = node as Record<string, unknown>;
  const entryId = toIntOrNull(record["id"]);
  const entryName = typeof record["name"] === "string" ? record["name"].trim() : "";
  if (entryId !== null && entryName) {
    out.push({ roomId: entryId, roomName: entryName });
  }

  for (const [key, value] of Object.entries(record)) {
    const mapRoomId = toIntOrNull(key);
    if (mapRoomId !== null && typeof value === "string") {
      const mapRoomName = value.trim();
      if (mapRoomName) {
        out.push({ roomId: mapRoomId, roomName: mapRoomName });
        continue;
      }
    }
    collectRooms(value, out);
  }
}

export function extractDreameRooms(rawRooms: unknown): DreameRoom[] {
  const collected: DreameRoom[] = [];
  collectRooms(rawRooms, collected);

  const byId = new Map<number, string>();
  for (const room of collected) {
    byId.set(room.roomId, room.roomName);
  }

  return Array.from(byId.entries())
    .map(([roomId, roomName]) => ({ roomId, roomName }))
    .sort((a, b) => a.roomId - b.roomId);
}
