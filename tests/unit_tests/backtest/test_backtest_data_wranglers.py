# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2021 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

import pytest

from nautilus_trader.backtest.data.wranglers import BarDataWrangler
from nautilus_trader.backtest.data.wranglers import QuoteTickDataWrangler
from nautilus_trader.backtest.data.wranglers import TradeTickDataWrangler
from nautilus_trader.common.clock import TestClock
from nautilus_trader.model.enums import AggressorSide
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from tests.test_kit.providers import TestDataProvider
from tests.test_kit.providers import TestInstrumentProvider
from tests.test_kit.stubs import TestStubs


AUDUSD_SIM = TestStubs.audusd_id()


class TestQuoteTickDataWrangler:
    def setup(self):
        # Fixture Setup
        self.clock = TestClock()

    def test_tick_data(self):
        # Arrange, Act
        ticks = TestDataProvider.usdjpy_ticks()

        # Assert
        assert len(ticks) == 1000

    def test_process_tick_data(self):
        # Arrange
        usdjpy = TestInstrumentProvider.default_fx_ccy("USD/JPY")

        wrangler = QuoteTickDataWrangler(instrument=usdjpy)

        # Act
        ticks = wrangler.process(
            data=TestDataProvider.usdjpy_ticks(),
            default_volume=1000000,
        )

        # Assert
        assert len(ticks) == 1000
        assert ticks[0].instrument_id == usdjpy.id
        assert ticks[0].bid == Price.from_str("86.655")
        assert ticks[0].ask == Price.from_str("86.728")
        assert ticks[0].bid_size == Quantity.from_int(1000000)
        assert ticks[0].ask_size == Quantity.from_int(1000000)
        assert ticks[0].ts_event == 1357077600295000064

    def test_pre_process_with_bar_data(self):
        # Arrange
        usdjpy = TestInstrumentProvider.default_fx_ccy("USD/JPY")
        bid_data = TestDataProvider.usdjpy_1min_bid()[:100]
        ask_data = TestDataProvider.usdjpy_1min_ask()[:100]

        wrangler = QuoteTickDataWrangler(instrument=usdjpy)

        # Act
        ticks = wrangler.process_bar_data(
            bid_data=bid_data,
            ask_data=ask_data,
            default_volume=1000000,
        )

        # Assert
        assert len(ticks) == 400
        assert ticks[0].instrument_id == usdjpy.id
        assert ticks[0].bid == Price.from_str("91.715")
        assert ticks[0].ask == Price.from_str("91.717")
        assert ticks[0].bid_size == Quantity.from_int(1000000)
        assert ticks[0].ask_size == Quantity.from_int(1000000)
        assert ticks[0].ts_event == 1359676799700000000


class TestTradeTickDataWrangler:
    def setup(self):
        # Fixture Setup
        self.clock = TestClock()

    def test_tick_data(self):
        # Arrange, Act
        ticks = TestDataProvider.ethusdt_trades()[:100]

        # Assert
        assert len(ticks) == 100

    def test_process(self):
        # Arrange
        ethusdt = TestInstrumentProvider.ethusdt_binance()
        wrangler = TradeTickDataWrangler(instrument=ethusdt)

        # Act
        ticks = wrangler.process(TestDataProvider.ethusdt_trades()[:100])

        # Assert
        assert len(ticks) == 100
        assert ticks[0].price == Price.from_str("423.760")
        assert ticks[0].size == Quantity.from_str("2.67900")
        assert ticks[0].aggressor_side == AggressorSide.SELL
        assert ticks[0].match_id == "148568980"
        assert ticks[0].ts_init == 1597399200223000064


class TestBarDataWrangler:
    def setup(self):
        # Fixture Setup
        instrument = TestInstrumentProvider.default_fx_ccy("GBP/USD")
        bar_type = TestStubs.bartype_gbpusd_1min_bid()
        self.wrangler = BarDataWrangler(
            bar_type=bar_type,
            instrument=instrument,
        )

    def test_process(self):
        # Arrange, Act
        bars = self.wrangler.process(TestDataProvider.gbpusd_1min_bid()[:1000])

        # Assert
        assert len(bars) == 1000
        assert bars[0].open == Price.from_str("1.57597")
        assert bars[0].high == Price.from_str("1.57606")
        assert bars[0].low == Price.from_str("1.57576")
        assert bars[0].close == Price.from_str("1.57576")
        assert bars[0].volume == Quantity.from_int(1000000)

    def test_process_with_default_volume(self):
        # Arrange, Act
        bars = self.wrangler.process(
            data=TestDataProvider.gbpusd_1min_bid()[:1000],
            default_volume=10,
        )

        # Assert
        assert len(bars) == 1000
        assert bars[0].open == Price.from_str("1.57597")
        assert bars[0].high == Price.from_str("1.57606")
        assert bars[0].low == Price.from_str("1.57576")
        assert bars[0].close == Price.from_str("1.57576")
        assert bars[0].volume == Quantity.from_int(10)  # <-- default volume


@pytest.mark.skip(reason="WIP")
class TestTardisQuoteDataWrangler:
    def setup(self):
        # Fixture Setup
        self.clock = TestClock()

    def test_tick_data(self):
        # Arrange, Act
        ticks = TestDataProvider.tardis_quotes()

        # Assert
        assert len(ticks) == 9999

    def test_pre_process_with_tick_data(self):
        # Arrange
        instrument = TestInstrumentProvider.btcusdt_binance()
        wrangler = QuoteTickDataWrangler(instrument=instrument)

        print(TestDataProvider.tardis_quotes())
        # Act
        ticks = wrangler.process(TestDataProvider.tardis_quotes())

        # Assert
        assert len(ticks) == 9999
        # assert ticks[0].ts_event == 0
        # assert ticks[0].bid_size == "0.670000"
        # assert ticks[0].ask_size == "0.840000"
        # assert ticks[0].bid == "9681.92"
        # assert ticks[0].ask == "9682.00"


class TestTardisTradeDataWrangler:
    def setup(self):
        # Fixture Setup
        self.clock = TestClock()

    def test_tick_data(self):
        # Arrange, Act
        ticks = TestDataProvider.tardis_trades()

        # Assert
        assert len(ticks) == 9999

    def test_process(self):
        # Arrange
        instrument = TestInstrumentProvider.btcusdt_binance()
        wrangler = TradeTickDataWrangler(instrument=instrument)

        # Act
        ticks = wrangler.process(TestDataProvider.tardis_trades())

        # Assert
        assert len(ticks) == 9999
        assert ticks[0].price == Price.from_str("9682.00")
        assert ticks[0].size == Quantity.from_str("0.132000")
        assert ticks[0].aggressor_side == AggressorSide.BUY
        assert ticks[0].match_id == "42377944"
        assert ticks[0].ts_init == 1582329602418379008
