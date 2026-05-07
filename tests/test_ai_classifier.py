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

    def __init__(self, payload=None):
        self.payload = payload or {
            "output": [
                {
                    "content": [
                        {"text": '{"trash_class":"yellow"}'}
                    ]
                }
            ]
        }

    def json(self):
        return self.payload


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

    def test_classify_parses_text_from_later_response_output_items(self):
        classifier = GPTClassifier()
        response_payload = {
            "output": [
                {"type": "reasoning", "summary": []},
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{"trash_class":"brown"}',
                        }
                    ],
                },
            ]
        }

        with (
            patch.object(classifier, "_encode_image_to_base64", return_value="encoded-image"),
            patch("core.ai_classifier.requests.post", return_value=FakeResponse(response_payload)),
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "brown")

    def test_classify_logs_raw_response_when_text_is_empty(self):
        classifier = GPTClassifier()
        response_payload = {"output": [{"type": "reasoning", "summary": []}]}

        with (
            patch.object(classifier, "_encode_image_to_base64", return_value="encoded-image"),
            patch("core.ai_classifier.requests.post", return_value=FakeResponse(response_payload)),
            self.assertLogs("core.ai_classifier", level="WARNING") as logs,
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "")
        self.assertTrue(
            any("GPT raw response" in message for message in logs.output),
            logs.output,
        )


if __name__ == "__main__":
    unittest.main()
