import os
import lancedb

def connect_lancedb(default_uri: str = "data/lancedb"):
    """Connect to LanceDB using environment variables if available."""
    uri = os.getenv("LANCEDB_URI", default_uri)
    api_key = os.getenv("LANCEDB_API_KEY")
    region = os.getenv("LANCEDB_REGION")

    if uri.startswith("db://") and api_key:
        return lancedb.connect(uri=uri, api_key=api_key, region=region)
    return lancedb.connect(uri)

