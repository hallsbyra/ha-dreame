// @vitest-environment happy-dom

import { describe, expect, it } from "vitest";

import "../../../custom_components/ha_dreame/frontend/ha-dreame-queue-card.js";

describe("packaged HA Dreame queue card", () => {
  it("keeps room names and queue fields bound to their own labels", async () => {
    const card = document.createElement("ha-dreame-queue-card") as any;
    card.setConfig({ entity: "sensor.test_queue", title: "Musse" });
    card.hass = {
      states: {
        "sensor.test_queue": {
          state: "completed",
          attributes: {
            config_entry_id: "test-entry",
            vacuum_entity_id: "vacuum.musse",
            queue_items: [
              {
                item_id: "item-1",
                room_id: 1,
                room_name: "Glasverandan",
                status: "completed",
              },
            ],
            pending_items: 0,
            running_items: 0,
            completed_items: 1,
            total_items: 1,
          },
        },
        "vacuum.musse": {
          state: "docked",
          attributes: {
            rooms: {
              Nere: [{ id: 1, name: "Glasverandan" }],
            },
          },
        },
      },
    };
    document.body.append(card);

    await card.updateComplete;

    const shadowRoot = card.shadowRoot as ShadowRoot;
    expect(
      Array.from(shadowRoot.querySelectorAll(".room-chip")).map((button) =>
        button.textContent?.trim(),
      ),
    ).toEqual(["Glasverandan"]);
    expect(shadowRoot.querySelector(".room-name")?.textContent?.trim()).toBe("1. Glasverandan");
    expect(shadowRoot.querySelector(".row-status")?.textContent?.trim()).toBe("Completed");
  });
});
