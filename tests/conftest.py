import sys
from unittest.mock import MagicMock

# Mock dependencies to avoid installation issues
sys.modules["browser_use"] = MagicMock()
sys.modules["browser_use.llm"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["whisper"] = MagicMock()
sys.modules["python.helpers.call_llm"] = MagicMock()
