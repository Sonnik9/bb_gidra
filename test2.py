    
# # class Strategiess(INDICATORS):
# #     def __init__(self) -> None:
# #         super().__init__()

# #         # Декорируем методы с логированием исключений
# #         methods_to_wrap = [
# #             method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
# #             if not method_name.startswith("__")  # Исключаем специальные методы
# #         ]
# #         for method_name in methods_to_wrap:
# #             setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

# #     # strategy 1:
# #     async def strategy_1(self, signals_dict, asset_id, token):

# #         in_position_long = self.cashe_data_book_dict[asset_id][token]["LONG"]["in_position"]
# #         in_position_short = self.cashe_data_book_dict[asset_id][token]["SHORT"]["in_position"]
# #         is_tp = self.cashe_data_book_dict[asset_id][token]["tp_rate"]
# #         is_sl = self.cashe_data_book_dict[asset_id][token]["sl_rate"]

# #         cur_time = self.get_date_time_now(self.tz_location)

# #         if in_position_long:
# #             if is_tp:
# #                 if signals_dict["tp_long"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по тейк-профиту. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["LONG"]["is_closing"] = True
# #             else:
# #                 if signals_dict["upper_cross"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по сигналу пересечения с верхней линией Боллинджера. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["LONG"]["is_closing"] = True

# #             if is_sl:
# #                 if signals_dict["sl_long"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по стоп-лоссу. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["LONG"]["is_closing"] = True
# #             else:
# #                 if signals_dict["lower_cross"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по сигналу пересечения с нижней линией Боллинджера. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["LONG"]["is_closing"] = True          

# #         if in_position_short:
# #             if is_tp:
# #                 if signals_dict["tp_short"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по тейк-профиту. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["SHORT"]["is_closing"] = True
# #             else:
# #                 if signals_dict["lower_cross"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по сигналу пересечения с нижней линией Боллинджера. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["SHORT"]["is_closing"] = True

# #             if is_sl:
# #                 if signals_dict["sl_short"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по стоп-лоссу. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["SHORT"]["is_closing"] = True
# #             else:
# #                 if signals_dict["upper_cross"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по сигналу пересечения с верхней линией Боллинджера. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["SHORT"]["is_closing"] = True

# #         if signals_dict["middle_long_cross"] or signals_dict["middle_short_cross"]:
# #             if not in_position_long:
# #                 async with self.async_lock:
# #                     self.is_any_signal = True
# #                 self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 1. Открываем новую Лонг позицию. Время: {cur_time}")               
# #                 self.cashe_data_book_dict[asset_id][token]["LONG"]["is_opening"] = True
# #             if not in_position_short:
# #                 async with self.async_lock:
# #                     self.is_any_signal = True
# #                 self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Position: 2. Открываем новую Шорт позицию. Время: {cur_time}") 
# #                 self.cashe_data_book_dict[asset_id][token]["SHORT"]["is_opening"] = True

# #     # strategy 2:
# #     async def strategy_2(self, signals_dict, asset_id, token):

# #         in_position_long = self.cashe_data_book_dict[asset_id][token]["LONG"]["in_position"]
# #         in_position_short = self.cashe_data_book_dict[asset_id][token]["SHORT"]["in_position"]
# #         is_sl = self.cashe_data_book_dict[asset_id][token]["sl_rate"]

# #         cur_time = self.get_date_time_now(self.tz_location)

# #         if in_position_long:
# #             if signals_dict["upper_cross"]:
# #                 async with self.async_lock:
# #                     self.is_any_signal = True
# #                 self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Закрываем лонг позицию по сигналу пересечения с верхней линией Боллинджера. Время: {cur_time}")
# #                 self.cashe_data_book_dict[asset_id][token]["LONG"]["is_closing"] = True

# #             if is_sl:
# #                 if signals_dict["sl_long"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Закрываем лонг позицию по стоп-лоссу. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["LONG"]["is_closing"] = True

# #         elif in_position_short:
# #             if signals_dict["lower_cross"]:
# #                 async with self.async_lock:
# #                     self.is_any_signal = True
# #                 self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Закрываем шорт позицию по сигналу пересечения с нижней линией Боллинджера. Время: {cur_time}")
# #                 self.cashe_data_book_dict[asset_id][token]["SHORT"]["is_closing"] = True

# #             if is_sl:
# #                 if signals_dict["sl_short"]:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Закрываем шорт позицию по стоп-лоссу. Время: {cur_time}")
# #                     self.cashe_data_book_dict[asset_id][token]["SHORT"]["is_closing"] = True
# #         else:
# #             if signals_dict["lower_cross"]:
# #                 if not in_position_long:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Открываем новую Лонг позицию.")               
# #                     self.cashe_data_book_dict[asset_id][token]["LONG"]["is_opening"] = True
# #             elif signals_dict["upper_cross"]:
# #                 if not in_position_short:
# #                     async with self.async_lock:
# #                         self.is_any_signal = True
# #                     self.log_info_loger(f"Asset Id: {asset_id}. Token: {token}. Открываем новую Шорт позицию.") 
# #                     self.cashe_data_book_dict[asset_id][token]["SHORT"]["is_opening"] = True



# # class Strategiess_1(INDICATORS):
# #     async def handle_signal(self, position_type, signal_type, asset_id, token, log_message):
# #         """
# #         Универсальный метод для обработки сигналов закрытия/открытия позиций.
# #         """
# #         async with self.async_lock:
# #             self.is_any_signal = True
# #         self.log_info_loger(log_message)
# #         self.cashe_data_book_dict[asset_id][token][position_type][signal_type] = True

# #     # strategy 1:
# #     async def strategy_1(self, signals_dict, asset_id, token):
# #         cur_time = self.get_date_time_now(self.tz_location)
# #         positions = {
# #             "LONG": {
# #                 "in_position": self.cashe_data_book_dict[asset_id][token]["LONG"]["in_position"],
# #                 "is_closing": "is_closing",
# #                 "tp_signal": "tp_long",
# #                 "sl_signal": "sl_long",
# #                 "upper_cross_signal": "upper_cross",
# #                 "lower_cross_signal": "lower_cross",
# #                 "tp_rate": self.cashe_data_book_dict[asset_id][token]["tp_rate"],
# #                 "sl_rate": self.cashe_data_book_dict[asset_id][token]["sl_rate"],
# #                 "log_messages": {
# #                     "tp": f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по тейк-профиту. Время: {cur_time}",
# #                     "upper_cross": f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по сигналу пересечения с верхней линией Боллинджера. Время: {cur_time}",
# #                     "sl": f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по стоп-лоссу. Время: {cur_time}",
# #                     "lower_cross": f"Asset Id: {asset_id}. Token: {token}. Position: 1. Закрываем лонг позицию по сигналу пересечения с нижней линией Боллинджера. Время: {cur_time}",
# #                 }
# #             },
# #             "SHORT": {
# #                 "in_position": self.cashe_data_book_dict[asset_id][token]["SHORT"]["in_position"],
# #                 "is_closing": "is_closing",
# #                 "tp_signal": "tp_short",
# #                 "sl_signal": "sl_short",
# #                 "upper_cross_signal": "upper_cross",
# #                 "lower_cross_signal": "lower_cross",
# #                 "tp_rate": self.cashe_data_book_dict[asset_id][token]["tp_rate"],
# #                 "sl_rate": self.cashe_data_book_dict[asset_id][token]["sl_rate"],
# #                 "log_messages": {
# #                     "tp": f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по тейк-профиту. Время: {cur_time}",
# #                     "lower_cross": f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по сигналу пересечения с нижней линией Боллинджера. Время: {cur_time}",
# #                     "sl": f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по стоп-лоссу. Время: {cur_time}",
# #                     "upper_cross": f"Asset Id: {asset_id}. Token: {token}. Position: 2. Закрываем шорт позицию по сигналу пересечения с верхней линией Боллинджера. Время: {cur_time}",
# #                 }
# #             }
# #         }

# #         for position, data in positions.items():
# #             if data["in_position"]:
# #                 if data["tp_rate"] and signals_dict[data["tp_signal"]]:
# #                     await self.handle_signal(position, data["is_closing"], asset_id, token, data["log_messages"]["tp"])
# #                 elif signals_dict[data["upper_cross_signal"] if position == "LONG" else "lower_cross_signal"]:
# #                     signal_type = "upper_cross" if position == "LONG" else "lower_cross"
# #                     await self.handle_signal(position, data["is_closing"], asset_id, token, data["log_messages"][signal_type])
# #                 if data["sl_rate"] and signals_dict[data["sl_signal"]]:
# #                     await self.handle_signal(position, data["is_closing"], asset_id, token, data["log_messages"]["sl"])
# #                 elif signals_dict[data["lower_cross_signal"] if position == "LONG" else "upper_cross_signal"]:
# #                     signal_type = "lower_cross" if position == "LONG" else "upper_cross"
# #                     await self.handle_signal(position, data["is_closing"], asset_id, token, data["log_messages"][signal_type])

# #         if signals_dict["middle_long_cross"] and not positions["LONG"]["in_position"]:
# #             await self.handle_signal("LONG", "is_opening", asset_id, token,
# #                                      f"Asset Id: {asset_id}. Token: {token}. Position: 1. Открываем новую Лонг позицию. Время: {cur_time}")
# #         if signals_dict["middle_short_cross"] and not positions["SHORT"]["in_position"]:
# #             await self.handle_signal("SHORT", "is_opening", asset_id, token,
# #                                      f"Asset Id: {asset_id}. Token: {token}. Position: 2. Открываем новую Шорт позицию. Время: {cur_time}")


# class BaseStrategy:
#     """
#     Базовый класс для стратегий.
#     """
#     async def process_position(self, position_type, action, signal_reason, asset_id, token):
#         """
#         Обрабатывает действия с позициями (открытие/закрытие).
#         """
#         async with self.async_lock:
#             self.is_any_signal = True
#         self.cashe_data_book_dict[asset_id][token][position_type][action] = True
#         self.log_info_loger(
#             f"Asset Id: {asset_id}. Token: {token}. {signal_reason}. Время: {self.get_date_time_now(self.tz_location)}"
#         )

#     async def process_signals(self, signals_dict, asset_id, token):
#         """
#         Обрабатывает сигналы. Реализуется в дочерних классах.
#         """
#         raise NotImplementedError("Метод должен быть реализован в дочернем классе.")


# class Strategy1(BaseStrategy):
#     """
#     Реализация стратегии 1.
#     """
#     async def process_signals(self, signals_dict, asset_id, token):
#         in_position_long = self.cashe_data_book_dict[asset_id][token]["LONG"]["in_position"]
#         in_position_short = self.cashe_data_book_dict[asset_id][token]["SHORT"]["in_position"]
#         is_tp = self.cashe_data_book_dict[asset_id][token]["tp_rate"]
#         is_sl = self.cashe_data_book_dict[asset_id][token]["sl_rate"]

#         # Обработка длинных позиций
#         if in_position_long:
#             if is_tp and signals_dict["tp_long"]:
#                 await self.process_position(
#                     "LONG", "is_closing", "Закрываем лонг по тейк-профиту", asset_id, token
#                 )
#             elif signals_dict["upper_cross"]:
#                 await self.process_position(
#                     "LONG", "is_closing", "Закрываем лонг по пересечению с верхней линией", asset_id, token
#                 )
#             elif is_sl and signals_dict["sl_long"]:
#                 await self.process_position(
#                     "LONG", "is_closing", "Закрываем лонг по стоп-лоссу", asset_id, token
#                 )
#             elif signals_dict["lower_cross"]:
#                 await self.process_position(
#                     "LONG", "is_closing", "Закрываем лонг по пересечению с нижней линией", asset_id, token
#                 )

#         # Обработка коротких позиций
#         if in_position_short:
#             if is_tp and signals_dict["tp_short"]:
#                 await self.process_position(
#                     "SHORT", "is_closing", "Закрываем шорт по тейк-профиту", asset_id, token
#                 )
#             elif signals_dict["lower_cross"]:
#                 await self.process_position(
#                     "SHORT", "is_closing", "Закрываем шорт по пересечению с нижней линией", asset_id, token
#                 )
#             elif is_sl and signals_dict["sl_short"]:
#                 await self.process_position(
#                     "SHORT", "is_closing", "Закрываем шорт по стоп-лоссу", asset_id, token
#                 )
#             elif signals_dict["upper_cross"]:
#                 await self.process_position(
#                     "SHORT", "is_closing", "Закрываем шорт по пересечению с верхней линией", asset_id, token
#                 )

#         # Открытие новых позиций
#         if signals_dict["middle_long_cross"] and not in_position_long:
#             await self.process_position(
#                 "LONG", "is_opening", "Открываем новую лонг позицию", asset_id, token
#             )
#         if signals_dict["middle_short_cross"] and not in_position_short:
#             await self.process_position(
#                 "SHORT", "is_opening", "Открываем новую шорт позицию", asset_id, token
#             )


# class Strategy2(BaseStrategy):
#     """
#     Реализация стратегии 2.
#     """
#     async def process_signals(self, signals_dict, asset_id, token):
#         in_position_long = self.cashe_data_book_dict[asset_id][token]["LONG"]["in_position"]
#         in_position_short = self.cashe_data_book_dict[asset_id][token]["SHORT"]["in_position"]
#         is_sl = self.cashe_data_book_dict[asset_id][token]["sl_rate"]

#         if in_position_long:  # Активна длинная позиция
#             if signals_dict["upper_cross"]:
#                 await self.process_position(
#                     "LONG", "is_closing", "Закрываем Лонг по пересечению с верхней линией", asset_id, token
#                 )
#             elif is_sl and signals_dict["sl_long"]:
#                 await self.process_position(
#                     "LONG", "is_closing", "Закрываем Лонг по стоп-лоссу", asset_id, token
#                 )
#         elif in_position_short:  # Активна короткая позиция
#             if signals_dict["lower_cross"]:
#                 await self.process_position(
#                     "SHORT", "is_closing", "Закрываем Шорт по пересечению с нижней линией", asset_id, token
#                 )
#             elif is_sl and signals_dict["sl_short"]:
#                 await self.process_position(
#                     "SHORT", "is_closing", "Закрываем Шорт по стоп-лоссу", asset_id, token
#                 )
#         else:  # Позиции отсутствуют
#             if signals_dict["lower_cross"]:
#                 await self.process_position(
#                     "LONG", "is_opening", "Открываем Лонг", asset_id, token
#                 )
#             elif signals_dict["upper_cross"]:
#                 await self.process_position(
#                     "SHORT", "is_opening", "Открываем Шорт", asset_id, token
#                 )


# class CombinedStrategy:
#     """
#     Комбинированный класс для работы с обеими стратегиями.
#     """
#     def __init__(self, strategy_type):
#         if strategy_type == "strategy_1":
#             self.strategy = Strategy1()
#         elif strategy_type == "strategy_2":
#             self.strategy = Strategy2()
#         else:
#             raise ValueError("Неизвестный тип стратегии")

#     async def process_signals(self, signals_dict, asset_id, token):
#         await self.strategy.process_signals(signals_dict, asset_id, token)



    # async def fetch_klines_for_symbols(self, session, asset_id, symbols, interval, fetch_limit=1):
    #     async def fetch_kline(symbol, fetch_limit):
    #         try:
    #             return symbol, await self.get_klines(session, symbol, interval, fetch_limit)
    #         except Exception as e:
    #             print(f"Error fetching klines for {symbol}: {e}")
    #             return symbol, None

    #     # Создаем задачи для всех символов
    #     tasks = [fetch_kline(symbol, fetch_limit) for symbol in symbols]

    #     # Выполняем задачи параллельно
    #     results = await asyncio.gather(*tasks, return_exceptions=True)

    #     # Обновляем словарь клиний
    #     for result in results:
    #         if isinstance(result, tuple):
    #             symbol, new_klines = result
    #             if new_klines is None or new_klines.empty:
    #                 print(f"No valid klines for {symbol}")
    #                 continue

    #             if asset_id not in self.klines_data_dict:
    #                 self.klines_data_dict[asset_id] = {}
    #             if symbol not in self.klines_data_dict[asset_id]:
    #                 self.klines_data_dict[asset_id][symbol] = pd.DataFrame(
    #                     columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    #                 )

    #             if fetch_limit == 1:
    #                 self.klines_data_dict[asset_id][symbol] = pd.concat(
    #                     [self.klines_data_dict[asset_id][symbol], new_klines]
    #                 ).drop_duplicates().tail(fetch_limit)
    #             else:
    #                 self.klines_data_dict[asset_id][symbol] = new_klines
    #         else:
    #             print(f"Exception occurred: {result}")



    # async def get_klines(self, session, symbol, interval, limit, api_key=None):
    #     """
    #     Загружает данные свечей (klines) для заданного символа.
    #     """
    #     params = {
    #         "symbol": symbol,
    #         "interval": interval,
    #         "limit": limit
    #     }
        
    #     headers = {}
    #     if api_key:
    #         headers["X-MBX-APIKEY"] = api_key  # Добавляем ключ в заголовки

    #     try:
    #         async with session.get(self.klines_url, params=params, headers=headers) as response:
    #             if response.status != 200:
    #                 self.log_error_loger(f"Failed to fetch klines: {response.status}, symbol: {symbol}")
    #                 return pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

    #             klines = await response.json()
    #             if not klines:
    #                 return pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

    #         # Преобразование данных в DataFrame
    #         data = pd.DataFrame(klines).iloc[:, :6]
    #         data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    #         data['Time'] = pd.to_datetime(data['Time'], unit='ms')  # Преобразуем метки времени
    #         data.set_index('Time', inplace=True)
    #         return data.astype(float)

    #     except Exception as ex:
    #         self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name}")
    #     return pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

            

            # in_position_long = self.cashe_data_book_dict[asset_id][symbol]["LONG"]["in_position"]
            # in_position_short = self.cashe_data_book_dict[asset_id][symbol]["SHORT"]["in_position"]









    # async def process_signals(self, session):
    #     """Ищем торговые сигналы и интегрируем их в структуру данных."""
    #     trades = []
    #     for asset_id, asset in self.assets_dict.items():
    #         trade_item = {}
    #         symbols = asset.get('symbols', [])                
    #         api_key = asset.get("BINANCE_API_PUBLIC_KEY")
    #         api_secret = asset.get("BINANCE_API_PRIVATE_KEY")   

    #         indicator_number = asset.get("indicator_number")     
            
    #         time_frame = asset.get(f"indicator_{indicator_number}").get("tfr_main")
    #         fetch_limit = asset.get(f"indicator_{indicator_number}").get("bb_period")
    #         std_rate = asset.get(f"indicator_{indicator_number}").get("std_rate") 

    #         if self.hot_symbols[asset_id]:
    #             symbols = [self.hot_symbols[asset_id]]

    #         if not self.time_frame_seconds:
    #             self.time_frame_seconds = self.interval_to_seconds("1m") 

    #         fetch_klines_limit = fetch_limit if self.is_new_interval() else 1        
    #         await self.fetch_klines_for_symbols(session, asset_id, symbols, time_frame, fetch_klines_limit, api_key)

    #         for symbol in symbols:
    #             tp_rate = self.cashe_data_book_dict[asset_id][symbol]["tp_rate"]
    #             sl_rate = self.cashe_data_book_dict[asset_id][symbol]["sl_rate"]
    #             df = self.klines_data_dict[asset_id][symbol]
    #             signals_dict = await self.calculate_signals(df, indicator_number, fetch_limit, std_rate, sl_rate, tp_rate)
    #             await self.strategy_executer(indicator_number, signals_dict, asset_id, symbol)

    #         async with self.async_lock:
    #             if not self.is_any_signal:
    #                 continue

    #             symb = self.hot_symbols[asset_id]
    #             if not symb:
    #                 continue

    #             is_opening_long = self.cashe_data_book_dict[asset_id][symb]["LONG"]["is_opening"]
    #             is_closing_long = self.cashe_data_book_dict[asset_id][symb]["LONG"]["is_closing"]
    #             is_opening_short = self.cashe_data_book_dict[asset_id][symb]["SHORT"]["is_opening"]                    
    #             is_closing_short = self.cashe_data_book_dict[asset_id][symb]["SHORT"]["is_closing"]

    #             trade_item["asset_id"] = asset_id
    #             trade_item["symbol"] = symb
    #             trade_item["margin_type"] = asset.get("margin_type")
    #             trade_item["leverage"] = asset.get("leverage")
    #             trade_item["api_key"] = api_key
    #             trade_item["api_secret"] = api_secret
                
    #             side = ""
    #             pos_side = ""

    #             if is_opening_long:
    #                 side = "BUY"                        
    #                 pos_side = "LONG"

    #                 print(f"side: {side}")
    #                 print(f"Pos side: {pos_side}")
    #                 print("Opening")
                

    #             elif is_closing_long:
    #                 side = "SELL"
    #                 pos_side = "LONG"
                
    #                 print(f"side: {side}")
    #                 print(f"Pos side: {pos_side}")
    #                 print("Closing")
                    

    #             if is_opening_short:
    #                 side = "SELL"
    #                 pos_side = "SHORT"
                    
    #                 print(f"side: {side}")
    #                 print(f"Pos side: {pos_side}")
    #                 print("Opening")
                

    #             elif is_closing_short:
    #                 side = "BUY"
    #                 pos_side = "SHORT"
                    
    #                 print(f"side: {side}")
    #                 print(f"Pos side: {pos_side}")
    #                 print("Closing")
                    
    #             if side:
    #                 trade_item["side"] = side
    #                 trade_item["position_side"] = pos_side

    #                 trade_item["qty"] = 0.0

    #                 if is_opening_long or is_opening_short:
    #                     if symb in self.busy_symbols_set:
    #                         continue
    #                     quantity_precision = self.cashe_data_book_dict[asset_id][symb]["qty_precision"]
    #                     depo = asset.get("depo")
    #                     cur_price = self.klines_data_dict[asset_id][symbol].get("Close").iloc[-1]
    #                     trade_item["qty"] = self.usdt_to_qnt_converter(depo, cur_price, quantity_precision)

    #                 else:
    #                     trade_item["qty"] = self.cashe_data_book_dict[asset_id][symb][pos_side].get("comul_qty", 0.0)

    #                 if trade_item["qty"]:
    #                     trades.append(trade_item) # Добавляем сет в очередь для торговли
    #                 else:
    #                     self.log_error_loger(f"Ошибка при попытке расчитать объем позиции. Asset Id: {asset_id}. symbol: {symbol}")                

    #         print(self.klines_data_dict[asset_id])

    #     self.is_any_signal = False
    #     return trades




# def aiohttp_connector(func):
#     @wraps(func)
#     async def wrapper(self, *args, **kwargs):
#         async with aiohttp.ClientSession() as session:
#             try:
#                 return await func(self, session, *args, **kwargs)
#             except Exception as ex:
#                 print(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")
#     return wrapper

# async def open_session(session=None, timeout=10):
#     """
#     Открытие aiohttp сессии с таймаутом.
    
#     :param session: Существующая сессия или None.
#     :param timeout: Время в секундах до таймаута для открытия сессии (по умолчанию 10 секунд).
#     """
#     if not session:
#         try:
#             timeout_obj = aiohttp.ClientTimeout(total=timeout)
#             session = aiohttp.ClientSession(timeout=timeout_obj)
#         except asyncio.TimeoutError:
#             print(f"Ошибка: Таймаут при открытии сессии. Таймаут: {timeout} секунд.")
#             raise
#     return session

# async def close_session(session=None, timeout=5):
#     """
#     Закрытие aiohttp сессии с таймаутом.
    
#     :param session: Сессия для закрытия.
#     :param timeout: Время в секундах до таймаута для закрытия сессии (по умолчанию 5 секунд).
#     """
#     if session:
#         try:
#             await asyncio.wait_for(session.close(), timeout=timeout)
#         except asyncio.TimeoutError:
#             print(f"Ошибка: Таймаут при закрытии сессии. Таймаут: {timeout} секунд.")
#             # Здесь можно выполнить дополнительные действия, например, принудительно закрыть сессию.
#         finally:
#             session = None
#     return None




    # async def go_filter(self, all_binance_tickers, coinsMarket_tickers):
    #     """Фильтрация тикеров, соответствующих условиям по объёму в USDT."""
    #     exclusion_contains_list = ['UP', 'DOWN', 'RUB', 'EUR']

    #     # Фильтрация тикеров
    #     def is_valid_ticker(ticker) -> bool:
    #         symbol = ticker['symbol'].upper()

    #         # Условия для отбора
    #         is_usdt_pair = symbol.endswith('USDT')
    #         no_exclusions = all(exclusion not in symbol for exclusion in exclusion_contains_list)

    #         # Проверяем объём в USDT
    #         try:
    #             quote_volume = float(ticker.get('quoteVolume', 0))
    #         except ValueError:
    #             return False

    #         sufficient_volume = quote_volume >= self.MIN_VOLUM_USDT

    #         # Учет CoinMarketCap
    #         if self.is_coinMarketCup:
    #             return is_usdt_pair and no_exclusions and sufficient_volume and symbol in coinsMarket_tickers
    #         return is_usdt_pair and no_exclusions and sufficient_volume

    #     # Применяем фильтр
    #     filtered_tickers = [ticker['symbol'] for ticker in all_binance_tickers if is_valid_ticker(ticker)]

    #     return filtered_tickers


                            # signals_counter += 1
                            # if indicator_number == 1:
                            #     if signals_counter == 2:
                            #         break
                            # elif indicator_number == 2:
                            #     if signals_counter == 1:


            # if self.busy_symbols_set:
            # async with self.async_lock:
            #     print("here cache_trade_data")
                                    
            #     for ass_id, symbols_dict in self.cashe_data_book_dict.items():
            #         # Фильтруем словарь, оставляя только символы, которые присутствуют в busy_symbols_set
            #         self.cashe_data_book_dict[ass_id] = {
            #             symbol: val for symbol, val in symbols_dict.items() if symbol in self.busy_symbols_set
            #         }
            #     print(f"self.cashe_data_book_dict: {self.cashe_data_book_dict}")

            # await self.cache_data_to_file(self.cashe_data_book_dict)