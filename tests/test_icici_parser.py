import pandas as pd
from custom_parsers.icici_parser import parse


def test_icici_parser():
    parsed_df = parse("data/icici/icici_sample.pdf")
    expected_df = pd.read_csv("data/icici/result.csv")

    # Normalize NaNs for fair comparison
    pd.testing.assert_frame_equal(
        parsed_df.reset_index(drop=True),
        expected_df.reset_index(drop=True),
        check_dtype=False,
        check_exact=False,
        rtol=1e-3
    )
