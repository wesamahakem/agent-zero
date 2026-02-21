# DEBUG: Delete functionality missing

## Symptoms
"Delete removes comment" (Blocker).

## Investigation
- Inspected `webui/components/messages/action-buttons/simple-action-buttons.js`.
- **Finding**: Only `Copy` and `Speak` buttons are implemented.
- **Root Cause**: The "Delete" feature has not been implemented in the frontend component.

## Suggested Fix
1. Add a `delete-action` button to `simple-action-buttons.js`.
2. Implement backend endpoint in `python/api/chat_remove.py` or similar to handle specific message deletion.
