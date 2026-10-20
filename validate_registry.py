"""Validate both OSTT registries; --remote also checks pinned Hugging Face metadata."""

import argparse
import datetime
import json
import math
from pathlib import Path
import re
import urllib.parse
import urllib.request


def artifact_parts(model):
    url = urllib.parse.urlsplit(model["url"])
    parts = url.path.strip("/").split("/")
    if (url.scheme != "https" or url.netloc != "huggingface.co"
            or url.query or url.fragment or len(parts) < 5
            or parts[2] != "resolve" or not re.fullmatch(r"[0-9a-f]{40}", parts[3])):
        raise ValueError(f"{model['id']}: expected a pinned Hugging Face resolve URL")
    return "/".join(parts[:2]), parts[3], "/".join(parts[4:])


def validate(current, legacy):
    for document in (current, legacy):
        if document["version"] != 1:
            raise ValueError("Registry version must remain 1 for existing clients")
        datetime.date.fromisoformat(document["updated"])
        ids = set()
        filenames = set()
        for model in document["models"]:
            model_id = model["id"]
            if (not re.fullmatch(r"[a-z0-9._-]+", model_id)
                    or model_id in {".", ".."} or model_id in ids):
                raise ValueError(f"Unsafe or duplicate model ID: {model_id}")
            ids.add(model_id)
            provider = model["provider_id"]
            extension = {"whisper": ".bin", "parakeet": ".gguf"}.get(provider)
            if extension is None:
                raise ValueError(f"{model_id}: unsupported provider {provider}")
            _, _, artifact = artifact_parts(model)
            if not artifact.endswith(extension):
                raise ValueError(f"{model_id}: wrong artifact format for {provider}")
            filename = model_id + extension
            if filename in filenames:
                raise ValueError(f"Duplicate destination: {filename}")
            filenames.add(filename)
            if not re.fullmatch(r"[0-9a-f]{64}", model["sha256"] or ""):
                raise ValueError(f"{model_id}: missing SHA-256")
            if type(model["size_mb"]) is not int or model["size_mb"] <= 0:
                raise ValueError(f"{model_id}: invalid size")
            for field in ("name", "description", "recommended_hardware", "group_id"):
                if not isinstance(model[field], str) or not model[field].strip():
                    raise ValueError(f"{model_id}: missing {field}")
            if (not isinstance(model["languages"], list) or not model["languages"]
                    or any(not isinstance(code, str) or not code.strip()
                           for code in model["languages"])):
                raise ValueError(f"{model_id}: missing languages")
            if model["category"] not in {"canonical", "regional", "community"}:
                raise ValueError(f"{model_id}: unsupported category")

    whisper = [model for model in current["models"] if model["provider_id"] == "whisper"]
    if legacy["models"] != whisper or current["updated"] != legacy["updated"]:
        raise ValueError("Legacy registry must exactly mirror current Whisper entries and date")


def verify_remote(models):
    cache = {}
    for model in models:
        repo, revision, filename = artifact_parts(model)
        key = repo, revision
        if key not in cache:
            url = f"https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true"
            with urllib.request.urlopen(url, timeout=60) as response:
                metadata = json.load(response)
            if metadata["sha"] != revision:
                raise ValueError(f"{repo}: revision mismatch")
            cache[key] = {file["rfilename"]: file for file in metadata["siblings"]}
        artifact = cache[key][filename]
        if artifact["lfs"]["sha256"] != model["sha256"]:
            raise ValueError(f"{model['id']}: remote SHA-256 mismatch")
        if math.ceil(artifact["size"] / 1048576) != model["size_mb"]:
            raise ValueError(f"{model['id']}: remote size mismatch")
        print(f"Verified {model['provider_id']}/{model['id']}")


def load_registries():
    root = Path(__file__).resolve().parent
    return tuple(json.loads((root / name).read_text())
                 for name in ("models-v2.json", "models.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", action="store_true", help="Verify upstream sizes and LFS hashes (no model downloads)")
    args = parser.parse_args()
    current, legacy = load_registries()
    validate(current, legacy)
    if args.remote:
        verify_remote(current["models"])
    print(f"Valid: {len(current['models'])} current models, {len(legacy['models'])} legacy Whisper models")
