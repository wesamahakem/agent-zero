# Python Tools

18 default tools. Agent capabilities exposed via tool system.

## Tool Architecture

Each tool:
1. Python class in this directory (subclass of `Tool` from `python/helpers/tool.py`)
2. Matching prompt in `prompts/agent.system.tool.{name}.md`
3. Loaded dynamically via `extract_tools.py`

## Available Tools

| Tool | File | Purpose |
|------|------|---------|
| **code_execution** | `code_execution_tool.py` | Execute Python/bash, main OS interface |
| **call_subordinate** | `call_subordinate.py` | Delegate to sub-agent |
| **response** | `response.py` | Final response to user |
| **memory_save** | `memory_save.py` | Persist to vector DB |
| **memory_load** | `memory_load.py` | Recall from memory |
| **memory_delete** | `memory_delete.py` | Remove specific memories |
| **memory_forget** | `memory_forget.py` | Bulk memory removal |
| **browser_agent** | `browser_agent.py` | Web browsing via Playwright |
| **search_engine** | `search_engine.py` | SearXNG web search |
| **document_query** | `document_query.py` | RAG over documents |
| **scheduler** | `scheduler.py` | Schedule future tasks |
| **input** | `input.py` | Ask user for input |
| **notify_user** | `notify_user.py` | Push notification to user |
| **behaviour_adjustment** | `behaviour_adjustment.py` | Dynamic prompt changes |
| **wait** | `wait.py` | Pause execution |
| **vision_load** | `vision_load.py` | Load images for vision models |
| **a2a_chat** | `a2a_chat.py` | Agent-to-Agent protocol |
| **unknown** | `unknown.py` | Handler for unrecognized tools |

## Creating New Tools

1. Create `python/tools/my_tool.py`:
```python
from python.helpers.tool import Tool, Response

class MyTool(Tool):
    async def execute(self, **kwargs) -> Response:
        # Implementation
        return Response(message="result", break_loop=False)
```

2. Create `prompts/agent.system.tool.my_tool.md`:
```markdown
## my_tool
Use this tool to...
**Parameters:**
- param1: description
```

3. Tool auto-loads on next agent start.

## Tool Response

```python
Response(
    message: str,           # Result shown to agent
    break_loop: bool,       # True = stop agent loop (e.g., response tool)
    data: Any = None        # Optional structured data
)
```

## Key Tools Detail

### code_execution_tool.py
- Primary OS interface
- Executes in Docker container (SSH) or local shell
- Handles timeouts, output streaming
- **CRITICAL**: All file/system operations go through here

### call_subordinate.py
- Creates child agent with narrower focus
- Uses profiles from `agents/` directory
- Child reports back to parent

### memory_*.py
- Interface to FAISS vector DB in `memory/`
- Embeddings via configured embedding model
- Supports semantic search, exact match

### browser_agent.py
- Playwright-based browsing
- Headless by default
- Can capture screenshots
