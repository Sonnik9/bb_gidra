import json
from g_indicator_strategy import Strategies
import os
import inspect

class ReneveData(Strategies):
    def __init__(self):
        super().__init__()
        self.initial_restored_data = {}        
        # Декорируем методы с логированием исключений
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

        self.processed_transactions = set()  # Инициализация как множество

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

    def process_positions(self, positions, asset_id, symbols):
        """Обрабатывает позиции, создавая структуру initial_restored_data для каждой позиции"""
        # Инициализация данных
        for position in positions:
            symbol = position['symbol']
            position_side = position['positionSide']
            position_amt = float(position['positionAmt'])
            entry_price = float(position['entryPrice']) if position_amt != 0 else 0.0
            
            if symbol in symbols and symbol in self.all_active_symbols:

                if position_amt != 0:
                    # Проверка лонга или шорта
                    if position_side == 'LONG':
                        self.cashe_data_book_dict[asset_id][symbol]["in_position_long"] = True
                        self.cashe_data_book_dict[asset_id][symbol]["comul_qty_long"] = position_amt
                        self.cashe_data_book_dict[asset_id][symbol]["entry_point_long"] = entry_price
                    elif position_side == 'SHORT':
                        self.cashe_data_book_dict[asset_id][symbol]["in_position_short"] = True
                        self.cashe_data_book_dict[asset_id][symbol]["comul_qty_short"] = position_amt
                        self.cashe_data_book_dict[asset_id][symbol]["entry_point_short"] = entry_price

    async def check_position_data(self, session):
        """Проверка данных о позициях и их обработка"""
        try:
            for asset_id, asset in self.assets_dict.items():  
                bin_publik_key = asset.get("BINANCE_API_PUBLIC_KEY")
                bin_private_key = asset.get("BINANCE_API_PRIVATE_KEY")              
                account_info = await self.fetch_positions(session, bin_publik_key, bin_private_key)
                positions = account_info.get("positions", [])
                symbols = asset.get("symbols")            
                self.process_positions(positions, asset_id, symbols)

            for asset_id, _ in self.assets_dict.items():                
                for symbol in self.all_active_symbols:
                    if not self.cashe_data_book_dict[asset_id][symbol]["in_position_long"]:
                        self.cashe_data_book_dict[asset_id][symbol]["comul_qty_long"] = 0.0
                        self.cashe_data_book_dict[asset_id][symbol]["entry_point_long"] = 0.0

                    if not self.cashe_data_book_dict[asset_id][symbol]["in_position_short"]:
                        self.cashe_data_book_dict[asset_id][symbol]["comul_qty_short"] = 0.0
                        self.cashe_data_book_dict[asset_id][symbol]["entry_point_short"] = 0.0   

        except Exception as ex:
            self.log_error_loger((f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}"))            

    async def initialize_asset_data(self, exchange_data):
        """Инициализирует структуру cashe_data_book_dict для assets_dict."""
        for asset_id, asset in self.assets_dict.items():
            self.cashe_data_book_dict[asset_id] = {}
            
            for symbol in asset.get('symbols', []):
                symbol = symbol.upper()
                self.cashe_data_book_dict[asset_id][symbol] = {
                    "first_trade": True,
                    "qty_precision": self.get_qty_precisions(exchange_data, symbol),
                    "in_position_long": False,
                    "in_position_short": False,
                    "entry_point_long": 0.0,
                    "entry_point_short": 0.0,
                    "comul_qty_long": 0.0,
                    "comul_qty_short": 0.0,
                    "is_opening_long": False,
                    "is_opening_short": False,
                    "is_closing_long": False,
                    "is_closing_short": False,
                }

                # Добавляем символ в список активных, если его там нет
                if symbol not in self.all_active_symbols:
                    self.all_active_symbols.append(symbol)

            # Инициализируем структуру klines_data_dict
            self.cashe_data_book_dict[asset_id]["klines_data_dict"] = {}

    async def cache_trade_data(self, session):

        if self.cashe_data_book_dict:            
            await self.check_position_data(session)
            await self.cache_data_to_file(self.cashe_data_book_dict)
            return

        if not self.file_exists():
            exchange_data = await self.get_exchange_info(session)                  
            await self.initialize_asset_data(exchange_data)
            await self.check_position_data(session)
            await self.cache_data_to_file(self.cashe_data_book_dict)
        else:
            self.cashe_data_book_dict = await self.load_data_from_file()