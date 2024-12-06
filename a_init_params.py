import asyncio
import json
import pytz

config_file_path = "settings.json"

class ConfigManager:
    def __init__(self):
        self.assets_dict = {}
        self.tz_location_str = "UTC"
        self.inspection_interval = None
        self.MAX_LOG_LINES = None
        self.is_bible_quotes_introduction = None
        self.tz_location = None
        self._initialize_settings()

    def _initialize_settings(self):
        """Загружает настройки из JSON-файла и инициализирует атрибуты класса."""
        try:
            with open(config_file_path, 'r', encoding='utf-8') as file:
                config = json.load(file)

            # Проверка обязательных ключей
            required_keys = [
                'assets_dict', 'tz_location_str', 'inspection_interval', 
                'is_bible_quotes_introdaction', 'MAX_LOG_LINES'
            ]

            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                raise ValueError(f"Отсутствуют ключи в настройках: {', '.join(missing_keys)}")

            # Основные настройки
            self.assets_dict = config.get("assets_dict", {})
            self.tz_location_str = config.get("tz_location_str", "UTC")
            self.inspection_interval = config.get("inspection_interval", 10)
            self.MAX_LOG_LINES = config.get("MAX_LOG_LINES", 200)
            self.is_bible_quotes_introduction = config.get("is_bible_quotes_introdaction", True)

            # Установка временной зоны
            self.tz_location = pytz.timezone(self.tz_location_str)

            self.assets_dict = {k: v for k, v in self.assets_dict.items() if v.get("is_active")}

        except FileNotFoundError:
            print(f"Файл настроек '{config_file_path}' не найден.")
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON-файла.")
        except Exception as e:
            print(f"Произошла ошибка при загрузке настроек: {e}")

    def display_settings(self):
        """Выводит настройки в читаемом формате."""
        print("\n--- Настройки ---\n")
        print(f"Интервал проверки сигналов: {self.inspection_interval} сек.")
        print(f"Временная зона: {self.tz_location_str}")
        print(f"Лимит строк логов: {self.MAX_LOG_LINES}")
        print(f"Включение цитат из Библии: {'Да' if self.is_bible_quotes_introduction else 'Нет'}")
        print("\n--- Список активов ---\n")
        
        for asset_id, asset in self.assets_dict.items():
            print(f"ID: {asset_id}")
            print(f"Имя: {asset['my_name']}")
            print(f"Активен: {'Да' if asset['is_active'] else 'Нет'}")
            print(f"Символы: {', '.join(asset['symbols'])}")
            print(f"Депозит: {asset['depo']} USDT")
            print(f"Плечо: {asset['leverage']}")
            print(f"Тип маржи: {asset['margin_type']}")
            print(f"Номер стратегии: {asset['indicator_number']}")
            
            print("Индикатор 1:")
            for key, value in asset.get("indicator_1", {}).items():
                print(f"  {key}: {value}")
            
            print("Индикатор 2:")
            for key, value in asset.get("indicator_2", {}).items():
                print(f"  {key}: {value}")

            # print(f"Take Profit Rate: {asset.get('tp_rate', 0)}%")
            # print(f"Stop Loss Rate: {asset.get('sl_rate', 0)}%")
            
            print("\n--- API-ключи ---")
            print(f"Публичный ключ: {asset['BINANCE_API_PUBLIC_KEY'][:10]}... (скрыто)")
            print(f"Приватный ключ: {asset['BINANCE_API_PRIVATE_KEY'][:10]}... (скрыто)")
            print("\n" + "-" * 30 + "\n")

class VARIABLES(ConfigManager):
    first_iter = True  
    stop_bot = False 
    general_error_logger_list = []
    log_info_list = []
    log_response_list = []
    log_succ_order_list = []
    log_error_order_list = []     
    async_lock = asyncio.Lock()
    # ////
    interval_seconds = None
    last_fetch_timestamp = None
    exchange_data = []
    cashe_data_book_dict = {}
    klines_data_dict = {}
    busy_symbols_set = set()
    all_active_symbols_set = set()    
    is_any_signal = False

# # Использование
# if __name__ == "__main__":
#     manager = ConfigManager()
#     manager.display_settings()
