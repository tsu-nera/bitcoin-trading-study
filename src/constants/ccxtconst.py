import src.env as env

EXCHANGE_ID_BITFLYER = "bitflyer"
EXCHANGE_ID_COINCHECK = "coincheck"
EXCHANGE_ID_LIQUID = "liquid"

SYMBOL_BTC_JPY = "BTC/JPY"

API_KEY = "apiKey"
API_SECRET = "apiSecret"

EXCHANGE_AUTH_DICT = {
    EXCHANGE_ID_BITFLYER: {
        API_KEY: env.BITFLYER_API_KEY,
        API_SECRET: env.BITFLYER_API_SECRET
    },
    EXCHANGE_ID_COINCHECK: {
        API_KEY: env.COINCHECK_API_KEY,
        API_SECRET: env.COINCHECK_API_SECRET
    }
}
