# ai-agent-challenge
Coding agent challenge which write custom parsers for Bank statement PDF.
An autonomous AI agent that generates custom parsers for bank statement PDFs using LangGraph and Google Gemini.

The agent follows a plan → generate → test → self-correct loop to produce robust parsers that extract structured transaction data from PDFs and validate them against ground-truth CSVs.

🚀 Quick Start
1. Clone & Setup
git clone https://github.com/<your-username>/ai-agent-challenge.git
cd ai-agent-challenge
python -m venv env
source env/bin/activate   # Mac/Linux
# OR env\Scripts\activate # Windows
pip install -r requirements.txt

2. Configure API Key

Create a .env file in the project root:
GEMINI_API_KEY=your_api_key_here


3. Run the Agent
python agent.py --target icici

The agent will:
Analyze data/icici/icici_sample.pdf
Autonomously generate a parser (custom_parsers/icici_parser.py)
Validate output against data/icici/result.csv
Save parsed results as data/icici/icici_parsed.csv

📊 Example Output
Parsed transactions (first 5 rows):
| Date       | Description               | Debit Amt | Credit Amt | Balance  |
| ---------- | ------------------------- | --------- | ---------- | -------- |
| 01-08-2024 | Salary Credit XYZ Pvt Ltd | 1935.30   |            | 6864.58  |
| 02-08-2024 | Salary Credit XYZ Pvt Ltd |           | 1652.61    | 8517.19  |
| 03-08-2024 | IMPS UPI Payment Amazon   | 3886.08   |            | 4631.11  |
| 03-08-2024 | Mobile Recharge Via UPI   |           | 1648.72    | 6279.83  |
| 14-08-2024 | Fuel Purchase Debit Card  |           | 3878.57    | 10158.40 |


🏗️ Project Structure
ai-agent-challenge/
├── agent.py                 # Main agent orchestrator (LangGraph + Gemini)
├── custom_parsers/          # Generated parsers
│   └── icici_parser.py
├── data/
│   └── icici/
│       ├── icici_sample.pdf
│       ├── result.csv       # Ground truth for validation
│       └── icici_parsed.csv # Parser output
├── requirements.txt
├── tests/
│   └── test_icici_parser.py # Unit tests
├── README.md
└── .env.example

🔧 Adding New Banks
Add {bank}_sample.pdf and result.csv to data/{bank}/.
Run:
python agent.py --target {bank}
The agent will generate custom_parsers/{bank}_parser.py and validate against your CSV.

📦 Requirements
Python 3.10+
pdfplumber
pandas
langgraph
google-generativeai
python-dotenv
pytest
Install all dependencies:
pip install -r requirements.txt

🧪 Testing

Run the tests:
PYTHONPATH=. pytest tests/ -v


✨ Features
Autonomous parser generation with Gemini
Validation against ground-truth CSVs
Self-correcting loop (up to 3 attempts)
Extensible to multiple banks

📄 License
MIT License – free to use and modify.