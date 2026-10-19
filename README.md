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
| `size_mb`            | Download size in MiB, rounded up (`ceil(bytes / 1048576)`) |
| `url`                | Direct download URL to the model file (ggml `.bin` or `.gguf`), pinned to an immutable revision |
| `recommended_hardware` | Hardware guidance for running the model        |
| `sha256`             | SHA-256 of the model file, verified against Hugging Face LFS metadata |
| `category`           | `"canonical"` for upstream models, `"regional"` for localized models, `"community"` for third-party post-trained models |
| `group_id`           | Logical group for UI organisation (`ggerganov`, `distil-whisper`, `kblab`, `nbailab`, `parakeet`) |

Models are grouped by publisher and model family, with compact alternatives after the full-precision models.

## Catalog refresh (2026-10-20)

- Added English-only Whisper Tiny/Base/Small/Medium and [Distil-Whisper Large v3.5](https://huggingface.co/distil-whisper/distil-large-v3.5-ggml). These models do not support multilingual transcription.
- Added upstream Small Q5_1, Medium/Large v3/Turbo Q5_0, and Turbo Q8_0, plus official KB/NB Whisper Large Q5_0. Quantization reduces download size and weight memory, not necessarily latency; accuracy can change. Smaller regional quantizations and every English/quantization combination are intentionally omitted to keep the picker focused.
- All 32 files have immutable revision URLs and SHA-256 values from upstream LFS metadata. Existing IDs and filenames are preserved. Checksums describe the actual downloadable GGML/GGUF file, not the original PyTorch weights.
- Rechecked the four Parakeet entries; their revisions and metadata are unchanged. Removed the unsupported claim that Ultra is universally the most accurate Parakeet model.
- No Qwen, Moonshine, Canary or Voxtral local entries: OSTT currently exposes only Whisper and Parakeet engines. A `.gguf` extension alone does not establish engine compatibility. Older Whisper Large v1/v2 and older Distil releases are not added alongside the current models.

Primary artifact sources: [whisper.cpp](https://huggingface.co/ggerganov/whisper.cpp/tree/5359861c739e955e79d9a303bcbc70fb988958b1), [KBLab](https://huggingface.co/KBLab), [NbAiLab](https://huggingface.co/NbAiLab), [Distil-Whisper](https://huggingface.co/distil-whisper/distil-large-v3.5-ggml), and [handy-computer](https://huggingface.co/handy-computer). Exact revisions are recorded in each entry's URL.

## Validation

Python 3.11+; no third-party dependencies:

```sh
python3 -m unittest -v
python3 validate_registry.py
python3 validate_registry.py --remote
```

Offline tests protect schema safety, unique destinations, pinned URLs/checksums, and exact legacy/current Whisper parity. `--remote` checks every file's size and SHA-256 against the pinned Hugging Face revision without downloading weights. It fails on missing files, changed metadata or unavailable upstream requests; it is not an inference/accuracy test. Live checks are kept out of CI to avoid upstream network outages blocking unrelated changes.
