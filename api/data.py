import time
import logging
import multitasking
from dataclasses import dataclass, field
from typing import List
from config.matrix_config import MatrixConfig
from data.crypto import Crypto
from data.stock import Stock
from data.ticker import Ticker
from data.status import Status
from constants import DATE_FORMAT, UPDATE_RATE


@dataclass
class Data:
    config: MatrixConfig
    date: str = None
    time: str = None
    time_format: str = field(init=False)
    cryptos: List[Ticker] = None
    stocks: List[Ticker] = None
    valid_tickers: int = field(init=False)
    status: Status = Status.SUCCESS
    last_updated: float = None

    def __post_init__(self):
        self.time_format = self.config.time_format
        self.valid_tickers = len(self.config.stocks + self.config.cryptos)

        threads = min([self.valid_tickers, multitasking.cpu_count() * 2])
        multitasking.set_max_threads(threads)

        self.initialize()

    def initialize(self) -> Status:
        """
        Initialize Ticker instances, and append those which are valid to tickers list.
        :return: status: (data.Status) Update status
        :exception Timeout: If the request timed out
        """
        logging.info('Initializing data...')

        for stock in self.config.stocks:  # Initialize stocks
            self.fetch_stock(stock, self.config.currency)
        for crypto in self.config.cryptos:  # Initialize cryptos
            self.fetch_crypto(crypto, self.config.currency)
        # Wait until all tickers are initialized
        while len(self.stocks + self.cryptos) < self.valid_tickers:
            time.sleep(0.1)

        self.date = self.get_date()
        self.time = self.get_time()
        return Status.SUCCESS

    def update(self) -> Status:
        """
        Update tickers' prices, date, and time.
        :return: status: (data.Status) Update status
        """
        for ticker in self.stocks + self.cryptos:
            self.update_ticker(ticker)
        self.last_updated = time.time()

        return Status.SUCCESS

    def update_clock(self):
        """Update date & time"""
        self.date = self.get_date()
        self.time = self.get_time()

    @multitasking.task
    def fetch_stock(self, symbol: str, currency: str):
        """
        Fetch stock's data
        :param symbol: (str) Stock symbol
        :param currency: (str) Stock's prices currency
        """
        stock = Stock(symbol, currency)
        self.stocks.append(stock) if stock.valid else self.valid_tickers -= 1

    @multitasking.task
    def fetch_crypto(self, symbol: str, currency: str):
        """
        Fetch crypto's data
        :param symbol: (str) Crypto symbol
        :param currency: (str) Crypto's prices currency
        """
        crypto = Crypto(symbol, currency)
        self.cryptos.append(crypto) if crypto.valid else self.valid_tickers -= 1

    @multitasking.task
    def update_ticker(self, ticker: Ticker):
        """
        Update ticker's data
        :param ticker: (data.Ticker) Ticker object to update
        """
        ticker.update()

    def get_time(self) -> str:
        """
        Get current time as a string
        :return: time: (str) Current time
        """
        return time.strftime(self.time_format)

    @staticmethod
    def get_date() -> str:
        """
        Get current date as a string
        :return: date: (str) Current date
        """
        return time.strftime(DATE_FORMAT)

    def should_update(self) -> bool:
        """
        Returns Boolean value to determine if tickers should be updated.
        i.e. If 10 minutes have passed since data was last fetched, an update is needed.
        :return: should_update: (bool)
        """
        logging.info('Checking for update')
        time_delta = time.time() - self.last_updated
        return time_delta >= UPDATE_RATE