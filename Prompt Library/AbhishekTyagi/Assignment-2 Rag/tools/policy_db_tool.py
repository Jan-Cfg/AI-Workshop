from langchain.tools import tool
from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri(
    "mysql+pymysql://root:cfg%401234@localhost:3306/ins"
)

@tool
def query_policy_db(sql: str) -> str:
    """
    Run SQL queries on policies table.
    """
    return db.run(sql)