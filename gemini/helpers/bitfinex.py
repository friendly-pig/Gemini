import logging
import time

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def get_now(pair):
    """
    Return last info for crypto currency pair
    :param pair:
    :return:
    """

    url_key = "t"+pair
    return requests.get(('https://api.bitfinex.com/v2/ticker/'+url_key)).json()


def get_past(pair, period, days_history=30):
    """
    Return historical charts data from poloniex.com
    :param pair:
    :param period: 1m, 5m, 15m, 30m, 1h, 4h, 1D, 1M
    :param days_history:
    :return:
    """
    url_key = '/trade:'+period+':'+'t'+pair+'/hist'
    end = int(time.time())*1000
    start = end - (24 * 60 * 60 * days_history*1000)
    params = {
        'end': end,
        'start': start
    }

    response = requests.get(('https://api.bitfinex.com/v2/candles'+url_key), params=params)

    return response.json()



def convert_pair_bittrex(pair):
    converted = "{1}-{0}".format(*pair.split('-'))
    logger.warning('Warning: Pair was converted to ' + converted)
    return converted


def load_dataframe(pair, period, days_history=30):
    """
    Return historical charts data from poloniex.com
    :param pair:
    :param period:
    :param days_history:
    :param timeframe: H - hour, D - day, W - week, M - month
    :return:
    """
    try:
        #data = get_past(convert_pair_bittrex(pair), period)
        data = get_past(pair, period)
    except Exception as ex:
        raise ex

    if 'error' in data:
        raise Exception("Bad response: {}".format(data['error']))

    df = pd.DataFrame(data, columns=('time', 'open',
                                                 'hight', 'low',
                                                 'close', 'volume'))

    #df = pd.DataFrame((data)['result'])
    #df = df.set_index(['T'])
    df['time'] = pd.to_datetime(df['time'], unit='us')


    return df

h = load_dataframe('BTCUSD', '5m')
print(h)