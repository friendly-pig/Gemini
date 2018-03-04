from gemini.helpers import bittrex
import numpy as np


def test_load_dataframe():
    df = bittrex.load_dataframe('ETH_BTC', 1800, days_history=30)
    assert len(df) > 0
    assert df.index[0] < df.index[-1]

    for val in ['close', 'hight', 'low', 'open']:
        assert val in df.columns.values
        assert df.dtypes[val] == np.dtype('float64')


def test_convert_pair_bittrex():
    converted = bittrex.convert_pair_bittrex('ETH_BTC')
    assert converted == 'BTC-ETH'
