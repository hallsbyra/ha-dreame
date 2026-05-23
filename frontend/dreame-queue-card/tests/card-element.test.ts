// @vitest-environment happy-dom

import { describe, expect, it } from "vitest";

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
        ],
        pending_items: 0,
        running_items: 1,
        completed_items: 0,
        total_items: 1,
        vacuum_entity_id: "vacuum.robot",
      },
    },
    "vacuum.robot": {
      state: "cleaning",
      attributes: {},
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
  });
});
