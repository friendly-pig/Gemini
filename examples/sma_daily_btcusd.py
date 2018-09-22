try:
    from gemini.gemini import Gemini
except ImportError:
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')

import talib

from gemini.gemini import Gemini
from gemini.helpers import cryptocompare as cc
from gemini.helpers.analyze import analyze_bokeh


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
    short = talib.SMA(data['close'].values, timeperiod=5)
    long = talib.SMA(data['close'].values, timeperiod=30)

    if short[-1] > long[-1] and short[-2] < long[-2]:
        print(algo.account.date, 'BUY signal', len(data))
        entry_capital = algo.account.buying_power
        if entry_capital >= 0:
            algo.account.enter_position('Long', entry_capital, current_price)

    if short[-1] < long[-1] and short[-2] > long[-2]:
        print(algo.account.date, 'SELL signal', len(data))
        for position in algo.account.positions:
            if position.type_ == 'Long':
                algo.account.close_position(position, 1, current_price)

    algo.records.append({
        'date': algo.account.date,
        'price': current_price,
        'sma20': short[-1],
        'sma100': long[-1],
    })


pair = ['BTC', 'USD']  # Use ETH pricing data on the BTC market
days_history = 300  # From there collect X days of data
exchange = 'Bitstamp'

# Request data from cryptocompare.com
df = cc.load_dataframe(pair, days_history, exchange)

# Algorithm settings
sim_params = {
    'capital_base': 10000,
    'fee': {
        'Long': 0.0025 + 0.001,  # fee + spread
        'Short': 0.0025 + 0.001,
    }
}
gemini = Gemini(logic=logic, sim_params=sim_params, analyze=analyze_bokeh)

# start backtesting custom logic with 1000 (BTC) intital capital
gemini.run(df,
           title='SMA 5x30 History: {}'.format(days_history),
           show_trades=True)
