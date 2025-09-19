import pdfplumber
import pandas as pd

def parse(pdf_path: str) -> pd.DataFrame:
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                data.extend(table)

    df = pd.DataFrame(data[1:], columns=data[0])
    df = df[df['Date'] != 'Date']
    df = df.fillna("")
    return df