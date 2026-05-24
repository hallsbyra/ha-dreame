import { describe, expect, it } from "vitest";

import { buildCardViewModel } from "../src/card-view";

const queueAttributes = {
  queue_items: [
    {
      item_id: "item-1",
      room_id: 1,
      room_name: "Kitchen",
      status: "running",
    },
    {
      item_id: "item-2",
      room_id: 2,
      room_name: "Hallway",
      status: "pending",
      overrides: {
        repeats: 2,
        suction_level: 1,
        water_volume: 2,
      },
    },
    {
      item_id: "item-3",
      room_id: 3,
      room_name: "Office",
      status: "pending",
    },
  ],
  pending_items: 2,
  running_items: 1,
  completed_items: 0,
  total_items: 3,
  config_entry_id: "config-entry-1",
  vacuum_entity_id: "vacuum.robot",
};

const hass = {
  states: {
    "sensor.robot_queue_status": {
      state: "running",
      attributes: queueAttributes,
    },
    "vacuum.robot": {
      state: "cleaning",
      attributes: {
        rooms: {
          "1": "Kitchen",
          "2": "Hallway",
          "3": "Office",
        },
      },
    },
    "sensor.robot_state": {
      state: "sweeping_and_mopping",
      attributes: {},
    },
    "sensor.robot_task_status": {
      state: "room_cleaning",
      attributes: {},
    },
    "sensor.robot_error": {
      state: "no_error",
      attributes: {},
    },
  },
};

describe("card view model", () => {
  it("requires an explicit ha_dreame queue entity", () => {
    expect(buildCardViewModel(hass, {})).toEqual({
      title: "HA Dreame Queue",
      status: "not_configured",
      entityId: null,
      message: "Configure a HA Dreame queue status entity.",
      snapshot: null,
      activity: null,
      canClearPending: false,
      rooms: [],
      rows: [],
    });
  });

  it("reports a missing configured queue entity", () => {
    expect(buildCardViewModel(hass, { entity: "sensor.missing_queue" })).toMatchObject({
      status: "missing",
      entityId: "sensor.missing_queue",
      message: "Queue entity not found.",
    });
  });

  it("builds a read-only queue summary from the ha_dreame sensor shape", () => {
    expect(
      buildCardViewModel(hass, {
        entity: "sensor.robot_queue_status",
        title: "Robot queue",
      }),
    ).toEqual({
      title: "Robot queue",
      status: "ready",
      entityId: "sensor.robot_queue_status",
      message: null,
      snapshot: {
        runState: "running",
        configEntryId: "config-entry-1",
        vacuumEntityId: "vacuum.robot",
        pendingItems: 2,
        runningItems: 1,
        completedItems: 0,
        totalItems: 3,
        items: [
          {
            itemId: "item-1",
            roomId: 1,
            roomName: "Kitchen",
            status: "running",
            overrides: {},
            result: null,
          },
          {
            itemId: "item-2",
            roomId: 2,
            roomName: "Hallway",
            status: "pending",
            overrides: {
              repeats: 2,
              suction_level: 1,
              water_volume: 2,
            },
            result: null,
          },
          {
            itemId: "item-3",
            roomId: 3,
            roomName: "Office",
            status: "pending",
            overrides: {},
            result: null,
          },
        ],
      },
      activity: {
        phase: "cleaning",
        label: "Vacuuming + mopping",
      },
      canClearPending: true,
      rooms: [
        {
          roomId: 1,
          roomName: "Kitchen",
        },
        {
          roomId: 2,
          roomName: "Hallway",
        },
        {
          roomId: 3,
          roomName: "Office",
        },
      ],
      rows: [
        {
          itemId: "item-1",
          queuePosition: 0,
          roomName: "Kitchen",
          status: "running",
          statusLabel: "Running",
          overrides: {},
          canRemove: false,
          canMoveUp: false,
          canMoveDown: false,
          overrideControls: [],
        },
        {
          itemId: "item-2",
          queuePosition: 1,
          roomName: "Hallway",
          status: "pending",
          statusLabel: "Pending",
          overrides: {
            repeats: 2,
            suction_level: 1,
            water_volume: 2,
          },
          canRemove: true,
          canMoveUp: false,
          canMoveDown: true,
          overrideControls: [
            {
              field: "water_volume",
              label: "Water",
              valueLabel: "Med",
            },
            {
              field: "suction_level",
              label: "Suction",
              valueLabel: "Med",
            },
            {
              field: "repeats",
              label: "Repeats",
              valueLabel: "x2",
            },
          ],
        },
        {
          itemId: "item-3",
          queuePosition: 2,
          roomName: "Office",
          status: "pending",
          statusLabel: "Pending",
          overrides: {},
          canRemove: true,
          canMoveUp: true,
          canMoveDown: false,
          overrideControls: [
            {
              field: "water_volume",
              label: "Water",
              valueLabel: "Med",
            },
            {
              field: "suction_level",
              label: "Suction",
              valueLabel: "Med",
            },
            {
              field: "repeats",
              label: "Repeats",
              valueLabel: "x1",
            },
          ],
        },
      ],
    });
  });
});
