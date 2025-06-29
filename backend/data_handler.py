import sqlite3
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

# Initialize Gemini API with error handling
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print(f"Warning: Could not initialize Gemini API: {e}")
    model = None
db_path = "data/structured_data.db"

async def store_csv_excel(file):
    try:
        ext = file.filename.split('.')[-1]
        content = await file.read()
        df = pd.read_excel(BytesIO(content)) if ext in ['xlsx', 'xls'] else pd.read_csv(BytesIO(content))

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        df.to_sql("data_table", conn, if_exists="replace", index=False)
        conn.close()
        return {"message": "Structured data uploaded successfully."}
    except Exception as e:
        return {"error": f"Failed to upload structured data: {str(e)}"}

def convert_to_sql_llm(query: str):
    if model is None:
        return f"SELECT * FROM data_table LIMIT 10; -- Gemini API not available, showing sample query for: {query}"
    
    try:
        prompt = f"""Convert this natural language question to a clean SQL query for a table named 'data_table'. 
Return ONLY the SQL query with no explanations, no markdown, no code blocks:

Question: {query}

SQL:"""
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        
        # Clean up any markdown formatting more aggressively
        import re
        sql_query = re.sub(r'```sql\n?', '', sql_query)
        sql_query = re.sub(r'```\n?', '', sql_query)
        sql_query = re.sub(r'^sql\n?', '', sql_query, flags=re.IGNORECASE)
        sql_query = sql_query.strip()
        
        # If still has issues, use a simple fallback
        if '```' in sql_query or sql_query.count('\n') > 3:
            print(f"Warning: Complex SQL response, using fallback. Original: {sql_query}")
            return "SELECT COUNT(*) as count FROM data_table;"
        
        return sql_query
    except Exception as e:
        return f"SELECT * FROM data_table LIMIT 10; -- Error generating SQL: {str(e)}"

def execute_sql(sql: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        result = {"error": str(e)}
    conn.close()
    return result
