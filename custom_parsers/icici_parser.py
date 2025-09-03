# custom_parsers/icici_parser.py
import pandas as pd
import pdfplumber
import re
import numpy as np

def parse(pdf_path: str) -> pd.DataFrame:
    """
    Parses an ICICI bank statement PDF and returns a Pandas DataFrame
    aligned with the CSV schema.
    """
    try:
        data_rows = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for line in text.splitlines():
                    if line.startswith("Date") or not line.strip():
                        continue

                    # Regex: Date, Description, optional number(s), Balance
                    match = re.match(
                        r"^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d+)?\s*(\d+)?\s+(\d+)$", line
                    )
                    if match:
                        date, desc, num1, num2, balance = match.groups()
                        debit, credit = np.nan, np.nan

                        if num1 and num2:
                            # If two numbers → first = Debit, second = Credit
                            debit, credit = float(num1), float(num2)
                        elif num1:
                            # If only one number → decide using description
                            if any(word in desc.lower() for word in ["salary", "interest", "refund", "credited"]):
                                credit = float(num1)
                            else:
                                debit = float(num1)

                        data_rows.append([
                            date,          # keep as string (CSV format)
                            desc.strip(),
                            debit,
                            credit,
                            int(balance),
                        ])

        df = pd.DataFrame(data_rows, columns=["Date", "Description", "Debit", "Credit", "Balance"])
        return df

    except FileNotFoundError:
        print(f"Error: File not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return None
