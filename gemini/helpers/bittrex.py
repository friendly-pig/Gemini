import logging

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def get_now(pair):
    """
    Return last info for crypto currency pair
    :param pair: ex: btc-ltc
    :return:
    """
    info = {'marketName': pair, 'tickInterval': 'oneMin'}
    return requests.get('https://bittrex.com/Api/v2.0/pub/market/GetLatestTick', params=info).json()


def get_past(pair, period):
    """
    Return historical charts data from poloniex.com
    :param pair:
    :param period:
    :param days_history:
    :return:
    """
    periods_dict = {300: 'fiveMin', 1800: 'thirtyMin', 86400: 'day'}

    params = {'marketName': pair, 'tickInterval': periods_dict[period]}
    response = requests.get('https://bittrex.com/Api/v2.0/pub/market/GetTicks', params=params)

    return response.json()


def convert_pair_bittrex(pair):
    converted = "{1}-{0}".format(*pair.split('_'))
    logger.warning('Warning: Pair was converted to ' + converted)
    return converted


def load_dataframe(pair, period, days_history=30):
    """
    Return historical charts data from bittrex.com
    :param pair:
    :param period:
    :param days_history:
    :param timeframe: H - hour, D - day, W - week, M - month
    :return:
    """
    try:

        data = get_past(convert_pair_bittrex(pair), period)
    except Exception as ex:
        raise ex

    if 'error' in data:
        raise Exception("Bad response: {}".format(data['error']))

    df = pd.DataFrame((data)['result']).rename(columns={'C': 'close', 'H': 'hight',
                                                        'L': 'low', 'O': 'open'})
    df = df.set_index(['T'])

    return df
