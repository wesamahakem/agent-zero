# DEBUG: Reply button positioning

## Symptoms
Reply button positioned incorrectly (Minor).

## Investigation
- `messages.js` line 451: `drawMessageResponse` marks messages as `followUp: true`.
- Line 366: This adds the `message-followup` class to the container.
- **Root Cause**: The CSS for `message-followup` is likely not handling the button alignment for nested responses.

## Suggested Fix
Update `webui/index.css` or `webui/css/` to properly align `action-buttons` within `message-followup` containers.
