from datetime import datetime, timezone
# import math
import pytz
from c_log import Requests_Logger
import os
import inspect

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
                        
    # def get_current_ms_utc_time(self):
    #     return int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    
    def get_date_time_now(self, tz_location):
        now = datetime.now(tz_location)
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def milliseconds_to_datetime(self, milliseconds, tz_location):
        seconds = milliseconds / 1000
        dt = datetime.fromtimestamp(seconds, pytz.utc).astimezone(tz_location)
        return dt.strftime("%Y-%m-%d %H:%M:%S") + f".{int(milliseconds % 1000):03d}"

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
    
    def get_qty_precisions(self, symbol_info, symbol):
        
        symbol_data = next((item for item in symbol_info["symbols"] if item['symbol'] == symbol), None)
        if not symbol_data:
            return

        quantity_precision = int(float(symbol_data['quantityPrecision']))
        # price_precision_market = int(float(symbol_data['pricePrecision']))

        return quantity_precision
        
    def usdt_to_qnt_converter(self, depo, cur_price, quantity_precision):
        return round(depo / cur_price, quantity_precision)
    
# import pytz
# print(UTILS().get_cur_process_time(pytz.timezone("Europe/Berlin")))
