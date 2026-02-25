# Merge Conflict Audit Documentation

## Overview

The merge conflict audit tool analyzes previously merged pull requests to identify potential issues that may have been introduced through "keep both changes" conflict resolutions. This tool is designed for **analysis only** and does not modify any code.

## Purpose

When resolving merge conflicts, using "keep both changes" can sometimes introduce:
- Duplicated code blocks
- Duplicate import statements
- Duplicate function or class definitions
- Unresolved conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Repeated identical lines

This audit tool helps identify these patterns to facilitate manual review and correction.

## Installation

The audit script is located at `scripts/audit-merge-conflicts.py` and requires Python 3.6+. No additional dependencies beyond the standard library are needed.

## Usage

### Basic Usage

Run the audit on the last 50 merge commits (default):

```bash
python scripts/audit-merge-conflicts.py
```

### Common Options

#### Limit Number of Commits

Analyze only the last N merge commits:

```bash
python scripts/audit-merge-conflicts.py --limit 10
```

#### Analyze Specific Commits

Analyze specific commit hashes:

```bash
python scripts/audit-merge-conflicts.py --commits abc123,def456,789ghi
```

#### Generate HTML Report

Create a nicely formatted HTML report:

```bash
python scripts/audit-merge-conflicts.py --format html --output report.html
```

#### Generate JSON Report

Output findings in JSON format for programmatic processing:

```bash
python scripts/audit-merge-conflicts.py --format json --output findings.json
```

#### Fail on Findings (CI Mode)

Exit with non-zero status if any findings are detected (useful for CI pipelines):

```bash
python scripts/audit-merge-conflicts.py --fail-on-findings
```

### Full Command Reference

```
usage: audit-merge-conflicts.py [-h] [--limit LIMIT] [--commits COMMITS]
                                [--output OUTPUT]
                                [--format {markdown,html,json}]
                                [--fail-on-findings] [--repo-path REPO_PATH]

Audit merge commits for suspicious conflict resolutions

optional arguments:
  -h, --help            show this help message and exit
  --limit LIMIT         Maximum number of merge commits to analyze (default: 50)
  --commits COMMITS     Comma-separated list of specific commit hashes to analyze
  --output OUTPUT       Output file path (default: stdout)
  --format {markdown,html,json}
                        Output format (default: markdown)
  --fail-on-findings    Exit with non-zero status if findings are detected
  --repo-path REPO_PATH
                        Path to git repository (default: current directory)
```

## Understanding the Report

### Report Formats

1. **Markdown** (default): Human-readable text format suitable for terminal output and documentation
2. **HTML**: Interactive, styled web page with color-coded severity levels
3. **JSON**: Structured data format for programmatic processing and integration with other tools

### Severity Levels

The audit tool classifies findings into three severity levels:

- 🔴 **HIGH**: Critical issues that likely indicate problems
  - Conflict markers in merged code
  - Duplicate function/class definitions

- 🟡 **MEDIUM**: Suspicious patterns that should be reviewed
  - Duplicate import statements
  - Repeated code blocks (3+ consecutive identical lines)

- 🟢 **LOW**: Minor issues or potential false positives
  - Currently not used, reserved for future enhancements

### Finding Types

#### Conflict Markers

Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) found in merged code indicate an incomplete conflict resolution.

**Example:**
```
🔴 Line 42 (high)
- Git conflict marker '<<<<<<<<' found in merged code
- Code: `<<<<<<< HEAD`
```

**Action Required:** Remove conflict markers and properly merge the conflicting changes.

#### Duplicate Imports

The same import statement appears multiple times in added code.

**Example:**
```
🟡 Line 15 (medium)
- Duplicate import statement (also at line 10)
- Code: `import os`
```

**Action Required:** Remove redundant import statements to keep code clean.

#### Duplicate Blocks

The same line of code is repeated 3 or more times consecutively.

**Example:**
```
🟡 Line 88 (medium)
- Line repeated 5 times consecutively
- Code: `logger.info("Processing item")`
```

**Action Required:** Review the duplicated code and remove unnecessary repetitions.

#### Duplicate Definitions

The same function or class is defined multiple times in added code.

**Example:**
```
🔴 Line 120 (high)
- Duplicate definition of 'process_data' (also at line 95)
- Code: `def process_data(input):`
```

**Action Required:** Remove or rename duplicate definitions to avoid conflicts.

## Manual Review Checklist

When the audit identifies findings, follow this checklist for manual review:

### 1. Verify the Finding

- [ ] View the file at the reported line number
- [ ] Confirm the pattern is indeed present
- [ ] Check surrounding context to understand the intent

### 2. Assess Impact

- [ ] Does this affect functionality?
- [ ] Could this cause runtime errors?
- [ ] Does it violate code quality standards?
- [ ] Is this a false positive?

### 3. Determine Root Cause

- [ ] Review the merge commit's diff
- [ ] Check the conflicting branches
- [ ] Identify why "keep both" was problematic here

### 4. Fix if Necessary

- [ ] Remove duplicate/conflicting code
- [ ] Test the fix locally
- [ ] Create a new PR with the correction
- [ ] Reference the original merge commit in PR description

### 5. Document Findings

- [ ] Add notes to the audit report about false positives
- [ ] Update team documentation if this reveals a common issue
- [ ] Consider process improvements to prevent similar issues

## CI/CD Integration

### Running in CI Without Failing the Pipeline

By default, the audit exits with status 0 even if findings are detected:

```bash
# Runs audit and generates report, but doesn't fail the build
python scripts/audit-merge-conflicts.py --output audit-report.md
```

### Enforcing Audit Checks

To fail the CI pipeline when findings are detected:

```bash
# Exits with status 1 if any findings are found
python scripts/audit-merge-conflicts.py --fail-on-findings
```

### Example GitHub Actions Workflow

```yaml
name: Merge Conflict Audit

on:
  schedule:
    # Run weekly on Monday at 9 AM UTC
    - cron: '0 9 * * 1'
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch full history for merge commit analysis

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Run Merge Conflict Audit
        run: |
          python scripts/audit-merge-conflicts.py \
            --limit 20 \
            --format html \
            --output merge-audit-report.html

      - name: Upload Audit Report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: merge-audit-report
          path: merge-audit-report.html

      - name: Check for Findings and Comment (optional)
        run: |
          # Run with fail-on-findings to detect issues
          if ! python scripts/audit-merge-conflicts.py --limit 20 --fail-on-findings > /dev/null 2>&1; then
            echo "Merge conflict audit detected issues. Review the report artifact."
            exit 1
          fi
```

## Examples

### Example 1: Quick Check of Recent Merges

```bash
# Check last 5 merge commits
python scripts/audit-merge-conflicts.py --limit 5
```

**Sample Output:**
```markdown
# Merge Conflict Audit Report

**Generated:** 2026-01-28 10:30:45
**Commits Analyzed:** 5
**Total Findings:** 0

---

✅ **No suspicious patterns detected in analyzed merge commits.**
```

### Example 2: Detailed Analysis with HTML Output

```bash
# Analyze last 20 merges and create HTML report
python scripts/audit-merge-conflicts.py --limit 20 --format html --output report.html

# Open the report in your browser
open report.html  # macOS
xdg-open report.html  # Linux
start report.html  # Windows
```

### Example 3: Audit Specific PR Merge Commits

First, identify the merge commit hashes:

```bash
# Find merge commits for specific PRs
git log --merges --oneline --grep="#123\|#124\|#125"
```

Then run the audit:

```bash
# Audit those specific commits
python scripts/audit-merge-conflicts.py --commits a1b2c3d,e4f5g6h,i7j8k9l
```

### Example 4: JSON Output for Further Processing

```bash
# Generate JSON report
python scripts/audit-merge-conflicts.py --format json --output findings.json

# Process with jq (example: count findings by severity)
cat findings.json | jq '.commits[].files[].findings[] | .severity' | sort | uniq -c
```

## Limitations

### Known Limitations

1. **False Positives**: The tool may flag legitimate code patterns that happen to match the heuristics
2. **Language Support**: Pattern detection works best for Python, JavaScript/TypeScript, Java, Go, and Rust
   - Note: Java method detection may not catch all methods with complex return types (generics, arrays, fully-qualified types)
3. **Context Awareness**: The tool analyzes diffs without full semantic understanding of the code
4. **Intentional Duplicates**: Some patterns (like repeated logging statements) may be intentional
5. **Conflict Marker Detection**: Only detects markers at the start of lines to reduce false positives

### What the Tool Cannot Detect

- Semantic merge conflicts (code that compiles but has logic errors)
- Conflicts resolved by choosing one side completely
- Conflicts in binary files
- Complex multi-way conflicts

## Best Practices

1. **Run Regularly**: Schedule periodic audits (weekly or monthly) to catch issues early
2. **Review All High-Severity Findings**: Always manually review findings marked as "high" severity
3. **Track False Positives**: Document patterns that consistently trigger false positives
4. **Use in Code Review**: Run the audit on specific PRs before merging complex changes
5. **Combine with Testing**: Audit findings should supplement, not replace, comprehensive testing

## Troubleshooting

### "No merge commits found"

**Cause**: The repository has no merge commits, or you're on a branch without merge history.

**Solution**: 
- Ensure you've fetched the full git history: `git fetch --all`
- Check if merge commits exist: `git log --merges`
- Specify a different branch: `git checkout main`

### "Error getting diff for commit"

**Cause**: The commit hash doesn't exist or is not accessible.

**Solution**:
- Verify the commit exists: `git show <hash>`
- Ensure you have the commit in your local repository
- Try fetching: `git fetch --all`

### Script runs but finds nothing

**Cause**: The analyzed commits may not have the patterns the tool looks for.

**Solution**:
- This is normal if your merges are clean
- Try increasing `--limit` to analyze more commits
- Check recent complex merges manually to verify

## Contributing

If you encounter patterns that should be detected but aren't, or have suggestions for improvements:

1. Document the specific pattern with examples
2. Describe why it indicates a "keep both" conflict issue
3. Propose the detection logic
4. Submit an issue or pull request to the repository

## Support

For questions or issues with the audit tool:

1. Check this documentation for usage examples
2. Review the script's help: `python scripts/audit-merge-conflicts.py --help`
3. Check existing issues in the repository
4. Open a new issue with:
   - The command you ran
   - Expected vs. actual output
   - Repository context (if possible)
