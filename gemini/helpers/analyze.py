import logging
import time

import bokeh.plotting
import matplotlib.pyplot as plt
import pandas as pd
from bokeh.models import LinearAxis, Range1d

logger = logging.getLogger(__name__)


def analyze_bokeh(algo, title=None, show_trades=False):
    """
    Draw charts for backtest results

    Use Bokeh

    :param title:
    :param show_trades:
    :return:
    """
    # TODO Replace to Gemini class

    bokeh.plotting.output_file("chart.html", title=title)
    p = bokeh.plotting.figure(x_axis_type="datetime", plot_width=1000,
                              plot_height=400,
                              title=title)
    p.grid.grid_line_alpha = 0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Equity'

    if algo.records:
        # Setting the second y axis range name and range
        p.extra_y_ranges = {
            "Records": Range1d(start=0, end=algo.data['close'].max())}
        # Adding the second axis to the plot.
        p.add_layout(LinearAxis(y_range_name="Records"), 'right')

        records = pd.DataFrame(algo.records)
        for c in records.columns:
            if c == 'date':
                continue

            p.line(records['date'], records[c], color='grey',
                   legend=c, y_range_name="Records")

    # print(algo.data[['date', 'close', 'sma50', 'sma150']])

    p.line(algo.data.index, algo.data['base_equity'], color='#CAD8DE',
           legend='Buy and Hold')
    p.line(algo.data.index, algo.data['equity'],
           color='#49516F',
           legend='Strategy')
    p.legend.location = "top_left"

    # check total trades
    total_trades = len(
        algo.account.opened_trades) + len(algo.account.closed_trades)
    # Always disable show trade when trades more than 200 (Work too slow)
    if total_trades > 200:
        show_trades = False
        logger.warning("Show trades disabled. Use analyze_mpl().")

    if show_trades:
        for trade in algo.account.opened_trades:
            x = time.mktime(trade.date.timetuple()) * 1000
            y = algo.data['equity'].loc[trade.date]
            if trade.type_ == 'Long':
                p.circle(x, y, size=6, color='green', alpha=0.5)
            elif trade.type_ == 'Short':
                p.circle(x, y, size=6, color='red', alpha=0.5)

        for trade in algo.account.closed_trades:
            x = time.mktime(trade.date.timetuple()) * 1000
            y = algo.data['equity'].loc[trade.date]
            if trade.type_ == 'Long':
                p.circle(x, y, size=6, color='blue', alpha=0.5)
            elif trade.type_ == 'Short':
                p.circle(x, y, size=6, color='orange', alpha=0.5)

    bokeh.plotting.show(p)


def analyze_mpl(algo, title=None, show_trades=False):
    """
    Draw charts for backtest results

    Use Matplotlib

    :param title:
    :param show_trades:
    :return:
    """
    # TODO Replace to Gemini class

    fig = plt.figure(figsize=(15, 10), facecolor='white')

    ax1 = fig.add_subplot(211)
    algo.data['base_equity'].plot(ax=ax1, label='Base Equity')
    ax1.set_ylabel('Equity')

    algo.data['equity'].plot(ax=ax1, label='Equity')

    ax2 = fig.add_subplot(212)
    ax2.set_ylabel('Records')

    if algo.records:
        records = pd.DataFrame(algo.records)
        records = records.set_index('date')
        records.plot(ax=ax2)

    if show_trades and False:
        # FIXME Fix x axis
        buys = dict()
        sells = dict()
        for trade in algo.account.opened_trades:
            if trade.type_ == 'Long':
                buys[trade.date] = algo.data['equity'].loc[trade.date]
            elif trade.type_ == 'Short':
                sells[trade.date] = algo.data['equity'].loc[trade.date]

        for trade in algo.account.closed_trades:
            if trade.type_ == 'Long':
                sells[trade.date] = algo.data['equity'].loc[trade.date]
            elif trade.type_ == 'Short':
                buys[trade.date] = algo.data['equity'].loc[trade.date]

        ax1.plot(buys.keys(), buys.values(), '^', markersize=5, color='m')
        ax1.plot(sells.keys(), sells.values(), 'v', markersize=5, color='k')

    plt.legend(loc=0)
    plt.show()
