import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

BITFLYER_API_KEY = os.environ.get("BITFLYER_API_KEY")
BITFLYER_API_SECRET = os.environ.get("BITFLYER_API_SECRET")
COINCHECK_API_KEY = os.environ.get("COINCHECK_API_KEY")
COINCHECK_API_SECRET = os.environ.get("COINCHECK_API_SECRET")
LIQUID_API_KEY = os.environ.get("LIQUID_API_KEY")
LIQUID_API_SECRET = os.environ.get("LIQUID_API_SECRET")
BITBANK_API_KEY = os.environ.get("BITBANK_API_KEY")
BITBANK_API_SECRET = os.environ.get("BITBANK_API_SECRET")
BITMEX_API_KEY = os.environ.get("BITMEX_API_KEY")
BITMEX_API_SECRET = os.environ.get("BITMEX_API_SECRET")
BITMEX_TESTNET_API_KEY = os.environ.get("BITMEX_TESTNET_API_KEY")
BITMEX_TESTNET_API_SECRET = os.environ.get("BITMEX_TESTNET_API_SECRET")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_SECRET = os.environ.get("GEMINI_API_SECRET")
GEMINI_SANDBOX_API_KEY = os.environ.get("GEMINI_SANDBOX_API_KEY")
GEMINI_SANDBOX_API_SECRET = os.environ.get("GEMINI_SANDBOX_API_SECRET")

SLACK_WEBHOOK_URL_TRADE = os.environ.get("SLACK_WEBHOOK_URL_TRADE")
SLACK_WEBHOOK_URL_ASSET = os.environ.get("SLACK_WEBHOOK_URL_ASSET")
SLACK_WEBHOOK_URL_ERROR = os.environ.get("SLACK_WEBHOOK_URL_ERROR")
