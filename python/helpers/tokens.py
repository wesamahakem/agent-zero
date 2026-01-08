from typing import Literal
import tiktoken

# Heuristic: ~3 characters per token is a safe approximation (usually ~4 for English/Code)
# This avoids expensive BPE encoding for simple checks
CHARS_PER_TOKEN = 3.0
TRIM_BUFFER = 0.8


def count_tokens(text: str, encoding_name="cl100k_base") -> int:
    """
    Counts the exact number of tokens in a text string using tiktoken.
    This is an O(N) operation where N is the length of the text.
    """
    if not text:
        return 0

    # Get the encoding
    encoding = tiktoken.get_encoding(encoding_name)

    # Encode the text and count the tokens
    tokens = encoding.encode(text, disallowed_special=())
    token_count = len(tokens)

    return token_count


def approximate_tokens(
    text: str,
) -> int:
    """
    Approximates the number of tokens in a text string using a character-based heuristic.
    This is an O(1) operation (relative to tokenization complexity) and is significantly faster than count_tokens.
    """
    if not text:
        return 0
    return approximate_tokens_from_len(len(text))


def approximate_tokens_from_len(
    length: int,
) -> int:
    """
    Approximates the number of tokens based on character length.
    """
    if length <= 0:
        return 0
    # Ensure at least 1 token for non-empty text
    return max(1, int(length / CHARS_PER_TOKEN))


def trim_to_tokens(
    text: str,
    max_tokens: int,
    direction: Literal["start", "end"],
    ellipsis: str = "...",
) -> str:
    chars = len(text)
    # We still use exact count here because trimming needs to be precise enough not to exceed limits
    # but efficient enough. However, if performance is critical here, we could use heuristic too.
    # For now, keeping exact count for safety in trimming, as this is likely used for hard limits.
    tokens = count_tokens(text)

    if tokens <= max_tokens:
        return text

    approx_chars = int(chars * (max_tokens / tokens) * TRIM_BUFFER)

    if direction == "start":
        return text[:approx_chars] + ellipsis
    return ellipsis + text[chars - approx_chars : chars]
