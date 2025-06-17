import argparse
import os
from typing import List

import lancedb
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from utils.tokenizer import OpenAITokenizerWrapper
from dotenv import load_dotenv


def parse_args():
    parser = argparse.ArgumentParser(description="Bulk ingest PDFs into LanceDB")
    parser.add_argument("input_dir", help="Directory containing PDF files")
    parser.add_argument("db_path", help="Path to LanceDB database")
    parser.add_argument("--table", default="docling", help="LanceDB table name")
    return parser.parse_args()


class ChunkMetadata(LanceModel):
    filename: str | None
    page_numbers: List[int] | None
    title: str | None


class Chunks(LanceModel):
    text: str
    vector: Vector(1536)
    metadata: ChunkMetadata


def main():
    args = parse_args()
    load_dotenv()

    os.makedirs(args.db_path, exist_ok=True)

    db = lancedb.connect(args.db_path)

    if args.table in db.table_names():
        table = db.open_table(args.table)
    else:
        func = get_registry().get("openai").create(name="text-embedding-3-large")

        class TableSchema(LanceModel):
            text: str = func.SourceField()
            vector: Vector(func.ndims()) = func.VectorField()  # type: ignore
            metadata: ChunkMetadata

        table = db.create_table(args.table, schema=TableSchema, mode="create")

    converter = DocumentConverter()
    tokenizer = OpenAITokenizerWrapper()
    chunker = HybridChunker(tokenizer=tokenizer, max_tokens=tokenizer.model_max_length, merge_peers=True)

    pdf_files = [f for f in os.listdir(args.input_dir) if f.lower().endswith(".pdf")]

    for fname in pdf_files:
        path = os.path.join(args.input_dir, fname)
        try:
            result = converter.convert(path)
            if not result.document:
                continue
            chunks = list(chunker.chunk(result.document))
        except Exception as e:
            print(f"Failed processing {fname}: {e}")
            continue

        records = [
            {
                "text": c.text,
                "metadata": {
                    "filename": c.meta.origin.filename,
                    "page_numbers": sorted({prov.page_no for it in c.meta.doc_items for prov in it.prov}) or None,
                    "title": c.meta.headings[0] if c.meta.headings else None,
                },
            }
            for c in chunks
        ]
        table.add(records)
        print(f"Ingested {len(records)} chunks from {fname}")


if __name__ == "__main__":
    main()
