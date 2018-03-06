import numpy as np

from gemini.helpers import bitfinex


def test_load_dataframe():
    df = bitfinex.load_dataframe('ETH_USD', 1800, days_history=30)
    assert len(df) > 0
    assert df.index[0] < df.index[-1]

    for val in ['close', 'hight', 'low', 'open']:
        assert val in df.columns.values
        assert df.dtypes[val] == np.dtype('float64')


def test_convert_pair_bitfinex():
    converted = bitfinex.convert_pair_bitfinex('ETH_USD')
    assert converted == 'ETHUSD'
