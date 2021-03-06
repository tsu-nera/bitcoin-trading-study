import os
import sys
import traceback

import ccxt
import shutil

import src.constants.exchange as exchange
import src.constants.ccxtconst as ccxtconst
from src.libs.asset import Asset
from src.libs.profit import Profit

from src.core.arbitrage_trading import ArbitrageTrading

from src.loggers.logger import get_trading_logger_with_stdout

from src.libs.slack_client import SlackClient
import src.env as env
import src.constants.path as path


def _copy_if_exist(target_dir_path, file):
    if os.path.exists(file):
        file_name = os.path.basename(file)
        target_file_path = os.path.join(target_dir_path, file_name)
        shutil.copy(file, target_file_path)


def backup_trading_logs(current_trading_dir):
    target_dir_path = os.path.join(current_trading_dir, path.LOG_DIR)
    os.mkdir(target_dir_path)

    for file in path.TRADES_LOGS:
        _copy_if_exist(target_dir_path, file)


def backup_trading_assets(current_trading_dir):
    target_dir_path = os.path.join(current_trading_dir, path.ASSETS_DIR)
    os.mkdir(target_dir_path)

    for file in path.TRADES_ASSETS:
        _copy_if_exist(target_dir_path, file)


def backup_trading_orders(current_trading_dir):
    target_dir_path = os.path.join(current_trading_dir, path.TRADES_DIR)
    os.mkdir(target_dir_path)

    file = path.BOT_ORDER_CSV_FILE_PATH
    _copy_if_exist(target_dir_path, file)

    file = path.BOT_PROFIT_CSV_FILE_PATH
    _copy_if_exist(target_dir_path, file)

    for exchange_id in exchange.EXCHANGE_ID_LIST:
        file = "{}.csv".format(exchange_id)
        _copy_if_exist(target_dir_path, file)


def clean_trading_logs():
    for file in path.TRADES_LOGS:
        if os.path.exists(file):
            # os.removeだと loggerとの関係がうまくいかなかった
            with open(file, 'w'):
                pass


def clean_trading_assets():
    for file in path.TRADES_ASSETS:
        if os.path.exists(file):
            # os.removeだと loggerとの関係がうまくいかなかった
            with open(file, 'w'):
                pass


def run_trading(demo_mode=False):
    clean_trading_logs()
    clean_trading_assets()

    logger = get_trading_logger_with_stdout()
    asset = Asset()

    # verify asset condition
    if not asset.is_equal_btc_amount():
        logger.info(
            "each exchange has different btc balance, not running trading bot."
        )
        asset.display()
        sys.exit(1)

    profit = Profit(asset)

    # run trade
    arbitrage = ArbitrageTrading(exchange.ExchangeId.LIQUID,
                                 exchange.ExchangeId.BITBANK,
                                 ccxtconst.SYMBOL_BTC_JPY,
                                 profit,
                                 demo_mode=demo_mode)

    slack = SlackClient(env.SLACK_WEBHOOK_URL_TRADE)

    current_trading_dir = arbitrage.get_current_trading_data_dir()

    if demo_mode:
        logger.info("====================================")
        logger.info("=== trading bot start(demo mode) ===")
        logger.info("====================================")
    else:
        logger.info("=========================")
        logger.info("=== trading bot start ===")
        logger.info("=========================")
        slack.notify_with_datetime("Trading Botの稼働を開始しました。")
        asset.save(asset.TRADIGNG_START)
        profit.update()

    try:
        arbitrage.run()
    except KeyboardInterrupt:
        # Botを手動で止めるときはCtrl+Cなのでそのアクションを捕捉
        logger.info("keyboard interuption occured. stop trading bot...")
    except ccxt.InsufficientFunds:
        # circuit breaker でログを残しているのでここでログしなくてもいい。
        slack_error = SlackClient(env.SLACK_WEBHOOK_URL_ERROR)
        slack_error.notify_error(traceback.format_exc())
    except Exception as e:
        # エラー発生したらログとslack通知
        slack_error = SlackClient(env.SLACK_WEBHOOK_URL_ERROR)
        slack_error.notify_error(traceback.format_exc())
        logger.exception(e)
    finally:
        print()
        print()
        if demo_mode:
            logger.info("==================================")
            logger.info("=== trading bot end(demo mode) ===")
            logger.info("==================================")
        else:
            logger.info("=======================")
            logger.info("=== trading bot end ===")
            logger.info("=======================")

            # teardown
            asset.save(asset.TRADING_END)
            backup_trading_logs(current_trading_dir)
            backup_trading_assets(current_trading_dir)
            backup_trading_orders(current_trading_dir)

            slack.notify_with_datetime("Trading Botの稼働を終了しました。")
