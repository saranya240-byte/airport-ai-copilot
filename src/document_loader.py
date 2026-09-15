from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


POLICY_DIRECTORY = "data/airport_policies"


def clean_text(text):
    """
    Clean unnecessary whitespace from policy text.
    """

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def get_metadata(file_path):
    """
    Extract metadata from the policy filename.
    """

    filename = file_path.name
    parts = filename.replace(".md", "").split("_")

    airport = parts[0].upper()
    category = "_".join(parts[1:])

    return {
        "source": filename,
        "airport": airport,
        "category": category
    }


def load_policy_documents(directory=POLICY_DIRECTORY):
    """
    Load all markdown policy documents.
    """

    documents = []

    directory_path = Path(directory)

    for file_path in directory_path.glob("*.md"):

        text = file_path.read_text(encoding="utf-8")

        cleaned_text = clean_text(text)

        metadata = get_metadata(file_path)

        documents.append({
            "text": cleaned_text,
            "metadata": metadata
        })

    return documents


def chunk_documents(documents):
    """
    Split policy documents into smaller chunks.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = []

    for document in documents:

        split_texts = text_splitter.split_text(
            document["text"]
        )

        for chunk in split_texts:

            chunks.append({
                "text": chunk,
                "metadata": document["metadata"]
            })

    return chunks