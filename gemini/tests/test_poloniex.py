from gemini.helpers import poloniex
import random

pair = 'ETH_BTC'
period = 1800
days = 30
control = ['close', 'high', 'low', 'open']


def test_load_dataframe():
    df = poloniex.load_dataframe(pair, period, days_history=days)
    assert len(df) > 0
    assert df.index[0] < df.index[-1]

    columns_names = list(df)
    for val in control:
        assert val in columns_names
        assert isinstance(df[val][random.randint(0, len(df))], float)
