import sys
import types
import unittest
from unittest.mock import patch

inference_sdk_stub = types.ModuleType("inference_sdk")
inference_sdk_stub.InferenceHTTPClient = object
sys.modules.setdefault("inference_sdk", inference_sdk_stub)

from core.ai_classifier import GPTClassifier


class FakeResponse:
    status_code = 200
    text = ""

    def json(self):
        return {
            "output": [
                {
                    "content": [
                        {"text": '{"trash_class":"yellow"}'}
                    ]
                }
            ]
        }


class GPTClassifierResponsesTest(unittest.TestCase):
    def test_classify_uses_responses_api_and_parses_output_text(self):
        classifier = GPTClassifier()
        classifier.api_key = "test-key"

        captured_request = {}

        def fake_post(url, headers, json, timeout):
            captured_request["url"] = url
            captured_request["headers"] = headers
            captured_request["json"] = json
            captured_request["timeout"] = timeout
            return FakeResponse()

        with (
            patch.object(classifier, "_encode_image_to_base64", return_value="encoded-image"),
            patch("core.ai_classifier.requests.post", side_effect=fake_post),
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "yellow")
        self.assertEqual(captured_request["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(captured_request["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(captured_request["timeout"], 60)
        self.assertEqual(captured_request["json"]["model"], classifier.model)
        self.assertEqual(captured_request["json"]["max_output_tokens"], classifier.max_tokens)
        self.assertEqual(captured_request["json"]["reasoning"], {"effort": "low"})
        self.assertEqual(
            captured_request["json"]["input"][0]["content"],
            [
                {"type": "input_text", "text": classifier.prompt},
                {
                    "type": "input_image",
                    "image_url": "data:image/jpeg;base64,encoded-image",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
