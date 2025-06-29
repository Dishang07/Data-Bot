import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini API with error handling
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print(f"Warning: Could not initialize Gemini API: {e}")
    model = None

def classify_query_llm(query: str) -> str:
    if model is None:
        # Fallback classification based on keywords
        sql_keywords = ['count', 'sum', 'average', 'total', 'how many', 'show me', 'list', 'find']
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in sql_keywords):
            return "sql"
        return "semantic"
    
    try:
        prompt = f"""
Classify this query as either 'SQL' if it's about structured data or 'Semantic' if it's about policy, rules, or general text understanding:
Query: "{query}"
Only reply with SQL or Semantic.
"""
        response = model.generate_content(prompt)
        result = response.text.strip().lower()
        return "sql" if "sql" in result else "semantic"
    except Exception as e:
        # Fallback to keyword-based classification
        sql_keywords = ['count', 'sum', 'average', 'total', 'how many', 'show me', 'list', 'find']
        query_lower = query.lower()
        return "sql" if any(keyword in query_lower for keyword in sql_keywords) else "semantic"
