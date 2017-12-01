import logging
import time
import types
import numpy as np

from empyrical import max_drawdown

import gemini.settings as settings
from gemini import exchange
from gemini.helpers import helpers
from gemini.helpers.timeframe_resampler import resample

FEES = getattr(settings, "FEES", dict())

logger = logging.getLogger(__name__)


class Gemini:
    """
    Main class of Backtester
    """
    data = None  # storage for history data
    account = None  # exchange account simulator
    sim_params = {
        'capital_base': 10e5,
        'data_frequency': 'D',
        'fee': FEES,  # Fees in percent of trade amount
    }
    records = []
    performance = []

    def __init__(self, initialize=None, logic=None, analyze=None, results=None,
                 sim_params=None):
        """
        Create backtester with own methods.

        sim_params :: Backtester's settings:
            * start_session :: not use
            * end_session :: not use
            * capital_base :: default 10k
            * data_frequency :: not use
            *

        :param initialize:
        :param logic:
        :param analyze:
        :param sim_params:
        """

        if initialize is not None:
            self.initialize = types.MethodType(initialize, self)

        if logic is not None:
            self.logic = types.MethodType(logic, self)

        if analyze is not None:
            self.analyze = types.MethodType(analyze, self)

        if results is None:
            self.results = self.results_default
        elif results:
            self.results = types.MethodType(results, self)

        if sim_params is not None:
            # replace only received items
            for k, item in self.sim_params.items():
                if k in sim_params:
                    self.sim_params[k] = sim_params[k]

    def initialize(self):
        """
        First method which will be called after start algorithm
        :return:
        """
        pass

    def logic(self, data):
        """
        Central method which will be called for every tick
        in trading interval.

        :param data:
        :return:
        """
        pass

    def run(self, data, **kwargs):
        """
        Main method to start backtest
        :param data :: history data with ticks or bars
        :param logic:
        :param trading_interval:
        :param lookback_period:
        :return:
        """

        self.account = exchange.Account(
            self.sim_params.get('capital_base', 10e5),
            fee=self.sim_params.get('fee', None)
        )
        self.records = []

        self.initialize()

        # TODO Add filter between start & end session from sim_params

        # resample data frame to 'D' by default
        self.data = resample(data, self.sim_params.get('data_frequency', 'D'))

        # start cycle
        for index, tick in self.data.iterrows():
            # Update account variables
            self.account.date = index
            # update total value in account
            # TODO Replace by pandas DataFrame
            self.account.equity.append(
                (index, self.account.total_value(tick['close'])))

            # Execute trading logic
            lookback_data = self.data.loc[:index]
            try:
                self.logic(lookback_data)
            except Exception as ex:
                logger.exception(ex)

            # Cleanup empty positions
            self.account.purge_positions()

        self.performance = self.prepare_performance()
        self.results()
        self.analyze(**kwargs)

        return self.performance

    def prepare_performance(self):
        start = time.time()
        perf = self.data.copy()

        perf['price'] = perf['close']

        shares = self.account.initial_capital / perf.iloc[0]['close']
        perf['base_equity'] = [price * shares for price in perf['close']]
        perf['equity'] = [e for _, e in self.account.equity]

        # BENCHMARK
        perf['benchmark_period_return'] = [
            helpers.percent_change(perf['base_equity'][0],
                                   perf['base_equity'][i])
            for i in range(0, len(perf['base_equity']))]

        perf['benchmark_max_drawdown'] = [
            max_drawdown(perf['base_equity'][:i].pct_change())
            for i in range(0, len(perf['base_equity']))]

        # STRATEGY
        perf['algorithm_period_return'] = [
            helpers.percent_change(perf['equity'][0],
                                   perf['equity'][i])
            for i in range(0, len(perf['equity']))]

        perf['returns'] = perf['equity'].pct_change()

        perf['max_drawdown'] = [
            max_drawdown(perf['equity'][:i].pct_change())
            for i in range(0, len(perf['equity']))]

        logger.debug(
            'Performance prepared for {:.2} sec'.format(time.time() - start))

        perf['ending_value'] = 0  # value of opened positions
        perf['alpha'] = '0'
        perf['beta'] = '0'
        perf['sharpe'] = '0'

        return perf

    def results(self):
        """
        Show results of strategy
        :return:
        """
        pass

    def results_default(self):
        """
        Print results of backtest to console
        :return:
        """
        title = "{:=^52}".format(
            " Results (freq {}) ".format(self.sim_params['data_frequency']))
        print(title + "\n")

        shares = self.account.initial_capital / self.data.iloc[0]['close']
        self.data['base_equity'] = [price * shares for price in
                                    self.data['close']]
        self.data['equity'] = [e for _, e in self.account.equity]

        # STRING FORMATS
        title_fmt = "{:-^40}"
        str_fmt = "{0:<13}: {1:.2f}{2}"

        # BENCHMARK
        percent_change = helpers.percent_change(self.data['base_equity'][0],
                                                self.data['base_equity'][-1])

        bench = [
            ("Capital", self.account.initial_capital, ""),
            ("Final Equity", self.data['base_equity'][-1], ""),
            ("Net profit",
             helpers.profit(self.account.initial_capital, percent_change),
             " ({:+.2f}%)".format(percent_change * 100)),
            ("Max Drawdown",
             max_drawdown(self.data['base_equity'].pct_change()) * 100, "%"),
        ]

        print(title_fmt.format(" Benchmark "))
        for r in bench:
            print(str_fmt.format(*r))

        # STRATEGY
        percent_change = helpers.percent_change(self.data['equity'][0],
                                                self.data['equity'][-1])
        fee = sum([t.fee for t in self.account.closed_trades])

        lst = [t.exit * t.shares - t.fee - t.entry * t.shares for t in self.account.closed_trades]
        array = np.array(lst)
        pnl_win = np.sum(array[array > 0])
        pnl_loss = np.sum(array[array < 0])
        trades_win = len(array[array > 0])
        trades_loss = len(array[array < 0])
        trades = len(array)

        # PnL % calculation
        win_avg = pnl_win / trades_win
        loss_avg = pnl_loss / trades_loss

        # Expected value
        """
        W% = trades_win / trades = win_avg
        L% = trades_loss / trades = loss_avg
        Ave W = pnl_win / trades_win
        Ave L = pnl_loss / trades_loss
        Expected value = (W% * Ave W) – (L% * Ave L)
        """
        ev = (trades_win / trades) * win_avg - (trades_loss / trades) * loss_avg
        success_rate = trades_win / trades * 100

        strategy = [
            ("Capital", self.account.initial_capital, ""),
            ("Final Equity", self.data['equity'][-1], ""),
            ("Net profit",
             helpers.profit(self.account.initial_capital, percent_change),
             " ({:+.2f}%)".format(percent_change * 100)),
            ("Max Drawdown",
             max_drawdown(self.data['equity'].pct_change()) * 100, "%"),
            ("Fees paid", fee, ""),
        ]

        # STATISTICS
        longs = len(
            [t for t in self.account.opened_trades if t.type_ == 'Long'])
        sells = len(
            [t for t in self.account.closed_trades if t.type_ == 'Long'])
        shorts = len(
            [t for t in self.account.opened_trades if t.type_ == 'Short'])
        covers = len(
            [t for t in self.account.closed_trades if t.type_ == 'Short'])

        print(title_fmt.format(" Strategy "))
        for r in strategy:
            print(str_fmt.format(*r))

        stat = [
            ('Success rate %', success_rate, 0, success_rate),
            ('Loss per trade', loss_avg, 0, loss_avg),
            ('Win per trade', win_avg, 0, win_avg),
            ('Expected value', ev, 0, ev),
            ('Open', longs, shorts, longs + shorts),
            ('Closed', sells, covers, sells + covers),
            ('Total Trades', longs + sells, shorts + covers, longs + shorts + sells + covers)
        ]

        str_fmt = "{:<20}: {:>7.4f} {:>10.4f} {:>10.4f}"
        title_fmt = "{:-^52}"

        print(title_fmt.format(" Statistics "))

        title_fmt = "{:<20} {:>7} {:>10} {:>10}"
        print(title_fmt.format('', 'Long', 'Short', 'All'))

        for r in stat:
            print(str_fmt.format(*r))

        print("-" * len(title))

    def analyze(self):
        pass
