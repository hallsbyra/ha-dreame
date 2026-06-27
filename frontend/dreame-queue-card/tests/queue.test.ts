import { describe, expect, it } from "vitest";

import {
  canClearQueue,
  getQueueItems,
  parseQueueSnapshot,
  pendingCount,
  queueRunStateLabel,
} from "../src/queue";

describe("HA Dreame queue helpers", () => {
  const attributes = {
    queue_items: [
      {
        item_id: "entry-1",
        room_id: 1,
        room_name: "Kitchen",
        status: "pending",
        overrides: { repeats: 2 },
        result: null,
      },
      {
        item_id: "entry-2",
        room_id: 2,
        room_name: "Hallway",
        status: "running",
        overrides: {},
        result: "started",
      },
      {
        item_id: 3,
        room_id: "bad",
        room_name: "Invalid",
        status: "pending",
      },
    ],
    pending_items: 1,
    running_items: 1,
    completed_items: 0,
    total_items: 2,
    allow_robot_commands: true,
    auto_reconcile_enabled: false,
    config_entry_id: "config-entry-1",
    vacuum_entity_id: "vacuum.robot",
  };

  it("parses public queue item attributes from the ha_dreame sensor shape", () => {
    expect(getQueueItems(attributes)).toEqual([
      {
        itemId: "entry-1",
        roomId: 1,
        roomName: "Kitchen",
        status: "pending",
        overrides: { repeats: 2 },
        result: null,
      },
      {
        itemId: "entry-2",
        roomId: 2,
        roomName: "Hallway",
        status: "running",
        overrides: {},
        result: "started",
      },
    ]);
  });

  it("ignores the legacy pyscript item attribute name", () => {
    expect(
      getQueueItems({
        items: [
          {
            item_id: "legacy",
            room_id: 1,
            room_name: "Kitchen",
            status: "pending",
          },
        ],
      }),
    ).toEqual([]);
  });

  it("derives a full queue snapshot from a Home Assistant state object", () => {
    expect(parseQueueSnapshot({ state: "running", attributes })).toEqual({
      runState: "running",
      allowRobotCommands: true,
      autoReconcileEnabled: false,
      configEntryId: "config-entry-1",
      vacuumEntityId: "vacuum.robot",
      pendingItems: 1,
      runningItems: 1,
      completedItems: 0,
      totalItems: 2,
      items: getQueueItems(attributes),
    });
  });

  it("falls back to parsed item counts when numeric attributes are unavailable", () => {
    const snapshot = parseQueueSnapshot({
      state: "unknown",
      attributes: {
        queue_items: [
          { item_id: "1", room_id: 1, room_name: "Kitchen", status: "pending" },
          { item_id: "2", room_id: 2, room_name: "Hallway", status: "completed" },
          { item_id: "3", room_id: 3, room_name: "Office", status: "running" },
        ],
      },
    });

    expect(snapshot.pendingItems).toBe(1);
    expect(snapshot.runningItems).toBe(1);
    expect(snapshot.completedItems).toBe(1);
    expect(snapshot.totalItems).toBe(3);
  });

  it("counts pending items", () => {
    expect(pendingCount(getQueueItems(attributes))).toBe(1);
  });

  it("allows clearing when the queue has any item", () => {
    expect(canClearQueue(getQueueItems(attributes))).toBe(true);
    expect(canClearQueue([])).toBe(false);
  });

  it("formats run state labels for route blocks", () => {
    expect(queueRunStateLabel("blocked")).toBe("Route blocked");
    expect(queueRunStateLabel("out_of_sync")).toBe("Out of sync");
    expect(queueRunStateLabel("")).toBe("Unknown");
  });
});
