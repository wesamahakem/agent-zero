# Scripts Directory

This directory contains utility scripts for the agent-zero project.

## Available Scripts

### audit-merge-conflicts.py

Audits merged pull requests to identify potential issues from "keep both changes" conflict resolutions.

**Documentation:** See [docs/merge-conflict-audit.md](../docs/merge-conflict-audit.md) for detailed usage instructions.

**Quick Start:**
```bash
# Audit last 10 merge commits
python scripts/audit-merge-conflicts.py --limit 10

# Generate HTML report
python scripts/audit-merge-conflicts.py --format html --output report.html
```

**Purpose:** Analysis only - identifies suspicious patterns like duplicated code blocks, imports, functions, and conflict markers in merged code.
