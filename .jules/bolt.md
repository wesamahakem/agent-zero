## 2024-05-24 - [Character-based Token Estimation]
**Learning:** `tiktoken` encoding is CPU intensive (O(N) for text length) and calling it frequently in `approximate_tokens` defeats the purpose of approximation if the goal is speed.
**Action:** Use a character-based heuristic (e.g., `len(text) // 2.5`) for `approximate_tokens` to make it O(1) in `python/helpers/tokens.py`, or cache the result in `Topic`/`Bulk` objects if exact count is needed.

## 2025-05-24 - [Image Token Estimation]
**Learning:** Serializing base64 images to JSON to estimate tokens (by length) is extremely inefficient and incorrect (overestimating by ~400x).
**Action:** Use a fixed token cost for images (e.g., 1000) and avoid serializing image data during token calculation. Traverse the message structure recursively.

## 2025-05-24 - [File Tree Bug and Optimization]
**Learning:** `python/helpers/file_tree.py` contained a `TypeError` due to missing arguments in `_list_directory_children` calls, and redundant path calculations.
**Action:** Fixed the bug and optimized the recursion to pass pre-calculated relative paths, saving string operations. When refactoring recursive file walkers, always check signature consistency across all recursive calls.

## 2025-05-25 - [Base64 in Summarization]
**Learning:** `Bulk.summarize` was defaulting to `strip_images=False` when generating text for the summarizer LLM, resulting in massive prompts containing full base64 image data.
**Action:** Explicitly pass `strip_images=True` to `output_text` when preparing content for summarization or other utility model calls where image data is not needed.

## 2025-06-25 - [Localization Performance and Dependency Hell]
**Learning:** `AgentContext.output()` is called frequently (polling) and naively created new `timezone` and `timedelta` objects via `Localization.serialize_datetime`. Caching the timezone object yielded ~50% speedup in serialization.
**Action:** When working with high-frequency serialization loops, cache immutable objects like `timezone`. Also, `agent.py` imports almost everything, making isolated testing difficult due to missing dependencies in `requirements.txt`.

## 2025-06-25 - [Deferred Serialization in Compression]
**Learning:** In `compress_large_messages`, iterating over all large messages and serializing them via `output_text` (which involves `json.dumps`) just to sort them by size was a significant bottleneck (~460ms for 20 msgs).
**Action:** Use cached metadata (like `get_tokens()`) to sort and select the best candidate first, then perform expensive operations only on the selected item. Reduced time to ~250ms.

## 2025-07-15 - [Avoid String Allocation for Length Calculation]
**Learning:** `Topic.compress_large_messages` was calling `output_text` to serialize large message structures (lists of multimodal content) into a huge string just to call `len()` on it. This caused massive memory allocation and CPU usage (1.6s for 25MB).
**Action:** Implemented `calculate_output_length` to recursively calculate the length of the string representation without constructing it. Achieved ~100x speedup (0.013s) for large contents. Avoid intermediate string construction whenever possible.
