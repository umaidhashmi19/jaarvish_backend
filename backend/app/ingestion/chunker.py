from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list[str]:
    """
    Split text into overlapping chunks.
    chunk_overlap prevents answer cutoff at chunk boundaries.
    """
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    document = Document(text=text)
    nodes = splitter.get_nodes_from_documents([document])

    return [node.get_content() for node in nodes]