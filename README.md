# USG Document Analyzer

This repository demonstrates how to build a local document analysis app using [Docling](https://github.com/DS4SD/docling), LanceDB and OpenAI models.  You'll convert documents, chunk them into searchable pieces, create vector embeddings and explore the results through a Streamlit interface.

The examples are organized so you can run them step by step, just like you would in a classroom lab exercise.

## How It Works

1. **Extraction** – `1-extraction.py` uses Docling to convert PDFs or web pages into a normalized structure (Markdown or JSON).
2. **Chunking** – `2-chunking.py` applies Docling's Hybrid Chunker to split each document into semantically meaningful blocks optimized for embeddings.
3. **Embedding** – `3-embedding.py` stores those chunks in a LanceDB table while generating OpenAI embeddings.
4. **Search** – `4-search.py` shows how to query the table and fetch the most relevant chunks.
5. **Chat** – `5-chat.py` launches a Streamlit app that retrieves context from LanceDB and passes it to an OpenAI chat model so you can ask questions about the ingested documents.

Running these scripts in order produces an interactive knowledge base of your documents.

## Local Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**

   Create a `.env` file in the project root and add your keys:

   ```bash
   OPENAI_API_KEY=your_openai_key
   LANCEDB_URI=optional_remote_uri
   LANCEDB_API_KEY=optional_remote_key
   LANCEDB_REGION=us-east-1
   ```

   If `LANCEDB_URI` is omitted, the scripts default to `data/lancedb` for local storage.

## Running the Pipeline

Execute the scripts sequentially:

```bash
python 1-extraction.py   # convert a sample document
python 2-chunking.py     # create structured chunks
python 3-embedding.py    # build the LanceDB table
python 4-search.py       # perform a simple search
streamlit run 5-chat.py  # start the chat interface
```

Open your browser at <http://localhost:8501> to ask questions about the processed documents.

## About Docling

Docling is a high-performance document understanding library capable of handling PDFs, Office files, HTML and more. It performs layout analysis, table structure recognition and advanced chunking so your retrieval system receives clean, structured content. Learn more at the [Docling documentation site](https://ds4sd.github.io/docling/).

## Next Steps

- Try `bulk_ingest.py` to process multiple PDFs into LanceDB.
- Explore LanceDB's features for filtering and hybrid search.
- Modify the Streamlit app to suit your own data and prompts.

