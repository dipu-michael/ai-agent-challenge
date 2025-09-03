# AI Agent Challenge – ICICI Bank Parser

## 📌 Overview
This project implements a parser for ICICI bank statements (PDF → DataFrame/CSV).
The solution includes:
- Parser (`custom_parsers/icici_parser.py`)
- Sample test data (`data/icici/`)
- Automated tests (`tests/test_icici.py`)
- Agent script (`agent.py`) to validate parser correctness

## ⚙️ Setup
```bash
git clone <your-repo-url>
cd ai-agent-challenge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

▶️ Run Parser
python agent.py --target icici

✅ Run Tests
PYTHONPATH=$(pwd) pytest -q

📂 Project Structure
ai-agent-challenge/
├── agent.py
├── custom_parsers/
│   ├── __init__.py
│   └── icici_parser.py
├── data/
│   └── icici/
│       ├── icici_sample.pdf
│       └── icici_sample.csv
├── tests/
│   └── test_icici.py
├── requirements.txt
└── README.md

Architecture for ai-agent-challenge
flowchart TD
    A[Start Agent] --> B[Run Pytest]
    B -->|✅ Pass| C[Success: Parser Works]
    B -->|❌ Fail| D[Self-Debug Loop]
    D --> E[Simulate Parser Regeneration]
    E --> F[Retry Pytest]
    F -->|Max Retries| G[⚠️ Manual Check]
