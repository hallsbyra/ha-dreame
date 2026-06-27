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
    "select.robot_suction_level": {
      state: "quiet",
      attributes: {},
    },
    "number.robot_wetness_level": {
      state: "16",
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
      summary: null,
      snapshot: null,
      activity: null,
      activeControls: [],
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
      summary: "Vacuuming + mopping",
      snapshot: {
        runState: "running",
        allowRobotCommands: null,
        autoReconcileEnabled: null,
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
      activeControls: [
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
      ],
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
          overrideControls: [
            {
              controlType: "running",
              field: "water_volume",
              label: "Water",
              valueLabel: "Med",
              value: 3,
            },
            {
              controlType: "running",
              field: "suction_level",
              label: "Suction",
              valueLabel: "Min",
              value: 1,
            },
          ],
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
              controlType: "pending",
              field: "water_volume",
              label: "Water",
              valueLabel: "Med",
            },
            {
              controlType: "pending",
              field: "suction_level",
              label: "Suction",
              valueLabel: "Med",
            },
            {
              controlType: "pending",
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
              controlType: "pending",
              field: "water_volume",
              label: "Water",
              valueLabel: "Med",
            },
            {
              controlType: "pending",
              field: "suction_level",
              label: "Suction",
              valueLabel: "Med",
            },
            {
              controlType: "pending",
              field: "repeats",
              label: "Repeats",
              valueLabel: "x1",
            },
          ],
        },
      ],
    });
  });

  it("offers a command-gated start control for idle queues with pending rooms", () => {
    const view = buildCardViewModel(
      hassWithQueueState("idle", {
        queue_items: [queueAttributes.queue_items[1]],
        pending_items: 1,
        running_items: 0,
        total_items: 1,
      }),
      {
        entity: "sensor.robot_queue_status",
        title: "Robot queue",
      },
    );

    expect(view.summary).toBe("Ready to start 1 room.");
    expect(view.activeControls).toEqual([
      {
        ariaLabel: "Start queue",
        label: "Start",
        service: "start_queue",
      },
    ]);
  });

  it("offers Continue and End when the active robot run is interrupted", () => {
    const view = buildCardViewModel(
      {
        ...hass,
        states: {
          ...hass.states,
          "sensor.robot_queue_status": {
            state: "running",
            attributes: {
              ...queueAttributes,
              allow_robot_commands: true,
            },
          },
          "vacuum.robot": {
            state: "error",
            attributes: {},
          },
          "sensor.robot_task_status": {
            state: "room_cleaning",
            attributes: {},
          },
          "sensor.robot_error": {
            state: "mop_removed",
            attributes: {},
          },
        },
      },
      {
        entity: "sensor.robot_queue_status",
      },
    );

    expect(view.summary).toBe("mop removed");
    expect(view.activity).toEqual({
      phase: "error",
      label: "mop removed",
    });
    expect(view.activeControls).toEqual([
      {
        ariaLabel: "Continue robot run",
        label: "Continue",
        service: "resume_queue",
      },
      {
        ariaLabel: "End robot run",
        label: "End",
        service: "cancel_queue",
      },
    ]);
  });

  it("disables robot command controls when the command gate is closed", () => {
    const view = buildCardViewModel(
      hassWithQueueState("idle", {
        allow_robot_commands: false,
        queue_items: [queueAttributes.queue_items[1]],
        pending_items: 1,
        running_items: 0,
        total_items: 1,
      }),
      {
        entity: "sensor.robot_queue_status",
      },
    );

    expect(view.activeControls).toEqual([
      {
        ariaLabel: "Start queue",
        disabled: true,
        disabledReason: "Robot commands disabled",
        label: "Start",
        service: "start_queue",
      },
    ]);
  });

  it("summarizes completed queues without active controls", () => {
    const view = buildCardViewModel(
      hassWithQueueState("completed", {
        queue_items: [
          {
            item_id: "item-1",
            room_id: 1,
            room_name: "Kitchen",
            status: "completed",
          },
        ],
        pending_items: 0,
        running_items: 0,
        completed_items: 1,
        total_items: 1,
      }),
      {
        entity: "sensor.robot_queue_status",
      },
    );

    expect(view.summary).toBe("Queue completed.");
    expect(view.activeControls).toEqual([]);
  });

  it("surfaces failure states without offering unsafe active controls", () => {
    const outOfSync = buildCardViewModel(
      hassWithQueueState("out_of_sync", {
        queue_items: [queueAttributes.queue_items[1]],
        pending_items: 1,
        running_items: 0,
        total_items: 1,
      }),
      {
        entity: "sensor.robot_queue_status",
      },
    );
    const blocked = buildCardViewModel(
      hassWithQueueState("blocked", {
        queue_items: [queueAttributes.queue_items[1]],
        pending_items: 1,
        running_items: 0,
        total_items: 1,
      }),
      {
        entity: "sensor.robot_queue_status",
      },
    );

    expect(outOfSync.summary).toBe("Queue out of sync. Review robot state before restarting.");
    expect(outOfSync.activeControls).toEqual([]);
    expect(blocked.summary).toBe("Route blocked. Review room access before restarting.");
    expect(blocked.activeControls).toEqual([]);
  });

  it("hides running override controls when companion entities are missing", () => {
    const view = buildCardViewModel(
      {
        ...hass,
        states: {
          ...hass.states,
          "select.robot_suction_level": undefined,
          "number.robot_wetness_level": undefined,
        },
      },
      {
        entity: "sensor.robot_queue_status",
      },
    );

    expect(view.rows[0].status).toBe("running");
    expect(view.rows[0].overrideControls).toEqual([]);
  });
});

function hassWithQueueState(
  state: string,
  attributes: Record<string, unknown>,
): typeof hass {
  return {
    ...hass,
    states: {
      ...hass.states,
      "sensor.robot_queue_status": {
        state,
        attributes: {
          ...queueAttributes,
          ...attributes,
        },
      },
    },
  };
}
