import os
import lancedb
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

def connect_lancedb():
    """
    Connects to LanceDB using credentials from environment variables for cloud
    or falls back to a local database.

    Reads the following environment variables for cloud connection:
    - LANCEDB_URI: The URI of the LanceDB database (e.g., db://your-database).
    - LANCEDB_API_KEY: The API key for authentication.
    - LANCEDB_REGION: The cloud region where the database is hosted.

    If LANCEDB_URI does not start with 'db://', it treats it as a local path.
    If LANCEDB_URI is not set, it defaults to 'data/lancedb'.
    """
    uri = os.getenv("LANCEDB_URI")

    if uri and uri.startswith("db://"):
        # Cloud/Enterprise connection
        api_key = os.getenv("LANCEDB_API_KEY")
        region = os.getenv("LANCEDB_REGION")
        
        if not all([api_key, region]):
            raise ValueError(
                "For LanceDB Cloud, LANCEDB_API_KEY and LANCEDB_REGION must be set."
            )
            
        print(f"Connecting to LanceDB Cloud at URI: {uri}")
        return lancedb.connect(uri=uri, api_key=api_key, region=region)
    
    else:
        # Local connection
        local_path = uri or "data/lancedb"
        print(f"Connecting to local LanceDB at path: {local_path}")
        return lancedb.connect(local_path)

