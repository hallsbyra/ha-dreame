import { describe, expect, it } from "vitest";

import { extractDreameRooms } from "../src/rooms";

describe("extractDreameRooms", () => {
  it("extracts rooms from nested Dreame group payloads", () => {
    expect(
      extractDreameRooms({
        Downstairs: [
          { id: 1, name: "Kitchen", icon: "mdi:home-outline" },
          { id: 7, name: "Hallway", icon: "mdi:home-outline" },
        ],
        Upstairs: [{ id: 8, name: "Office" }],
      }),
    ).toEqual([
      { roomId: 1, roomName: "Kitchen" },
      { roomId: 7, roomName: "Hallway" },
      { roomId: 8, roomName: "Office" },
    ]);
  });

  it("extracts rooms from id-name map payloads", () => {
    expect(
      extractDreameRooms({
        "3": "Dining room",
        "4": "Living room",
      }),
    ).toEqual([
      { roomId: 3, roomName: "Dining room" },
      { roomId: 4, roomName: "Living room" },
    ]);
  });

  it("de-duplicates by room id and keeps the latest room name", () => {
    expect(
      extractDreameRooms([
        { id: 5, name: "Bath" },
        { id: 5, name: "Bathroom" },
      ]),
    ).toEqual([{ roomId: 5, roomName: "Bathroom" }]);
  });

  it("returns an empty list for invalid payloads", () => {
    expect(extractDreameRooms(undefined)).toEqual([]);
    expect(extractDreameRooms("bad")).toEqual([]);
    expect(extractDreameRooms(42)).toEqual([]);
  });
});
