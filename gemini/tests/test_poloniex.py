import numpy as np

from gemini.helpers import poloniex


def test_load_dataframe():
    df = poloniex.load_dataframe('ETH_BTC', 1800, days_history=30)
    assert len(df) > 0
    assert df.index[0] < df.index[-1]

    for val in ['close', 'high', 'low', 'open']:
        assert val in df.columns.values
        assert df.dtypes[val] == np.dtype('float64')


def test_convert_pair_poloniex():
    converted = poloniex.convert_pair_poloniex('ETH_BTC')
    assert converted == 'BTC_ETH'
