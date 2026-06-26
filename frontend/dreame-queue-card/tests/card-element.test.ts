// @vitest-environment happy-dom

import { describe, expect, it, vi } from "vitest";

import {
  CARD_EDITOR_TAG,
  CARD_ELEMENT_TAG,
  type HaDreameQueueCardConfig,
  type HomeAssistantLike,
} from "../src/card-view";
import "../src/ha-dreame-queue-card";

type QueueCardConstructor = CustomElementConstructor & {
  getConfigElement: () => Promise<HTMLElement>;
  getStubConfig: (hass?: HomeAssistantLike) => HaDreameQueueCardConfig;
};

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

function queueCardConstructor(): QueueCardConstructor {
  return customElements.get(CARD_ELEMENT_TAG) as unknown as QueueCardConstructor;
}

describe("ha-dreame-queue-card", () => {
  it("registers the standalone HA Dreame card element", () => {
    expect(customElements.get(CARD_ELEMENT_TAG)).toBeDefined();
  });

  it("provides a Lovelace stub config from the public queue sensor shape", () => {
    const cardClass = queueCardConstructor();

    expect(cardClass.getStubConfig(hass)).toEqual({
      entity: "sensor.robot_queue_status",
    });
  });

  it("falls back to a generic public-safe stub config", () => {
    const cardClass = queueCardConstructor();

    expect(cardClass.getStubConfig({ states: {} })).toEqual({
      entity: "sensor.ha_dreame_queue_status",
    });
  });

  it("creates a Lovelace config editor element", async () => {
    const cardClass = queueCardConstructor();

    const editor = await cardClass.getConfigElement();

    expect(editor.tagName.toLowerCase()).toBe(CARD_EDITOR_TAG);
  });

  it("reports a masonry size that fits the room catalog and queue controls", () => {
    const element = document.createElement(CARD_ELEMENT_TAG) as any;

    expect(element.getCardSize()).toBe(6);
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

    const shadowRoot = element.shadowRoot as ShadowRoot | null;
    expect(element.shadowRoot?.textContent).toContain(
      "Queue out of sync. Review robot state before restarting.",
    );
    expect(
      shadowRoot?.querySelector<HTMLButtonElement>('button[aria-label="Start queue"]'),
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
    expect(hallwayButton?.querySelector("ha-icon")?.getAttribute("icon")).toBe("mdi:plus");
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
    expect(hallwayMoveDown?.querySelector("ha-icon")?.getAttribute("icon")).toBe(
      "mdi:arrow-down",
    );
    expect(officeMoveUp?.querySelector("ha-icon")?.getAttribute("icon")).toBe("mdi:arrow-up");

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

  it("cycles running overrides through the command-gated ha_dreame service", async () => {
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
    const runningSuction = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Kitchen suction level"]',
    );
    const runningRepeats = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Kitchen repeats"]',
    );

    expect(runningWater).not.toBeNull();
    expect(runningSuction).not.toBeNull();
    expect(runningRepeats).toBeNull();
    expect(runningWater!.querySelectorAll(".override-bar.active")).toHaveLength(2);
    expect(runningSuction!.querySelectorAll(".override-bar.active")).toHaveLength(1);

    runningWater!.click();
    runningSuction!.click();

    expect(callService).toHaveBeenNthCalledWith(1, "ha_dreame", "update_running_override", {
      config_entry_id: "config-entry-1",
      field: "water_volume",
      value: 3,
    });
    expect(callService).toHaveBeenNthCalledWith(2, "ha_dreame", "update_running_override", {
      config_entry_id: "config-entry-1",
      field: "suction_level",
      value: 1,
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
    const hallwayWater = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Hallway water volume"]',
    );
    const hallwaySuction = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Hallway suction level"]',
    );
    const hallwayRepeats = shadowRoot?.querySelector<HTMLButtonElement>(
      'button[aria-label="Cycle Hallway repeats"]',
    );

    expect(hallwayWater).not.toBeNull();
    expect(hallwaySuction).not.toBeNull();
    expect(hallwayRepeats).not.toBeNull();
    expect(hallwayWater!.querySelector("ha-icon")?.getAttribute("icon")).toBe(
      "mdi:water-percent",
    );
    expect(hallwayWater!.querySelectorAll(".override-bar.active")).toHaveLength(2);
    expect(hallwaySuction!.querySelector("ha-icon")?.getAttribute("icon")).toBe("mdi:fan");
    expect(hallwaySuction!.querySelectorAll(".override-bar.active")).toHaveLength(2);
    expect(hallwayRepeats!.querySelector("ha-icon")?.getAttribute("icon")).toBe("mdi:repeat");
    expect(hallwayRepeats!.textContent).toContain("x2");

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
    expect(startQueue!.querySelector("ha-icon")?.getAttribute("icon")).toBe("mdi:play");

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
    expect(cancelQueue!.querySelector("ha-icon")?.getAttribute("icon")).toBe("mdi:stop");
    expect(skipCurrentRoom!.querySelector("ha-icon")?.getAttribute("icon")).toBe(
      "mdi:skip-next",
    );

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
