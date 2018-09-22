try:
    from gemini.gemini import Gemini
except ImportError:
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')

import talib

from gemini.gemini import Gemini
from gemini.helpers import poloniex as px
from gemini.helpers.analyze import analyze_bokeh


def initialize(algo):
    algo.SHORT = 20
    algo.LONG = 100
    algo.MA_FUNC = talib.SMA
    {"LONG_PERIOD": 30, "MA_FUNC": "EMA", "SHORT_PERIOD": 5, "pairs": "BCH_BTC",
     "period": "2H"}


def logic(algo, data):
    """
    Main algorithm method, which will be called every tick.

    :param algo: Gemini object with account & positions
    :param data: History for current day
    """
    # Load into period class to simplify indexing
    if len(data) < 20:
        # Skip short history
        return

    today = data.iloc[-1]
    current_price = today['close']
    short = algo.MA_FUNC(data['close'].values, timeperiod=algo.SHORT)
    long = algo.MA_FUNC(data['close'].values, timeperiod=algo.LONG)

    if short[-1] > long[-1] and short[-2] < long[-2]:
        # print(today.name, 'BUY signal')
        entry_capital = algo.account.buying_power
        if entry_capital >= 0:
            algo.account.enter_position('Long', entry_capital, current_price)

    if short[-1] < long[-1] and short[-2] > long[-2]:
        # print(today.name, 'SELL signal')
        for position in algo.account.positions:
            if position.type_ == 'Long':
                algo.account.close_position(position, 1, current_price)

    algo.records.append({
        'date': today.name,
        'price': current_price,
        'short': short[-1],
        'long': long[-1],
    })


# Data settings
pair = "ETH_BTC"  # Use ETH pricing data on the BTC market
period = 1800  # Use 1800 second candles
days_history = 300  # From there collect 60 days of data

# Request data from Poloniex
df = px.load_dataframe(pair, period, days_history)

# Algorithm settings
sim_params = {
    'capital_base': 10,
    'fee': {
        'Long': 0.0025,
        'Short': 0.0025,
    },
    'data_frequency': '30T'
}
gemini = Gemini(initialize=initialize, logic=logic, sim_params=sim_params,
                analyze=analyze_bokeh)

# start backtesting custom logic with 10 (BTC) intital capital
gemini.run(df,
           title='SMA Cross {}: {}'.format(pair, days_history),
           show_trades=True)
