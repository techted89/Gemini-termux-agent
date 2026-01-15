from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List


def chunk_text(
    text: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[str]:
    """
    Splits text into chunks using RecursiveCharacterTextSplitter.

    Args:
        text: The text to split.
        chunk_size: The maximum size of each chunk.
        chunk_overlap: The overlap between chunks.

    Returns:
        A list of text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    return splitter.split_text(text)
