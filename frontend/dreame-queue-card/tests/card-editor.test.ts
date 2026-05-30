// @vitest-environment happy-dom

import { describe, expect, it } from "vitest";

import { CARD_EDITOR_TAG, type HaDreameQueueCardConfig } from "../src/card-view";
import "../src/ha-dreame-queue-card-editor";

const hass = {
  states: {
    "sensor.robot_queue_status": {
      state: "idle",
      attributes: {
        queue_items: [],
        config_entry_id: "config-entry-1",
      },
    },
    "sensor.temperature": {
      state: "21",
      attributes: {},
    },
  },
};

describe("ha-dreame-queue-card-editor", () => {
  it("registers the Lovelace card editor element", () => {
    expect(customElements.get(CARD_EDITOR_TAG)).toBeDefined();
  });

  it("renders entity and title fields with queue entity suggestions", async () => {
    const editor = document.createElement(CARD_EDITOR_TAG) as any;
    editor.hass = hass;
    editor.setConfig({
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    document.body.append(editor);

    await editor.updateComplete;

    const shadowRoot = editor.shadowRoot as ShadowRoot | null;
    const entityInput = shadowRoot?.querySelector<HTMLInputElement>('input[name="entity"]');
    const titleInput = shadowRoot?.querySelector<HTMLInputElement>('input[name="title"]');
    const suggestions = Array.from(
      shadowRoot?.querySelectorAll<HTMLOptionElement>("datalist option") ?? [],
    ).map((option) => option.value);

    expect(entityInput?.value).toBe("sensor.robot_queue_status");
    expect(titleInput?.value).toBe("Robot queue");
    expect(suggestions).toEqual(["sensor.robot_queue_status"]);
  });

  it("emits Lovelace config changes when fields update", async () => {
    const editor = document.createElement(CARD_EDITOR_TAG) as any;
    const changes: HaDreameQueueCardConfig[] = [];
    editor.hass = hass;
    editor.setConfig({
      type: "custom:ha-dreame-queue-card",
      entity: "sensor.robot_queue_status",
      title: "Robot queue",
    });
    editor.addEventListener("config-changed", (event: Event) => {
      changes.push((event as CustomEvent<{ config: HaDreameQueueCardConfig }>).detail.config);
    });
    document.body.append(editor);

    await editor.updateComplete;

    const shadowRoot = editor.shadowRoot as ShadowRoot | null;
    const entityInput = shadowRoot?.querySelector<HTMLInputElement>('input[name="entity"]');
    const titleInput = shadowRoot?.querySelector<HTMLInputElement>('input[name="title"]');

    entityInput!.value = "sensor.other_queue_status";
    entityInput!.dispatchEvent(new Event("input", { bubbles: true }));
    titleInput!.value = "";
    titleInput!.dispatchEvent(new Event("input", { bubbles: true }));

    expect(changes).toEqual([
      {
        type: "custom:ha-dreame-queue-card",
        entity: "sensor.other_queue_status",
        title: "Robot queue",
      },
      {
        type: "custom:ha-dreame-queue-card",
        entity: "sensor.other_queue_status",
      },
    ]);
  });
});
