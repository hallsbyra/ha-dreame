// @vitest-environment happy-dom

import { describe, expect, it, vi } from "vitest";

import { CARD_ELEMENT_TAG } from "../src/card-view";
import "../src/ha-dreame-queue-card";

const hass = {
  states: {
    "sensor.robot_queue_status": {
      state: "running",
      attributes: {
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
      },
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

const idleHass = {
  ...hass,
  states: {
    ...hass.states,
    "sensor.robot_queue_status": {
      state: "idle",
      attributes: {
        ...hass.states["sensor.robot_queue_status"].attributes,
        queue_items: [
          {
            item_id: "item-2",
            room_id: 2,
            room_name: "Hallway",
            status: "pending",
          },
        ],
        pending_items: 1,
        running_items: 0,
        completed_items: 0,
        total_items: 1,
      },
    },
  },
};

describe("ha-dreame-queue-card", () => {
  it("registers the standalone HA Dreame card element", () => {
    expect(customElements.get(CARD_ELEMENT_TAG)).toBeDefined();
  });

  it("renders a read-only queue summary", async () => {
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = hass;
    document.body.append(element);

    await element.updateComplete;

    expect(element.shadowRoot?.textContent).toContain("Robot queue");
    expect(element.shadowRoot?.textContent).toContain("Running");
    expect(element.shadowRoot?.textContent).toContain("Vacuuming + mopping");
    expect(element.shadowRoot?.textContent).toContain("Kitchen");
    expect(element.shadowRoot?.textContent).toContain("Available rooms");
    expect(element.shadowRoot?.textContent).toContain("Hallway");
  });

  it("renders terminal queue state guidance without start controls", async () => {
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = {
      ...hass,
      states: {
        ...hass.states,
        "sensor.robot_queue_status": {
          state: "out_of_sync",
          attributes: {
            ...hass.states["sensor.robot_queue_status"].attributes,
            pending_items: 1,
            running_items: 0,
          },
        },
      },
    };
    document.body.append(element);

    await element.updateComplete;

    expect(element.shadowRoot?.textContent).toContain(
      "Queue out of sync. Review robot state before restarting.",
    );
    expect(
      element.shadowRoot?.querySelector<HTMLButtonElement>('button[aria-label="Start queue"]'),
    ).toBeNull();
  });

  it("adds an available room through the ha_dreame queue service", async () => {
    const callService = vi.fn();
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = { ...hass, callService };
    document.body.append(element);

    await element.updateComplete;

    const shadowRoot = element.shadowRoot as ShadowRoot | null;
    const buttons = Array.from(
      shadowRoot?.querySelectorAll("button.room-chip") ?? [],
    ) as HTMLButtonElement[];
    const hallwayButton = buttons.find((button) => button.textContent?.includes("Hallway"));

    expect(hallwayButton).toBeDefined();
    hallwayButton?.click();

    expect(callService).toHaveBeenCalledWith("ha_dreame", "add_queue_room", {
      config_entry_id: "config-entry-1",
      room_id: 2,
      room_name: "Hallway",
    });
  });

  it("removes a pending queue item through the ha_dreame queue service", async () => {
    const callService = vi.fn();
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = { ...hass, callService };
    document.body.append(element);

    await element.updateComplete;

    const shadowRoot = element.shadowRoot as ShadowRoot | null;
    const runningRemove = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Remove Kitchen"]',
    );
    const pendingRemove = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Remove Hallway"]',
    );

    expect(runningRemove).toBeNull();
    expect(pendingRemove).toBeDefined();
    pendingRemove?.click();

    expect(callService).toHaveBeenCalledWith("ha_dreame", "remove_queue_item", {
      config_entry_id: "config-entry-1",
      item_id: "item-2",
    });
  });

  it("moves pending queue items through the ha_dreame queue service", async () => {
    const callService = vi.fn();
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = { ...hass, callService };
    document.body.append(element);

    await element.updateComplete;

    const shadowRoot = element.shadowRoot as ShadowRoot | null;
    const runningMoveUp = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Move Kitchen up"]',
    );
    const hallwayMoveUp = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Move Hallway up"]',
    );
    const hallwayMoveDown = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Move Hallway down"]',
    );
    const officeMoveUp = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Move Office up"]',
    );
    const officeMoveDown = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Move Office down"]',
    );

    expect(runningMoveUp).toBeNull();
    expect(hallwayMoveUp).toBeNull();
    expect(hallwayMoveDown).toBeDefined();
    expect(officeMoveUp).toBeDefined();
    expect(officeMoveDown).toBeNull();

    officeMoveUp?.click();
    hallwayMoveDown?.click();

    expect(callService).toHaveBeenNthCalledWith(1, "ha_dreame", "move_queue_item", {
      config_entry_id: "config-entry-1",
      item_id: "item-3",
      new_position: 1,
    });
    expect(callService).toHaveBeenNthCalledWith(2, "ha_dreame", "move_queue_item", {
      config_entry_id: "config-entry-1",
      item_id: "item-2",
      new_position: 2,
    });
  });

  it("clears pending queue items through the ha_dreame queue service", async () => {
    const callService = vi.fn();
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = { ...hass, callService };
    document.body.append(element);

    await element.updateComplete;

    const shadowRoot = element.shadowRoot as ShadowRoot | null;
    const clearPending = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Clear pending queue"]',
    );

    expect(clearPending).toBeDefined();
    clearPending?.click();

    expect(callService).toHaveBeenCalledWith("ha_dreame", "clear_pending_queue", {
      config_entry_id: "config-entry-1",
    });
  });

  it("cycles pending queue item overrides through the ha_dreame queue service", async () => {
    const callService = vi.fn();
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = { ...hass, callService };
    document.body.append(element);

    await element.updateComplete;

    const shadowRoot = element.shadowRoot as ShadowRoot | null;
    const runningWater = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Kitchen water volume"]',
    );
    const hallwayWater = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Hallway water volume"]',
    );
    const hallwaySuction = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Hallway suction level"]',
    );
    const hallwayRepeats = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Hallway repeats"]',
    );

    expect(runningWater).toBeNull();
    expect(hallwayWater).not.toBeNull();
    expect(hallwaySuction).not.toBeNull();
    expect(hallwayRepeats).not.toBeNull();
    expect(hallwayWater!.textContent).toContain("Water Med");
    expect(hallwaySuction!.textContent).toContain("Suction Med");
    expect(hallwayRepeats!.textContent).toContain("Repeats x2");

    hallwayWater!.click();
    hallwaySuction!.click();
    hallwayRepeats!.click();

    expect(callService).toHaveBeenNthCalledWith(1, "ha_dreame", "update_queue_item_overrides", {
      config_entry_id: "config-entry-1",
      item_id: "item-2",
      overrides: {
        repeats: 2,
        suction_level: 1,
        water_volume: 3,
      },
    });
    expect(callService).toHaveBeenNthCalledWith(2, "ha_dreame", "update_queue_item_overrides", {
      config_entry_id: "config-entry-1",
      item_id: "item-2",
      overrides: {
        repeats: 2,
        suction_level: 2,
        water_volume: 2,
      },
    });
    expect(callService).toHaveBeenNthCalledWith(3, "ha_dreame", "update_queue_item_overrides", {
      config_entry_id: "config-entry-1",
      item_id: "item-2",
      overrides: {
        repeats: 3,
        suction_level: 1,
        water_volume: 2,
      },
    });
  });

  it("starts an idle queue through the command-gated ha_dreame queue service", async () => {
    const callService = vi.fn();
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = { ...idleHass, callService };
    document.body.append(element);

    await element.updateComplete;

    const shadowRoot = element.shadowRoot as ShadowRoot | null;
    const startQueue = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Start queue"]',
    );
    const cancelQueue = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cancel queue"]',
    );
    const skipCurrentRoom = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Skip current room"]',
    );

    expect(startQueue).not.toBeNull();
    expect(cancelQueue).toBeNull();
    expect(skipCurrentRoom).toBeNull();

    startQueue!.click();

    expect(callService).toHaveBeenCalledWith("ha_dreame", "start_queue", {
      config_entry_id: "config-entry-1",
    });
  });

  it("cancels and skips a running queue through command-gated ha_dreame services", async () => {
    const callService = vi.fn();
    const element = document.createElement(CARD_ELEMENT_TAG) as any;
    element.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    element.hass = { ...hass, callService };
    document.body.append(element);

    await element.updateComplete;

    const shadowRoot = element.shadowRoot as ShadowRoot | null;
    const startQueue = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Start queue"]',
    );
    const cancelQueue = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cancel queue"]',
    );
    const skipCurrentRoom = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Skip current room"]',
    );

    expect(startQueue).toBeNull();
    expect(cancelQueue).not.toBeNull();
    expect(skipCurrentRoom).not.toBeNull();

    cancelQueue!.click();
    skipCurrentRoom!.click();

    expect(callService).toHaveBeenNthCalledWith(1, "ha_dreame", "cancel_queue", {
      config_entry_id: "config-entry-1",
    });
    expect(callService).toHaveBeenNthCalledWith(2, "ha_dreame", "skip_current_room", {
      config_entry_id: "config-entry-1",
    });
  });
});
