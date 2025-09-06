import os
from tools.file_io import read_file, write_file

def test_write_and_read_file_success(tmp_path):
    """
    Tests that writing to a file and then reading it back works correctly.
    tmp_path is a special pytest fixture that provides a temporary directory.
    """
    # Arrange: Define a filepath and content in the temporary directory
    filepath = tmp_path / "test_file.txt"
    content_to_write = "Hello, world!\nThis is a test."

    # Act: Write the file
    write_result = write_file.invoke({"filepath": str(filepath), "content": content_to_write})

    # Assert: Check if write was successful
    assert "Successfully wrote content" in write_result

    # Act: Read the file back
    read_content, error = read_file(str(filepath))

    # Assert: Check if read was successful and content matches
    assert error is None
    assert read_content == content_to_write

def test_read_file_not_found():
    """
    Tests that reading a non-existent file returns an appropriate error.
    """
    # Arrange: Define a path to a file that does not exist on Windows
    non_existent_filepath = r"C:\Windows\Temp\a_file_that_should_not_exist.tmp"

    # Act: Attempt to read the file
    content, error = read_file(non_existent_filepath)

    # Assert: Check that the content is None and an error message is returned
    assert content is None
    assert "File not found" in error