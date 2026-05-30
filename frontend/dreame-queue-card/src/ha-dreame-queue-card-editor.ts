import { LitElement, css, html } from "lit";

import {
  CARD_EDITOR_TAG,
  DEFAULT_CARD_TITLE,
  queueStatusEntityIds,
  type HaDreameQueueCardConfig,
  type HomeAssistantLike,
} from "./card-view";

class HaDreameQueueCardEditor extends LitElement {
  static properties = {
    hass: { attribute: false },
    _config: { state: true },
  };

  static styles = css`
    :host {
      display: block;
    }

    .editor {
      display: grid;
      gap: 12px;
    }

    label {
      color: var(--primary-text-color);
      display: grid;
      font-size: 0.86rem;
      font-weight: 600;
      gap: 5px;
      line-height: 1.25;
    }

    input {
      background: var(--card-background-color, transparent);
      border: 1px solid var(--divider-color);
      border-radius: 6px;
      box-sizing: border-box;
      color: var(--primary-text-color);
      font: inherit;
      min-width: 0;
      padding: 8px 9px;
      width: 100%;
    }

    .hint {
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      font-weight: 400;
      line-height: 1.3;
    }
  `;

  hass?: HomeAssistantLike;
  private _config: HaDreameQueueCardConfig = {};

  setConfig(config: HaDreameQueueCardConfig): void {
    this._config = { ...config };
  }

  protected render() {
    const candidates = queueStatusEntityIds(this.hass);

    return html`
      <div class="editor">
        <label>
          Queue entity
          <input
            list="ha-dreame-queue-entities"
            name="entity"
            placeholder="sensor.ha_dreame_queue_status"
            .value=${this._config.entity ?? ""}
            @input=${(event: Event) => this._fieldChanged("entity", event)}
          />
        </label>
        <datalist id="ha-dreame-queue-entities">
          ${candidates.map((entityId) => html`<option value=${entityId}></option>`)}
        </datalist>
        <label>
          Title
          <input
            name="title"
            placeholder=${DEFAULT_CARD_TITLE}
            .value=${this._config.title ?? ""}
            @input=${(event: Event) => this._fieldChanged("title", event)}
          />
          <span class="hint">Leave empty to use the default card title.</span>
        </label>
      </div>
    `;
  }

  private _fieldChanged(field: "entity" | "title", event: Event): void {
    const value = ((event.target as HTMLInputElement | null)?.value ?? "").trim();
    const nextConfig: HaDreameQueueCardConfig = { ...this._config };

    if (value) {
      nextConfig[field] = value;
    } else {
      delete nextConfig[field];
    }

    this._config = nextConfig;
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        bubbles: true,
        composed: true,
        detail: { config: nextConfig },
      }),
    );
  }
}

if (!customElements.get(CARD_EDITOR_TAG)) {
  customElements.define(CARD_EDITOR_TAG, HaDreameQueueCardEditor);
}
