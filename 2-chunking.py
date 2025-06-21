import os
import json
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from openai import OpenAI
from utils.tokenizer import OpenAITokenizerWrapper

load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# --- Configuration ---
INPUT_DIR = "data/extracted"
OUTPUT_DIR = "data/chunked"
MAX_TOKENS = 8191  # text-embedding-3-large's maximum context length

# --- Main Execution ---
def main():
    """
    Loads extracted Markdown files, chunks them, and saves the chunks as JSON.
    """
    print(f"Ensuring output directory exists: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # The converter is needed to load markdown files back into Document objects
    converter = DocumentConverter()
    tokenizer = OpenAITokenizerWrapper()
    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=MAX_TOKENS,
        merge_peers=True,
    )

    # Find all markdown files in the input directory
    try:
        markdown_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".md")]
        if not markdown_files:
            print(f"No Markdown files found in {INPUT_DIR}. Please run the extraction script first.")
            return
    except FileNotFoundError:
        print(f"Error: Input directory not found at '{INPUT_DIR}'. Please run the extraction script first.")
        return

    print(f"Found {len(markdown_files)} documents to chunk...")

    for md_filename in markdown_files:
        input_path = os.path.join(INPUT_DIR, md_filename)
        print(f"--> Processing and chunking: {input_path}")

        try:
            # Use the converter to load the markdown file back into a Docling Document
            result = converter.convert(input_path)

            if result.document:
                # Apply the hybrid chunker
                chunk_iter = chunker.chunk(dl_doc=result.document)
                chunks = list(chunk_iter)

                # Serialize chunks to a list of dictionaries
                chunk_data = [chunk.model_dump() for chunk in chunks]

                # Save the chunks to a JSON file
                output_filename = md_filename.replace(".md", ".json")
                output_path = os.path.join(OUTPUT_DIR, output_filename)

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(chunk_data, f, indent=2)

                print(f"    ✔ Saved {len(chunks)} chunks to {output_path}")
            else:
                print(f"    ✖ Failed to process document. Error: {result.error}")
        except Exception as e:
            print(f"    ✖ An unexpected error occurred: {e}")

    print("\nChunking process complete.")

if __name__ == "__main__":
    main()

