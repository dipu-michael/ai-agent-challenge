import os
import sys
import pandas as pd
import pandas.testing as pdt

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from custom_parsers.icici_parser import parse

def test_icici():
    expected = pd.read_csv(os.path.join(BASE_DIR, "data/icici/icici_sample.csv"))
    df = parse(os.path.join(BASE_DIR, "data/icici/icici_sample.pdf"))

    # Ensure column names match
    assert list(df.columns) == list(expected.columns)

    # Compare DataFrames, ignore dtype mismatches
    pdt.assert_frame_equal(df, expected, check_dtype=False)
