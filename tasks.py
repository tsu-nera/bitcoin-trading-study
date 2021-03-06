import shutil
from invoke import task, run

import os
import glob
import time
import datetime

import importlib
import psutil
from distutils.dir_util import copy_tree

import src.utils.public as public
import src.utils.private as private

from src.utils.trading import run_trading
from src.utils.backtesting import run_backtesting
from src.utils.historical import save_ticks
import src.utils.tool as tool
import src.utils.trade_history as trade_history
import src.utils.report as report
from src.utils.trade_analysis import run_analysis

from src.libs.ccxt_client import CcxtClient
from src.libs.slack_client import SlackClient
from src.libs.asset import Asset

import src.constants.path as path
import src.constants.exchange as exchange
import src.constants.ccxtconst as ccxtconst
import src.config as config
import src.env as env

import logging
from logging import basicConfig

basicConfig(level=logging.INFO, handlers=[])

TRADING_MODULE = importlib.import_module('src.utils.trading')
PUBLIC_MODULE = importlib.import_module('src.utils.public')


@task
def ping_coincheck(c):
    tool.ping(exchange.ExchangeId.COINCHECK)


@task
def ping_liquid(c):
    tool.ping(exchange.ExchangeId.LIQUID)


@task
def ping_bitbank(c):
    tool.ping(exchange.ExchangeId.BITBANK)


@task
def tick_bitflyer(c):
    public.fetch_ticks(exchange.ExchangeId.BITFLYER)


@task
def tick_coincheck(c):
    public.fetch_ticks(exchange.ExchangeId.COINCHECK)


@task
def tick_liquid(c):
    public.fetch_ticks(exchange.ExchangeId.LIQUID)


@task
def tick_bitbank(c):
    public.fetch_ticks(exchange.ExchangeId.BITBANK)


@task
def tick_bitmex(c):
    public.fetch_ticks(exchange.ExchangeId.BITMEX, exchange.SYMBOL_BTC_USD)


@task
def tick_testnet(c):
    public.fetch_ticks(exchange.ExchangeId.BITMEX_DEMO,
                       exchange.SYMBOL_BTC_USD)


@task
def tick_gemini_sandbox(c):
    public.fetch_ticks(exchange.ExchangeId.GEMINI_DEMO,
                       exchange.SYMBOL_BTC_USD)


@task
def ping_eff_coincheck(c):
    tool.ping(exchange.ExchangeId.COINCHECK, eff=True)


@task
def ping_eff_liquid(c):
    tool.ping(exchange.ExchangeId.LIQUID, eff=True)


@task
def ping_eff_bitbank(c):
    tool.ping(exchange.ExchangeId.BITBANK, eff=True)


@task
def tick_eff_coincheck(c):
    public.fetch_ticks(exchange.ExchangeId.COINCHECK, eff=True)


@task
def tick_eff_liquid(c):
    public.fetch_ticks(exchange.ExchangeId.LIQUID, eff=True)


@task
def tick_eff_bitbank(c):
    public.fetch_ticks(exchange.ExchangeId.BITBANK, eff=True)


'''
@task
def tick_ws_coincheck(c):    
    # websocket通信を利用したtickの取得(coincheck)
    
    public.fetch_ws_ticks(exchange.ExchangeId.COINCHECK)
'''


@task
def tick_ws_liquid(c):
    # websocket通信を利用したtickの取得(liquid)
    public.fetch_ws_ticks(exchange.ExchangeId.LIQUID)


@task
def tick_ws_bitbank(c):
    # websocket通信を利用したtickの取得(bitbank)
    public.fetch_ws_ticks(exchange.ExchangeId.BITBANK)


@task
def balance_bitflyer(c):
    print(private.fetch_balance(exchange.ExchangeId.BITFLYER))


@task
def balance_coincheck(c):
    print(private.fetch_balance(exchange.ExchangeId.COINCHECK))


@task
def balance_liquid(c):
    print(private.fetch_balance(exchange.ExchangeId.LIQUID))


@task
def balance_bitbank(c):
    print(private.fetch_balance(exchange.ExchangeId.BITBANK))


@task
def balance_testnet(c):
    print(private.fetch_balance(exchange.ExchangeId.BITMEX_DEMO))


@task
def balance_gemini_sandbox(c):
    print(private.fetch_balance(exchange.ExchangeId.GEMINI_DEMO))


@task
def board_coincheck(c):
    '''
    websocket通信を利用した板情報の取得(coincheck)
    '''
    public.fetch_board(exchange.ExchangeId.COINCHECK)


@task
def board_liquid(c):
    '''
    websocket通信を利用した板情報の取得(liquid)
    '''
    public.fetch_board(exchange.ExchangeId.LIQUID)


@task
def board_bitbank(c):
    '''
    websocket通信を利用した板情報の取得(bitbank)
    '''
    public.fetch_board(exchange.ExchangeId.BITBANK)


@task
def tick_board_coincheck(c):
    public.fetch_board_tick(exchange.ExchangeId.COINCHECK)


@task
def tick_board_liquid(c):
    public.fetch_board_tick(exchange.ExchangeId.LIQUID)


@task
def tick_board_bitbank(c):
    public.fetch_board_tick(exchange.ExchangeId.BITBANK)


@task
def bot(c):
    run_trading()


@task
def demo_trade(c):
    run_trading(demo_mode=True)


@task
def backtest(c, timestamp):
    run_backtesting(timestamp)


@task
def simulate(c, timestamp):
    run_backtesting(timestamp, simulate_mode=True)


@task
def get_historical_data(c):
    save_ticks()


@task
def symbols(c, exchange_id):
    __exchange_id = exchange.EXCHANGE_ID_DICT[exchange_id]
    c = CcxtClient(__exchange_id)
    print(c.symbols())


def __buy_with_amount(c, exchange_id, amount):
    response = private.create_buy_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                        float(amount))
    print(response)
    return response


@task
def buy(c, exchange_id):
    return __buy_with_amount(c, exchange_id, config.TRADE_AMOUNT)


def __sell_with_amount(c, exchange_id, amount):
    response = private.create_sell_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                         float(amount))
    print(response)
    return response


@task
def sell(c, exchange_id):
    return __sell_with_amount(c, exchange_id, config.TRADE_AMOUNT)


@task
def sell_coincheck_with_amount(c, amount):
    response = private.create_coincheck_sell_order(ccxtconst.SYMBOL_BTC_JPY,
                                                   float(amount))
    print(response)
    return response


@task
def sell_coincheck(c):
    return sell_coincheck_with_amount(c, config.TRADE_AMOUNT)


@task
def buy_coincheck_with_amount(c, amount):
    response = private.create_coincheck_buy_order(ccxtconst.SYMBOL_BTC_JPY,
                                                  float(amount))
    print(response)
    return response


@task
def buy_coincheck(c):
    return buy_coincheck_with_amount(c, config.TRADE_AMOUNT)


@task
def sell_liquid_with_amount(c, amount):
    return __sell_with_amount(c, exchange.ExchangeId.LIQUID, amount)


@task
def sell_liquid(c):
    return sell(c, exchange.ExchangeId.LIQUID)


@task
def buy_liquid_with_amount(c, amount):
    return __buy_with_amount(c, exchange.ExchangeId.LIQUID, amount)


@task
def buy_liquid(c):
    return buy(c, exchange.ExchangeId.LIQUID)


@task
def buy_coincheck_sell_liquid(c):
    ex1_jpy = int(buy_coincheck(c)["jpy"])
    ex2_jpy = int(sell_liquid(c)["jpy"])

    print("buy coincheck {}, sell liquid {}, profit={}".format(
        ex1_jpy, ex2_jpy, ex2_jpy - ex1_jpy))


@task
def sell_coincheck_buy_liquid(c):
    ex1_jpy = int(sell_coincheck(c)["jpy"])
    ex2_jpy = int(buy_liquid(c)["jpy"])

    print("buy liquid {}, sell coincheck {}, profit={}".format(
        ex2_jpy, ex1_jpy, ex1_jpy - ex2_jpy))


@task
def buy_bitbank(c):
    return buy_bitbank_with_amount(c, config.TRADE_AMOUNT)


@task
def buy_bitbank_with_amount(c, amount):
    response = private.create_bitbank_buy_order(ccxtconst.SYMBOL_BTC_JPY,
                                                float(amount))
    print(response)
    return response


@task
def sell_bitbank(c):
    return sell_bitbank_with_amount(c, config.TRADE_AMOUNT)


@task
def sell_bitbank_with_amount(c, amount):
    response = private.create_bitbank_sell_order(ccxtconst.SYMBOL_BTC_JPY,
                                                 float(amount))
    print(response)
    return response


@task
def buy_bitbank_sell_liquid(c):
    ex1_jpy = int(buy_bitbank(c)["jpy"])
    ex2_jpy = int(sell_liquid(c)["jpy"])

    print("buy bitbank {}, sell liquid {}, profit={}".format(
        ex1_jpy, ex2_jpy, ex2_jpy - ex1_jpy))


@task
def sell_bitbank_buy_liquid(c):
    ex1_jpy = int(sell_bitbank(c)["jpy"])
    ex2_jpy = int(buy_liquid(c)["jpy"])

    print("buy liquid {}, sell coincheck {}, profit={}".format(
        ex2_jpy, ex1_jpy, ex1_jpy - ex2_jpy))


@task
def buy_testnet(c):
    private.create_buy_order(exchange.ExchangeId.BITMEX_DEMO,
                             exchange.SYMBOL_BTC_USD, 1)


@task
def sell_testnet(c):
    private.create_sell_order(exchange.ExchangeId.BITMEX_DEMO,
                              exchange.SYMBOL_BTC_USD, 1)


@task
def fetch_orders(c):
    # private.fetch_open_orders(exchange.ExchangeId.BITMEX_DEMO)
    # private.fetch_open_orders(exchange.ExchangeId.COINCHECK)
    private.fetch_open_orders(exchange.ExchangeId.LIQUID)
    private.fetch_open_orders(exchange.ExchangeId.BITBANK)


@task
def fetch_positions(c):
    # private.get_positions(exchange.ExchangeId.BITMEX_DEMO)
    # private.get_positions(exchange.ExchangeId.COINCHECK)
    private.get_positions(exchange.ExchangeId.LIQUID)
    private.get_positions(exchange.ExchangeId.BITBANK)


@task
def save_coincheck_trades(c):
    trade_history.save_trades(exchange.ExchangeId.COINCHECK)


@task
def save_liquid_trades(c):
    trade_history.save_trades(exchange.ExchangeId.LIQUID)


@task
def save_bitbank_trades(c):
    trade_history.save_trades(exchange.ExchangeId.BITBANK)


@task
def save_trades(c):
    # save_coincheck_trades(c)
    save_liquid_trades(c)
    save_bitbank_trades(c)


###############
# Utils
###############
@task
def check_margin(c):
    tool.check_profit_margin()


@task
def asset(c):
    Asset().display()


@task
def bot_asset(c):
    Asset().run_bot()
    update_note_asset(c)


@task
def calc_btcjpy(c, btc_amount):
    '''
    BTCをJPYに変換した場合の金額を求める
    '''
    Asset().calc_btc_to_jpy(float(btc_amount))


@task
def calc_jpybtc(c, jpy_price):
    '''
    JPYで購入できるBTCの値を求める
    '''
    Asset().calc_jpy_to_btc(int(jpy_price))


# @task
def reload(c):
    # 検証中
    importlib.reload(PUBLIC_MODULE)


@task
def recent_profits(c):
    trade_history.show_recent_profits()


@task
def recent_profits_by(c, hour):
    trade_history.show_recent_profits(int(hour))


@task
def trade_analysis(c, timestamp):
    run_analysis(timestamp)


@task
def trade_latest_analysis(c):
    dir_path = path.REPORTS_DATA_DIR_PATH
    timestamp = get_latest_dirname(dir_path)
    run_analysis(timestamp)


@task
def display_report(c, timestamp):
    report.display(timestamp)


@task
def display_latest_report(c):
    dir_path = path.REPORTS_DATA_DIR_PATH
    timestamp = get_latest_dirname(dir_path)
    report.display(timestamp)


###############
# Othre Utils
###############
def get_latest_dirpath(dir_path):
    return max(glob.glob(os.path.join(dir_path, '*/')), key=os.path.getmtime)


def get_latest_dirname(dir_path):
    file_path = get_latest_dirpath(dir_path)
    return os.path.basename(os.path.dirname(file_path))


@task
def backup_latest_data(c):
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = get_latest_dirpath(production_dir)
    dir_name = from_dir.split('/')[-2]
    to_dir = os.path.join(path.BACKTEST_DATA_DIR_PATH, dir_name)

    copy_tree(from_dir, to_dir)


@task
def backup_data(c, dir_name):
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = os.path.join(production_dir, dir_name)
    to_dir = os.path.join(path.BACKTEST_DATA_DIR_PATH, dir_name)

    copy_tree(from_dir, to_dir)


@task
def generate_report(c, dir_name):
    report.generate(dir_name)


@task
def run_notebook(c, file_path):
    report.run_notebook(file_path)


@task
def export_trade_result(c, timestamp):
    report.export_trade_result(timestamp)


@task
def generate_latest_report(c):
    report.generate_latest()


@task
def backup_trades(c):
    trade_history.backup_trades()


@task
def note(c):
    run("jupyter notebook --notebook-dir='.'")


def _update_note(keyword):
    ipynb_file_path = "./data/notebooks/{}.ipynb".format(keyword)
    html_path_from = "./data/notebooks/{}.html".format(keyword)
    html_path_to = "./data/notebooks/html/{}.html".format(keyword)

    report.run_notebook(ipynb_file_path)
    report.convert_nb_html(ipynb_file_path)
    shutil.move(html_path_from, html_path_to)


@task
def update_note_asset(c):
    _update_note("asset")


@task
def update_note_trades(c):
    _update_note("trades")


@task
def update_notes(c):
    _update_note("asset")
    _update_note("trades")


@task
def slack(c, message):
    url = env.SLACK_WEBHOOK_URL_TRADE
    client = SlackClient(url)
    client.notify_with_datetime(message)


@task
def check_error(c, timestamp):
    root_dir_path = path.REPORTS_DATA_DIR_PATH
    dir_path = os.path.join(root_dir_path, timestamp)
    run('find {} -type f -name "*.log" | xargs grep ERROR'.format(dir_path))


@task
def check_latest_error(c):
    root_dir_path = path.REPORTS_DATA_DIR_PATH
    dir_path = get_latest_dirpath(root_dir_path)
    run('find {} -type f -name "*.log" | xargs grep ERROR'.format(dir_path))


@task
def is_bot(c):
    flag = any([
        p.cmdline()[2] == "trade" for p in psutil.process_iter()
        if len(p.cmdline()) == 3
    ])

    if flag:
        print("trading bot is running.")
    else:
        print("trading bot is stopped.")


###############
# perf tools
###############
def perf_func_execution_time(func):
    start_time = datetime.datetime.now()
    func()
    end_time = datetime.datetime.now()

    exec_time_ms = round((end_time - start_time).microseconds / 1000, 2)

    return exec_time_ms


@task
def perf_fetch_tick(c):
    def fetch_tick_with_serial():
        ret1 = public.fetch_tick(exchange.ExchangeId.COINCHECK)
        ret2 = public.fetch_tick(exchange.ExchangeId.LIQUID)

        return ret1, ret2

    for _ in range(10):
        time_ms = perf_func_execution_time(lambda: tool.ping_with_thb())
        print("get tick parallel time={} ms".format(time_ms))
        time.sleep(1)

        time_ms = perf_func_execution_time(fetch_tick_with_serial)
        print("get tick serial   time={} ms".format(time_ms))
        time.sleep(1)


@task
def perf_coincheck_buy_amount(c):
    tool.adjust_coincheck_buy_amount()
