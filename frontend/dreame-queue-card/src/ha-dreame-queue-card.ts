import { LitElement, css, html, nothing } from "lit";

import {
  buildCardViewModel,
  CARD_EDITOR_TAG,
  CARD_ELEMENT_TAG,
  defaultCardConfig,
  type ActiveQueueService,
  type CardOverrideControl,
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
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
    }

    .header-right {
      align-items: center;
      display: inline-flex;
      gap: 6px;
      min-width: 0;
    }

    .header-actions {
      align-items: center;
      display: inline-flex;
      gap: 4px;
    }

    .title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .activity-line {
      color: var(--secondary-text-color);
      font-size: 0.86rem;
      line-height: 1.25;
      margin: 3px 0 0;
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

    .empty {
      color: var(--secondary-text-color);
      font-size: 0.9rem;
      line-height: 1.35;
    }

    .room-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }

    .section-title {
      color: var(--secondary-text-color);
      font-size: 0.74rem;
      font-weight: 600;
      line-height: 1.2;
      margin: 12px 0 6px;
      text-transform: uppercase;
    }

    .room-chip {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: inherit;
      font-size: 0.84rem;
      line-height: 1;
      max-width: 100%;
      overflow: hidden;
      padding: 7px 11px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .room-chip:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }

    .room-chip:not(:disabled):hover,
    .override-btn:not(:disabled):hover,
    .icon-btn:not(:disabled):hover {
      background: color-mix(in srgb, var(--primary-color, #03a9f4) 10%, transparent);
    }

    .queue-list {
      display: grid;
      gap: 8px;
    }

    .queue-item {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      display: grid;
      gap: 8px;
      grid-template-columns: minmax(0, 1fr);
      padding: 8px 10px;
    }

    .queue-item.running {
      border-color: color-mix(in srgb, var(--state-active-color, #2e7d32) 45%, var(--divider-color));
    }

    .item-main,
    .item-title-block {
      min-width: 0;
    }

    .item-headline {
      align-items: center;
      display: flex;
      gap: 8px;
      justify-content: space-between;
    }

    .room-name {
      display: block;
      font-size: 0.96rem;
      font-weight: 600;
      line-height: 1.25;
      margin: 0;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .row-status {
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      text-align: left;
      text-transform: lowercase;
      white-space: nowrap;
    }

    .row-status.running {
      color: var(--state-active-color, #2e7d32);
    }

    .row-status.canceled,
    .row-status.blocked,
    .row-status.out_of_sync {
      color: var(--error-color, #d32f2f);
    }

    .item-actions {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }

    .progress {
      display: grid;
      gap: 4px;
      margin-top: 2px;
    }

    .progress-track {
      background: color-mix(in srgb, var(--divider-color) 55%, transparent);
      border-radius: 999px;
      height: 7px;
      overflow: hidden;
    }

    .progress-fill {
      background: var(--primary-color, #03a9f4);
      height: 100%;
      transition: width 180ms ease-out;
    }

    .progress-label {
      color: var(--secondary-text-color);
      font-size: 0.76rem;
      line-height: 1.2;
    }

    .item-queue-controls {
      align-items: center;
      display: flex;
      gap: 4px;
      justify-content: flex-end;
    }

    .override-controls {
      display: flex;
      flex: 1;
      flex-wrap: wrap;
      gap: 4px;
    }

    .icon-btn {
      align-items: center;
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      font-family: inherit;
      height: 32px;
      justify-content: center;
      padding: 0;
      width: 32px;
    }

    .icon-btn.delete {
      color: var(--error-color, #d32f2f);
    }

    .icon-btn:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
      opacity: 0.45;
    }

    .override-btn {
      align-items: center;
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      font-family: inherit;
      font-size: 0.72rem;
      gap: 6px;
      justify-content: center;
      line-height: 1.2;
      min-height: 26px;
      min-width: 68px;
      padding: 2px 8px;
      white-space: nowrap;
    }

    .override-btn:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
      opacity: 0.5;
    }

    .override-bars {
      align-items: flex-end;
      display: inline-flex;
      gap: 2px;
    }

    .override-bar {
      background: color-mix(in srgb, var(--divider-color) 80%, transparent);
      border-radius: 999px;
      width: 3px;
    }

    .override-bar.active {
      background: var(--primary-color, #03a9f4);
    }
  `;

  hass?: HomeAssistantLike;
  private _config: HaDreameQueueCardConfig = {};

  static async getConfigElement(): Promise<HTMLElement> {
    await import("./ha-dreame-queue-card-editor");
    return document.createElement(CARD_EDITOR_TAG);
  }

  static getStubConfig(hass?: HomeAssistantLike): HaDreameQueueCardConfig {
    return defaultCardConfig(hass);
  }

  setConfig(config: HaDreameQueueCardConfig): void {
    if (!config || typeof config !== "object") {
      throw new Error("Invalid HA Dreame queue card configuration");
    }
    this._config = { ...config };
  }

  getCardSize(): number {
    return 6;
  }

  protected render() {
    const view = buildCardViewModel(this.hass, this._config);
    const snapshot = view.snapshot;
    const configEntryId = snapshot?.configEntryId;

    return html`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${view.title}</h2>
            <p class="activity-line">${view.summary ?? view.entityId ?? "Queue controls"}</p>
          </div>
          <div class="header-right">
            ${snapshot
              ? this._renderHeaderActions(
                  view.activeControls,
                  view.canClearPending,
                  configEntryId,
                )
              : nothing}
            ${snapshot
              ? html`<span class="state-pill ${snapshot.runState}"
                  >${this._stateLabel(snapshot.runState)}</span
                >`
              : nothing}
          </div>
        </div>

        ${view.message
          ? html`<div class="message">${view.message}</div>`
          : html`
              ${view.rooms.length
                ? html`
                    <div class="section-title">Available rooms</div>
                    <div class="room-actions">
                      ${view.rooms.map(
                        (room) => html`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!configEntryId}
                            @click=${() => this._addRoom(configEntryId, room.roomId, room.roomName)}
                          >
                            <ha-icon icon="mdi:plus"></ha-icon>
                            ${room.roomName}
                          </button>
                        `,
                      )}
                    </div>
                  `
                : nothing}
              <div class="queue-list">
                ${view.rows.length
                  ? view.rows.map(
                      (row) => html`
                        <div class="queue-item ${row.status}">
                          <div class="item-main">
                            <div class="item-headline">
                              <div class="item-title-block">
                                <span class="room-name"
                                  >${row.queuePosition + 1}. ${row.roomName}</span
                                >
                                <span class="row-status ${row.status}">${row.statusLabel}</span>
                              </div>
                              ${this._renderQueueItemActions(row, configEntryId)}
                            </div>
                            ${row.overrideControls.length
                              ? html`
                                  <div class="item-actions">
                                    <div class="override-controls">
                                      ${row.overrideControls.map((control) =>
                                        this._renderOverrideControl(
                                          row.roomName,
                                          row.itemId,
                                          row.overrides,
                                          control,
                                          configEntryId,
                                        ),
                                      )}
                                    </div>
                                  </div>
                                `
                              : nothing}
                            ${row.progress !== undefined
                              ? this._renderProgress(row.progress)
                              : nothing}
                          </div>
                        </div>
                      `,
                    )
                  : html`<div class="empty">Queue is empty.</div>`}
              </div>
            `}
      </ha-card>
    `;
  }

  private _renderProgress(progress: number) {
    return html`
      <div class="progress">
        <div
          aria-label="Room cleaning progress"
          aria-valuemax="100"
          aria-valuemin="0"
          aria-valuenow=${progress}
          class="progress-track"
          role="progressbar"
        >
          <div class="progress-fill" style=${`width: ${progress}%;`}></div>
        </div>
        <span class="progress-label">${progress}%</span>
      </div>
    `;
  }

  private _renderHeaderActions(
    controls: Array<{
      ariaLabel: string;
      disabled?: boolean;
      disabledReason?: string;
      service: ActiveQueueService;
    }>,
    canClearPending: boolean,
    configEntryId: string | null | undefined,
  ) {
    if (!controls.length && !canClearPending) {
      return nothing;
    }

    return html`
      <div class="header-actions">
        ${controls.map(
          (control) => html`
            <button
              aria-label=${control.ariaLabel}
              class="icon-btn ${control.service === "cancel_queue" ? "delete" : ""}"
              title=${control.disabledReason ?? control.ariaLabel}
              type="button"
              ?disabled=${!configEntryId || control.disabled === true}
              @click=${() => this._callQueueService(configEntryId, control.service)}
            >
              <ha-icon icon=${this._activeControlIcon(control.service)}></ha-icon>
            </button>
          `,
        )}
        ${canClearPending
          ? html`
              <button
                aria-label="Clear pending queue"
                class="icon-btn"
                title="Clear pending queue"
                type="button"
                ?disabled=${!configEntryId}
                @click=${() => this._clearPending(configEntryId)}
              >
                <ha-icon icon="mdi:playlist-remove"></ha-icon>
              </button>
            `
          : nothing}
      </div>
    `;
  }

  private _renderQueueItemActions(
    row: {
      canMoveDown: boolean;
      canMoveUp: boolean;
      canRemove: boolean;
      itemId: string;
      queuePosition: number;
      roomName: string;
    },
    configEntryId: string | null | undefined,
  ) {
    if (!row.canMoveUp && !row.canMoveDown && !row.canRemove) {
      return nothing;
    }

    return html`
      <div class="item-queue-controls">
        ${row.canMoveUp
          ? html`
              <button
                aria-label=${`Move ${row.roomName} up`}
                class="icon-btn"
                title="Move up"
                type="button"
                ?disabled=${!configEntryId}
                @click=${() => this._moveItem(configEntryId, row.itemId, row.queuePosition - 1)}
              >
                <ha-icon icon="mdi:arrow-up"></ha-icon>
              </button>
            `
          : nothing}
        ${row.canMoveDown
          ? html`
              <button
                aria-label=${`Move ${row.roomName} down`}
                class="icon-btn"
                title="Move down"
                type="button"
                ?disabled=${!configEntryId}
                @click=${() => this._moveItem(configEntryId, row.itemId, row.queuePosition + 1)}
              >
                <ha-icon icon="mdi:arrow-down"></ha-icon>
              </button>
            `
          : nothing}
        ${row.canRemove
          ? html`
              <button
                aria-label=${`Remove ${row.roomName}`}
                class="icon-btn delete"
                title="Remove"
                type="button"
                ?disabled=${!configEntryId}
                @click=${() => this._removeItem(configEntryId, row.itemId)}
              >
                <ha-icon icon="mdi:delete"></ha-icon>
              </button>
            `
          : nothing}
      </div>
    `;
  }

  private _renderOverrideControl(
    roomName: string,
    itemId: string,
    overrides: Record<string, unknown>,
    control: CardOverrideControl,
    configEntryId: string | null | undefined,
  ) {
    return html`
      <button
        aria-label=${`Cycle ${roomName} ${this._overrideAriaField(control.field)}`}
        class="override-btn"
        title=${`${control.label}: ${control.valueLabel}`}
        type="button"
        ?disabled=${!configEntryId}
        @click=${() =>
          this._cycleOverride(configEntryId, itemId, overrides, control)}
      >
        <ha-icon icon=${this._overrideIcon(control.field, control.valueLabel)}></ha-icon>
        ${this._renderOverrideValue(control.field, control.valueLabel)}
      </button>
    `;
  }

  private _renderOverrideValue(field: OverrideField, valueLabel: string) {
    if (field === "repeats") {
      return html`<span>${valueLabel}</span>`;
    }

    const total = field === "water_volume" ? 3 : 4;
    return this._renderBars(total, this._overrideActiveBars(field, valueLabel));
  }

  private _renderBars(total: number, active: number) {
    const normalizedActive = Math.max(0, Math.min(total, active));
    return html`
      <span class="override-bars" aria-hidden="true">
        ${Array.from({ length: total }, (_, index) => {
          const height = 6 + index * 2;
          const isActive = index < normalizedActive;
          return html`
            <span
              class="override-bar ${isActive ? "active" : ""}"
              style=${`height:${height}px;`}
            ></span>
          `;
        })}
      </span>
    `;
  }

  private _stateLabel(runState: string): string {
    return runState
      .split("_")
      .filter((part) => part.length > 0)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }

  private _activeControlIcon(service: ActiveQueueService): string {
    if (service === "start_queue" || service === "resume_queue") {
      return "mdi:play";
    }
    if (service === "skip_current_room") {
      return "mdi:skip-next";
    }
    return "mdi:stop";
  }

  private _overrideIcon(field: OverrideField, valueLabel: string): string {
    if (field === "water_volume") {
      return valueLabel === "Off" ? "mdi:water-off" : "mdi:water-percent";
    }
    if (field === "suction_level") {
      return valueLabel === "Off" ? "mdi:fan-off" : "mdi:fan";
    }
    return "mdi:repeat";
  }

  private _overrideActiveBars(field: OverrideField, valueLabel: string): number {
    if (valueLabel === "Off") {
      return 0;
    }
    if (field === "water_volume") {
      return { Min: 1, Med: 2, Max: 3 }[valueLabel] ?? 0;
    }
    if (field === "suction_level") {
      return { Min: 1, Med: 2, Max: 3, Turbo: 4 }[valueLabel] ?? 0;
    }
    return 0;
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

  private _callQueueService(
    configEntryId: string | null | undefined,
    service: ActiveQueueService,
  ): void {
    if (!configEntryId || !this.hass?.callService) {
      return;
    }

    void this.hass.callService("ha_dreame", service, {
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

  private _cycleOverride(
    configEntryId: string | null | undefined,
    itemId: string,
    overrides: Record<string, unknown>,
    control: CardOverrideControl,
  ): void {
    if (control.controlType === "running") {
      this._updateRunningOverride(configEntryId, control.field, control.value);
      return;
    }

    this._updateOverrides(configEntryId, itemId, control.field, overrides);
  }

  private _updateRunningOverride(
    configEntryId: string | null | undefined,
    field: OverrideField,
    value: number | undefined,
  ): void {
    if (!configEntryId || !this.hass?.callService || field === "repeats" || value === undefined) {
      return;
    }

    void this.hass.callService("ha_dreame", "update_running_override", {
      config_entry_id: configEntryId,
      field,
      value,
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
    description: "Queue controls for HA Dreame.",
  });
}
