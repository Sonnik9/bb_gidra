import time
from datetime import datetime as dttm
import math
from c_log import Requests_Logger
import os
import inspect

current_file = os.path.basename(__file__)

class UTILS(Requests_Logger):
    def __init__(self):  
        super().__init__()
        # Декорируем методы с логированием исключений
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")  # Исключаем специальные методы
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))
                        
    def milliseconds_to_datetime(self, milliseconds):
        seconds, milliseconds = divmod(milliseconds, 1000)
        time = dttm.utcfromtimestamp(seconds)
        return time.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_cur_process_time(self, local_tz) -> str:
        now_time = dttm.now(local_tz)
        return now_time.strftime('%Y-%m-%d %H:%M:%S')    
  
    def time_signal_info(self, signal, symbol, cur_price):
        ssignal_time = self.get_cur_process_time()
        signal_mess = 'LONG' if signal == 1 else 'SHORT'
        print(f"Сигнал: {signal_mess}. Монета: {symbol}. Время сигнала: {ssignal_time}. Текущая цена: {cur_price}")

    def time_calibrator(self, kline_time: int, time_frame: str):
        current_time = time.time()
        
        # Преобразуем таймфрейм в секунды
        time_in_seconds = {
            'm': 60,
            'h': 3600,
            'd': 86400
        }.get(time_frame, 0) * kline_time

        if time_in_seconds == 0:
            raise ValueError("Unsupported time frame. Use 'm', 'h', or 'd'.")
        
        # Рассчитываем интервал для ожидания до следующего значения
        next_interval = math.ceil(current_time / time_in_seconds) * time_in_seconds
        wait_time = next_interval - current_time

        # Определяем специальные интервалы ожидания
        special_intervals = {
            ('m', 15): 300, # 5 min
            ('m', 30): 300,
            ('h', 1): 300,
            ('h', 4): 900, # 15 min
            ('h', 6): 900,
            ('h', 12): 900,
            ('d', kline_time): 900
        }

        # Рассчитываем второй интервал ожидания (wait_time_2) для специальных временных интервалов
        special_seconds = special_intervals.get((time_frame, kline_time), 0)

        if special_seconds:
            next_interval_2 = math.ceil(current_time / special_seconds) * special_seconds
            wait_time_2 = next_interval_2 - current_time
        else:
            wait_time_2 = wait_time
        
        return int(wait_time) + 1, int(wait_time_2) + 1
    
    def get_qty_precisions(self, symbol_info, symbol):
        
        symbol_data = next((item for item in symbol_info["symbols"] if item['symbol'] == symbol), None)
        if not symbol_data:
            return

        quantity_precision = int(float(symbol_data['quantityPrecision']))
        price_precision_market = int(float(symbol_data['pricePrecision']))

        return quantity_precision, price_precision_market
        
    def usdt_to_qnt_converter(self, depo, cur_price, quantity_precision):
        return round(depo / cur_price, quantity_precision)
    
# import pytz
# print(UTILS().get_cur_process_time(pytz.timezone("Europe/Berlin")))
