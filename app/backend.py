from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import requests

# App Setup
app = FastAPI(title="FinSolve RBAC Chatbot")
security = HTTPBasic()

# Vector Store Initialization
_vectordb = Chroma(
    persist_directory="chroma_db",
    embedding_function=SentenceTransformerEmbeddings("all-MiniLM-L6-v2"),
    collection_name="company_docs"
)

# Dummy User Store
users_db: Dict[str, Dict[str, str]] = {
    "Arjun":   {"password": "devpass123",   "role": "engineering"},
    "Meera":   {"password": "marketwise",   "role": "marketing"},
    "Kiran":   {"password": "finsecure",    "role": "finance"},
    "Ravi":    {"password": "codeflow",     "role": "engineering"},
    "Lina":    {"password": "brandpass",    "role": "marketing"},
    "Anita":   {"password": "peoplecare",   "role": "hr"},
    "Rajesh":  {"password": "visionlead",   "role": "c-levelexecutives"},
    "Nina":    {"password": "genaccess",    "role": "employee"},
}

# Authentication
def authenticate(credentials: HTTPBasicCredentials = Depends(security)) -> Dict[str, str]:
    user = users_db.get(credentials.username)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": credentials.username, "role": user["role"]}

# Role-based Retrieval
def fetch_docs(message: str, user_role: str):
    role = user_role.lower()
    if "c-levelexecutives" in role:
        # Execs: wide access
        docs = _vectordb.similarity_search(message, k=3)
        return docs or _vectordb.similarity_search(
            message, k=5,
            filter={"role": {"$in": ["engineering", "hr", "finance", "marketing", "general"]}}
        )
    if "employee" in role:
        # Employees: only general
        return _vectordb.similarity_search(message, k=3, filter={"category": "general"})
    # Everyone else: department-specific
    return _vectordb.similarity_search(message, k=3, filter={"role": user_role})

# Prompt Builder
def make_prompt(user: Dict[str, Any], docs: list, query: str) -> str:
    context = "\n\n".join(doc.page_content for doc in docs)
    return f"""
You are an AI assistant at FinSolve Technologies. The user has the role: {user['role']}.
Use the context below to answer their question in a friendly, clear, conversational style,
like you're explaining it to a colleague. Summarize naturally — avoid just bullet points.

Context:
{context}

Question: {query}

Answer:
"""

# Ollama Request
def query_llm(prompt: str) -> str:
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }
    resp = requests.post("http://localhost:11434/api/generate", json=payload)
    if resp.status_code != 200:
        return f"Ollama LLM error: {resp.text}"
    return resp.json().get("response", "No response from model.")

# Endpoints
@app.get("/login")
def login(user=Depends(authenticate)):
    return {"message": f"Welcome {user['username']}!", "role": user["role"]}


@app.get("/test")
def test(user=Depends(authenticate)):
    return {"message": f"Hello {user['username']}! You can now chat.", "role": user["role"]}


@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user = data["user"]
        query = data["message"]

        docs = fetch_docs(query, user["role"])
        if not docs:
            return {"response": f"No relevant data found for your role: {user['role']}"}

        prompt = make_prompt(user, docs, query)
        answer = query_llm(prompt)

        return {
            "username": user["username"],
            "role": user["role"],
            "query": query,
            "response": answer
        }
    except Exception as e:
        return {"response": f"Error during chat: {str(e)}"}
