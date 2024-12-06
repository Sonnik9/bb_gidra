import asyncio
import aiohttp
from datetime import datetime
# from statistics import mean
import aiohttp
# from functools import wraps
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


# def aiohttp_connector(func):
#     @wraps(func)
#     async def wrapper(self, *args, **kwargs):
#         async with aiohttp.ClientSession() as session:
#             try:
#                 return await func(self, session, *args, **kwargs)
#             except Exception as ex:
#                 print(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")
#     return wrapper

async def open_session(session=None, timeout=10):
    """
    Открытие aiohttp сессии с таймаутом.
    
    :param session: Существующая сессия или None.
    :param timeout: Время в секундах до таймаута для открытия сессии (по умолчанию 10 секунд).
    """
    if not session:
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            session = aiohttp.ClientSession(timeout=timeout_obj)
        except asyncio.TimeoutError:
            print(f"Ошибка: Таймаут при открытии сессии. Таймаут: {timeout} секунд.")
            raise
    return session

async def close_session(session=None, timeout=5):
    """
    Закрытие aiohttp сессии с таймаутом.
    
    :param session: Сессия для закрытия.
    :param timeout: Время в секундах до таймаута для закрытия сессии (по умолчанию 5 секунд).
    """
    if session:
        try:
            await asyncio.wait_for(session.close(), timeout=timeout)
        except asyncio.TimeoutError:
            print(f"Ошибка: Таймаут при закрытии сессии. Таймаут: {timeout} секунд.")
            # Здесь можно выполнить дополнительные действия, например, принудительно закрыть сессию.
        finally:
            session = None
    return None

class MainLogic(TEMP):
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


    # async def _run(self):
    #     """Основной цикл выполнения."""
    #     if self.is_bible_quotes_introduction:
    #         print(f"\n{generate_bible_quote()}")

    #     session = None
    #     tik_counter = 0           

    #     while not self.stop_bot:
    #         try:
    #             print("tik")
    #             tik_counter += 1
    #             if tik_counter == 10 or self.first_iter:
    #                 session = await open_session(session)
    #                 # print(session)
    #                 if self.first_iter:
    #                     print("Проверка новых сообщений...")
    #                     await self.cache_trade_data(session)
    #                     await self.hedg_temp(session)  

    #             trades = await self.process_signals(session) or []
    #             # print(messages)
    #             # if trades:                    
    #             #     results_order = await self.place_orders_gather(session, trades)
    #             #     if results_order:
    #             #         for item_response in results_order:
    #             #             order_resp, asset_id, symbol, side = item_response
    #             #             await self.process_order_temp(order_resp, asset_id, symbol, side)
    #             #     # print(f"Результаты ордеров: {results_order}")                

    #         except Exception as e:
    #             self.log_error_loger(f"Ошибка в {os.path.basename(__file__)}: {e}", True)

    #         finally:                
    #             if tik_counter == 10:

    #                 # Кешируем данные
    #                 await self.cache_trade_data(session)                    

    #                 # Логируем после выполнения
    #                 self.write_logs()
    #                 tik_counter = 0

    #                 session = await close_session(session)

    #             self.first_iter = False
    #             return

    #             # Пауза перед следующей итерацией
    #             await asyncio.sleep(self.inspection_time_frame)

    async def start(self):
        """Инициализация и запуск логики."""
        print("Инструкция в README.md. Настройки — в settings.json.")
        print("Текущие настройки: ")
        self.display_settings()
        print()
        await self._run()

async def main():
    """Точка входа."""
    instance = MainLogic()
    await instance.start()

if __name__ == "__main__":
    asyncio.run(main())