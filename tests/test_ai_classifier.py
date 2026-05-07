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
    headers: dict = {}

    def __init__(self, payload=None, status_code=200):
        self.status_code = status_code
        self.payload = payload or {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": '{"trash_class":"yellow"}'}
                    ],
                }
            ]
        }

    def json(self):
        return self.payload


def _make_classifier(api_key: str = "test-key") -> GPTClassifier:
    classifier = GPTClassifier()
    classifier.api_key = api_key
    return classifier


class GPTClassifierResponsesTest(unittest.TestCase):
    def test_classify_uses_responses_api_and_parses_output_text(self):
        classifier = _make_classifier()

        captured_request = {}

        def fake_post(url, headers, json, timeout):
            captured_request["url"] = url
            captured_request["headers"] = headers
            captured_request["json"] = json
            captured_request["timeout"] = timeout
            return FakeResponse()

        with (
            patch.object(classifier, "_encode_image_to_base64", return_value="encoded-image"),
            patch.object(classifier._session, "post", side_effect=fake_post),
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "yellow")
        self.assertEqual(captured_request["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(captured_request["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(captured_request["timeout"], 60)
        payload = captured_request["json"]
        self.assertEqual(payload["model"], classifier.model)
        self.assertEqual(payload["max_output_tokens"], classifier.max_tokens)
        self.assertEqual(payload["reasoning"], {"effort": classifier.reasoning_effort})
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertEqual(payload["text"]["format"]["name"], "trash_classification")
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual(
            payload["input"][0]["content"],
            [
                {"type": "input_text", "text": classifier.prompt},
                {
                    "type": "input_image",
                    "image_url": "data:image/jpeg;base64,encoded-image",
                },
            ],
        )

    def test_classify_parses_text_from_later_response_output_items(self):
        classifier = _make_classifier()
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
            patch.object(classifier._session, "post", return_value=FakeResponse(response_payload)),
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "brown")

    def test_classify_logs_raw_response_when_text_is_empty(self):
        classifier = _make_classifier()
        response_payload = {"output": [{"type": "reasoning", "summary": []}]}

        with (
            patch.object(classifier, "_encode_image_to_base64", return_value="encoded-image"),
            patch.object(classifier._session, "post", return_value=FakeResponse(response_payload)),
            self.assertLogs("core.ai_classifier", level="WARNING") as logs,
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "")
        self.assertTrue(
            any("GPT returned no text" in message for message in logs.output),
            logs.output,
        )

    def test_classify_handles_incomplete_status(self):
        classifier = _make_classifier()
        response_payload = {
            "status": "incomplete",
            "incomplete_details": {"reason": "max_output_tokens"},
            "output": [],
        }

        with (
            patch.object(classifier, "_encode_image_to_base64", return_value="encoded-image"),
            patch.object(classifier._session, "post", return_value=FakeResponse(response_payload)),
            self.assertLogs("core.ai_classifier", level="WARNING") as logs,
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "")
        self.assertTrue(
            any("incomplete" in message for message in logs.output),
            logs.output,
        )

    def test_classify_retries_on_transient_status(self):
        classifier = _make_classifier()
        responses = [FakeResponse(status_code=503), FakeResponse()]

        def fake_post(url, headers, json, timeout):
            return responses.pop(0)

        with (
            patch.object(classifier, "_encode_image_to_base64", return_value="encoded-image"),
            patch.object(classifier._session, "post", side_effect=fake_post),
            patch("core.ai_classifier.time.sleep"),
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "yellow")
        self.assertEqual(responses, [])

    def test_classify_returns_empty_when_api_key_missing(self):
        classifier = _make_classifier(api_key="")

        with (
            patch.object(classifier, "_encode_image_to_base64", return_value="encoded-image"),
            patch.object(classifier._session, "post") as post_mock,
            self.assertLogs("core.ai_classifier", level="ERROR") as logs,
        ):
            result = classifier.classify(image=object())

        self.assertEqual(result, "")
        post_mock.assert_not_called()
        self.assertTrue(
            any("OPENAI_API_KEY" in message for message in logs.output),
            logs.output,
        )


if __name__ == "__main__":
    unittest.main()
