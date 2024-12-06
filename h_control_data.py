import json
from collections import deque
from g_strategies import Strategiess
import os
import inspect

# Файлы логов
LOG_ERROR_FILE = "log_error.txt"
LOG_INFO_FILE = "log_info.txt"
LOG_ERROR_ORDERS_FILE = "log_error_orders.txt"
LOG_SUCCESS_ORDERS_FILE = "log_succ_orders.txt"

class DataController(Strategiess):
    def __init__(self):
        super().__init__()
     
        # Декорируем методы с логированием исключений
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

    def write_logs(self):
        """Записывает логи в файлы и очищает соответствующие списки."""
        logs = [
            (self.general_error_logger_list, LOG_ERROR_FILE),
            (self.log_info_list, LOG_INFO_FILE),
            (self.log_error_order_list, LOG_ERROR_ORDERS_FILE),
            (self.log_succ_order_list, LOG_SUCCESS_ORDERS_FILE),
        ]

        for log_list, file_name in logs:
            if not log_list:
                continue

            # Проверяем существование и ограничиваем размер файла
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as f:
                    lines = deque(f, maxlen=self.MAX_LOG_LINES)  # Хранит только последние строки

                with open(file_name, "w", encoding="utf-8") as f:
                    f.writelines(lines)  # Перезаписываем обрезанный файл

            # Добавляем новые записи
            with open(file_name, "a", encoding="utf-8") as f:
                f.writelines(f"{log}\n" for log in log_list)

            # Очищаем лог-лист после записи
            log_list.clear()

    def file_exists(self, file_name="cache.json"):
        """
        Проверяет, существует ли файл с указанным именем и не является ли он пустым.
        """
        if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
            # print(f"File '{file_name}' exists and is not empty.")
            return True
        # print(f"File '{file_name}' does not exist or is empty.")
        return False

    async def load_data_from_file(self, file_name="cache.json"):
        """
        Читает словарь из JSON файла. Конвертирует списки обратно в множества, если необходимо.
        """
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data_dict = json.load(file)
            
            return data_dict
        except FileNotFoundError:
            print(f"File {file_name} not found. Returning empty dictionary.")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_name}: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error while reading {file_name}: {e}")
            return {}

    async def cache_data_to_file(self, data_dict, file_name="cache.json"):
        """
        Сохраняет словарь в JSON файл. Конвертирует множества в списки для записи.
        """
        if not data_dict:
            print("No data to cache.")
            return
        try:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(data_dict, file, indent=4, ensure_ascii=False)
            # print(f"Data successfully cached to {file_name}")
        except Exception as e:
            print(f"Error while caching data: {e}")
    
    def init_cache_structure_dict(self, symbol): 
        return {
                    "qty_precision": self.get_qty_precisions(self.exchange_data, symbol),
                    "LONG": {
                        "in_position": False,                  
                        "entry_point": 0.0,                     
                        "comul_qty": 0.0,                  
                        "is_opening": False,          
                        "is_closing": False
                    },
                    "SHORT": {
                        "in_position": False,                  
                        "entry_point": 0.0,                     
                        "comul_qty": 0.0,                  
                        "is_opening": False,          
                        "is_closing": False
                    },
                    "tp_rate": None,
                    "sl_rate": None
        }

    def process_positions(self, positions, asset_id):
        """Обрабатывает позиции, создавая структуру initial_restored_data для каждой позиции"""
        # Инициализация данных
        for position in positions:
            symbol = position['symbol'].upper()
            position_side = position['positionSide'].upper()
            position_amt = float(position['positionAmt'])
            entry_price = float(position['entryPrice'])
            
            if symbol in self.busy_symbols_set:
                self.cashe_data_book_dict[asset_id][symbol][position_side].update({
                    "in_position": position_amt != 0,
                    "comul_qty": position_amt,
                    "entry_point": entry_price if position_amt != 0 else 0.0
                })

    async def check_position_data(self, session):
        """Проверка данных о позициях и их обработка"""
        try:
            for asset_id, asset in self.assets_dict.items():  
                bin_publik_key = asset.get("BINANCE_API_PUBLIC_KEY")
                bin_private_key = asset.get("BINANCE_API_PRIVATE_KEY")              
                account_info = await self.fetch_positions(session, bin_publik_key, bin_private_key)
                positions = account_info.get("positions", [])       
                self.process_positions(positions, asset_id)

        except Exception as ex:
            self.log_error_loger((f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}"))            
    
    async def initialize_asset_data(self):
        """Инициализирует структуру cashe_data_book_dict для assets_dict."""
        for asset_id, asset in self.assets_dict.items():
            self.cashe_data_book_dict[asset_id] = {}
            self.klines_data_dict[asset_id] = {}  
            
            for symbol in asset.get('symbols', []):
                symbol = symbol.upper()
                self.cashe_data_book_dict[asset_id][symbol] = self.init_cache_structure_dict(symbol)
                indicator_number = asset.get("indicator_number")
                # self.cashe_data_book_dict[asset_id][symbol]["indicator_number"] = indicator_number                
                self.cashe_data_book_dict[asset_id][symbol]["tp_rate"] = asset.get(f"indicator_{indicator_number}").get("tp_rate", None)
                self.cashe_data_book_dict[asset_id][symbol]["sl_rate"] = asset.get(f"indicator_{indicator_number}").get("sl_rate", None)
             
                self.all_active_symbols_set.add(symbol)          

    async def cache_trade_data(self, session):

        if self.cashe_data_book_dict:            
            await self.check_position_data(session)
            await self.cache_data_to_file(self.cashe_data_book_dict)
            return

        if not self.file_exists():
            self.exchange_data = await self.get_exchange_info(session)                  
            await self.initialize_asset_data()
            await self.check_position_data(session)
            await self.cache_data_to_file(self.cashe_data_book_dict)
        else:
            self.cashe_data_book_dict = await self.load_data_from_file()