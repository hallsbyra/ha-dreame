import { LitElement, css, html, nothing } from "lit";

import {
  buildCardViewModel,
  CARD_ELEMENT_TAG,
  type HaDreameQueueCardConfig,
  type HomeAssistantLike,
} from "./card-view";
import { cycledOverrides, type OverrideField } from "./queue-overrides";

class HaDreameQueueCard extends LitElement {
  static properties = {
    hass: { attribute: false },
    _config: { state: true },
  };

  static styles = css`
    :host {
      display: block;
    }

    ha-card {
      display: block;
      padding: 14px;
    }

    .header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: start;
      gap: 10px;
      margin-bottom: 12px;
    }

    .title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .subtitle {
      margin: 3px 0 0;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .state-pill {
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.2;
      padding: 4px 9px;
      white-space: nowrap;
    }

    .state-pill.running {
      border-color: var(--state-active-color, #2e7d32);
      color: var(--state-active-color, #2e7d32);
    }

    .state-pill.blocked,
    .state-pill.out_of_sync,
    .state-pill.error {
      border-color: var(--error-color, #d32f2f);
      color: var(--error-color, #d32f2f);
    }

    .message {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      color: var(--secondary-text-color);
      font-size: 0.86rem;
      line-height: 1.35;
      padding: 10px;
    }

    .counts {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 8px;
    }

    .count {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      min-width: 0;
      padding: 7px 8px;
    }

    .count-value {
      display: block;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.1;
    }

    .count-label {
      color: var(--secondary-text-color);
      display: block;
      font-size: 0.72rem;
      line-height: 1.2;
      margin-top: 3px;
      overflow-wrap: anywhere;
    }

    .queue-list {
      display: grid;
      gap: 6px;
    }

    .queue-actions {
      display: flex;
      justify-content: flex-end;
      margin: 0 0 12px;
    }

    .section-title {
      color: var(--secondary-text-color);
      font-size: 0.74rem;
      font-weight: 600;
      line-height: 1.2;
      margin: 12px 0 6px;
      text-transform: uppercase;
    }

    .room-catalog {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .room-chip {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.78rem;
      line-height: 1.2;
      max-width: 100%;
      overflow: hidden;
      padding: 5px 9px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .room-chip:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }

    .queue-row {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      display: grid;
      gap: 8px;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      min-height: 34px;
      padding: 7px 9px;
    }

    .room-name {
      font-size: 0.88rem;
      font-weight: 600;
      line-height: 1.25;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .row-status {
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      white-space: nowrap;
    }

    .row-actions {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      justify-content: flex-end;
    }

    .row-action {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.74rem;
      line-height: 1.2;
      padding: 3px 8px;
      white-space: nowrap;
    }

    .row-action:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }
  `;

  hass?: HomeAssistantLike;
  private _config: HaDreameQueueCardConfig = {};

  setConfig(config: HaDreameQueueCardConfig): void {
    if (!config || typeof config !== "object") {
      throw new Error("Invalid HA Dreame queue card configuration");
    }
    this._config = { ...config };
  }

  getCardSize(): number {
    return 3;
  }

  protected render() {
    const view = buildCardViewModel(this.hass, this._config);
    const snapshot = view.snapshot;

    return html`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${view.title}</h2>
            <p class="subtitle">${view.activity?.label ?? view.entityId ?? "Read-only queue"}</p>
          </div>
          ${snapshot
            ? html`<span class="state-pill ${snapshot.runState}"
                >${this._stateLabel(snapshot.runState)}</span
              >`
            : nothing}
        </div>

        ${view.message
          ? html`<div class="message">${view.message}</div>`
          : html`
              <div class="counts">
                ${this._count("Pending", snapshot?.pendingItems ?? 0)}
                ${this._count("Running", snapshot?.runningItems ?? 0)}
                ${this._count("Done", snapshot?.completedItems ?? 0)}
                ${this._count("Total", snapshot?.totalItems ?? 0)}
              </div>
              ${view.canClearPending
                ? html`
                    <div class="queue-actions">
                      <button
                        aria-label="Clear pending queue"
                        class="row-action"
                        type="button"
                        ?disabled=${!snapshot?.configEntryId}
                        @click=${() => this._clearPending(snapshot?.configEntryId)}
                      >
                        Clear pending
                      </button>
                    </div>
                  `
                : nothing}
              <div class="queue-list">
                ${view.rows.length
                  ? view.rows.map(
                      (row) => html`
                        <div class="queue-row">
                          <span class="room-name">${row.roomName}</span>
                          <div class="row-actions">
                            <span class="row-status">${row.statusLabel}</span>
                            ${row.overrideControls.map(
                              (control) => html`
                                <button
                                  aria-label=${`Cycle ${row.roomName} ${this._overrideAriaField(
                                    control.field,
                                  )}`}
                                  class="row-action"
                                  type="button"
                                  ?disabled=${!snapshot?.configEntryId}
                                  @click=${() =>
                                    this._updateOverrides(
                                      snapshot?.configEntryId,
                                      row.itemId,
                                      control.field,
                                      row.overrides,
                                    )}
                                >
                                  ${control.label} ${control.valueLabel}
                                </button>
                              `,
                            )}
                            ${row.canMoveUp
                              ? html`
                                  <button
                                    aria-label=${`Move ${row.roomName} up`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!snapshot?.configEntryId}
                                    @click=${() =>
                                      this._moveItem(
                                        snapshot?.configEntryId,
                                        row.itemId,
                                        row.queuePosition - 1,
                                      )}
                                  >
                                    Up
                                  </button>
                                `
                              : nothing}
                            ${row.canMoveDown
                              ? html`
                                  <button
                                    aria-label=${`Move ${row.roomName} down`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!snapshot?.configEntryId}
                                    @click=${() =>
                                      this._moveItem(
                                        snapshot?.configEntryId,
                                        row.itemId,
                                        row.queuePosition + 1,
                                      )}
                                  >
                                    Down
                                  </button>
                                `
                              : nothing}
                            ${row.canRemove
                              ? html`
                                  <button
                                    aria-label=${`Remove ${row.roomName}`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!snapshot?.configEntryId}
                                    @click=${() =>
                                      this._removeItem(snapshot?.configEntryId, row.itemId)}
                                  >
                                    Remove
                                  </button>
                                `
                              : nothing}
                          </div>
                        </div>
                      `,
                    )
                  : html`<div class="message">Queue is empty.</div>`}
              </div>
              ${view.rooms.length
                ? html`
                    <div class="section-title">Available rooms</div>
                    <div class="room-catalog">
                      ${view.rooms.map(
                        (room) => html`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!snapshot?.configEntryId}
                            @click=${() =>
                              this._addRoom(
                                snapshot?.configEntryId,
                                room.roomId,
                                room.roomName,
                              )}
                          >
                            ${room.roomName}
                          </button>
                        `,
                      )}
                    </div>
                  `
                : nothing}
            `}
      </ha-card>
    `;
  }

  private _count(label: string, value: number) {
    return html`
      <div class="count">
        <span class="count-value">${value}</span>
        <span class="count-label">${label}</span>
      </div>
    `;
  }

  private _stateLabel(runState: string): string {
    return runState
      .split("_")
      .filter((part) => part.length > 0)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }

  private _addRoom(
    configEntryId: string | null | undefined,
    roomId: number,
    roomName: string,
  ): void {
    if (!configEntryId || !this.hass?.callService) {
      return;
    }

    void this.hass.callService("ha_dreame", "add_queue_room", {
      config_entry_id: configEntryId,
      room_id: roomId,
      room_name: roomName,
    });
  }

  private _removeItem(configEntryId: string | null | undefined, itemId: string): void {
    if (!configEntryId || !this.hass?.callService) {
      return;
    }

    void this.hass.callService("ha_dreame", "remove_queue_item", {
      config_entry_id: configEntryId,
      item_id: itemId,
    });
  }

  private _moveItem(
    configEntryId: string | null | undefined,
    itemId: string,
    newPosition: number,
  ): void {
    if (!configEntryId || !this.hass?.callService) {
      return;
    }

    void this.hass.callService("ha_dreame", "move_queue_item", {
      config_entry_id: configEntryId,
      item_id: itemId,
      new_position: newPosition,
    });
  }

  private _clearPending(configEntryId: string | null | undefined): void {
    if (!configEntryId || !this.hass?.callService) {
      return;
    }

    void this.hass.callService("ha_dreame", "clear_pending_queue", {
      config_entry_id: configEntryId,
    });
  }

  private _updateOverrides(
    configEntryId: string | null | undefined,
    itemId: string,
    field: OverrideField,
    overrides: Record<string, unknown>,
  ): void {
    if (!configEntryId || !this.hass?.callService) {
      return;
    }

    void this.hass.callService("ha_dreame", "update_queue_item_overrides", {
      config_entry_id: configEntryId,
      item_id: itemId,
      overrides: cycledOverrides(field, overrides, {}),
    });
  }

  private _overrideAriaField(field: OverrideField): string {
    if (field === "water_volume") {
      return "water volume";
    }
    if (field === "suction_level") {
      return "suction level";
    }
    return "repeats";
  }
}

if (!customElements.get(CARD_ELEMENT_TAG)) {
  customElements.define(CARD_ELEMENT_TAG, HaDreameQueueCard);
}

declare global {
  interface Window {
    customCards?: Array<Record<string, string>>;
  }
}

window.customCards = window.customCards ?? [];
if (!window.customCards.some((card) => card["type"] === CARD_ELEMENT_TAG)) {
  window.customCards.push({
    type: CARD_ELEMENT_TAG,
    name: "HA Dreame Queue",
    description: "Read-only queue summary for HA Dreame.",
  });
}
