import pandas as pd
import pdfplumber

def parse(pdf_path: str) -> pd.DataFrame:
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                print(f"[DEBUG] Page {page_num}: No text extracted")
                continue

            print(f"\n=== Page {page_num} raw text ===")
            for line_num, line in enumerate(text.split("\n"), start=1):
                print(f"[DEBUG] Line {line_num}: {line}")
    return pd.DataFrame(rows)
