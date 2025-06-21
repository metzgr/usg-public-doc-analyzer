import lancedb
from dotenv import load_dotenv
from utils.db import connect_lancedb

load_dotenv()

# --------------------------------------------------------------
# Connect to the database
# --------------------------------------------------------------

uri = "data/lancedb"
db = connect_lancedb(default_uri=uri)


# --------------------------------------------------------------
# Load the table
# --------------------------------------------------------------

table = db.open_table("docling")


# --------------------------------------------------------------
# Search the table
# --------------------------------------------------------------

result = table.search(query="what's docling?", query_type="vector").limit(3)
result.to_pandas()
