import sys
import os
import unittest
import json
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock dependencies to avoid installing heavy libraries
sys.modules["python.helpers.settings"] = MagicMock()
sys.modules["python.helpers.call_llm"] = MagicMock()
sys.modules["python.helpers.messages"] = MagicMock()

# Mock langchain_core
mock_langchain_core = MagicMock()
sys.modules["langchain_core"] = mock_langchain_core
sys.modules["langchain_core.messages"] = MagicMock()

# tokens is lightweight, but let's check if it needs mocking
try:
    import python.helpers.tokens
except ImportError:
    sys.modules["python.helpers.tokens"] = MagicMock()
    # history.py uses tokens.approximate_tokens_from_len
    sys.modules["python.helpers.tokens"].approximate_tokens_from_len = lambda x: x // 3

# Now import history
from python.helpers.history import calculate_output_length, output_text, OutputMessage, MessageContent

class TestHistoryLength(unittest.TestCase):
    def check_length(self, messages, strip_images=False):
        # We need to ensure output_text uses the real implementation
        # output_text calls _stringify_output -> _stringify_content
        expected = len(output_text(messages, strip_images=strip_images))
        actual = calculate_output_length(messages, strip_images=strip_images)
        self.assertEqual(actual, expected, f"Failed for messages: {messages}")

    def test_simple_string(self):
        messages = [{"ai": True, "content": "Hello world"}]
        self.check_length(messages)
        self.check_length(messages, strip_images=True)

    def test_list_of_strings(self):
        messages = [{"ai": False, "content": ["Hello", " ", "world"]}]
        self.check_length(messages)
        self.check_length(messages, strip_images=True)

    def test_image_placeholder(self):
        # Dict with image
        content = {"type": "image_url", "image_url": "http://example.com/image.png"}
        messages = [{"ai": True, "content": content}]

        # When strip_images=False, it dumps to JSON
        self.check_length(messages, strip_images=False)

        # When strip_images=True, it replaces with [IMAGE]
        self.check_length(messages, strip_images=True)

    def test_text_dict(self):
        content = {"type": "text", "text": "Some text"}
        messages = [{"ai": True, "content": content}]
        self.check_length(messages, strip_images=True)
        self.check_length(messages, strip_images=False)

    def test_mixed_list(self):
        content = [
            {"type": "text", "text": "Look at this: "},
            {"type": "image_url", "image_url": "base64data..."},
            "Raw string"
        ]
        messages = [{"ai": False, "content": content}]
        self.check_length(messages, strip_images=True)
        self.check_length(messages, strip_images=False)

    def test_multiple_messages(self):
        messages = [
            {"ai": False, "content": "User says hi"},
            {"ai": True, "content": "AI responds"},
            {"ai": False, "content": ["User", " ", "replies"]}
        ]
        self.check_length(messages, strip_images=True)

    def test_raw_message(self):
        # Raw message structure
        content = {"raw_content": "some raw content", "preview": "Preview text"}
        messages = [{"ai": True, "content": content}]
        self.check_length(messages, strip_images=True)
        self.check_length(messages, strip_images=False)

    def test_raw_message_no_preview(self):
        content = {"raw_content": {"some": "json"}}
        messages = [{"ai": True, "content": content}]
        self.check_length(messages, strip_images=True)
        self.check_length(messages, strip_images=False)

    def test_nested_list(self):
        # Recursive list
        content = ["level1", ["level2", ["level3"]]]
        messages = [{"ai": True, "content": content}]
        self.check_length(messages, strip_images=True)

if __name__ == "__main__":
    unittest.main()
