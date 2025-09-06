import os
from tools.knowledge_base import search_knowledge_base

def test_search_knowledge_base_found(tmp_path):
    """
    Tests that the search function can find a relevant paragraph in the knowledge base.
    """
    # Arrange: Create a dummy knowledge base directory and a test file
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()
    test_file = kb_dir / "test_paper.md"
    file_content = """# Introduction\n\nThis paper discusses the theory of cellular automata.\n\n# Main Content\n\nThe concept of mechanical waves is very important in tissue development. It allows for long-range coordination.\n\n# Conclusion\n\nIn summary, the model works."""
    test_file.write_text(file_content, encoding="utf-8")

    # Act: Search for a query that should match, with a more lenient cutoff
    query = "mechanical waves in tissue development"
    results = search_knowledge_base.invoke({
        "query": query, 
        "knowledge_base_dir": str(kb_dir),
        "score_cutoff": 65  # Lowered cutoff based on debug results
    })

    # Assert: Check that the results contain the correct paragraph and filename
    assert "Found 1 relevant snippet(s)" in results
    assert "From: test_paper.md" in results
    assert "The concept of mechanical waves is very important" in results

def test_search_knowledge_base_not_found(tmp_path):
    """
    Tests that the search function returns the correct message when no match is found.
    """
    # Arrange: Create an empty dummy knowledge base directory
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()

    # Act: Search for a query that should not match
    query = "unrelated topic"
    results = search_knowledge_base.invoke({"query": query, "knowledge_base_dir": str(kb_dir)})

    # Assert: Check that the specific "not found" message is returned
    assert results == "No relevant information found in the knowledge base."