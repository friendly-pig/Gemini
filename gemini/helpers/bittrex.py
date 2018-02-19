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
    params = {'marketName': pair, 'tickInterval': period}
    response = requests.get('https://bittrex.com/Api/v2.0/pub/market/GetTicks', params=params)

    return response.json()


def convert_pair_bittrex(pair):
    converted = "{0}-{1}".format(*pair.split('_'))
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

        data = get_past(pair, period)
    except Exception as ex:
        raise ex

    if 'error' in data:
        raise Exception("Bad response: {}".format(data['error']))

    df = pd.DataFrame((data)['result'])
    df = df.set_index(['T'])

    return df

print(convert_pair_bittrex('BTC_LTC'))