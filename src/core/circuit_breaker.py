import datetime
import time
import ccxt

from src.loggers.logger import get_trading_logger_with_stdout
import src.constants.exchange as exchange
import src.constants.ccxtconst as ccxtconst
import src.utils.private as private

from src.libs.asset import Asset

import src.config as config


class CircuitBreaker():
    def __init__(self, exchange_ids):
        self.exchange_ids = exchange_ids
        self.logger = get_trading_logger_with_stdout()

        self.trade_amount_btc = config.TRADE_AMOUNT

        self.maintenance_log_flag = False

    def __display_message(self):
        self.logger.info("=============================")
        self.logger.info("= CIRCUIT BREAKER CALLED!!! =")
        self.logger.info("=============================")

    def __wait(self, sec):
        self.logger.info("waiting for {} sec ...".format(sec))
        time.sleep(sec)

    def _is_liquid_server_maintenance(self):
        now = datetime.datetime.now()
        # 6:55
        maintenance_start_time = datetime.datetime(now.year, now.month,
                                                   now.day, 6, 55, 0)
        # 7:05
        maintenance_end_time = datetime.datetime(now.year, now.month, now.day,
                                                 7, 5, 0)

        if maintenance_start_time <= now and now <= maintenance_end_time:
            if not self.maintenance_log_flag:
                self.logger.info(
                    "liquid is currently daily server maintenance...(6:55-7:05)"
                )
                self.maintenance_log_flag = True
            return True
        else:
            self.maintenance_log_flag = False
            return False

    def _is_server_maintenance(self, exchange_id):
        # 臨時サーバメンテナンスのときもとりあえずここに判定を追記していく。

        if exchange_id == exchange.ExchangeId.LIQUID:
            return self._is_liquid_server_maintenance()
        else:
            return False

    def is_server_maintenance(self):
        # 臨時サーバメンテナンスのときもとりあえずここに判定を追記していく。

        return any([
            self._is_server_maintenance(exchange_id)
            for exchange_id in self.exchange_ids
        ])

    def recover_exchange_not_available(self):
        self.__display_message()

        self.__wait(3)

        self.logger.info("exchange not available error recovery start")

        self._recover_exchange_not_available()

        self.logger.info("exchange not available error recovery completed")

    def _move_jpy_to_btc(self, exchange_id, amount):
        time.sleep(1)
        if exchange_id == exchange.ExchangeId.COINCHECK:
            private.create_coincheck_buy_order(ccxtconst.SYMBOL_BTC_JPY,
                                               amount)
        else:
            private.create_buy_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                     amount)

    def _recover_exchange_not_available(self):
        # 資産状況のチェック
        assets_btc = []
        assets_jpy = []
        balances = {}

        for exchange_id in self.exchange_ids:
            balance = private.fetch_balance(exchange_id)

            balances[exchange_id] = balance

            asset_btc = {"id": exchange_id, "value": balance["BTC"]}
            asset_jpy = {"id": exchange_id, "value": balance["JPY"]}
            assets_btc.append(asset_btc)
            assets_jpy.append(asset_jpy)

        # 資金不足でBotを落とすかどうかを判定
        trade_amount_btc = config.TRADE_AMOUNT
        trade_amount_jpys = Asset().calc_btc_to_jpy(config.TRADE_AMOUNT,
                                                    verbose=False)
        for exchange_id, balance in balances.items():
            btc = balance["BTC"]
            jpy = balance["JPY"]

            trade_amount_jpy = trade_amount_jpys[exchange_id]

            if btc < trade_amount_btc and jpy < trade_amount_jpy:
                self.logger.error(
                    "{} don't have enough btc={} amount_btc={}/jpy={} amount_jpy={}"
                    .format(exchange_id, btc, trade_amount_btc, jpy,
                            trade_amount_jpy))

                self.logger.info("!!! STOP BOT TRADING !!!")
                raise ccxt.InsufficientFunds

        for asset in assets_btc:
            exchange_id = asset['id']
            btc = asset['value']
            amount = config.TRADE_AMOUNT

            if btc < amount:
                self.logger.info(
                    '{} BTC is not enough (available:{} / neseccery:{})'.
                    format(exchange_id, btc, amount))

                move_amount = amount - btc + 0.001
                self.logger.info('try buy {} BTC at {}'.format(
                    move_amount, exchange_id))
                self._move_jpy_to_btc(exchange_id, move_amount)

        # BTC to JPY は未実装
        # 現状coincheckのBTCが不足するエラーのみなので

    def recover_ddos_protection(self):
        self.__display_message()

        self.logger.info("ddos protection error recovery start")

        self._recover_ddos_protection()

        self.logger.info("ddos protection error recovery completed")

    def _recover_ddos_protection(self):
        # liquid API rate limit exceeded. Please retry after 300s
        # こういうエラーなので、 300secだけsleepする。
        self.__wait(300)

    def recover_network_error(self):
        self.__display_message()

        self.logger.info("network error recovery start")

        self._recover_network_error()

        self.logger.info("network error recovery completed")

    def _recover_network_error(self):
        # ネットワークエラーはとりあえず5秒sleep
        # 様子を見て追加対応する
        self.__wait(5)

    def is_opening_longtime(self, timestamp):
        '''
        openしてから一定時間経過したかどうかチェック
        '''
        if not timestamp:
            return False
        else:
            now = datetime.datetime.now()
            if now > timestamp + datetime.timedelta(
                    minutes=config.FORCE_CLOSING_MIN):
                return True
            else:
                return False

    def recover_opening_longtime(self, arbitrage):
        self.__display_message()

        self.__wait(3)
        message = "opening for {} minutes, force closing start.".format(
            config.FORCE_CLOSING_MIN)
        self.logger.info(message)

        arbitrage.force_closing()

        self.__wait(3)
        self.logger.info("force closing end.")
