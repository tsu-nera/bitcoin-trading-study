from abc import ABCMeta, abstractmethod
from src.core.arbitrage_analyzer import ArbitrageAnalyzer


class ArbitrageBase(metaclass=ABCMeta):
    STRATEGY_BUY_X_AND_SELL_Y = "buy x and sell y"
    STRATEGY_BUY_Y_AND_SELL_X = "buy y and sell x"
    STRATEGY_DO_NOTHING = "no strategy"
    ACTION_OPEN = "OPEN"
    ACTION_CLOSE = "CLOSE"

    def __init__(self):
        self._closing()
        self.analyzer = ArbitrageAnalyzer()
        self.opened = False

    @abstractmethod
    def run(self):
        pass

    def next(self):
        # tick取得
        x, y = self._get_tick()

        if x and y:
            # 判定
            result = self._evaluate(x, y)

            # アクション
            self._action(result, x, y)

    @abstractmethod
    def _get_tick(self):
        pass

    def _evaluate(self, x, y):
        self.analyzer.update(y.bid - x.ask, x.bid - y.ask)
        if self.analyzer.check_period():
            self.open_threshold = self.analyzer.get_new_open_threshold()
            self.analyzer.reset()

        if self._check_status_buyx_selly(y.bid, x.ask):
            return self.STRATEGY_BUY_X_AND_SELL_Y
        elif self._check_status_buyy_sellx(x.bid, y.ask):
            return self.STRATEGY_BUY_Y_AND_SELL_X
        else:
            return self.STRATEGY_DO_NOTHING

    @abstractmethod
    def _action(self, result, x, y):
        pass

    def _get_profit_margin(self, bid, ask):
        return int(bid - ask)

    def _update_entry_open_margin(self, value):
        if not self.opened:
            self.entry_open_margin = value
        else:
            self.entry_open_margin = None

    def _check_opening_threshold(self, bid, ask):
        profit_margin = self._get_profit_margin(bid, ask)
        return profit_margin > self.open_threshold

    def _get_close_threshold(self):
        return self.profit_margin_diff - max(self.entry_open_margin,
                                             self.open_threshold)

    def _check_closeing_threshold(self, bid, ask):
        profit_margin = self._get_profit_margin(bid, ask)
        close_threshold = self._get_close_threshold()
        return profit_margin > close_threshold

    def _check_status_buyx_selly(self, bid, ask):
        if not self.opened:
            return self._check_opening_threshold(bid, ask)
        else:
            if self._check_closeing_threshold(bid, ask):
                return self.open_direction
            else:
                return False

    def _check_status_buyy_sellx(self, bid, ask):
        if not self.opened:
            return self._check_opening_threshold(bid, ask)
        else:
            if self._check_closeing_threshold(bid, ask):
                return not self.open_direction
            else:
                return False

    def _change_status_buyx_selly(self):
        if not self.opened:
            self._opening_buyy_sellx()
        else:
            self._closing()

    def _change_status_buyy_sellx(self):
        if not self.opened:
            self._opening_buyx_selly()
        else:
            self._closing()

    def _closing(self):
        self.opened = False
        self.open_direction = None

    def _opening_buyx_selly(self):
        self.opened = True
        self.open_direction = True

    def _opening_buyy_sellx(self):
        self.opened = True
        self.open_direction = False
