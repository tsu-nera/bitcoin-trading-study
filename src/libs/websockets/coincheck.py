import socketio

from src.libs.websockets.websocket_client_base import WebsocketClientBase
from src.constants.wsconst import SOCKETIO_URL_COINCHECK, WsDataOrderbook, WsDataTrade


class WebsocketClientCoincheck(WebsocketClientBase):
    def __init__(self, queue, symbol):
        self.queue = queue
        self.symbol = symbol

        self.sio = socketio.Client()

        self.PAIR = self._build_pair(symbol)
        self.CHANNEL_ORDERBOOK = "{}-orderbook".format(self.PAIR)
        self.CHANNEL_TRADES = "{}-trades".format(self.PAIR)

        self.__connect()

    def __connect(self):
        self.sio.on('connect', self.__on_connect)
        self.sio.on('trades', self.__on_trades)
        self.sio.on('orderbook', self.__on_orderbook)
        self.sio.connect(SOCKETIO_URL_COINCHECK,
                         transports=['polling'],
                         socketio_path='socket.io')

    def __on_orderbook(self, data):
        orderbook = WsDataOrderbook(data[1]["bids"], data[1]["asks"])
        self.queue.put(orderbook)

    def __on_trades(self, data):
        trade = WsDataTrade(float(data[2]), float(data[3]), data[4])
        self.queue.put(trade)

    def __on_connect(self):
        self.sio.emit('subscribe', self.CHANNEL_ORDERBOOK)
        self.sio.emit('subscribe', self.CHANNEL_TRADES)

    def fetch_ticks(self):
        self.sio.wait()
