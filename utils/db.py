import os
import lancedb

def connect_lancedb(default_uri: str = "data/lancedb"):
    """
    Connect to a local LanceDB database.

    This function is hardcoded to use a local path to ensure the application
    runs in a local-only mode, preventing connection errors to remote databases.
    """
    # The default_uri points to a local directory, e.g., 'data/lancedb'
    return lancedb.connect(default_uri)

