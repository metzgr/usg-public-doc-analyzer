import os
from docling.document_converter import DocumentConverter

# --- Configuration ---
# List of PDF documents to process
URLS_TO_PROCESS = [
    "https://www.gao.gov/assets/gao-25-106977.pdf",
    "https://www.usda.gov/sites/default/files/documents/23-2026-CJ-AMS.pdf"
]
# Directory to save the extracted Markdown files
OUTPUT_DIR = "data/extracted"

# --- Main Execution ---
def main():
    """
    Extracts content from a list of PDF URLs and saves them as Markdown files.
    """
    print(f"Ensuring output directory exists: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    converter = DocumentConverter()

    print(f"Starting extraction for {len(URLS_TO_PROCESS)} documents...")

    for url in URLS_TO_PROCESS:
        print(f"--> Processing: {url}")
        try:
            result = converter.convert(url)
            
            if result.document:
                document = result.document
                markdown_output = document.export_to_markdown()
                
                # Create a clean filename from the URL
                filename = os.path.basename(url).replace(".pdf", ".md")
                output_path = os.path.join(OUTPUT_DIR, filename)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(markdown_output)
                
                print(f"    ✔ Saved Markdown to {output_path}")
            else:
                print(f"    ✖ Failed to process. Error: {result.error}")
        except Exception as e:
            print(f"    ✖ An unexpected error occurred: {e}")

    print("\nExtraction process complete.")

if __name__ == "__main__":
    main()