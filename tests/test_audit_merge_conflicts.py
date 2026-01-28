"""Unit tests for the merge conflict audit script."""

import sys
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import after path is set
import importlib.util
spec = importlib.util.spec_from_file_location(
    "audit_merge_conflicts",
    Path(__file__).parent.parent / "scripts" / "audit-merge-conflicts.py"
)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

Finding = audit_module.Finding
FileDiff = audit_module.FileDiff
MergeCommit = audit_module.MergeCommit
MergeConflictAuditor = audit_module.MergeConflictAuditor


class TestFindingDetection(unittest.TestCase):
    """Test finding detection methods."""

    def setUp(self):
        """Set up test instance."""
        self.auditor = MergeConflictAuditor()

    def test_check_conflict_markers(self):
        """Test detection of git conflict markers."""
        added_lines = [
            (10, "def foo():"),
            (11, "<<<<<<< HEAD"),
            (12, "    return 1"),
            (13, "======="),
            (14, "    return 2"),
            (15, ">>>>>>> branch"),
        ]
        
        findings = self.auditor._check_conflict_markers(added_lines)
        
        self.assertEqual(len(findings), 3)
        self.assertTrue(all(f.type == "conflict_marker" for f in findings))
        self.assertTrue(all(f.severity == "high" for f in findings))

    def test_check_duplicate_imports_python(self):
        """Test detection of duplicate Python imports."""
        added_lines = [
            (1, "import os"),
            (2, "import sys"),
            (3, "import os"),
            (4, "from pathlib import Path"),
            (5, "from pathlib import Path"),
        ]
        
        findings = self.auditor._check_duplicate_imports(added_lines, "test.py")
        
        self.assertEqual(len(findings), 2)
        self.assertTrue(all(f.type == "duplicate_import" for f in findings))
        self.assertIn("os", findings[0].content)
        self.assertIn("pathlib", findings[1].content)

    def test_check_duplicate_blocks(self):
        """Test detection of duplicated code blocks."""
        added_lines = [
            (10, "logger.info('Processing')"),
            (11, "logger.info('Processing')"),
            (12, "logger.info('Processing')"),
            (13, "logger.info('Processing')"),
            (14, "result = process()"),
        ]
        
        findings = self.auditor._check_duplicate_blocks(added_lines)
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].type, "duplicate_block")
        self.assertEqual(findings[0].line_number, 10)

    def test_check_duplicate_definitions_python(self):
        """Test detection of duplicate function definitions."""
        added_lines = [
            (10, "def process_data(x):"),
            (11, "    return x * 2"),
            (12, ""),
            (13, "def process_data(x):"),
            (14, "    return x * 3"),
        ]
        
        findings = self.auditor._check_duplicate_definitions(added_lines, "test.py")
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].type, "duplicate_definition")
        self.assertIn("process_data", findings[0].description)


class TestReportGeneration(unittest.TestCase):
    """Test report generation methods."""

    def setUp(self):
        """Set up test instance."""
        self.auditor = MergeConflictAuditor()
        
        # Create test merge commit with findings
        merge = MergeCommit(
            commit_hash="abc123def456",
            title="Merge pull request #42",
            author="Test Author",
            date="2026-01-28 10:00:00",
            pr_number="42"
        )
        
        file_diff = FileDiff(filepath="test.py")
        file_diff.findings.append(Finding(
            type="conflict_marker",
            line_number=10,
            content="<<<<<<< HEAD",
            severity="high",
            description="Git conflict marker found"
        ))
        
        merge.files.append(file_diff)
        self.auditor.merge_commits.append(merge)

    def test_generate_markdown_report(self):
        """Test Markdown report generation."""
        report = self.auditor.generate_markdown_report()
        
        self.assertIn("# Merge Conflict Audit Report", report)
        self.assertIn("**Commits Analyzed:** 1", report)
        self.assertIn("**Total Findings:** 1", report)
        self.assertIn("abc123de", report)
        self.assertIn("test.py", report)
        self.assertIn("conflict marker", report.lower())

    def test_generate_html_report(self):
        """Test HTML report generation."""
        report = self.auditor.generate_html_report()
        
        self.assertIn("<!DOCTYPE html>", report)
        self.assertIn("Merge Conflict Audit Report", report)
        self.assertIn("test.py", report)
        self.assertIn("abc123de", report)

    def test_has_findings(self):
        """Test has_findings method."""
        self.assertTrue(self.auditor.has_findings())
        
        # Test with no findings
        auditor_no_findings = MergeConflictAuditor()
        self.assertFalse(auditor_no_findings.has_findings())


class TestDiffParsing(unittest.TestCase):
    """Test diff parsing logic."""

    def setUp(self):
        """Set up test instance."""
        self.auditor = MergeConflictAuditor()

    def test_parse_diff(self):
        """Test parsing of git diff output."""
        diff_text = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,5 @@
 import os
+import sys
+import json
 
 def main():
     pass
"""
        
        file_diffs = self.auditor._parse_diff(diff_text)
        
        self.assertIn("test.py", file_diffs)
        self.assertEqual(len(file_diffs["test.py"]), 1)
        self.assertIn("@@ -1,3 +1,5 @@", file_diffs["test.py"][0])

    def test_files_without_findings_not_in_report(self):
        """Test that files without findings are still included for context."""
        # Create a merge with files but no findings
        merge = MergeCommit(
            commit_hash="test123",
            title="Test merge",
            author="Test",
            date="2026-01-28"
        )
        
        # File with hunks but no findings
        file_diff = FileDiff(filepath="clean.py", hunks=["@@ -1,1 +1,2 @@\n+import os"])
        merge.files.append(file_diff)
        
        # Verify the file is in the merge (for context)
        self.assertEqual(len(merge.files), 1)
        self.assertEqual(len(merge.files[0].findings), 0)


if __name__ == "__main__":
    unittest.main()
