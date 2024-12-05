# import pandas_ta as ta
# import numpy as np
# from datetime import datetime as dttm
from datetime import datetime, timezone
# from time import sleep
import asyncio
from e_bapi import BINANCE_API
# import math
import os
import inspect
current_file = os.path.basename(__file__)

class KlineFetcher(BINANCE_API):
    def __init__(self) -> None:
        super().__init__()
        self.interval_seconds = None
        self.all_active_symbols = []
        self.last_fetch_timestamp = None

        # Декорируем методы с логированием исключений
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")  # Исключаем специальные методы
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

    def interval_to_seconds(self, interval):
        """
        Преобразует строковый интервал Binance в количество секунд.
        """
        mapping = {
            "1m": 60,
            "3m": 180,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "2h": 7200,
            "4h": 14400,
            "1d": 86400,
        }
        return mapping.get(interval, 60)  # По умолчанию "1m"

    def is_new_interval(self):
        """
        Проверяет, появилась ли новая метка времени кратная интервалу.
        """
        if not self.interval_seconds:
            return False
        
        now = datetime.now(timezone.utc)  # Используем объект времени с временной зоной UTC
        current_timestamp = int(now.timestamp())

        # Рассчитываем ближайшую кратную метку времени
        nearest_timestamp = (current_timestamp // self.interval_seconds) * self.interval_seconds

        if self.last_fetch_timestamp is None or nearest_timestamp > self.last_fetch_timestamp:
            self.last_fetch_timestamp = nearest_timestamp
            return True

        return False

    async def fetch_klines_for_symbols(self, session, asset_id, interval=None):
        """
        Асинхронно получает клинья для списка символов с учетом регулярных обновлений.
        """
        symbols = self.cashe_data_book_dict[asset_id].get("symbols")
        indicator_number = self.cashe_data_book_dict[asset_id].get("indicator_number", 1)
        limit = self.cashe_data_book_dict[asset_id][f"indicator_{indicator_number}"].get("bb_period", 50)
        if interval is None:
            interval = self.cashe_data_book_dict[asset_id][f"indicator_{indicator_number}"].get("bb_main_time_frame", None)
    
        async def fetch_kline(symbol, fetch_limit):
            try:
                return symbol, await self.get_klines(session, symbol, interval, fetch_limit)
            except Exception as e:
                print(f"Error fetching klines for {symbol}: {e}")
                return symbol, None

        self.interval_seconds = self.interval_to_seconds(interval)
        # Определяем лимит для загрузки
        fetch_limit = limit if (self.first_iter or self.is_new_interval()) else 1

        # Создаем задачи для всех символов
        tasks = [fetch_kline(symbol, fetch_limit) for symbol in symbols]

        # Выполняем задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обновляем словарь клиний
        for symbol, new_klines in results:
            if new_klines is not None:
                if (self.first_iter or self.is_new_interval()):
                    self.cashe_data_book_dict[asset_id]["klines_data_dict"][symbol] = new_klines
                else:
                    self.cashe_data_book_dict[asset_id]["klines_data_dict"][symbol] = (
                        self.cashe_data_book_dict[asset_id]["klines_data_dict"][symbol][:-1] + new_klines
                    )

class INDICATORS(KlineFetcher):
    def __init__(self) -> None:
        super().__init__()
        self.is_any_signal = False

        # Декорируем методы с логированием исключений
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")  # Исключаем специальные методы
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))
            
    def calculate_bollinger_middle(self, df, bb_period):
        """
        Вычисляет среднюю линию (moving average) для Боллинджера.
        """
        df['bb_middle'] = df['Close'].rolling(window=bb_period).mean()
        return df

    def calculate_bollinger_bands(self, df, bollinger_std, suffix=''):
        """
        Вычисляет верхнюю и нижнюю линии Боллинджера.
        """
        middle_col = 'bb_middle'
        std_col = f'std{suffix}'
        upper_col = f'bb_upper{suffix}'
        lower_col = f'bb_lower{suffix}'

        # Вычисляем стандартное отклонение и линии
        df[std_col] = df['Close'].rolling(window=len(df[middle_col].dropna())).std()
        df[upper_col] = df[middle_col] + (bollinger_std * df[std_col])
        df[lower_col] = df[middle_col] - (bollinger_std * df[std_col])
        return df

    async def calculate_signals(self, df, bb_period=50, basik_std=2, tp_rate=1, sl_rate=1):
        """
        Рассчитывает сигналы Боллинджера.
        """
        # Сначала вычисляем среднюю линию
        df = self.calculate_bollinger_middle(df, bb_period)

        # Основные полосы Боллинджера
        df = self.calculate_bollinger_bands(df, basik_std)

        # Добавляем TP и SL полосы
        if tp_rate is None:
            tp_rate = 1 

        if sl_rate is None:
            sl_rate = 1 

        tp_suffix = f'_tp_{tp_rate}'
        sl_suffix = f'_sl_{sl_rate}'
        df = self.calculate_bollinger_bands(df, basik_std * tp_rate, suffix=tp_suffix)
        df = self.calculate_bollinger_bands(df, basik_std * sl_rate, suffix=sl_suffix)

        # Последние цены
        last_close_price = df["Close"].iloc[-1]
        prelast_close_price = df["Close"].iloc[-2]

        # Основные линии
        signals_dict = {
            "middle_long_cross": (last_close_price > df['bb_middle'].iloc[-1]) and 
                                (prelast_close_price < df['bb_middle'].iloc[-2]),
            "middle_short_cross": (last_close_price < df['bb_middle'].iloc[-1]) and 
                                (prelast_close_price > df['bb_middle'].iloc[-2]),
            "upper_cross": (last_close_price > df[f'bb_upper'].iloc[-1]),
            "lower_cross": (last_close_price < df[f'bb_lower'].iloc[-1]),
            "tp_long": (last_close_price > df[f'bb_upper{tp_suffix}'].iloc[-1]),
            "tp_short": (last_close_price < df[f'bb_lower{tp_suffix}'].iloc[-1]),
            "sl_short": (last_close_price > df[f'bb_upper{sl_suffix}'].iloc[-1]),
            "sl_long": (last_close_price < df[f'bb_lower{sl_suffix}'].iloc[-1]),
        }

        # Проверяем наличие любого сигнала
        async with self.async_lock:
            self.is_any_signal = any(signals_dict.values())

        return signals_dict
    
class Strategies(KlineFetcher):
    def __init__(self) -> None:
        super().__init__()

        # Декорируем методы с логированием исключений
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")  # Исключаем специальные методы
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

    # strategy 2:
    def strategy_1(self, signals_dict, asset_id, token):

        in_position_long = self.cashe_data_book_dict[asset_id][token]["in_position_long"] # long apriory
        in_position_short = self.cashe_data_book_dict[asset_id][token]["in_position_short"] # short apriory

        cur_time = self.get_cur_process_time(self.tz_location)

        if in_position_long:
            if signals_dict["tp_long"]:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по тейк-профиту в плюс. Время: {cur_time}")
                self.cashe_data_book_dict[asset_id][token]["is_closing_long"] = True
            elif signals_dict["sl_long"]:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по стоп-лоссу в минус. Время: {cur_time}")
                self.cashe_data_book_dict[asset_id][token]["is_closing_long"] = True

        if in_position_short:
            if signals_dict["tp_short"]:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по тейк-профиту в плюс. Время: {cur_time}")
                self.cashe_data_book_dict[asset_id][token]["is_closing_short"] = True
            elif signals_dict["sl_short"]:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по стоп-лоссу в минус. Время: {cur_time}")
                self.cashe_data_book_dict[asset_id][token]["is_closing_short"] = True

        if signals_dict["middle_long_cross"] or signals_dict["middle_short_cross"]:
            if not in_position_long:  
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 1. Открываем новую Лонг позицию. Время: {cur_time}")               
                self.cashe_data_book_dict[asset_id][token]["is_opening_long"] = True
            if not in_position_short:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 2. Открываем новую Шорт позицию. Время: {cur_time}") 
                self.cashe_data_book_dict[asset_id][token]["is_opening_short"] = True

    # strategy 2:
    def strategy_2(self, signals_dict, asset_id, token):

        in_position_long = self.cashe_data_book_dict[asset_id][token]["in_position_long"] # long apriory
        in_position_short = self.cashe_data_book_dict[asset_id][token]["in_position_short"] # short apriory

        if in_position_long:
            if signals_dict["tp_long"]:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Закрываем лонг позицию по тейк-профиту в плюс")
                self.cashe_data_book_dict[asset_id][token]["is_closing_long"] = True
            elif signals_dict["sl_long"]:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Закрываем лонг позицию по стоп-лоссу в минус")
                self.cashe_data_book_dict[asset_id][token]["is_closing_long"] = True

        elif in_position_short:
            if signals_dict["tp_short"]:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Закрываем шорт позицию по тейк-профиту в плюс")
                self.cashe_data_book_dict[asset_id][token]["is_closing_short"] = True
            elif signals_dict["sl_short"]:
                self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Закрываем шорт позицию по стоп-лоссу в минус")
                self.cashe_data_book_dict[asset_id][token]["is_closing_short"] = True

        else:
            if signals_dict["lower_cross"]:
                if not in_position_long:  
                    self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Открываем новую Лонг позицию.")               
                    self.cashe_data_book_dict[asset_id][token]["is_opening_long"] = True
            elif signals_dict["upper_cross"]:
                if not in_position_short:
                    self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Открываем новую Шорт позицию.") 
                    self.cashe_data_book_dict[asset_id][token]["is_opening_short"] = True

