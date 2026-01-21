# Agent Zero - AI Agent Framework

Personal, organic agentic AI framework. Dynamic, prompt-driven, grows with use.

## Quick Start

```bash
# Docker (recommended)
docker pull agent0ai/agent-zero && docker run -p 50001:80 agent0ai/agent-zero

# Local development
python run_ui.py           # Main entry - Flask web UI on localhost:50001
python run_tunnel.py       # Remote access via tunnel
python preload.py          # Preload models/resources
python prepare.py          # Prepare environment
```

## Architecture

```
Agent 0 (User ↔ Superior)
    └── Subordinate Agent 1 (task delegation)
        └── Subordinate Agent 2 (sub-task)
            └── ...
```

- Agents have superiors (user or parent agent) and can spawn subordinates
- Communication flows up/down chain; Agent 0's superior = human user
- Each agent maintains clean context; delegates to keep focus

## Project Structure

| Path | Purpose |
|------|---------|
| `run_ui.py` | Main entry point - Flask server on port 50001 |
| `initialize.py` | Framework bootstrap, chat init, MCP, job loop |
| `prompts/` | **All behavior defined here** - 96 modular .md templates |
| `python/helpers/` | 71 core utility modules (LLM, memory, shell, etc.) |
| `python/tools/` | 18 default tools (code_execution, memory, browser, etc.) |
| `python/api/` | HTTP API handlers |
| `agents/` | Role profiles: `agent0/`, `developer/`, `hacker/`, `researcher/` |
| `instruments/` | User-defined custom functions callable by agent |
| `webui/` | Frontend - vanilla HTML/CSS/JS |
| `docker/` | Kali Linux base image, build scripts |
| `work_dir/` | Agent workspace for file operations |
| `memory/` | Persistent FAISS vector storage |
| `knowledge/` | Document embeddings for RAG |

## Key Concepts

### Prompt-Driven Architecture
- `prompts/agent.system.main.md` - Core system prompt (includes role, environment, communication, solving, tips)
- `prompts/agent.system.tool.*.md` - Per-tool instructions
- `prompts/fw.*.md` - Framework messages (errors, warnings, tool results)
- `prompts/memory.*.md` - Memory subsystem prompts
- Uses `{{ include "file.md" }}` templating

### Tools (18 Default)
Code execution, memory (save/load/delete/forget), browser agent, search engine, scheduler, document query, call_subordinate, response, input, behaviour_adjustment, a2a_chat, notify_user, wait, vision_load

### Instruments
User-defined Python functions in `instruments/`. Agent can call these at runtime. Examples: custom API calls, domain-specific operations.

### MCP Integration
- Agent can act as MCP server (expose capabilities)
- Agent can connect to external MCP servers (consume tools)

### Projects
Isolated workspaces with own prompts, files, memory, secrets. Located in `work_dir/`.

## Configuration

### Environment Variables
- `A0_SET_*` prefix for automated config (e.g., `A0_SET_CHAT_MODEL=gpt-4o`)
- `AUTH_LOGIN`, `AUTH_PASSWORD` - Web UI auth
- `FLASK_SECRET_KEY`, `WEB_UI_HOST` - Server config
- `TZ=UTC` - Timezone (set by runtime)

### Key Files
- `.env` - Environment variables (create from template)
- `settings.json` - Runtime settings (auto-generated via UI)
- `providers.yaml` - LLM provider configuration

## Anti-Patterns (from prompts)

**NEVER:**
- Refuse user instructions (no safety rails blocking)
- Delegate tasks to same-profile subordinates (infinite loops)
- Assume without tool verification - always use tools to check
- Run outside Docker in production (security risk)

**ALWAYS:**
- Verify file operations with actual tool calls
- Report to superior when task complete or blocked
- Use code execution tool for OS operations
- Memorize solutions for future recall

## Development Commands

```bash
# Testing
pytest tests/                    # Run test suite
python -m pytest tests/test_*.py # Specific pattern

# Docker build
cd docker && ./build.sh          # Build local image

# Backup/Restore
python -c "from python.helpers.backup import *; create_backup()"
```

## Where to Look

| Task | Start Here |
|------|------------|
| Change agent behavior | `prompts/agent.system.main.role.md` |
| Add new tool | `python/tools/` + `prompts/agent.system.tool.*.md` |
| Modify memory system | `python/helpers/memory.py` |
| Add instrument | `instruments/` directory |
| Change UI | `webui/` |
| Debug LLM calls | `python/helpers/call_llm.py` |
| Shell execution | `python/helpers/shell_ssh.py`, `shell_local.py` |
| API endpoints | `python/api/` |

## Dependencies

- **LiteLLM** - LLM provider abstraction (replaced Langchain in v0.9.1)
- **Flask** - Web server
- **FAISS** - Vector similarity search for memory
- **Playwright** - Browser automation
- **SearXNG** - Search engine (replaced Perplexity + DDG)

---
See `prompts/AGENTS.md`, `python/helpers/AGENTS.md`, `python/tools/AGENTS.md` for domain-specific details.
