import unittest
from unittest.mock import MagicMock

class TestMLTrader(unittest.TestCase):

    def setUp(self):
        self.trader = MLTrader()

    def test_position_sizing(self):
        self.trader.get_cash = MagicMock(return_value=10000)
        self.trader.get_last_price = MagicMock(return_value=200)
        self.trader.calculate_atr = MagicMock(return_value=10)

        cash, last_price, quantity, take_profit, stop_loss = self.trader.position_sizing()

        self.assertEqual(cash, 10000)
        self.assertEqual(last_price, 200)
        self.assertEqual(quantity, 25)
        self.assertEqual(take_profit, 220)
        self.assertEqual(stop_loss, 180)

    def test_get_dates(self):
        self.trader.get_datetime = MagicMock(return_value=pd.Timestamp('2022-01-01'))
        today, three_days_prior = self.trader.get_dates()

        self.assertEqual(today, '2022-01-01')
        self.assertEqual(three_days_prior, '2021-12-29')

    def test_get_sentiment(self):
        self.trader.get_dates = MagicMock(return_value=('2022-01-01', '2021-12-29'))
        self.trader.api.get_news = MagicMock(return_value=['News 1', 'News 2'])
        estimate_sentiment = MagicMock(return_value=(0.8, 'positive'))

        with patch('__main__.estimate_sentiment', estimate_sentiment):
            probability, sentiment = self.trader.get_sentiment()

        self.assertEqual(probability, 0.8)
        self.assertEqual(sentiment, 'positive')

    def test_on_trading_iteration(self):
        self.trader.get_cash = MagicMock(return_value=10000)
        self.trader.get_last_price = MagicMock(return_value=200)
        self.trader.position_sizing = MagicMock(return_value=(10000, 200, 25, 220, 180))
        self.trader.get_sentiment = MagicMock(return_value=(0.8, 'positive'))
        self.trader.last_trade = "sell"
        self.trader.sell_all = MagicMock()
        self.trader.create_order = MagicMock()
        self.trader.submit_order = MagicMock()

        self.trader.on_trading_iteration()

        self.trader.sell_all.assert_called_once()
        self.trader.create_order.assert_called_once_with(
            self.trader.symbol,
            25,
            "buy",
            type="bracket",
            take_profit_price=220,
            stop_loss_price=180
        )
        self.trader.submit_order.assert_called_once()

if __name__ == '__main__':
    unittest.main()