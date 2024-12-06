    
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
