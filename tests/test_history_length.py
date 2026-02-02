
import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock dependencies
sys.modules["litellm"] = MagicMock()
sys.modules["models"] = MagicMock()
sys.modules["python.helpers.call_llm"] = MagicMock()
sys.modules["langchain_core"] = MagicMock()
sys.modules["langchain_core.messages"] = MagicMock()

# Mock settings
sys.modules["python.helpers.settings"] = MagicMock()
sys.modules["python.helpers.settings"].get_settings.return_value = {
    "chat_model_ctx_length": 4096,
    "chat_model_ctx_history": 0.5
}

# Ensure tiktoken is mocked if not present
if "tiktoken" not in sys.modules:
    try:
        import tiktoken
    except ImportError:
        sys.modules["tiktoken"] = MagicMock()

from python.helpers import history

class TestHistoryLength(unittest.TestCase):
    def test_calculate_output_length_simple(self):
        content = "Hello world"
        # OutputMessage structure
        msg = {"ai": True, "content": content}
        messages = [msg]

        # "ai: Hello world" -> 15 chars
        expected = len("ai: Hello world")
        actual = history.calculate_output_length(messages)
        self.assertEqual(actual, expected)

        # Verify against output_text
        text = history.output_text(messages)
        self.assertEqual(len(text), actual)

    def test_calculate_output_length_multiple(self):
        msg1 = {"ai": True, "content": "Hello"}
        msg2 = {"ai": False, "content": "Hi"}
        messages = [msg1, msg2]

        # "ai: Hello\nuser: Hi"
        # 3+2+5 + 1 + 4+2+2 = 10 + 1 + 8 = 19
        text = history.output_text(messages)
        actual = history.calculate_output_length(messages)
        self.assertEqual(actual, len(text))

    def test_calculate_output_length_strip_images(self):
        # Mock image dict
        image_content = {"type": "image_url", "image_url": "base64..."}
        text_content = "Some text"

        # List of contents
        content = [image_content, text_content]
        msg = {"ai": True, "content": content}
        messages = [msg]

        # With strip_images=True
        # output_text should produce: "ai: [IMAGE]Some text" (no space unless in text)
        # _stringify_content joins parts with "".

        text = history.output_text(messages, strip_images=True)
        actual = history.calculate_output_length(messages, strip_images=True)
        self.assertEqual(actual, len(text))

        # Ensure it contains [IMAGE]
        self.assertIn("[IMAGE]", text)

    def test_calculate_output_length_recursive_list(self):
        content = ["A", ["B", "C"], "D"]
        # Nested lists: _stringify_content recurses.
        # "A" + "B" + "C" + "D" -> "ABCD"
        msg = {"ai": True, "content": content}
        messages = [msg]

        text = history.output_text(messages, strip_images=True)
        actual = history.calculate_output_length(messages, strip_images=True)
        self.assertEqual(actual, len(text))
        self.assertEqual(text, "ai: ABCD")

if __name__ == "__main__":
    unittest.main()
