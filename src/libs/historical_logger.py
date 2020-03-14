import os
import datetime
from logging import getLogger

from src.libs.logger import create_historical_logger
import src.constants.ccxtconst as ccxtconst
import src.constants.common as common


class HistoricalLogger():
    def __init__(self):
        self.exchange_ids = [
            ccxtconst.EXCHANGE_ID_COINCHECK, ccxtconst.EXCHANGE_ID_LIQUID
        ]
        self.dir_path = self._get_dir_path()

        # create directory
        os.mkdir(self.dir_path)

        # save asset

        # sava params

        # initialze loggers
        [self._create_logger(exchange_id) for exchange_id in self.exchange_ids]

        # add header
        [
            self._logging_header(exchange_id)
            for exchange_id in self.exchange_ids
        ]

    def logging(self, exchange_id, timestamp, bid, ask):
        logger = self._get_logger(exchange_id)
        message = "{},{},{}".format(timestamp, bid, ask)
        logger.info(message)

    def _logging_header(self, exchange_id):
        header = 'timestamp,bid,ask'
        logger = self._get_logger(exchange_id)
        logger.info(header)

    def _get_dir_path(self):
        now = datetime.datetime.now()
        now_string = now.strftime("%y%m%d%H%M")
        return os.path.join(common.HISTORICAL_DATA_DIR_PATH, now_string)

    def _get_file_path(self, dir_path, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        return os.path.join(dir_path, file_name)

    def _get_logger_name(self, exchange_id):
        return "{}.historical".format(exchange_id)

    def _create_logger(self, exchange_id):
        file_path = self._get_file_path(self.dir_path, exchange_id)
        logger_name = self._get_logger_name(exchange_id)
        create_historical_logger(file_path, logger_name)

    def _get_logger(self, exchange_id):
        logger_name = self._get_logger_name(exchange_id)
        return getLogger(logger_name)
