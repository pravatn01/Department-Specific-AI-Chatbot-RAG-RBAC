# 🤖 Department-Specific AI Chatbot (RAG + RBAC)

An intelligent chatbot powered by **LLMs + Vector Search (RAG)** with **Role-Based Access Control (RBAC)** for Finance, HR, Engineering, Marketing, Employees, and C-Level Executives.

---

## 🧩 Background
Fintech teams often face delays and inefficiencies due to scattered documents and lack of secure, role-specific access.
This chatbot centralizes knowledge, ensuring each role only sees what’s relevant.

---

## 🧠 Solution
- Retrieval-Augmented Generation (RAG) via **LLaMA 3 (Ollama)**
- Role-Based Filtering on vector search
- Backend: FastAPI | Frontend: Streamlit
- Department-wise documents stored with metadata

---

## 👥 Role-Based Access

| Role               | Permissions                                     |
|--------------------|-------------------------------------------------|
| C-Level Executives | Full unrestricted access                        |
| Finance Team       | Reports, expenses, reimbursements               |
| Marketing Team     | Campaigns, insights, sales data                 |
| HR Team            | Handbook, leave, payroll                        |
| Engineering Dept.  | Architecture, deployment, CI/CD                 |
| Employees          | FAQs, policies, events                          |

---

## 🛠 Tech Stack

| Layer     | Tool                  |
|-----------|-----------------------|
| Frontend  | Streamlit             |
| Backend   | FastAPI               |
| Embedding | SentenceTransformers  |
| Vector DB | ChromaDB              |
| LLM       | LLaMA 3 (Ollama)      |
| Docs      | Markdown (.md)        |

---

## 🧪 Sample Users

```python
users_db = {
    "Arjun":  {"password": "devpass123", "role": "engineering"},
    "Meera":  {"password": "marketwise", "role": "marketing"},
    "Kiran":  {"password": "finsecure", "role": "finance"},
    "Ravi":   {"password": "codeflow", "role": "engineering"},
    "Lina":   {"password": "brandpass", "role": "marketing"},
    "Anita":  {"password": "peoplecare", "role": "hr"},
    "Rajesh": {"password": "visionlead", "role": "c-levelexecutives"},
    "Nina":   {"password": "genaccess", "role": "employee"},
}
````

---

## ⚙️ Setup (Quickstart)

```bash
# 1. Clone repo
git clone https://github.com/pravatn01/Department-Specific-AI-Chatbot-RAG-RBAC.git
cd Department-Specific-AI-Chatbot-RAG-RBAC

# 2. Backend setup
cd app
python -m venv venv
venv\Scripts\activate # On Windows
pip install -r ../requirements.txt

# Start Ollama LLaMA3 in another terminal
ollama run llama3

# Run FastAPI backend
uvicorn app.backend:app --reload

# 3. Frontend
streamlit run app/frontend.py

# 4. Embed documents (run once)
python app/vector_embeddings.py
