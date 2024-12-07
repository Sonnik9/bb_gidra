import asyncio
import aiohttp
from datetime import datetime
import aiohttp
# import math
from i_templates import TEMP
import os
import inspect

def generate_bible_quote():
    random_bible_list = [
        "<<Благодать Господа нашего Иисуса Христа, и любовь Бога Отца, и общение Святаго Духа со всеми вами. Аминь.>>\n___(2-е Коринфянам 13:13)___",
        "<<Притом знаем, что любящим Бога, призванным по Его изволению, все содействует ко благу.>>\n___(Римлянам 8:28)___",
        "<<Спокойно ложусь я и сплю, ибо Ты, Господи, един даешь мне жить в безопасности.>>\n___(Пс 4:9)___"
    ]
    
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return random_bible_list[0]
    elif 12 <= current_hour < 23:
        return random_bible_list[1]
    return random_bible_list[2]

class COInN_FILTER(TEMP):
    def __init__(self):
        super().__init__()
        self._decorate_methods_with_logging()

    def _decorate_methods_with_logging(self):
        """Оборачивает методы в декоратор логирования исключений."""
        methods = [
            name for name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not name.startswith("__")
        ]
        for method_name in methods:
            original_method = getattr(self, method_name)
            setattr(self, method_name, self.log_exceptions_decorator(original_method))

    async def top_coins_request(self, session, limit):
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.CoinMarketCup_Api_Token,
        }
        params = {
            'start': '1',
            'limit': limit,
            'convert': 'USD',
        }

        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('data', [])
            return []

    async def coin_market_cup_top(self, session, limit):
        top_coins_total_list = []
        top_coins = await self.top_coins_request(session, limit)
        
        if top_coins:
            for coin in top_coins:
                symbol = coin.get('symbol', '')
                if symbol:
                    top_coins_total_list.append(f"{symbol}USDT")
            return top_coins_total_list
        return []

    async def go_filter(self, all_binance_tickers, coinsMarket_tickers, is_coinMarketCup):
        """Фильтрация тикеров, соответствующих условиям по объёму в USDT."""
        exclusion_contains_list = ['UP', 'DOWN', 'RUB', 'EUR']

        # Фильтрация тикеров
        def is_valid_ticker(ticker) -> bool:
            symbol = ticker['symbol'].upper()

            # Условия для отбора
            is_usdt_pair = symbol.endswith('USDT')
            no_exclusions = all(exclusion not in symbol for exclusion in exclusion_contains_list)

            # Проверяем объём в USDT
            try:
                quote_volume = float(ticker.get('quoteVolume', 0))
            except ValueError:
                return False

            sufficient_volume = quote_volume >= self.MIN_VOLUM_USDT

            # Учет CoinMarketCap
            if is_coinMarketCup:
                return is_usdt_pair and no_exclusions and sufficient_volume and symbol in coinsMarket_tickers
            return is_usdt_pair and no_exclusions and sufficient_volume

        # Применяем фильтр
        filtered_tickers = [ticker['symbol'] for ticker in all_binance_tickers if is_valid_ticker(ticker)]

        return filtered_tickers
    
    async def get_top_coins_template(self, session, coinMarketCup_cup_slice=200, is_coinMarketCup=True):
        all_binance_tickers = await self.get_all_tickers(session) 
        coinsMarket_tickers = await self.coin_market_cup_top(session, coinMarketCup_cup_slice) if is_coinMarketCup else []

        # Фильтрация тикеров
        total_coin_list = await self.go_filter(all_binance_tickers, coinsMarket_tickers, is_coinMarketCup)

        return total_coin_list

class MainLogic(COInN_FILTER):
    """Главный класс логики."""

    def __init__(self):
        super().__init__()
        self._decorate_methods_with_logging()

    def _decorate_methods_with_logging(self):
        """Оборачивает методы в декоратор логирования исключений."""
        methods = [
            name for name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not name.startswith("__")
        ]
        for method_name in methods:
            original_method = getattr(self, method_name)
            setattr(self, method_name, self.log_exceptions_decorator(original_method))

    async def process_signals(self, session):
        """Ищем торговые сигналы и интегрируем их в структуру данных."""
        trades = []

        for asset_id, asset in self.assets_dict.items():
            symbols = [self.hot_symbols[asset_id]] if self.hot_symbols[asset_id] else asset.get('symbols', [])
            api_key, api_secret = asset.get("BINANCE_API_PUBLIC_KEY"), asset.get("BINANCE_API_PRIVATE_KEY")
            indicator_number = asset.get("indicator_number")
            indicator_config = asset.get(f"indicator_{indicator_number}", {})
            
            time_frame = indicator_config.get("tfr_main")
            fetch_limit = indicator_config.get("bb_period")
            std_rate = indicator_config.get("std_rate")
            
            if not self.time_frame_seconds:
                self.time_frame_seconds = self.interval_to_seconds("1m")

            fetch_klines_limit = fetch_limit if self.is_new_interval() else 1
            await self.fetch_klines_for_symbols(session, asset_id, symbols, time_frame, fetch_klines_limit, api_key)

            for symbol in symbols:
                try:
                    tp_rate = self.cashe_data_book_dict[asset_id][symbol]["tp_rate"]
                    sl_rate = self.cashe_data_book_dict[asset_id][symbol]["sl_rate"]
                    df = self.klines_data_dict[asset_id].get(symbol)

                    if df is None or df.empty:
                        self.log_error_loger(f"Нет данных свечей для {symbol}, asset_id: {asset_id}")
                        continue

                    signals_dict = await self.calculate_signals(df, indicator_number, fetch_limit, std_rate, sl_rate, tp_rate)
                    await self.strategy_executer(indicator_number, signals_dict, asset_id, symbol)

                except KeyError as e:
                    self.log_error_loger(f"Ошибка обработки {symbol}: {e}")
                    continue

            async with self.async_lock:
                if not self.is_any_signal:
                    continue

                hot_symbol = self.hot_symbols[asset_id]
                if not hot_symbol:
                    continue

                position_data = self.cashe_data_book_dict[asset_id][hot_symbol]
                margin_type = asset.get("margin_type")
                leverage = asset.get("leverage")

                for pos_side, actions in (("LONG", ("is_opening", "is_closing")), 
                                        ("SHORT", ("is_opening", "is_closing"))):
                    if position_data[pos_side][actions[0]]:
                        side, action = ("BUY", "Opening") if pos_side == "LONG" else ("SELL", "Opening")
                    elif position_data[pos_side][actions[1]]:
                        side, action = ("SELL", "Closing") if pos_side == "LONG" else ("BUY", "Closing")
                    else:
                        continue

                    trade_qty = 0.0
                    if action == "Opening" and hot_symbol not in self.busy_symbols_set:
                        precision = position_data["qty_precision"]
                        depo = asset.get("depo")
                        cur_price = self.klines_data_dict[asset_id][hot_symbol]["Close"].iloc[-1]
                        trade_qty = self.usdt_to_qnt_converter(depo, cur_price, precision)
                    elif action == "Closing":
                        trade_qty = position_data[pos_side].get("comul_qty", 0.0)

                    if trade_qty:
                        trades.append({
                            "asset_id": asset_id,
                            "symbol": hot_symbol,
                            "margin_type": margin_type,
                            "leverage": leverage,
                            "api_key": api_key,
                            "api_secret": api_secret,
                            "side": side,
                            "position_side": pos_side,
                            "qty": trade_qty
                        })
                    else:
                        self.log_error_loger(f"Ошибка расчета объема для {hot_symbol}, asset_id: {asset_id}")

        self.is_any_signal = False
        return trades

    async def _run(self):
        """Основной цикл выполнения."""
        if self.is_bible_quotes_introduction:
            print(f"\n{generate_bible_quote()}")

        tik_counter = 0           

        async with aiohttp.ClientSession() as session:
            # print(await self.get_top_coins_template(session))
            # return
            while not self.stop_bot:
                try:
                    print("tik")
                    tik_counter += 1

                    if self.first_iter:
                        print("Проверка новых сообщений...")
                        await self.cache_trade_data(session)
                        await self.hedg_temp(session)

                    trades = await self.process_signals(session) or []
                    trades = [trd for trd in trades if trd]

                    if trades:                    
                        results_order = await self.place_orders_gather(session, trades)
                        if results_order:
                            for item_response in results_order:
                                order_resp, asset_id, symbol, side = item_response
                                await self.process_order_temp(order_resp, asset_id, symbol, side)
                        # print(f"Результаты ордеров: {results_order}")  

                except Exception as e:
                    self.log_error_loger(f"Ошибка в {os.path.basename(__file__)}: {e}", True)

                finally:
                    if tik_counter == 10:
                        # Кешируем данные
                        await self.cache_trade_data(session)

                        # Логируем после выполнения
                        self.write_logs()
                        tik_counter = 0

                    self.first_iter = False

                # Пауза перед следующей итерацией
                await asyncio.sleep(self.inspection_interval)
            self.log_info_loger("Бот завершил работу.", True)

    async def start(self):
        """Инициализация и запуск логики."""
        print("Запуск программы. Подробная инструкция доступна в файле README.md.")
        print("Используемые настройки:")
        self.display_settings()
        print("\nИнициализация завершена.\n")
        await self._run()        

async def main():
    """Точка входа."""
    instance = MainLogic()
    await instance.start()   

if __name__ == "__main__":
    asyncio.run(main())