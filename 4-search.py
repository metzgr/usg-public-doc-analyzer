import lancedb
from dotenv import load_dotenv
from utils.db import connect_lancedb
from lancedb.embeddings import get_registry

load_dotenv(override=True)

# --------------------------------------------------------------
# Connect to the database
# --------------------------------------------------------------
# Connect to LanceDB
db = connect_lancedb()


# --------------------------------------------------------------
# Open the table
# --------------------------------------------------------------
TABLE_NAME = "docling"
table = db.open_table(TABLE_NAME)

# Get the OpenAI embedding function
func = get_registry().get("openai").create(name="text-embedding-3-large")

# --------------------------------------------------------------
# Perform the search
# --------------------------------------------------------------
query_string = "what are the major programs at usda?"
query_vector = func.generate_embeddings([query_string])[0]
result = table.search(query=query_vector).limit(3)
df = result.to_pandas()

print(f"Search results for: '{query_string}'")
print(df)
