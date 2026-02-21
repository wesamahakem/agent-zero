# DEBUG: Comment not refreshing immediately

## Symptoms
User reported: "works but doesn't show until I refresh the page".

## Investigation
- `webui/index.js` line 65 calls `setMessage` with a generated GUID.
- `webui/js/messages.js` appends to `chatHistory`.
- **Hypothesis**: The `poll()` function (line 293 in `index.js`) resets the `chatHistory.innerHTML = ""` if `lastLogGuid` changes. When a message is sent, the backend might start a new log session or the GUID might mismatch, causing a full wipe and re-poll.

## Root Cause
Race condition between `setMessage` (local) and `poll()` (remote) combined with `lastLogGuid` mismatch logic.

## Suggested Fix
Ensure local message IDs persist during polling or synchronize the GUID before sending.
