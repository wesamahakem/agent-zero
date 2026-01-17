## 2024-05-24 - [Character-based Token Estimation]
**Learning:** `tiktoken` encoding is CPU intensive (O(N) for text length) and calling it frequently in `approximate_tokens` defeats the purpose of approximation if the goal is speed.
**Action:** Use a character-based heuristic (e.g., `len(text) // 2.5`) for `approximate_tokens` to make it O(1) in `python/helpers/tokens.py`, or cache the result in `Topic`/`Bulk` objects if exact count is needed.

## 2025-05-24 - [Image Token Estimation]
**Learning:** Serializing base64 images to JSON to estimate tokens (by length) is extremely inefficient and incorrect (overestimating by ~400x).
**Action:** Use a fixed token cost for images (e.g., 1000) and avoid serializing image data during token calculation. Traverse the message structure recursively.
