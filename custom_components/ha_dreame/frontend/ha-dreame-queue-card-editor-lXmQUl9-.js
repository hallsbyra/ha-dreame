import{i as r,a as d,q as c,D as h,b as o,C as l}from"./ha-dreame-queue-card.js";const s=class s extends r{constructor(){super(...arguments),this._config={}}setConfig(e){this._config={...e}}render(){const e=c(this.hass);return o`
      <div class="editor">
        <label>
          Queue entity
          <input
            list="ha-dreame-queue-entities"
            name="entity"
            placeholder="sensor.ha_dreame_queue_status"
            .value=${this._config.entity??""}
            @input=${t=>this._fieldChanged("entity",t)}
          />
        </label>
        <datalist id="ha-dreame-queue-entities">
          ${e.map(t=>o`<option value=${t}></option>`)}
        </datalist>
        <label>
          Title
          <input
            name="title"
            placeholder=${h}
            .value=${this._config.title??""}
            @input=${t=>this._fieldChanged("title",t)}
          />
          <span class="hint">Leave empty to use the default card title.</span>
        </label>
      </div>
    `}_fieldChanged(e,t){const n=(t.target?.value??"").trim(),i={...this._config};n?i[e]=n:delete i[e],this._config=i,this.dispatchEvent(new CustomEvent("config-changed",{bubbles:!0,composed:!0,detail:{config:i}}))}};s.properties={hass:{attribute:!1},_config:{state:!0}},s.styles=d`
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
  `;let a=s;customElements.get(l)||customElements.define(l,a);
