import os, sys

# To load local folders
project_root = os.path.abspath(os.path.join(os.path.dirname('__file__'), '..'))
sys.path.insert(0, project_root)
from pysrc.getters import *

import heapq

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# if 'stds' not in globals():
#     stock_codes = [path.strip(".csv") for path in os.listdir(PRICE_PATH)]
#     stds = dict()
#     for stock_code in stock_codes:
#         df = getPriceByStockCode(stock_code)
#         stds[stock_code] = df['涨跌幅'].std()
#     selected_stock_codes = pd.DataFrame({"stock_code": stds.keys(), "std": stds.values()}).sort_values("std", ascending=False)[:10]['stock_code'].to_list()

WINDOW_SIZE = 63


def getAlgo(stock_code: str):
    df = getRawPriceByStockCode(stock_code)
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values("日期")
    # Calculate the rolling 3-month high and low for "收盘"
    df['3月最高'] = df['最高'].rolling(window=WINDOW_SIZE, min_periods=1).max()
    df['3月最低'] = df['最低'].rolling(window=WINDOW_SIZE, min_periods=1).min()
    df['开仓点'] = df['3月最低'] * (df['最低'] <= df['3月最低'])
    MAX_RATE = 0.2
    df['涨停板'] = round(df['收盘'].shift(1) * (1 + MAX_RATE), 2)
    df['半涨停板'] = round(df['收盘'].shift(1) * (1 + MAX_RATE / 2), 2)
    df['跌停板'] = round(df['收盘'].shift(1) * (1 - MAX_RATE / 2), 2)
    df['补仓点'] = df['跌停板'] * (df['最低'] <= df['跌停板'])
    df['半涨停卖出点'] = df['半涨停板'] * (df['最高'] >= df['半涨停板'])
    df['涨停卖出点'] = df['涨停板'] * (df['最高'] >= df['涨停板'])
    df = df[df['日期'] >= pd.DateOffset(WINDOW_SIZE) + df['日期'].min()]
    df = df.reset_index()
    df = trade(df)
    return df


def trade(df: pd.DataFrame):
    # init
    trades, positions, exec_pxs = [0], [0], [0]
    longs, longs_indices = [], []
    for i in range(1, len(df)):
        # curr status
        trade, position, exec_px = 0, positions[-1], 0  # exec_px=0 indicating no execution
        # long
        if position == 0 and df['开仓点'][i] > 0:
            trade += 1
            position += trade
            exec_px = df['开仓点'][i]
            heapq.heappush(longs, exec_px)
            longs_indices.append(i)
        elif position > 0 and i >= longs_indices[-1] + 3 and df['补仓点'][i] > 0:
            trade += 1
            position += trade
            exec_px = df['补仓点'][i]
            heapq.heappush(longs, exec_px)
            longs_indices.append(i)
        # short
        if position > 0 and len(longs) > 0 and longs[0] < df['半涨停卖出点'][i]:  # longs[0] < df['半涨停卖出点'] - epslon
            last_min_long = heapq.heappop(longs)
            trade = -min(position, 1 * (last_min_long > df['半涨停卖出点'][i]) + 1 * (last_min_long > df['涨停卖出点'][i]))
            position += trade
            if trade == -1:
                exec_px = df['半涨停卖出点'][i]
            elif trade == -2:
                exec_px = (df['半涨停卖出点'][i] + df['涨停卖出点'][i]) / 2
        # record
        trades.append(trade)
        positions.append(position)
        exec_pxs.append(exec_px)
    # append to df
    df['交易量'] = trades
    df["仓位"] = positions
    df['成交价'] = exec_pxs
    df['交易额'] = 100 * df['交易量'] * df['成交价']
    df['GMV'] = df['交易额'].cumsum()
    df['收盘仓位市值'] = 100 * df['仓位'] * df['收盘']
    df['dPnL'] = (df['收盘仓位市值'] - df['GMV']).diff(1)
    df['PnL'] = df['dPnL'].cumsum()
    return df


def temp_main_plot(df: pd.DataFrame):
    def figAddLine(fig: go.Figure, col: str, mode: str = "lines", mode_type: dict = None):
        """Method. Return None. Adds a line to the figure with optional line styling."""
        if mode == "lines":
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df[col],
                mode=mode,
                name=col,
                line=mode_type
            ))
        elif mode == "markers":
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=df[col],
                mode=mode,
                name=col,
                marker=mode_type
            ))

    # Initialize the figure
    fig1 = go.Figure()
    figAddLine(fig1, "收盘")
    figAddLine(fig1, "3月最高", mode_type=dict(dash='dash'))
    figAddLine(fig1, "3月最低", mode_type=dict(dash='dash'))
    # markers
    figAddLine(fig1, "开仓点", mode="markers", mode_type=dict(symbol='triangle-up', color="darkred", size=10, opacity=0.1))
    figAddLine(fig1, "补仓点", mode="markers", mode_type=dict(symbol='triangle-up', color="lightcoral", size=10, opacity=0.1))
    figAddLine(fig1, "半涨停卖出点", mode="markers", mode_type=dict(symbol='triangle-down', color="lightgreen", size=10, opacity=0.1))  # dark green
    figAddLine(fig1, "涨停卖出点", mode="markers", mode_type=dict(symbol='triangle-down', color="darkgreen", size=10, opacity=0.1))
    df['实际买入点'] = df['成交价'] * (df['交易额'] > 0)
    df['实际卖出点'] = df['成交价'] * (df['交易额'] < 0)
    figAddLine(fig1, "实际买入点", mode="markers", mode_type=dict(symbol='triangle-up', color="darkred", size=12))
    figAddLine(fig1, "实际卖出点", mode="markers", mode_type=dict(symbol='triangle-down', color="darkgreen", size=12))
    # Customize layout
    fig1.update_layout(
        title=stock_code,
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white"
    )

    # Initialize the figure
    fig2 = go.Figure()
    figAddLine(fig2, "仓位")
    # Customize layout
    fig2.update_layout(
        title=stock_code,
        xaxis_title="Date",
        yaxis_title="仓位",
        template="plotly_white"
    )

    # Initialize the figure
    fig3 = go.Figure()
    figAddLine(fig3, "GMV")
    figAddLine(fig3, "收盘仓位市值")
    # Customize layout
    fig3.update_layout(
        title=stock_code,
        xaxis_title="Date",
        yaxis_title="volume",
        template="plotly_white"
    )

    # Initialize the figure
    fig4 = go.Figure()
    figAddLine(fig4, "PnL")

    # Customize layout
    fig4.update_layout(
        title=stock_code,
        xaxis_title="Date",
        yaxis_title="volume",
        template="plotly_white"
    )

    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=('走势图', '仓位', 'GMV', 'PnL'),
        row_heights=[0.6, 0.2, 0.2, 0.2],
        shared_xaxes=True,
        vertical_spacing=0.1
    )

    # Add the first figure to row 1, column 1
    for trace in fig1.data:
        fig.add_trace(trace, row=1, col=1)

    # Add the second figure to row 2, column 1
    for trace in fig2.data:
        fig.add_trace(trace, row=2, col=1)

    # Add the third figure to row 3, column 1
    for trace in fig3.data:
        fig.add_trace(trace, row=3, col=1)

    # Add the PnL to row 4, column 1
    for trace in fig4.data:
        fig.add_trace(trace, row=4, col=1)

    # Update layout
    fig.update_layout(
        height=800,  # Set the height of the entire figure
        title_text="风险分析",
        showlegend=True,
        template="plotly_white"
    )

    # Show the figure
    return fig


def main(stock_code: str):
    df = getAlgo(stock_code)
    fig = temp_main_plot(df)
    fig.to_image(f"D://Documents//PycharmProject//eastmoney_data//figs//temp//{stock_code}.png")


stock_code = "000636"
main(stock_code)
