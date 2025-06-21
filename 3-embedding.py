import os
import json
from typing import List
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from utils.db import connect_lancedb

load_dotenv(override=True)

# --- Configuration ---
INPUT_DIR = "data/chunked"
TABLE_NAME = "docling"

# --- LanceDB Schema Definition ---

# Get the OpenAI embedding function from the LanceDB registry
func = get_registry().get("openai").create(name="text-embedding-3-large")

class ChunkMetadata(LanceModel):
    """Metadata schema for each chunk. Fields must be in alphabetical order."""
    filename: str | None
    page_numbers: List[int]
    title: str | None

class Chunks(LanceModel):
    """Main table schema with text, vector, and metadata."""
    text: str = func.SourceField()
    vector: Vector(func.ndims()) = func.VectorField() # type: ignore
    metadata: ChunkMetadata

# --- Main Execution ---
def main():
    """
    Loads chunked JSON files, generates embeddings, and stores them in LanceDB.
    """
    # Connect to the LanceDB database
    db = connect_lancedb()

    # Create or open the LanceDB table
    try:
        table = db.open_table(TABLE_NAME)
        print(f"Opened existing table: '{TABLE_NAME}'")
    except Exception:
        print(f"Table '{TABLE_NAME}' not found. Creating a new one.")
        table = db.create_table(TABLE_NAME, schema=Chunks, mode="create")

    # Find all JSON files in the input directory
    try:
        json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        if not json_files:
            print(f"No JSON files found in {INPUT_DIR}. Please run the chunking script first.")
            return
    except FileNotFoundError:
        print(f"Error: Input directory not found at '{INPUT_DIR}'. Please run the chunking script first.")
        return

    print(f"Found {len(json_files)} chunked documents to process...")

    all_processed_chunks = []
    for json_filename in json_files:
        input_path = os.path.join(INPUT_DIR, json_filename)
        print(f"--> Loading chunks from: {input_path}")

        with open(input_path, "r", encoding="utf-8") as f:
            chunk_list = json.load(f)

        # Prepare each chunk to match the LanceDB schema
        for chunk_dict in chunk_list:
            meta = chunk_dict.get("meta", {})
            origin = meta.get("origin", {})
            headings = meta.get("headings", [])
            doc_items = meta.get("doc_items", [])

            # Safely extract page numbers
            page_numbers = []
            if doc_items:
                page_nos_set = set()
                for item in doc_items:
                    for prov in item.get("prov", []):
                        if 'page_no' in prov and prov['page_no'] is not None:
                            page_nos_set.add(prov['page_no'])
                page_numbers = sorted(list(page_nos_set))

            processed_chunk = {
                "text": chunk_dict.get("text", ""),
                "metadata": {
                    "filename": origin.get("filename"),
                    "page_numbers": page_numbers,
                    "title": headings[0] if headings else None,
                },
            }
            all_processed_chunks.append(processed_chunk)

    if not all_processed_chunks:
        print("No chunks were processed. Exiting.")
        return

    print(f"\nAdding {len(all_processed_chunks)} chunks to the '{TABLE_NAME}' table...")
    # This step automatically handles embedding generation
    table.add(all_processed_chunks)

    print("\nEmbedding and storage process complete.")
    print(f"Total rows in table: {table.count_rows()}")

if __name__ == "__main__":
    main()

