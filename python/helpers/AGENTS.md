# Python Helpers

71 utility modules. Core infrastructure for agent framework.

## Module Categories

### LLM & Providers
| Module | Purpose |
|--------|---------|
| `call_llm.py` | LiteLLM wrapper, all model calls go here |
| `providers.py` | Provider configuration from `providers.yaml` |
| `tokens.py` | Token counting utilities |
| `rate_limiter.py` | API rate limiting |

### Memory & Knowledge
| Module | Purpose |
|--------|---------|
| `memory.py` | Main memory interface (save, load, search) |
| `memory_consolidation.py` | Merge/dedupe memories via AI |
| `vector_db.py` | FAISS wrapper for embeddings |
| `knowledge_import.py` | Document ingestion for RAG |
| `document_query.py` | RAG query execution |

### Shell & Execution
| Module | Purpose |
|--------|---------|
| `shell_ssh.py` | SSH-based command execution (Docker runtime) |
| `shell_local.py` | Local shell execution (dev mode) |
| `tty_session.py` | Interactive terminal sessions |
| `docker.py` | Docker container management |
| `process.py` | Process lifecycle management |

### Browser & Web
| Module | Purpose |
|--------|---------|
| `browser.py` | Browser session management |
| `browser_use.py` | Browser-use library integration |
| `browser_use_monkeypatch.py` | Browser-use compatibility fixes |
| `playwright.py` | Playwright browser automation |
| `searxng.py` | SearXNG search integration |

### Communication & Protocols
| Module | Purpose |
|--------|---------|
| `mcp_server.py` | MCP server mode (expose agent as tool) |
| `mcp_handler.py` | MCP message handling |
| `fasta2a_server.py` | A2A protocol server |
| `fasta2a_client.py` | A2A protocol client |
| `rfc.py`, `rfc_exchange.py`, `rfc_files.py` | RFC-style messaging |

### Context & State
| Module | Purpose |
|--------|---------|
| `context.py` | Agent context management |
| `history.py` | Conversation history |
| `messages.py` | Message formatting |
| `persist_chat.py` | Chat persistence to disk |
| `subagents.py` | Subordinate agent configuration |

### Files & Storage
| Module | Purpose |
|--------|---------|
| `files.py` | File operations, path resolution, templates |
| `file_browser.py` | Web UI file browser |
| `file_tree.py` | Directory tree generation |
| `backup.py` | Backup/restore functionality |

### Infrastructure
| Module | Purpose |
|--------|---------|
| `runtime.py` | Runtime initialization, args, ports |
| `settings.py` | Settings management (from UI) |
| `dotenv.py` | Environment variable loading |
| `api.py` | Base API handler class |
| `extension.py` | Extension system base |
| `tool.py` | Base tool class |
| `extract_tools.py` | Dynamic tool/handler loading |

### Utilities
| Module | Purpose |
|--------|---------|
| `print_style.py` | Colored terminal output |
| `dirty_json.py` | Lenient JSON parsing |
| `strings.py` | String utilities |
| `guids.py` | Short ID generation |
| `crypto.py` | Encryption helpers |
| `secrets.py` | Credential management |
| `images.py` | Image processing |
| `wait.py` | Async wait utilities |

### Speech
| Module | Purpose |
|--------|---------|
| `whisper.py` | Speech-to-text |
| `kokoro_tts.py` | Text-to-speech |

## Key Patterns

### Import Style
```python
from python.helpers import files, runtime, dotenv
from python.helpers.print_style import PrintStyle
```

### Async First
Most modules use `asyncio`. Check for `async def` and `await`.

### Extension Points
- `tool.py` - Subclass for new tools
- `api.py` - Subclass `ApiHandler` for new endpoints
- `extension.py` - Framework extensions
