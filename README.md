# Backend Service

This is a Python-based backend service structured for scalability and modularity. The application includes core business logic, database interaction, and external service integrations.

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py               # Entry point of the backend service
│   ├── crud.py               # CRUD operations
│   ├── models.py             # Database models
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # Database connection setup
│   ├── services/
│   │   ├── rag_agent.py      # Retrieval-Augmented Generation logic
│   │   └── teams_notifier.py # Microsoft Teams notification integration
├── .env                      # Environment configuration
├── requirements.txt          # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- `pip` or `poetry` (recommended)
- PostgreSQL (or your configured DB)

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory with necessary variables. Example:

```env
# Get your Gemini API key from Google AI Studio
GOOGLE_API_KEY="AIz..."

# Get your Tavily API key from tavily.com
TAVILY_API_KEY="tvly-dev-..."

# Connection details for your PostgreSQL database
DATABASE_URL="postgresql://..."

# Connection details for your MongoDB database
MONGO_URL = "mongodb+srv://..."

# Add the new key for the Teams webhook
TEAMS_WEBHOOK_URL="https://..."
```

### Running the App

```bash
uvicorn app.main:app --reload
```

This will start the app locally at `http://127.0.0.1:8000`.

## 🧪 Testing

To run tests (if available):

```bash
pytest
```

## 📦 Dependencies

Dependencies are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

## 📬 Integrations

- **RAG Agent**: Custom AI logic in `services/rag_agent.py`
- **Microsoft Teams Notifier**: Sends alerts to Teams via `services/teams_notifier.py`

## 📄 License

[MIT License](LICENSE) – Customize if needed.
