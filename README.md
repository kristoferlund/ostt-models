# models

Default local model registry for [OSTT](https://ostt.app). Models in this repository are shown by default in the OSTT TUI and are available to all OSTT users.

## Files

- `models-v2.json`: the registry read by current OSTT versions. Contains Whisper and Parakeet models.
- `models.json`: Whisper-only registry for older OSTT versions, which reject the whole file if any entry has a provider they do not know. Keep its Whisper entries in sync with `models-v2.json`, and never add other providers to it.

## JSON Schema

| Field                | Description                                       |
|----------------------|---------------------------------------------------|
| `id`                 | Unique model identifier                           |
| `provider_id`        | Local transcription engine/provider (`whisper` or `parakeet`) |
| `name`               | Human-readable model name                         |
| `description`        | Short description of the model                    |
| `languages`          | Supported language codes (e.g. `["multi"]`, `["sv"]`) |
| `size_mb`            | Approximate download size in MB                   |
| `url`                | Direct download URL to the model file (ggml `.bin` or `.gguf`), pinned to a revision where possible |
| `recommended_hardware` | Hardware guidance for running the model        |
| `sha256`             | SHA-256 checksum (null if not verified)           |
| `category`           | `"canonical"` for upstream models, `"regional"` for localized models, `"community"` for third-party post-trained models |
| `group_id`           | Logical group for UI organisation (`ggerganov`, `kblab`, `nbailab`, `parakeet`) |

Models are sorted by group and size (tiny to large).
