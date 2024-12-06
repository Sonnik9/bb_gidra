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

    def process_signals(self):
        """Ищем торговые сигналы и интегрируем их в структуру данных."""
        # symbols = self.cashe_data_book_dict[asset_id].get("symbols")
        # indicator_number = self.cashe_data_book_dict[asset_id].get("indicator_number", 1)
        # limit = self.cashe_data_book_dict[asset_id][f"indicator_{indicator_number}"].get("bb_period", 50)
        # if interval is None:
        #     interval = self.cashe_data_book_dict[asset_id][f"indicator_{indicator_number}"].get("bb_main_time_frame", None)
    
        # self.interval_seconds = self.interval_to_seconds(interval)
        # # Определяем лимит для загрузки
        # fetch_limit = limit if (self.first_iter or self.is_new_interval()) else 1

        # asset_id, symbol, margin_type, leverage, qty, side, position_side, api_key, api_secret = trade.get("asset_id"), trade.get("symbol"), trade.get("margin_type"), trade.get("leverage"), trade.get("qty"), trade.get("side"), trade.get("position_side"), trade.get("api_key"), trade.get("api_secret")

        return []

    async def _run(self):
        """Основной цикл выполнения."""
        if self.is_bible_quotes_introduction:
            print(f"\n{generate_bible_quote()}")

        session = None              

        while not self.stop_bot:
            try:
                session = await open_session(session)
                # print(session)
                if self.first_iter:
                    print("Проверка новых сообщений...")
                    await self.cache_trade_data(session)
                    await self.hedg_temp(session)  

                trades = await self.process_signals() or []
                # print(messages)
                if trades:                    
                    results_order = await self.place_orders_gather(session, trades)
                    if results_order:
                        for item_response in results_order:
                            order_resp, asset_id, symbol = item_response
                            await self.process_order_temp(order_resp, asset_id, symbol)
                    # print(f"Результаты ордеров: {results_order}")

                self.first_iter = False

            except Exception as e:
                self.log_error_loger(f"Ошибка в {os.path.basename(__file__)}: {e}", True)

            finally:                
                # Кешируем данные
                await self.cache_trade_data(session)

                # Логируем после выполнения
                self.write_logs()

                session = await close_session(session)

                # Пауза перед следующей итерацией
                await asyncio.sleep(self.inspection_interval)

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