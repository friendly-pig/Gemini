try:
    from gemini.gemini import Gemini
except ImportError:
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')

import talib

from gemini.gemini import Gemini
from gemini.helpers import poloniex as px
from gemini.helpers.analyze import analyze_mpl


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
    rsi = talib.RSI(data['close'].values, timeperiod=RSI_PERIOD)

    if rsi[-1] > RSI_OPEN < rsi[-2]:
        entry_capital = algo.account.buying_power
        if entry_capital > 0.00001:
            algo.account.new_order(pair, 3, current_price - 0.0001, 'Limit')
            algo.account.new_order(pair, 3, current_price, 'Market')

    if len(algo.account.positions) > 0:
        if rsi[-1] < RSI_OPEN - RSI_DEVIATION:
            for position in algo.account.positions:
                if position.type_ == 'Long':
                    algo.account.close_position(position, 1, current_price)

    algo.records.append({
        'date': today['date'],
        'rsi': rsi[-1],
    })


# Data settings
pair = "ETC_BTC"  # Use ETH pricing data on the BTC market
period = 300  # Use 1800 second candles
days_history = 30  # From there collect 60 days of data
RSI_OPEN = 55
RSI_DEVIATION = 10
RSI_PERIOD = 14

# Request data from Poloniex
df = px.load_dataframe(pair, period, days_history)

# Algorithm settings
sim_params = {
    'capital_base': 1,
    'data_frequency': '30T',
    'fee': {
        'Long': 0.0025,
        'Short': 0.0025,
    }
}

gemini = Gemini(logic=logic, sim_params=sim_params, analyze=analyze_mpl)

gemini.run(df)
