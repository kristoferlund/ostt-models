import copy
import unittest

from validate_registry import artifact_parts, load_registries, validate


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.current, self.legacy = load_registries()

    def test_published_registries_remain_compatible(self):
        validate(self.current, self.legacy)

    def test_non_whisper_entries_cannot_break_old_clients(self):
        self.legacy["models"].append(copy.deepcopy(next(
            model for model in self.current["models"] if model["provider_id"] == "parakeet")))
        with self.assertRaisesRegex(ValueError, "Legacy registry"):
            validate(self.current, self.legacy)

    def test_whisper_metadata_cannot_drift_between_clients(self):
        self.legacy["models"][0]["description"] += " changed"
        with self.assertRaisesRegex(ValueError, "Legacy registry"):
            validate(self.current, self.legacy)

    def test_mutable_urls_and_unverified_downloads_are_rejected(self):
        for field, value, message in [
            ("url", self.current["models"][0]["url"].replace(
                artifact_parts(self.current["models"][0])[1], "main"), "pinned"),
            ("sha256", None, "SHA-256"),
            ("id", "../escape", "Unsafe"),
            ("provider_id", "moonshine", "unsupported provider"),
        ]:
            current = copy.deepcopy(self.current)
            current["models"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, message):
                validate(current, self.legacy)

    def test_duplicate_download_destinations_are_rejected(self):
        self.current["models"].append(copy.deepcopy(self.current["models"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate model ID"):
            validate(self.current, self.legacy)

    def test_english_models_do_not_advertise_multilingual_support(self):
        for model in self.current["models"]:
            if model["id"].endswith(".en") or model["id"] == "distil-large-v3.5":
                self.assertEqual(model["languages"], ["en"], model["id"])


if __name__ == "__main__":
    unittest.main()
