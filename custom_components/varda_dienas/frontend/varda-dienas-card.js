/**
 * Vārda dienas Card — Lovelace custom card
 *
 * Shows today's Latvian name days, optional extended names, tomorrow,
 * and highlights configured favorites.
 *
 * type: custom:varda-dienas-card
 * entity: sensor.varda_dienas_today   # optional, auto-detected
 * show_extended: true                 # optional override
 * show_tomorrow: true                 # optional, default true
 * show_favorites: true                # optional, default true
 * title: Vārda dienas                 # optional
 */

class VardaDienasCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  setConfig(config) {
    this._config = {
      show_tomorrow: true,
      show_favorites: true,
      ...config,
    };
  }

  getCardSize() {
    return this._config?.show_tomorrow === false ? 2 : 3;
  }

  static getConfigForm() {
    return {
      schema: [
        { name: "entity", selector: { entity: { filter: { domain: "sensor" } } } },
        { name: "title", selector: { text: {} } },
        { name: "show_extended", selector: { boolean: {} } },
        { name: "show_tomorrow", selector: { boolean: {} } },
        { name: "show_favorites", selector: { boolean: {} } },
      ],
    };
  }

  static getStubConfig() {
    return {
      show_extended: false,
      show_tomorrow: true,
      show_favorites: true,
    };
  }

  _findEntity() {
    if (this._config.entity && this._hass.states[this._config.entity]) {
      return this._config.entity;
    }
    const match = Object.keys(this._hass.states).find((entityId) => {
      if (!entityId.startsWith("sensor.")) return false;
      const state = this._hass.states[entityId];
      return (
        state.attributes?.month_day &&
        Array.isArray(state.attributes?.names) &&
        Array.isArray(state.attributes?.tomorrow_names)
      );
    });
    return match || null;
  }

  _formatDate(iso) {
    if (!iso) return "";
    const date = new Date(`${iso}T12:00:00`);
    return date.toLocaleDateString(undefined, {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
  }

  _renderNames(names, favorites, className) {
    if (!names || !names.length) {
      return `<span class="empty">—</span>`;
    }
    const favoriteSet = new Set((favorites || []).map((n) => n.toLowerCase()));
    return names
      .map((name) => {
        const isFavorite = favoriteSet.has(String(name).toLowerCase());
        return `<span class="name ${className || ""} ${isFavorite ? "favorite" : ""}">${this._escape(name)}</span>`;
      })
      .join('<span class="sep">, </span>');
  }

  _escape(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  _render() {
    if (!this._hass || !this._config) return;

    const entityId = this._findEntity();
    const stateObj = entityId ? this._hass.states[entityId] : null;
    const shadow = this.shadowRoot;

    if (!stateObj) {
      shadow.innerHTML = `
        <style>${this._styles()}</style>
        <ha-card>
          <div class="content">
            <div class="title">${this._escape(this._config.title || "Vārda dienas")}</div>
            <div class="empty">Add the Vārda dienas integration, then reload this card.</div>
          </div>
        </ha-card>`;
      return;
    }

    const attrs = stateObj.attributes || {};
    const showExtended =
      this._config.show_extended !== undefined
        ? Boolean(this._config.show_extended)
        : Boolean(attrs.show_extended);
    const showTomorrow = this._config.show_tomorrow !== false;
    const showFavorites = this._config.show_favorites !== false;

    const favorites = attrs.favorites || [];
    const favoriteToday = attrs.favorite_today || [];
    const favoriteTomorrow = attrs.favorite_tomorrow || [];
    const main = attrs.names || [];
    const extended = attrs.extended_names || [];
    const tomorrow = attrs.tomorrow_names || [];
    const tomorrowExtended = attrs.tomorrow_extended_names || [];

    const title = this._config.title || "Vārda dienas";
    const dateLabel = this._formatDate(attrs.date);

    shadow.innerHTML = `
      <style>${this._styles()}</style>
      <ha-card>
        <div class="content">
          <div class="header">
            <div>
              <div class="title">${this._escape(title)}</div>
              <div class="date">${this._escape(dateLabel)}</div>
            </div>
            <ha-icon icon="mdi:calendar-heart"></ha-icon>
          </div>

          <div class="section">
            <div class="label">Šodien</div>
            <div class="names">${this._renderNames(main, favorites, "main")}</div>
            ${
              showExtended && extended.length
                ? `<div class="names extended">${this._renderNames(extended, favorites, "ext")}</div>`
                : ""
            }
          </div>

          ${
            showFavorites && favoriteToday.length
              ? `<div class="banner today">Šodien svin: ${this._escape(favoriteToday.join(", "))}</div>`
              : ""
          }

          ${
            showTomorrow
              ? `<div class="section muted">
                  <div class="label">Rīt</div>
                  <div class="names">${this._renderNames(tomorrow, favorites, "main")}</div>
                  ${
                    showExtended && tomorrowExtended.length
                      ? `<div class="names extended">${this._renderNames(tomorrowExtended, favorites, "ext")}</div>`
                      : ""
                  }
                </div>`
              : ""
          }

          ${
            showFavorites && favoriteTomorrow.length
              ? `<div class="banner tomorrow">Rīt svin: ${this._escape(favoriteTomorrow.join(", "))}</div>`
              : ""
          }

          ${
            showFavorites && favorites.length
              ? `<div class="favorites-footer">Mīļākie: ${this._escape(favorites.join(", "))}</div>`
              : ""
          }
        </div>
      </ha-card>`;
  }

  _styles() {
    return `
      :host { display: block; }
      ha-card {
        overflow: hidden;
        background:
          radial-gradient(circle at top right, rgba(196, 74, 74, 0.18), transparent 42%),
          var(--ha-card-background, var(--card-background-color));
      }
      .content { padding: 16px; display: grid; gap: 14px; }
      .header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
      }
      .title {
        font-size: 1.15rem;
        font-weight: 650;
        letter-spacing: 0.01em;
      }
      .date {
        color: var(--secondary-text-color);
        font-size: 0.9rem;
        margin-top: 2px;
      }
      ha-icon { color: var(--primary-color); opacity: 0.9; }
      .section { display: grid; gap: 8px; }
      .section.muted { opacity: 0.92; }
      .label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--secondary-text-color);
      }
      .names {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .name {
        display: inline-flex;
        align-items: center;
        padding: 0.15rem 0;
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.25;
      }
      .sep { color: var(--secondary-text-color); opacity: 0.7; }
      .name.ext {
        font-size: 0.92rem;
        font-weight: 500;
        color: var(--secondary-text-color);
      }
      .name.favorite {
        color: var(--primary-color);
      }
      .name.favorite::before {
        content: "★";
        font-size: 0.75em;
        margin-right: 0.3em;
        opacity: 0.85;
      }
      .banner {
        border-radius: 10px;
        padding: 10px 12px;
        font-weight: 600;
      }
      .banner.today {
        background: color-mix(in srgb, var(--primary-color) 16%, transparent);
        color: var(--primary-text-color);
      }
      .banner.tomorrow {
        background: color-mix(in srgb, var(--secondary-text-color) 12%, transparent);
      }
      .favorites-footer {
        font-size: 0.82rem;
        color: var(--secondary-text-color);
      }
      .empty { color: var(--secondary-text-color); }
    `;
  }
}

customElements.define("varda-dienas-card", VardaDienasCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "varda-dienas-card",
  name: "Vārda dienas Card",
  description: "Latvian name days for today and tomorrow, with favorites.",
  preview: true,
});
