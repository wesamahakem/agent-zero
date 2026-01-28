#!/usr/bin/env python3
"""
Audit/Reporting Workflow for Merge Conflict Resolutions

This script analyzes merged pull requests to identify potential issues from
"keep both changes" conflict resolutions. It flags suspicious patterns like
duplicated blocks, imports, functions, and conflict markers.

Usage:
    python scripts/audit-merge-conflicts.py [options]

Examples:
    # Audit last 10 merged PRs
    python scripts/audit-merge-conflicts.py --limit 10

    # Audit specific commits
    python scripts/audit-merge-conflicts.py --commits abc123,def456

    # Generate HTML report and fail if findings
    python scripts/audit-merge-conflicts.py --output report.html --fail-on-findings
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Finding:
    """Represents a suspicious pattern found in a merge conflict resolution."""
    type: str
    line_number: int
    content: str
    severity: str = "medium"
    description: str = ""


@dataclass
class FileDiff:
    """Represents changes to a file in a merge commit."""
    filepath: str
    hunks: List[str] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)


@dataclass
class MergeCommit:
    """Represents a merge commit with its metadata and changes."""
    commit_hash: str
    title: str
    author: str
    date: str
    pr_number: Optional[str] = None
    files: List[FileDiff] = field(default_factory=list)


class MergeConflictAuditor:
    """Main auditor class for analyzing merge commits."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.merge_commits: List[MergeCommit] = []

    def get_merge_commits(self, limit: int = 50, commit_hashes: Optional[List[str]] = None) -> List[str]:
        """
        Get list of merge commit hashes.

        Args:
            limit: Maximum number of merge commits to retrieve
            commit_hashes: Specific commit hashes to analyze (overrides limit)

        Returns:
            List of commit hashes
        """
        if commit_hashes:
            return commit_hashes

        try:
            cmd = [
                "git", "-C", str(self.repo_path),
                "log", "--merges", "--pretty=format:%H",
                f"-{limit}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            commits = result.stdout.strip().split('\n')
            return [c for c in commits if c]
        except subprocess.CalledProcessError as e:
            print(f"Error getting merge commits: {e}", file=sys.stderr)
            return []

    def get_commit_metadata(self, commit_hash: str) -> Optional[MergeCommit]:
        """
        Extract metadata from a merge commit.

        Args:
            commit_hash: Git commit hash

        Returns:
            MergeCommit object with metadata
        """
        try:
            # Get commit message, author, and date
            cmd = [
                "git", "-C", str(self.repo_path),
                "show", "--no-patch", "--pretty=format:%s|%an|%ai",
                commit_hash
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            parts = result.stdout.strip().split('|')

            if len(parts) < 3:
                return None

            title, author, date = parts[0], parts[1], parts[2]

            # Try to extract PR number from commit message
            pr_match = re.search(r'#(\d+)', title)
            pr_number = pr_match.group(1) if pr_match else None

            return MergeCommit(
                commit_hash=commit_hash,
                title=title,
                author=author,
                date=date,
                pr_number=pr_number
            )
        except subprocess.CalledProcessError as e:
            print(f"Error getting metadata for {commit_hash}: {e}", file=sys.stderr)
            return None

    def get_commit_diff(self, commit_hash: str) -> Dict[str, List[str]]:
        """
        Get the diff for a merge commit.

        Args:
            commit_hash: Git commit hash

        Returns:
            Dictionary mapping file paths to their diff hunks
        """
        try:
            # Get the diff with context
            cmd = [
                "git", "-C", str(self.repo_path),
                "show", "--format=", "-U5",  # 5 lines of context
                commit_hash
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return self._parse_diff(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error getting diff for {commit_hash}: {e}", file=sys.stderr)
            return {}

    def _parse_diff(self, diff_text: str) -> Dict[str, List[str]]:
        """
        Parse git diff output into file paths and hunks.

        Args:
            diff_text: Raw git diff output

        Returns:
            Dictionary mapping file paths to their diff hunks
        """
        file_diffs = {}
        current_file = None
        current_hunk = []

        for line in diff_text.split('\n'):
            if line.startswith('diff --git'):
                # Save previous file's hunk
                if current_file and current_hunk:
                    if current_file not in file_diffs:
                        file_diffs[current_file] = []
                    file_diffs[current_file].append('\n'.join(current_hunk))
                    current_hunk = []

                # Extract file path
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)

            elif line.startswith('@@'):
                # New hunk - save previous hunk
                if current_file and current_hunk:
                    if current_file not in file_diffs:
                        file_diffs[current_file] = []
                    file_diffs[current_file].append('\n'.join(current_hunk))
                    current_hunk = []
                current_hunk.append(line)

            elif current_file and current_hunk:
                current_hunk.append(line)

        # Save final hunk
        if current_file and current_hunk:
            if current_file not in file_diffs:
                file_diffs[current_file] = []
            file_diffs[current_file].append('\n'.join(current_hunk))

        return file_diffs

    def analyze_hunk(self, hunk: str, filepath: str) -> List[Finding]:
        """
        Analyze a diff hunk for suspicious patterns.

        Args:
            hunk: Diff hunk text
            filepath: Path to the file being analyzed

        Returns:
            List of Finding objects
        """
        findings = []
        lines = hunk.split('\n')

        # Extract added lines and their line numbers
        added_lines = []
        line_num = 0

        # Parse hunk header to get starting line number
        header_match = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', lines[0])
        if header_match:
            line_num = int(header_match.group(1)) - 1

        for line in lines[1:]:
            if line.startswith('+'):
                line_num += 1
                added_lines.append((line_num, line[1:]))
            elif not line.startswith('-'):
                line_num += 1

        # Check for conflict markers
        findings.extend(self._check_conflict_markers(added_lines))

        # Check for duplicate imports
        if filepath.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs')):
            findings.extend(self._check_duplicate_imports(added_lines, filepath))

        # Check for duplicated code blocks
        findings.extend(self._check_duplicate_blocks(added_lines))

        # Check for duplicate function/class definitions
        findings.extend(self._check_duplicate_definitions(added_lines, filepath))

        return findings

    def _check_conflict_markers(self, added_lines: List[Tuple[int, str]]) -> List[Finding]:
        """Check for git conflict markers in added lines."""
        findings = []
        markers = ['<<<<<<<', '=======', '>>>>>>>']

        for line_num, content in added_lines:
            stripped = content.strip()
            for marker in markers:
                # Check if line starts with marker to reduce false positives
                if stripped.startswith(marker):
                    findings.append(Finding(
                        type="conflict_marker",
                        line_number=line_num,
                        content=content.strip(),
                        severity="high",
                        description=f"Git conflict marker '{marker}' found in merged code"
                    ))
                    break

        return findings

    def _check_duplicate_imports(self, added_lines: List[Tuple[int, str]], filepath: str) -> List[Finding]:
        """Check for duplicate import statements."""
        findings = []
        import_patterns = {
            '.py': [r'^\s*import\s+', r'^\s*from\s+.+\s+import\s+'],
            '.js': [r'^\s*import\s+', r'^\s*require\s*\('],
            '.ts': [r'^\s*import\s+', r'^\s*require\s*\('],
            '.jsx': [r'^\s*import\s+', r'^\s*require\s*\('],
            '.tsx': [r'^\s*import\s+', r'^\s*require\s*\('],
            '.java': [r'^\s*import\s+'],
            '.go': [r'^\s*import\s+'],
            '.rs': [r'^\s*use\s+'],
        }

        ext = Path(filepath).suffix
        if ext not in import_patterns:
            return findings

        imports_seen = {}
        for line_num, content in added_lines:
            for pattern in import_patterns[ext]:
                if re.match(pattern, content):
                    normalized = content.strip()
                    if normalized in imports_seen:
                        findings.append(Finding(
                            type="duplicate_import",
                            line_number=line_num,
                            content=content.strip(),
                            severity="medium",
                            description=f"Duplicate import statement (also at line {imports_seen[normalized]})"
                        ))
                    else:
                        imports_seen[normalized] = line_num
                    break

        return findings

    def _check_duplicate_blocks(self, added_lines: List[Tuple[int, str]]) -> List[Finding]:
        """Check for adjacent duplicated code blocks."""
        findings = []

        # Look for sequences of 3+ identical consecutive lines
        i = 0
        while i < len(added_lines) - 2:
            line1_num, line1 = added_lines[i]
            
            # Skip blank lines
            if not line1.strip():
                i += 1
                continue

            # Check if we have repeating pattern
            line1_stripped = line1.strip()
            
            # Count consecutive duplicates
            count = 1
            j = i + 1
            while j < len(added_lines):
                line_j_stripped = added_lines[j][1].strip()
                # Skip blank lines in the check
                if not line_j_stripped:
                    j += 1
                    continue
                # Check if it matches the pattern
                if line_j_stripped == line1_stripped:
                    count += 1
                    j += 1
                else:
                    break

            if count >= 3:
                findings.append(Finding(
                    type="duplicate_block",
                    line_number=line1_num,
                    content=line1_stripped,
                    severity="medium",
                    description=f"Line repeated {count} times consecutively"
                ))
                i = j
                continue

            i += 1

        return findings

    def _check_duplicate_definitions(self, added_lines: List[Tuple[int, str]], filepath: str) -> List[Finding]:
        """Check for duplicate function or class definitions."""
        findings = []

        definition_patterns = {
            '.py': [r'^\s*def\s+(\w+)\s*\(', r'^\s*class\s+(\w+)\s*[:(]'],
            '.js': [r'^\s*function\s+(\w+)\s*\(', r'^\s*class\s+(\w+)\s*[{]'],
            '.ts': [r'^\s*function\s+(\w+)\s*\(', r'^\s*class\s+(\w+)\s*[{]'],
            '.jsx': [r'^\s*function\s+(\w+)\s*\(', r'^\s*class\s+(\w+)\s*[{]'],
            '.tsx': [r'^\s*function\s+(\w+)\s*\(', r'^\s*class\s+(\w+)\s*[{]'],
            '.java': [r'^\s*(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(', r'^\s*(?:public|private|protected)?\s*class\s+(\w+)'],
            '.go': [r'^\s*func\s+(\w+)\s*\('],
            '.rs': [r'^\s*fn\s+(\w+)\s*\(', r'^\s*struct\s+(\w+)'],
        }

        ext = Path(filepath).suffix
        if ext not in definition_patterns:
            return findings

        definitions_seen = {}
        for line_num, content in added_lines:
            for pattern in definition_patterns[ext]:
                match = re.match(pattern, content)
                if match:
                    name = match.group(1)
                    if name in definitions_seen:
                        findings.append(Finding(
                            type="duplicate_definition",
                            line_number=line_num,
                            content=content.strip(),
                            severity="high",
                            description=f"Duplicate definition of '{name}' (also at line {definitions_seen[name]})"
                        ))
                    else:
                        definitions_seen[name] = line_num
                    break

        return findings

    def analyze_merge_commit(self, commit_hash: str) -> Optional[MergeCommit]:
        """
        Analyze a single merge commit for suspicious patterns.

        Args:
            commit_hash: Git commit hash

        Returns:
            MergeCommit object with findings
        """
        merge = self.get_commit_metadata(commit_hash)
        if not merge:
            return None

        file_diffs_dict = self.get_commit_diff(commit_hash)

        for filepath, hunks in file_diffs_dict.items():
            file_diff = FileDiff(filepath=filepath, hunks=hunks)

            for hunk in hunks:
                findings = self.analyze_hunk(hunk, filepath)
                file_diff.findings.extend(findings)

            # Only add files that have hunks (even if no findings detected)
            # Files without findings can still be useful for context in the report
            if file_diff.hunks:
                merge.files.append(file_diff)

        return merge

    def run_audit(self, limit: int = 50, commit_hashes: Optional[List[str]] = None) -> None:
        """
        Run the audit on merge commits.

        Args:
            limit: Maximum number of merge commits to analyze
            commit_hashes: Specific commit hashes to analyze
        """
        commits = self.get_merge_commits(limit=limit, commit_hashes=commit_hashes)
        print(f"Analyzing {len(commits)} merge commit(s)...", file=sys.stderr)

        for commit_hash in commits:
            merge = self.analyze_merge_commit(commit_hash)
            if merge:
                self.merge_commits.append(merge)

        print(f"Analysis complete. Processed {len(self.merge_commits)} merge commit(s).", file=sys.stderr)

    def generate_markdown_report(self) -> str:
        """
        Generate a Markdown report of the audit findings.

        Returns:
            Markdown-formatted report string
        """
        report = []
        report.append("# Merge Conflict Audit Report\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Commits Analyzed:** {len(self.merge_commits)}\n")

        total_findings = sum(
            len(f.findings)
            for merge in self.merge_commits
            for f in merge.files
        )
        report.append(f"**Total Findings:** {total_findings}\n")
        report.append("\n---\n")

        if total_findings == 0:
            report.append("\n✅ **No suspicious patterns detected in analyzed merge commits.**\n")
        else:
            report.append("\n## Summary by Severity\n")
            severity_counts = defaultdict(int)
            for merge in self.merge_commits:
                for file_diff in merge.files:
                    for finding in file_diff.findings:
                        severity_counts[finding.severity] += 1

            for severity in ["high", "medium", "low"]:
                if severity in severity_counts:
                    report.append(f"- **{severity.upper()}:** {severity_counts[severity]}\n")

            report.append("\n---\n")

        for merge in self.merge_commits:
            findings_in_commit = sum(len(f.findings) for f in merge.files)

            if findings_in_commit > 0:
                report.append(f"\n## Commit: {merge.commit_hash[:8]}\n")
                report.append(f"**Title:** {merge.title}\n")
                if merge.pr_number:
                    report.append(f"**PR:** #{merge.pr_number}\n")
                report.append(f"**Author:** {merge.author}\n")
                report.append(f"**Date:** {merge.date}\n")
                report.append(f"**Findings:** {findings_in_commit}\n")

                for file_diff in merge.files:
                    if file_diff.findings:
                        report.append(f"\n### File: `{file_diff.filepath}`\n")

                        # Group findings by type
                        findings_by_type = defaultdict(list)
                        for finding in file_diff.findings:
                            findings_by_type[finding.type].append(finding)

                        for finding_type, findings in findings_by_type.items():
                            report.append(f"\n#### {finding_type.replace('_', ' ').title()}\n")
                            for finding in findings:
                                severity_emoji = {
                                    "high": "🔴",
                                    "medium": "🟡",
                                    "low": "🟢"
                                }.get(finding.severity, "⚪")

                                report.append(f"\n{severity_emoji} **Line {finding.line_number}** ({finding.severity})\n")
                                report.append(f"- {finding.description}\n")
                                report.append(f"- Code: `{finding.content}`\n")

                report.append("\n---\n")

        return ''.join(report)

    def generate_html_report(self) -> str:
        """
        Generate an HTML report of the audit findings.

        Returns:
            HTML-formatted report string
        """
        total_findings = sum(
            len(f.findings)
            for merge in self.merge_commits
            for f in merge.files
        )

        severity_counts = defaultdict(int)
        for merge in self.merge_commits:
            for file_diff in merge.files:
                for finding in file_diff.findings:
                    severity_counts[finding.severity] += 1

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Merge Conflict Audit Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .severity-high {{ color: #e53e3e; }}
        .severity-medium {{ color: #dd6b20; }}
        .severity-low {{ color: #38a169; }}
        .commit {{
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .commit-header {{
            background: #f7fafc;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .commit-title {{
            font-size: 18px;
            font-weight: 600;
            margin: 0 0 10px 0;
        }}
        .commit-meta {{
            color: #718096;
            font-size: 14px;
        }}
        .file {{
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .file:last-child {{
            border-bottom: none;
        }}
        .file-path {{
            font-family: 'Monaco', 'Menlo', monospace;
            background: #f7fafc;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
            margin-bottom: 15px;
        }}
        .finding {{
            margin: 10px 0;
            padding: 15px;
            border-left: 4px solid;
            background: #f7fafc;
            border-radius: 4px;
        }}
        .finding.high {{ border-left-color: #e53e3e; }}
        .finding.medium {{ border-left-color: #dd6b20; }}
        .finding.low {{ border-left-color: #38a169; }}
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .finding-type {{
            font-weight: 600;
            text-transform: capitalize;
        }}
        .finding-line {{
            color: #718096;
            font-size: 14px;
        }}
        .finding-description {{
            margin: 5px 0;
            color: #4a5568;
        }}
        .finding-code {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            overflow-x: auto;
            margin-top: 8px;
        }}
        .no-findings {{
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .no-findings-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Merge Conflict Audit Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <div class="summary-card">
            <h3>Commits Analyzed</h3>
            <div class="value">{len(self.merge_commits)}</div>
        </div>
        <div class="summary-card">
            <h3>Total Findings</h3>
            <div class="value">{total_findings}</div>
        </div>
        <div class="summary-card">
            <h3>High Severity</h3>
            <div class="value severity-high">{severity_counts.get('high', 0)}</div>
        </div>
        <div class="summary-card">
            <h3>Medium Severity</h3>
            <div class="value severity-medium">{severity_counts.get('medium', 0)}</div>
        </div>
    </div>
"""

        if total_findings == 0:
            html += """
    <div class="no-findings">
        <div class="no-findings-icon">✅</div>
        <h2>No Suspicious Patterns Detected</h2>
        <p>All analyzed merge commits appear to be clean.</p>
    </div>
"""
        else:
            for merge in self.merge_commits:
                findings_in_commit = sum(len(f.findings) for f in merge.files)
                if findings_in_commit > 0:
                    pr_info = f" (PR #{merge.pr_number})" if merge.pr_number else ""
                    html += f"""
    <div class="commit">
        <div class="commit-header">
            <div class="commit-title">{merge.title}{pr_info}</div>
            <div class="commit-meta">
                <strong>Commit:</strong> {merge.commit_hash[:8]} |
                <strong>Author:</strong> {merge.author} |
                <strong>Date:</strong> {merge.date} |
                <strong>Findings:</strong> {findings_in_commit}
            </div>
        </div>
"""

                    for file_diff in merge.files:
                        if file_diff.findings:
                            html += f"""
        <div class="file">
            <div class="file-path">{file_diff.filepath}</div>
"""
                            for finding in file_diff.findings:
                                finding_type = finding.type.replace('_', ' ').title()
                                html += f"""
            <div class="finding {finding.severity}">
                <div class="finding-header">
                    <span class="finding-type">{finding_type}</span>
                    <span class="finding-line">Line {finding.line_number} • {finding.severity.upper()}</span>
                </div>
                <div class="finding-description">{finding.description}</div>
                <div class="finding-code">{finding.content}</div>
            </div>
"""
                            html += """
        </div>
"""

                    html += """
    </div>
"""

        html += """
</body>
</html>
"""
        return html

    def has_findings(self) -> bool:
        """Check if any findings were detected."""
        return any(
            len(f.findings) > 0
            for merge in self.merge_commits
            for f in merge.files
        )


def main():
    """Main entry point for the audit script."""
    parser = argparse.ArgumentParser(
        description="Audit merge commits for suspicious conflict resolutions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audit last 10 merged PRs
  %(prog)s --limit 10

  # Audit specific commits
  %(prog)s --commits abc123,def456,789ghi

  # Generate HTML report
  %(prog)s --limit 20 --output report.html

  # Fail if findings detected (for CI)
  %(prog)s --fail-on-findings

  # Output JSON for programmatic processing
  %(prog)s --format json --output findings.json
        """
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of merge commits to analyze (default: 50)"
    )

    parser.add_argument(
        "--commits",
        type=str,
        help="Comma-separated list of specific commit hashes to analyze"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: stdout)"
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "html", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with non-zero status if findings are detected"
    )

    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="Path to git repository (default: current directory)"
    )

    args = parser.parse_args()

    # Parse commit hashes if provided
    commit_hashes = None
    if args.commits:
        commit_hashes = [c.strip() for c in args.commits.split(',') if c.strip()]

    # Run the audit
    auditor = MergeConflictAuditor(repo_path=args.repo_path)
    auditor.run_audit(limit=args.limit, commit_hashes=commit_hashes)

    # Generate report
    if args.format == "markdown":
        report = auditor.generate_markdown_report()
    elif args.format == "html":
        report = auditor.generate_html_report()
    elif args.format == "json":
        # Generate JSON report
        json_data = {
            "generated_at": datetime.now().isoformat(),
            "commits_analyzed": len(auditor.merge_commits),
            "total_findings": sum(len(f.findings) for m in auditor.merge_commits for f in m.files),
            "commits": []
        }

        for merge in auditor.merge_commits:
            commit_data = {
                "hash": merge.commit_hash,
                "title": merge.title,
                "author": merge.author,
                "date": merge.date,
                "pr_number": merge.pr_number,
                "files": []
            }

            for file_diff in merge.files:
                file_data = {
                    "path": file_diff.filepath,
                    "findings": [
                        {
                            "type": f.type,
                            "line_number": f.line_number,
                            "content": f.content,
                            "severity": f.severity,
                            "description": f.description
                        }
                        for f in file_diff.findings
                    ]
                }
                commit_data["files"].append(file_data)

            json_data["commits"].append(commit_data)

        report = json.dumps(json_data, indent=2)

    # Output report
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding='utf-8')
        print(f"Report written to: {output_path}", file=sys.stderr)
    else:
        print(report)

    # Exit with appropriate code
    if args.fail_on_findings and auditor.has_findings():
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
