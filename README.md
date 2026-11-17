# Vārda dienas — Home Assistant Integration

Latvian name days (vārda dienas) for Home Assistant — today/tomorrow sensors, favorites, calendars, and a Lovelace card so you do not miss people you care about.

**Repository:** https://github.com/fassko/varda-dienas-ha

Data is bundled from the companion Android app calendars (traditional + extended).

## What's included

```
custom_components/varda_dienas/   ← drop into config/custom_components/
```

| Piece | Purpose |
|-------|---------|
| `sensor.varda_dienas_today` | Traditional names today (+ attributes for extended / tomorrow / favorites) |
| `sensor.varda_dienas_tomorrow` | Traditional names tomorrow |
| `sensor.varda_dienas_favorites_today` | Favorites celebrating today |
| `binary_sensor.varda_dienas_favorite_today` | On when a favorite celebrates today |
| `binary_sensor.varda_dienas_favorite_tomorrow` | On when a favorite celebrates tomorrow |
| `calendar.varda_dienas` | Full name-day calendar (extended names follow the option) |
| `calendar.varda_dienas_favorites` | Favorites-only calendar |
| `custom:varda-dienas-card` | Dashboard card: today, optional extended, tomorrow, favorites |

## Installation

### Home Assistant Marketplace / HACS

1. Open **Settings → Marketplace** (HA 2026.11+) or **HACS**.
2. **Add from link** / **Custom repositories** and paste:

   `https://github.com/fassko/varda-dienas-ha`

   Category / type: **Integration**.
3. Install **Vārda dienas (Latvia Name Days)**.
4. Restart Home Assistant.
5. **Settings → Devices & Services → Add Integration → Vārda dienas**.
6. Add the Lovelace resource:

| URL | Type |
|-----|------|
| `/varda_dienas_frontend/varda-dienas-card.js` | JavaScript module |

### Manual installation

Copy `custom_components/varda_dienas` into your HA `config/custom_components/` folder, restart, then add the integration and Lovelace resource as above.

## Configure favorites

During setup (or later under **Configure**):

- **Include extended names by default** — full calendar and card default include the expanded calendar.
- **Favorite names** — comma-separated list, e.g. `Anna, Jānis, Madara`.

Services:

```yaml
action: varda_dienas.add_favorite
data:
  name: Anna

action: varda_dienas.remove_favorite
data:
  name: Anna

action: varda_dienas.set_favorites
data:
  names:
    - Anna
    - Jānis
```

## Dashboard card

```yaml
type: custom:varda-dienas-card
# entity: sensor.varda_dienas_today   # optional; auto-detected
show_extended: false
show_tomorrow: true
show_favorites: true
```

## Do-not-miss automation example

Notify in the morning when a favorite celebrates today:

```yaml
alias: Favorite name day today
triggers:
  - trigger: time
    at: "09:00:00"
conditions:
  - condition: state
    entity_id: binary_sensor.varda_dienas_favorite_today
    state: "on"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: Vārda diena
      message: >
        Šodien svin
        {{ state_attr('binary_sensor.varda_dienas_favorite_today', 'names') | join(', ') }}
```

Use `calendar.varda_dienas_favorites` on a calendar dashboard view for an overview of upcoming favorites.

## Notes

- “Today” uses the `Europe/Riga` calendar date.
- Extended names are the expanded calendar entries that are not already in the traditional list for that day.
- No cloud dependency — calendars ship inside the integration.
