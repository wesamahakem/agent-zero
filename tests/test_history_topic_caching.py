import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import asyncio

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock dependencies to avoid import errors
sys.modules["litellm"] = MagicMock()
sys.modules["models"] = MagicMock()
sys.modules["browser_use"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["whisper"] = MagicMock()
sys.modules["git"] = MagicMock()
sys.modules["cryptography"] = MagicMock()
sys.modules["cryptography.hazmat"] = MagicMock()
sys.modules["cryptography.hazmat.primitives"] = MagicMock()
sys.modules["cryptography.hazmat.primitives.asymmetric"] = MagicMock()
sys.modules["nest_asyncio"] = MagicMock()
sys.modules["webcolors"] = MagicMock()
sys.modules["pytz"] = MagicMock()
sys.modules["html2text"] = MagicMock()
sys.modules["simpleeval"] = MagicMock()
sys.modules["imapclient"] = MagicMock()
sys.modules["pytest_asyncio"] = MagicMock()
sys.modules["flask"] = MagicMock()
sys.modules["dotenv"] = MagicMock()
sys.modules["dotenv.parser"] = MagicMock()
sys.modules["aiohttp"] = MagicMock()
sys.modules["yaml"] = MagicMock()
sys.modules["regex"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["agent"] = MagicMock()
sys.modules["langchain_core"] = MagicMock()
sys.modules["langchain_core.messages"] = MagicMock()
sys.modules["langchain_core.prompts"] = MagicMock()
sys.modules["langchain_core.language_models"] = MagicMock()
sys.modules["langchain_core.language_models.chat_models"] = MagicMock()
sys.modules["langchain_core.language_models.llms"] = MagicMock()

from python.helpers.history import History, Topic, Message
from python.helpers import tokens

class TestHistoryTopicCaching(unittest.TestCase):
    def setUp(self):
        self.agent = MagicMock()
        self.history = History(self.agent)
        self.topic = self.history.current

    def test_get_tokens_caching(self):
        # Initial state
        self.assertIsNone(self.topic._messages_tokens)

        # Add a message
        msg1 = self.topic.add_message(ai=True, content="Hello")
        # _messages_tokens should remain None until get_tokens is called
        self.assertIsNone(self.topic._messages_tokens)

        # Call get_tokens to prime the cache
        tokens1 = self.topic.get_tokens()
        self.assertIsNotNone(self.topic._messages_tokens)
        self.assertEqual(tokens1, self.topic._messages_tokens)
        self.assertEqual(tokens1, msg1.get_tokens())

        # Add another message
        msg2 = self.topic.add_message(ai=False, content="World")
        # Cache should update immediately because it's not None anymore
        self.assertEqual(self.topic._messages_tokens, tokens1 + msg2.get_tokens())

        # Verify total via get_tokens
        self.assertEqual(self.topic.get_tokens(), tokens1 + msg2.get_tokens())

    def test_cache_update_on_compress_large_messages(self):
        # Add a large message
        content = "A" * 1000
        msg = self.topic.add_message(ai=True, content=content)
        # Prime cache
        initial_tokens = self.topic.get_tokens()
        self.assertIsNotNone(self.topic._messages_tokens)

        # Mock settings to force compression
        with patch("python.helpers.settings.get_settings") as mock_settings:
            # Set context length small enough so msg > limit
            # limit = len * hist * topic_ratio * large_msg_ratio
            # 100 * 1 * 0.5 * 0.25 = 12.5 tokens
            # "A"*1000 is ~333 tokens.
            mock_settings.return_value = {
                "chat_model_ctx_length": 100,
                "chat_model_ctx_history": 1.0,
            }

            # Mock truncate to return something smaller
            with patch("python.helpers.messages.truncate_dict_by_ratio", return_value={"text": "TRUNCATED"}):
                 # Run compression
                 async def run():
                     await self.topic.compress_large_messages()
                 asyncio.run(run())

        # Check if summary was set (compression happened)
        self.assertTrue(msg.summary)

        # Check if tokens updated
        new_tokens = self.topic.get_tokens()
        self.assertLess(new_tokens, initial_tokens)
        self.assertEqual(new_tokens, self.topic._messages_tokens)
        self.assertEqual(new_tokens, msg.get_tokens())

if __name__ == "__main__":
    unittest.main()
