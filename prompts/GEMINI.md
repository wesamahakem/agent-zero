# Prompts Directory

All agent behavior defined via modular markdown templates. 96 files, ~95% of framework personality.

## Template System

Uses `{{ include "filename.md" }}` for composition. Files are concatenated at runtime.

## File Naming Convention

| Pattern | Purpose |
|---------|---------|
| `agent.system.*` | System prompt components |
| `agent.system.tool.*` | Per-tool instructions (appended to system) |
| `agent.system.main.*` | Core behavior sections (role, environment, communication) |
| `agent.extras.*` | Optional context additions |
| `fw.*` | Framework messages (errors, warnings, prompts) |
| `memory.*` | Memory subsystem (consolidation, queries, filtering) |
| `behaviour.*` | Dynamic behavior adjustment prompts |
| `browser_agent.*` | Browser automation prompts |

## Core Files (Start Here)

| File | Purpose |
|------|---------|
| `agent.system.main.md` | Root - includes role, environment, communication, solving, tips |
| `agent.system.main.role.md` | Agent identity and persona |
| `agent.system.main.communication.md` | How agent talks to user/subordinates |
| `agent.system.main.solving.md` | Problem-solving methodology |
| `agent.system.tools.md` | Tool usage instructions header |

## Tool Prompts

Each tool in `python/tools/` has matching `agent.system.tool.{name}.md`:
- `code_exe` - Code execution rules
- `memory` - Memory save/load/delete instructions
- `browser` - Browser agent guidelines
- `call_sub` - Subordinate delegation rules
- `response` - How to respond to user
- `search_engine`, `scheduler`, `document_query`, etc.

## Framework Messages (`fw.*`)

| File | When Used |
|------|-----------|
| `fw.error.md` | Tool execution errors |
| `fw.tool_result.md` | Wrap tool outputs |
| `fw.tool_not_found.md` | Unknown tool called |
| `fw.intervention.md` | User interrupts agent |
| `fw.msg_timeout.md` | Response timeout |
| `fw.msg_misformat.md` | Malformed agent output |
| `fw.memory_saved.md` | Confirm memory persistence |
| `fw.code.*.md` | Code execution states (running, reset, pause, max_time) |

## Memory Prompts

| File | Purpose |
|------|---------|
| `memory.consolidation.*` | Merge/dedupe memories |
| `memory.keyword_extraction.*` | Extract search terms |
| `memory.memories_filter.*` | AI filtering of recalled memories |
| `memory.memories_query.*` | Query formatting |
| `memory.solutions_*` | Solution-specific memory handling |

## Editing Guidelines

- **DO NOT** remove `{{ include }}` directives without understanding dependencies
- Test changes with actual agent interaction
- Changes apply immediately on next agent message (no restart needed)
- Keep prompts concise - token budget matters
- Use markdown formatting agent understands
