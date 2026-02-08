import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock dependencies
sys.modules["python.helpers.settings"] = MagicMock()
sys.modules["python.helpers.call_llm"] = MagicMock()

sys.modules["openai"] = MagicMock()
sys.modules["litellm"] = MagicMock()
sys.modules["litellm.types"] = MagicMock()
sys.modules["litellm.types.utils"] = MagicMock()
sys.modules["browser_use"] = MagicMock()
sys.modules["browser_use.llm"] = MagicMock()
sys.modules["browser_use.agent"] = MagicMock()
sys.modules["browser_use.browser"] = MagicMock()
sys.modules["browser_use.controller"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["whisper"] = MagicMock()
sys.modules["git"] = MagicMock()
sys.modules["dotenv"] = MagicMock()
sys.modules["aiohttp"] = MagicMock()
sys.modules["cryptography"] = MagicMock()
sys.modules["webcolors"] = MagicMock()
sys.modules["yaml"] = MagicMock()
sys.modules["simpleeval"] = MagicMock()
sys.modules["imapclient"] = MagicMock()
sys.modules["flask"] = MagicMock()
sys.modules["pytz"] = MagicMock()
sys.modules["html2text"] = MagicMock()
sys.modules["pathspec"] = MagicMock()
sys.modules["tiktoken"] = MagicMock()

# Mock langchain_core
langchain_core = MagicMock()
sys.modules["langchain_core"] = langchain_core
sys.modules["langchain_core.language_models"] = MagicMock()
sys.modules["langchain_core.language_models.chat_models"] = MagicMock()
sys.modules["langchain_core.outputs"] = MagicMock()
sys.modules["langchain_core.outputs.chat_generation"] = MagicMock()
sys.modules["langchain_core.prompts"] = MagicMock()
sys.modules["langchain_core.prompts.chat"] = MagicMock()
sys.modules["langchain_core.prompts.pipeline"] = MagicMock()
sys.modules["langchain_core.callbacks"] = MagicMock()
sys.modules["langchain_core.callbacks.manager"] = MagicMock()
sys.modules["langchain_core.runnables"] = MagicMock()
sys.modules["langchain_core.runnables.config"] = MagicMock()

sys.modules["langchain"] = MagicMock()
sys.modules["langchain.embeddings"] = MagicMock()
sys.modules["langchain.embeddings.base"] = MagicMock()

sys.modules["langchain_community"] = MagicMock()
sys.modules["langchain_community.chat_models"] = MagicMock()

# Mock langchain_core.messages
class MockBaseMessage:
    def __init__(self, content):
        self.content = content
class MockHumanMessage(MockBaseMessage): pass
class MockSystemMessage(MockBaseMessage): pass
class MockAIMessage(MockBaseMessage): pass

langchain_core_messages = MagicMock()
langchain_core_messages.BaseMessage = MockBaseMessage
langchain_core_messages.HumanMessage = MockHumanMessage
langchain_core_messages.SystemMessage = MockSystemMessage
langchain_core_messages.AIMessage = MockAIMessage
sys.modules["langchain_core.messages"] = langchain_core_messages


from python.helpers.history import Message, output_text, calculate_output_length

class TestHistoryLength(unittest.TestCase):
    def test_calculate_output_length_simple(self):
        content = "Hello world"
        msg = Message(ai=True, content=content)
        out = msg.output()

        expected_len = len(output_text(out, strip_images=True))
        calculated_len = calculate_output_length(out, strip_images=True)

        self.assertEqual(calculated_len, expected_len)

    def test_calculate_output_length_list(self):
        content = ["part1", "part2"]
        msg = Message(ai=True, content=content)
        out = msg.output()

        expected_len = len(output_text(out, strip_images=True))
        calculated_len = calculate_output_length(out, strip_images=True)

        self.assertEqual(calculated_len, expected_len)

    def test_calculate_output_length_dict(self):
        content = {"key": "value"}
        msg = Message(ai=True, content=content)
        out = msg.output()

        expected_len = len(output_text(out, strip_images=True))
        calculated_len = calculate_output_length(out, strip_images=True)

        self.assertEqual(calculated_len, expected_len)

    def test_calculate_output_length_strip_images(self):
        # Image placeholder is [IMAGE]
        content = [{"type": "image_url", "image_url": "http://example.com/image.jpg"}]
        msg = Message(ai=True, content=content)
        out = msg.output()

        expected_len = len(output_text(out, strip_images=True))
        calculated_len = calculate_output_length(out, strip_images=True)

        self.assertEqual(calculated_len, expected_len)

if __name__ == "__main__":
    unittest.main()
