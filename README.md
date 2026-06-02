# models

Default Whisper model registry for [OSTT](https://ostt.app). Models in this repository are shown by default in the OSTT TUI and are available to all OSTT users.

## JSON Schema

| Field                | Description                                       |
|----------------------|---------------------------------------------------|
| `id`                 | Unique model identifier                           |
| `provider_id`        | Local transcription engine/provider (`whisper`)   |
| `name`               | Human-readable model name                         |
| `description`        | Short description of the model                    |
| `languages`          | Supported language codes (e.g. `["multi"]`, `["sv"]`) |
| `size_mb`            | Approximate download size in MB                   |
| `url`                | Direct download URL to the ggml binary            |
| `recommended_hardware` | Hardware guidance for running the model        |
| `sha256`             | SHA-256 checksum (null if not verified)           |
| `category`           | `"canonical"` for upstream Whisper, `"regional"` for localized models |
| `group_id`           | Logical group for UI organisation (`ggerganov`, `kblab`, `nbailab`) |

Models are sorted by group and size (tiny to large).
