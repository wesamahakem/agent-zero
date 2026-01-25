import os
import pytest
import tempfile
import shutil
from python.helpers import files

@pytest.fixture
def temp_dir():
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path)

def test_read_text_files_in_dir_basic(temp_dir):
    # Create some files
    with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
        f.write("content1")
    with open(os.path.join(temp_dir, "file2.txt"), "w") as f:
        f.write("content2")

    result = files.read_text_files_in_dir(temp_dir)
    assert len(result) == 2
    assert result["file1.txt"] == "content1"
    assert result["file2.txt"] == "content2"

def test_read_text_files_in_dir_pattern(temp_dir):
    with open(os.path.join(temp_dir, "match.txt"), "w") as f:
        f.write("match")
    with open(os.path.join(temp_dir, "ignore.log"), "w") as f:
        f.write("ignore")

    result = files.read_text_files_in_dir(temp_dir, pattern="*.txt")
    assert len(result) == 1
    assert "match.txt" in result
    assert "ignore.log" not in result

def test_read_text_files_in_dir_size_limit(temp_dir):
    with open(os.path.join(temp_dir, "small.txt"), "w") as f:
        f.write("small")
    with open(os.path.join(temp_dir, "large.txt"), "w") as f:
        f.write("a" * 1000)

    result = files.read_text_files_in_dir(temp_dir, max_size=100)
    assert len(result) == 1
    assert "small.txt" in result
    assert "large.txt" not in result

def test_read_text_files_in_dir_binary_ignore(temp_dir):
    with open(os.path.join(temp_dir, "text.txt"), "w") as f:
        f.write("text")
    # Binary file (png signature)
    with open(os.path.join(temp_dir, "image.png"), "wb") as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')

    result = files.read_text_files_in_dir(temp_dir)
    assert "text.txt" in result
    # It might depend on mimetypes.guess_type.
    # If .png is recognized as image/png, it should be skipped.
    assert "image.png" not in result

def test_read_text_files_in_dir_empty(temp_dir):
    result = files.read_text_files_in_dir(temp_dir)
    assert result == {}

def test_read_text_files_non_existent_dir():
    result = files.read_text_files_in_dir("non_existent_dir_12345")
    assert result == {}
