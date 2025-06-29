from .data_handler import convert_to_sql_llm, execute_sql
from .unstructured_handler import search_unstructured
from .utils import classify_query_llm


async def route_query(query: str):
    query_type = classify_query_llm(query)
    if query_type == "sql":
        sql = convert_to_sql_llm(query)
        return execute_sql(sql)
    else:
        return search_unstructured(query)
