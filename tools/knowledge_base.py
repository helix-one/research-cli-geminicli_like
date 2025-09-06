
import os
from thefuzz import fuzz
from langchain.tools import tool

@tool
def search_knowledge_base(query: str, knowledge_base_dir: str = "knowledge_base", score_cutoff: int = 80) -> str:
    """
    Searches through all .md files in a directory using fuzzy string matching
    and returns paragraphs that are similar to the query.

    Args:
        query: The string to search for.
        knowledge_base_dir: The directory containing the knowledge base files.
        score_cutoff: The minimum similarity score (0-100) to consider a match.

    Returns:
        A formatted string containing the search results, or a message if no results were found.
    """
    if not os.path.isdir(knowledge_base_dir):
        return f"Error: Knowledge base directory not found at '{knowledge_base_dir}'"

    matches = []
    for filename in os.listdir(knowledge_base_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(knowledge_base_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    # Split content into paragraphs based on blank lines
                    paragraphs = f.read().split('\n\n')
                    for para in paragraphs:
                        if not para.strip():
                            continue
                        # Use partial_ratio for better matching of phrases within larger paragraphs
                        score = fuzz.partial_ratio(query.lower(), para.lower())
                        if score >= score_cutoff:
                            matches.append({
                                "filepath": filename,
                                "paragraph": para.strip(),
                                "score": score
                            })
            except Exception as e:
                print(f"Could not read file {filepath}: {e}")

    if not matches:
        return "No relevant information found in the knowledge base."

    # Sort matches by score, highest first
    matches.sort(key=lambda x: x['score'], reverse=True)

    # Format the results
    results_str = f"Found {len(matches)} relevant snippet(s) for '{query}':\n"
    for match in matches:
        results_str += f"\n--- From: {match['filepath']} (Similarity Score: {match['score']}) ---\n"
        results_str += match['paragraph']
        results_str += "\n"
    
    return results_str
