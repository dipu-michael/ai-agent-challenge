import os
import sys
import argparse
import logging
from pathlib import Path
import importlib.util
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# --- Setup ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel("gemini-1.5-flash")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("agent")

ROOT = Path(".").resolve()
DATA_DIR = ROOT / "data"
PARSERS_DIR = ROOT / "custom_parsers"
PARSERS_DIR.mkdir(exist_ok=True)

# --- Helpers ---
def find_sample_files(target: str):
    d = DATA_DIR / target
    pdfs = list(d.glob("*.pdf"))
    csvs = list(d.glob("*.csv"))
    if not pdfs or not csvs:
        raise FileNotFoundError(f"No PDF/CSV pair found in {d}")
    return pdfs[0], csvs[0]

def import_parser_module(file_path: Path):
    spec = importlib.util.spec_from_file_location("parser_module", str(file_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules["parser_module"] = module
    spec.loader.exec_module(module)
    return module

def validate_parser(parser_path: Path, pdf_path: Path, csv_path: Path):
    try:
        module = import_parser_module(parser_path)
        if not hasattr(module, "parse"):
            return False, "Parser missing `parse` function."

        parsed_df = module.parse(str(pdf_path))
        expected_df = pd.read_csv(csv_path, dtype=str).fillna("")
        parsed_df = parsed_df.astype(str).fillna("")

        is_equal = parsed_df.reset_index(drop=True).equals(expected_df.reset_index(drop=True))
        if is_equal:
            return True, None
        else:
            return False, f"Mismatch: parsed shape {parsed_df.shape}, expected {expected_df.shape}"
    except Exception as e:
        return False, f"Exception during validation: {e}"

def generate_parser_code(target: str, csv_path: Path, attempt: int, error_message: str | None = None):
    csv_df = pd.read_csv(csv_path, nrows=5)
    csv_sample = csv_df.to_csv(index=False)
    columns = list(csv_df.columns)

    feedback = f"\nPrevious error:\n{error_message}" if error_message else ""

    prompt = f"""
Generate Python code only (no markdown, no text).
Requirements:
- Must define: def parse(pdf_path: str) -> pd.DataFrame
- Use pdfplumber + pandas ONLY
- Output DataFrame with columns: {columns}
- Extract all rows from all PDF pages
- Remove duplicate header rows (rows where first cell is 'Date')
- Replace missing values with ""
Target CSV sample:
{csv_sample}
Attempt: {attempt}
{feedback}
"""

    response = llm.generate_content(prompt)
    code = response.text.replace("```python", "").replace("```", "").strip()

    try:
        compile(code, "<parser>", "exec")
    except SyntaxError as e:
        logger.warning(f"Invalid code from Gemini: {e}")
        code = ""
    return code

def write_parser_file(target: str, code: str) -> Path:
    path = PARSERS_DIR / f"{target}_parser.py"
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return path

# --- LangGraph Nodes ---
def plan_node(state: dict):
    state["attempt"] = state.get("attempt", 0) + 1
    return state

def codegen_node(state: dict):
    target = state["target"]
    _, csv_path = state["files"]
    attempt = state["attempt"]
    error_message = state.get("error_message")

    logger.info(f"Generating parser for {target}, attempt {attempt}")
    code = generate_parser_code(target, csv_path, attempt, error_message)
    parser_path = write_parser_file(target, code)
    state["parser_path"] = parser_path
    return state

def test_node(state: dict):
    parser_path = state["parser_path"]
    pdf_path, csv_path = state["files"]

    ok, error = validate_parser(parser_path, pdf_path, csv_path)
    state["success"] = ok
    state["error_message"] = None if ok else error

    if ok:
        # Run parser and save output CSV
        module = import_parser_module(parser_path)
        df = module.parse(str(pdf_path))

        out_csv = DATA_DIR / state["target"] / f"{state['target']}_parsed.csv"
        df.to_csv(out_csv, index=False)
        logger.info(f"✅ Parser validated successfully, output saved to {out_csv}")
    else:
        logger.warning(f"Validation failed (attempt {state['attempt']}): {error}")
    return state

def decide_node(state: dict):
    if state.get("success"):
        return END
    elif state.get("attempt", 0) >= 3:
        logger.error("❌ Max attempts reached, giving up")
        return END
    else:
        return "plan"

# --- Build LangGraph ---
graph = StateGraph(dict)
graph.add_node("plan", plan_node)
graph.add_node("codegen", codegen_node)
graph.add_node("test", test_node)
graph.set_entry_point("plan")

graph.add_edge("plan", "codegen")
graph.add_edge("codegen", "test")
graph.add_conditional_edges("test", decide_node)

app = graph.compile()

# --- CLI Entrypoint ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="Bank target (e.g. icici)")
    args = ap.parse_args()

    pdf, csv = find_sample_files(args.target)
    init_state = {"target": args.target, "files": (pdf, csv)}

    final_state = app.invoke(init_state)
    if not final_state.get("success"):
        sys.exit(1)

if __name__ == "__main__":
    main()
