# Config-System Template_app_v002

## Prinzip

**Python-Defaults (\_base/)** + **Optional: JSON-Überschreibungen (\_custom/)** = **Finale Config**

```
_base/config/app_config.py     → Python-Defaults (updatebar)
          +
_custom/config/app_config.json → Überschreibungen (bleibt bei Updates)
          =
      app_config               → Finale Config
```

## Struktur

```
Template_app_v002/
├── _base/
│   └── config/
│       ├── __init__.py
│       └── app_config.py          ← Defaults im Python-Code
└── _custom/
    └── config/
        └── app_config.json        ← Optional: Deine Überschreibungen
```

## Funktionsweise

### 1. Defaults sind in Python (\_base/config/app_config.py)

```python
config = {
    "app_display_name": self.app_name,
    "app_version": "0.0.0",
    "logger": {"level": "INFO"},
    "features": {
        "socketio_enabled": True,
        "scheduler_enabled": True
    }
}
```

### 2. Optional: Überschreiben via JSON (\_custom/config/app_config.json)

```json
{
  "app_display_name": "Meine App",
  "app_version": "1.0.0",
  "tasks_intervall": {
    "app_keep_alive_log": 200
  },
  "meine_settings": {
    "api_key": "secret123"
  }
}
```

### 3. Zugriff im Code

```python
from . import app_config

# Properties
app_config.app_name              # "Template_app_v002"
app_config.app_version           # "1.0.0" (aus JSON)
app_config.logger_level          # "INFO" (Default)

# Feature Flags
if app_config.socketio_enabled:
    setup_socketio()

# Beliebige Keys
api_key = app_config.get("meine_settings.api_key")
```

## Setup in **init**.py

```python
from pathlib import Path
from ._base.config.app_config import AppConfig

# App-Name aus Ordnername
APP_NAME = Path(__file__).parent.name
APP_ROOT = Path(__file__).parent

# Config laden
app_config = AppConfig(APP_NAME, APP_ROOT)

# Blueprint mit Config-Werten
blueprint = Blueprint(
    APP_NAME,
    __name__,
    url_prefix=app_config.blueprint_url_prefix,
    static_url_path=app_config.blueprint_static_url_path,
)
```

## Update-Workflow

```bash
# _base/ aktualisieren (z.B. git pull)
```

**Was passiert:**

- ✅ `_base/config/app_config.py` → Aktualisiert
- ✅ Python-Defaults ändern sich
- ✅ `_custom/config/app_config.json` → Bleibt unverändert
- ✅ Deine Überschreibungen bleiben erhalten

## Wichtige Properties

| Property                             | Beschreibung              |
| ------------------------------------ | ------------------------- |
| `app_config.app_name`                | App-Name (aus Ordnername) |
| `app_config.app_display_name`        | Anzeigename               |
| `app_config.app_version`             | Version                   |
| `app_config.blueprint_url_prefix`    | Blueprint URL             |
| `app_config.logger_name`             | Logger-Name               |
| `app_config.logger_level`            | Log-Level                 |
| `app_config.socketio_enabled`        | SocketIO aktiviert?       |
| `app_config.scheduler_enabled`       | Scheduler aktiviert?      |
| `app_config.get_task_interval(name)` | Task-Intervall            |
| `app_config.get(key, default)`       | Beliebiger Wert           |

## Beispiele

### Minimale Custom-Config

```json
{
  "app_display_name": "My App"
}
```

### Erweiterte Custom-Config

```json
{
  "app_display_name": "Media Player",
  "app_version": "2.0.0",
  "tasks_intervall": {
    "cleanup": 60,
    "backup": 120
  },
  "media_settings": {
    "formats": ["mp4", "mkv"],
    "quality": "4K"
  }
}
```

### Zugriff auf Custom-Settings

```python
formats = app_config.get("media_settings.formats", [])
quality = app_config.get("media_settings.quality", "1080p")
```

## Zusammenfassung

| Was              | Wo                               | Updatebar? |
| ---------------- | -------------------------------- | ---------- |
| Defaults         | `_base/config/app_config.py`     | ✅ Ja      |
| Überschreibungen | `_custom/config/app_config.json` | ❌ Bleibt  |
| Zugriff          | `from . import app_config`       | -          |
