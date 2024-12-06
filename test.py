# from datetime import datetime, timezone
# from time import sleep

# class KlineFetcher:
#     def __init__(self, interval):
#         self.interval_seconds = self.interval_to_seconds(interval)
#         self.klines_data_dict = {}
#         self.last_fetch_timestamp = None

#     def interval_to_seconds(self, interval):
#         """
#         Преобразует строковый интервал Binance в количество секунд.
#         """
#         mapping = {
#             "1m": 60,
#             "3m": 180,
#             "5m": 300,
#             "15m": 900,
#             "30m": 1800,
#             "1h": 3600,
#             "2h": 7200,
#             "4h": 14400,
#             "1d": 86400,
#         }
#         return mapping.get(interval, 60)  # По умолчанию "1m"

#     def is_new_interval(self):
#         """
#         Проверяет, появилась ли новая метка времени кратная интервалу.
#         """
#         now = datetime.now(timezone.utc)  # Используем объект времени с временной зоной UTC
#         current_timestamp = int(now.timestamp())
#         if self.last_fetch_timestamp is None:
#             self.last_fetch_timestamp = (current_timestamp // self.interval_seconds) * self.interval_seconds
#             return True

#         next_expected_timestamp = self.last_fetch_timestamp + self.interval_seconds
#         if current_timestamp >= next_expected_timestamp:
#             self.last_fetch_timestamp = next_expected_timestamp
#             return True

#         return False
    
# # Тестирование
# kl = KlineFetcher("3m")
# print(kl.interval_seconds)

# while True:
#     print(kl.is_new_interval())
#     sleep(5)

            # "aver_down": {
            #     "is_active": false,
            #     "value_%": [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
            # },


    # def calculate_bollinger_bands(self, df, bb_period, bollinger_std, suffix=''):
    #     """
    #     Вычисляем полосы Боллинджера.
        
    #     Args:
    #         df (pd.DataFrame): Данные по свечам (OHLCV).
    #         bollinger_std (float): Множитель стандартного отклонения.
    #         suffix (str): Суффикс для уникальности имен колонок.
        
    #     Returns:
    #         pd.DataFrame: DataFrame с рассчитанными полосами Боллинджера.
    #     """
    #     middle_col = f'bb_middle{suffix}'
    #     upper_col = f'bb_upper{suffix}'
    #     lower_col = f'bb_lower{suffix}'
    #     std_col = f'std{suffix}'

    #     # Вычисляем линии Боллинджера
    #     df[middle_col] = df['Close'].rolling(window=bb_period).mean()
    #     df[std_col] = df['Close'].rolling(window=bb_period).std()
    #     df[upper_col] = df[middle_col] + (bollinger_std * df[std_col])
    #     df[lower_col] = df[middle_col] - (bollinger_std * df[std_col])

    #     return df

# closes_prices = df.loc[:, "Close"]


    # def calculate_bollinger_middle(self, df, bb_period):
    #     """
    #     Вычисляет среднюю линию (moving average) для Боллинджера.
    #     """
    #     df['bb_middle'] = df['Close'].rolling(window=bb_period).mean()
    #     return df

    # def calculate_bollinger_bands(self, df, bollinger_std, suffix=''):
    #     """
    #     Вычисляет верхнюю и нижнюю линии Боллинджера.
    #     """
    #     middle_col = 'bb_middle'
    #     std_col = f'std{suffix}'
    #     upper_col = f'bb_upper{suffix}'
    #     lower_col = f'bb_lower{suffix}'

    #     # Вычисляем стандартное отклонение и линии
    #     df[std_col] = df['Close'].rolling(window=len(df[middle_col].dropna())).std()
    #     df[upper_col] = df[middle_col] + (bollinger_std * df[std_col])
    #     df[lower_col] = df[middle_col] - (bollinger_std * df[std_col])
    #     return df

    # def get_signals(self, df, bb_period=50, basik_std=2, tp_rate=0.9, sl_rate=1.1):
    #     """
    #     Рассчитывает сигналы Боллинджера.
    #     """
    #     # Сначала вычисляем среднюю линию
    #     df = self.calculate_bollinger_middle(df, bb_period)

    #     # Основные полосы Боллинджера
    #     df = self.calculate_bollinger_bands(df, basik_std)

    #     # Добавляем TP и SL полосы
    #     tp_suffix = f'_tp_{tp_rate}'
    #     sl_suffix = f'_sl_{sl_rate}'
    #     df = self.calculate_bollinger_bands(df, basik_std * tp_rate, suffix=tp_suffix)
    #     df = self.calculate_bollinger_bands(df, basik_std * sl_rate, suffix=sl_suffix)

    #     # Последние цены
    #     last_close_price = df["Close"].iloc[-1]
    #     prelast_close_price = df["Close"].iloc[-2]

    #     # Основные линии
    #     signals_dict = {
    #         "long_middle_cross": (last_close_price > df['bb_middle'].iloc[-1]) and 
    #                             (prelast_close_price < df['bb_middle'].iloc[-2]),
    #         "short_middle_cross": (last_close_price < df['bb_middle'].iloc[-1]) and 
    #                             (prelast_close_price > df['bb_middle'].iloc[-2]),
    #         "short_upper_cross": (last_close_price > df[f'bb_upper'].iloc[-1]),
    #         "long_lower_cross": (last_close_price < df[f'bb_lower'].iloc[-1]),
    #         "tp_upper_cross": (last_close_price > df[f'bb_upper{tp_suffix}'].iloc[-1]),
    #         "tp_lower_cross": (last_close_price < df[f'bb_lower{tp_suffix}'].iloc[-1]),
    #         "sl_upper_cross": (last_close_price > df[f'bb_upper{sl_suffix}'].iloc[-1]),
    #         "sl_lower_cross": (last_close_price < df[f'bb_lower{sl_suffix}'].iloc[-1]),
    #     }

    #     # Проверяем наличие любого сигнала
    #     self.is_any_signal = any(signals_dict.values())

    #     return signals_dict

            # "upper_cross": (last_close_price > df[f'bb_upper'].iloc[-1]),
            # "lower_cross": (last_close_price < df[f'bb_lower'].iloc[-1]),


    # def count_decimal_places(self, number):
    #     if isinstance(number, (int, float)):
    #         number_str = f'{number:.10f}'.rstrip('0')
    #         if '.' in number_str:
    #             return len(number_str.split('.')[1])
    #     return 0  
    
    
    # # /////////////////////////////
    # def count_multipliter_places(self, number):
    #     if isinstance(number, (int, float)):
    #         number_str = str(number)
    #         if '.' in number_str:
    #             return len(number_str.split('.')[1])
    #     return 0


    # def get_spot_qty_precisions(self, symbol_info, token):
    #     # Находим данные о символе

    #     symbol_data = next((item for item in symbol_info["symbols"] if item['symbol'] == token + 'USDT'), None)
    #     if not symbol_data:
    #         return

    #     lot_size_filter = next((f for f in symbol_data.get('filters', []) if f.get('filterType') == 'LOT_SIZE'), None)
    #     if not lot_size_filter:
    #         return

    #     step_size = float(lot_size_filter.get('stepSize', '1'))
    #     return -int(math.log10(step_size))


            
                     
        # bin_publik_key = asset.get("BINANCE_API_PUBLIC_KEY")
        # bin_private_key = asset.get("BINANCE_API_PRIVATE_KEY")

    # def process_positions(self, positions, ):
    #     symbol_beasy_list = []
    #     res_list = []
        
    #     for position in positions:
    #         if float(position['positionAmt']) != 0:
    #             pos_nn = 1 if position['symbol'] not in symbol_beasy_list else 2
    #             symbol_beasy_list.append(position['symbol'])
    #             symbol = position['symbol']
    #             if symbol in 
    #             self.initial_restored_data[symbol]
    #                 {   "in_position_long": False,
    #                     "in_position_short": False,
    #                     "comul_qty_long": 0.0,
    #                     "comul_qty_short": 0.0,
    #                 }
    #                 # position['symbol'], 
    #                 # position['positionSide'], 
    #                 # abs(float(position['positionAmt'])), 
    #                 # float(position['entryPrice']),
    #                 # pos_nn
            
    #     return res_list  


    # # @aiohttp_connector
    # async def make_order(self, session, asset_id, api_key, api_secret, symbol, qty, side, market_type, position_side, side_marker, reduce_only=False, target_price=None):
    #     print("Параметры запроса:")
    #     print(symbol, qty, side, market_type, position_side)
    #     try:
    #         params = {
    #             "symbol": symbol,
    #             "side": side,
    #             "type": market_type,
    #             "quantity": abs(qty),
    #             "positionSide": position_side,
    #             "recvWindow": 20000,
    #             "newOrderRespType": 'RESULT'
    #         }
    #         headers = {
    #             'X-MBX-APIKEY': api_key
    #         }
            
    #         if market_type in ['STOP_MARKET', 'TAKE_PROFIT_MARKET']:
    #             params['stopPrice'] = target_price
    #             params['closePosition'] = True
    #         elif market_type == 'LIMIT':
    #             params["price"] = target_price
    #             params["timeInForce"] = 'GTC'

    #         if reduce_only:
    #             params["reduceOnly"] = reduce_only                

    #         params = self.get_signature(params, api_secret)
    #         async with session.post(self.create_order_url, headers=headers, params=params) as response:
    #             return await response.json(), symbol, side_marker
    #     except Exception as ex:
    #         self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")

    #     return {}, symbol, side_marker


              
    # async def is_closing_position_true(self, session, symbol, position_side, api_key, api_secret):
    #     params = {
    #         "symbol": symbol,
    #         "positionSide": position_side,
    #         'recvWindow': 20000,
    #     }
    #     headers = {
    #         'X-MBX-APIKEY': api_key
    #     }
    #     try:
    #         params = self.get_signature(params, api_secret)
    #         async with session.get(self.positions_url, headers=headers, params=params) as response:
    #             positions = await response.json()
    #         for position in positions:
    #             if position['symbol'] == symbol and position['positionSide'] == position_side and float(position['positionAmt']) != 0:
    #                 return False, symbol
    #         return True, symbol
    #     except Exception as ex:
    #         self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")
            
    #     return False, symbol   


    # async def get_remaining_position_quantity(self, session, symbol, position_side, api_key, api_secret):
    #     params = {
    #         "symbol": symbol,
    #         "positionSide": position_side,
    #         'recvWindow': 20000,
    #     }

    #     headers = {
    #         'X-MBX-APIKEY': api_key
    #     }
    #     try:
    #         params = self.get_signature(params, api_secret)
    #         async with session.get(self.positions_url, headers=headers, params=params) as response:
    #             positions = await response.json()
            
    #         for position in positions:
    #             if position['symbol'] == symbol and position['positionSide'] == position_side:
    #                 remaining_qty = float(position['positionAmt'])
    #                 return remaining_qty, symbol
            
    #         return 0.0, symbol  # Return 0 if no position is found
    #     except Exception as ex:
    #         self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")
    #         return 0.0, symbol



            # логика присвоения соответсвующих данных из self.initial_restored_data в self.cashe_data_book_dict по соответствующим ключам. на выходе должен быть обновленный словарь self.cashe_data_book_dict


                # else:
                #     # Если позиция не открыта
                #     self.cashe_data_book_dict[asset_id][symbol]["in_position_long"] = False
                #     self.cashe_data_book_dict[asset_id][symbol]["in_position_short"] = False
                #     self.cashe_data_book_dict[asset_id][symbol]["comul_qty_long"] = 0.0
                #     self.cashe_data_book_dict[asset_id][symbol]["entry_point_long"] = 0.0
                #     self.cashe_data_book_dict[asset_id][symbol]["comul_qty_short"] = 0.0
                #     self.cashe_data_book_dict[asset_id][symbol]["entry_point_short"] = 0.0   


  
    # def time_signal_info(self, signal, symbol, cur_price):
    #     ssignal_time = self.get_cur_process_time()
    #     signal_mess = 'LONG' if signal == 1 else 'SHORT'
    #     print(f"Сигнал: {signal_mess}. Монета: {symbol}. Время сигнала: {ssignal_time}. Текущая цена: {cur_price}")

    # def time_calibrator(self, kline_time: int, time_frame: str):
    #     current_time = time.time()
        
    #     # Преобразуем таймфрейм в секунды
    #     time_in_seconds = {
    #         'm': 60,
    #         'h': 3600,
    #         'd': 86400
    #     }.get(time_frame, 0) * kline_time

    #     if time_in_seconds == 0:
    #         raise ValueError("Unsupported time frame. Use 'm', 'h', or 'd'.")
        
    #     # Рассчитываем интервал для ожидания до следующего значения
    #     next_interval = math.ceil(current_time / time_in_seconds) * time_in_seconds
    #     wait_time = next_interval - current_time

    #     # Определяем специальные интервалы ожидания
    #     special_intervals = {
    #         ('m', 15): 300, # 5 min
    #         ('m', 30): 300,
    #         ('h', 1): 300,
    #         ('h', 4): 900, # 15 min
    #         ('h', 6): 900,
    #         ('h', 12): 900,
    #         ('d', kline_time): 900
    #     }

    #     # Рассчитываем второй интервал ожидания (wait_time_2) для специальных временных интервалов
    #     special_seconds = special_intervals.get((time_frame, kline_time), 0)

    #     if special_seconds:
    #         next_interval_2 = math.ceil(current_time / special_seconds) * special_seconds
    #         wait_time_2 = next_interval_2 - current_time
    #     else:
    #         wait_time_2 = wait_time
        
    #     return int(wait_time) + 1, int(wait_time_2) + 1


    # def write_logs(self):
    #     """Записывает логи в файлы и очищает соответствующие списки."""
    #     logs = [
    #         (self.general_error_logger_list, LOG_ERROR_FILE),
    #         (self.log_info_list, LOG_INFO_FILE),
    #         (self.log_error_order_list, LOG_ERROR_ORDERS_FILE),
    #         (self.log_succ_order_list, LOG_SUCCESS_ORDERS_FILE),
    #     ]
        
    #     for log_list, file_name in logs:
    #         if log_list:
    #             # Проверяем и подрезаем файл, если превышен лимит строк
    #             if os.path.exists(file_name):
    #                 with open(file_name, "r", encoding="utf-8") as f:
    #                     lines = f.readlines()

    #                 # Если количество строк в файле превышает лимит
    #                 if len(lines) > self.MAX_LOG_LINES:
    #                     # Обрезаем файл, удаляя старые записи
    #                     with open(file_name, "w", encoding="utf-8") as f:
    #                         # Оставляем только последние MAX_LOG_LINES строк
    #                         f.writelines(lines[-self.MAX_LOG_LINES:])
                
    #             # Открываем файл и записываем новые данные
    #             with open(file_name, "a", encoding="utf-8") as f:
    #                 f.writelines(f"{log}\n" for log in log_list)

    #             # Очищаем список после записи
    #             log_list.clear()



                # "tp_long": (last_close_price > df[f'bb_upper{tp_suffix}'].iloc[-1]),
                # "tp_short": (last_close_price < df[f'bb_lower{tp_suffix}'].iloc[-1]),
                # "sl_short": (last_close_price > df[f'bb_upper{sl_suffix}'].iloc[-1]),
                # "sl_long": (last_close_price < df[f'bb_lower{sl_suffix}'].iloc[-1])


            # tp_suffix = f'_tp_{tp_rate}'            
            # df = self.calculate_bollinger_bands(df, bb_period, basik_std * tp_rate, suffix=tp_suffix)
            # sl_suffix = f'_sl_{sl_rate}'
            # df = self.calculate_bollinger_bands(df, bb_period, basik_std * sl_rate, suffix=sl_suffix)


        # async with self.async_lock:
        #     self.is_any_signal = any(signals_dict.values())