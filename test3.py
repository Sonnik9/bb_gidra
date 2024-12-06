# import asyncio
# import aiohttp
# from datetime import datetime as dttm
# from typing import List, Tuple, Dict
# from renew_data import ReneveData
# import os
# import inspect

# current_file = os.path.basename(__file__)

# class TEMP(ReneveData):
#     def __init__(self) -> None:
#         super().__init__()
#         # Декорируем методы с логированием исключений
#         methods_to_wrap = [
#             method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
#             if not method_name.startswith("__")  # Исключаем специальные методы
#         ]
#         for method_name in methods_to_wrap:
#             setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

#     async def trade_setup_template(self, session, trading_data_service_list) -> None:
#         async def trade_setup_unit(session, symbol) -> None:
#             try:              
#                 self.log_info_list.append(await self.set_margin_type(session, symbol))
#                 self.log_info_list.append(await self.set_leverage(session, symbol))
#             except Exception as ex:
#                 self.log_info_loger(
#                     f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}"
#                 )

#         tasks = [
#             trade_setup_unit(session, symbol_item.get("symbol"))
#             for symbol_item in trading_data_service_list 
#             if symbol_item.get("first_trade") and symbol_item.get("symbol")
#         ]
        
#         if tasks:
#             await asyncio.gather(*tasks)

#     async def is_closing_positions_template(self, session: aiohttp.ClientSession, pos_num: int, trading_data_service_list: List, current_pos_viewer_flag: bool = False) -> List:
#         exception_symbol_list = []

#         tasks = [
#             self.is_closing_position_true(session, symbol_item.get("symbol"), symbol_item[f"position_{pos_num}_side"])
#             for symbol_item in trading_data_service_list
#             if symbol_item.get("symbol")
#         ]

#         if tasks:
#             is_closing_positions_symbol_list = await asyncio.gather(*tasks)

#             for symbol_item in trading_data_service_list:
#                 for is_closed, symb in is_closing_positions_symbol_list:
#                     if symbol_item["symbol"] == symb:
#                         if current_pos_viewer_flag:
#                             if is_closed:
#                                 exception_symbol_list.append(symb)
#                                 break
#                         else:
#                             should_open, should_others = self.should_open_position(symbol_item)                             
#                             if (self.should_close_position(symbol_item) and is_closed) or \
#                             ((should_open and not should_others) and not is_closed):
#                                 exception_symbol_list.append(symb)
#                                 break

#         return exception_symbol_list
        
#     def should_open_position(self, symbol_item: Dict) -> bool:
#        return (symbol_item.get("is_opening_1_pos") or symbol_item.get("is_opening_2_pos")), (symbol_item.get("is_aver_down"))

#     def should_close_position(self, symbol_item: Dict) -> bool:
#         return symbol_item.get("is_closing_1_pos") or symbol_item.get("is_closing_2_pos")
       
#     def get_side(self, symbol_item: Dict, pos_number: int) -> None:
#         position_side = symbol_item.get(f"position_{pos_number}_side")
#         if symbol_item.get("is_re_trade"):
#             return "SELL" if position_side == "LONG" else "BUY"
#         should_open, _ = self.should_open_position(symbol_item)
#         should_close = self.should_close_position(symbol_item)
#         if should_close or should_open:                   
#             if should_close:
#                 return "SELL" if position_side == "LONG" else "BUY"
#             elif should_open:
#                 return "BUY" if position_side == "LONG" else "SELL"
#         return None
    
#     def orders_logger_hundler(self, order_answer, symbol):
#         if order_answer:
#             specific_key_list = ["orderId", "symbol", "positionSide", "side", "executedQty", "avgPrice"]
#             try:
#                 now_time = dttm.now(self.local_tz).strftime('%Y-%m-%d %H:%M:%S')
#                 order_details = "\n".join(f"{k}: {v}" for k, v in order_answer.items() if k in specific_key_list)
#                 order_answer_str = f'Время создания ордера: {now_time}\n{order_details}'
#             except Exception as ex:
#                 self.log_info_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")
        

#             if order_answer.get('status') in ['FILLED', 'NEW', 'PARTIALLY_FILLED']:
#                 self.log_info_loger(order_answer_str, True)
#                 return True

#         self.log_info_loger(f"При попытке создания ордера возникла ошибка. Текст ответа:\n {order_answer}. Символ: {symbol}")
#         return False

# import asyncio
# from decimal import Decimal, getcontext, ROUND_DOWN
# from h_control_data import DataController
# import os
# # import inspect

# # Устанавливаем глобальную точность Decimal
# getcontext().prec = 20

# class TEMP(DataController):
#     def __init__(self):
#         super().__init__()

    # def print_order_data(self, place_market_order_resp_j, asset_id):
    #     """Печатает данные ордера или ошибку."""
            
    #     specific_key_list = [
    #         "orderId", "status", "symbol", "side", 
    #         "executedQty", "cummulativeQuoteQty", "transactTime"
    #     ]
    #     order_details = "\n".join(
    #         f"{k}: {v}" for k, v in place_market_order_resp_j.items() if k in specific_key_list
    #     )
    #     # Время транзакции для Binance
    #     timestamp = place_market_order_resp_j.get("transactTime")

    #     # Проверяем и конвертируем timestamp в дату
    #     if timestamp:
    #         try:
    #             now_time = self.milliseconds_to_datetime(int(timestamp), self.tz_location)
    #         except ValueError as ve:
    #             self.general_error_logger_list.append(f"Ошибка в {os.path.basename(__file__)}: {ve}. Неверный формат времени: {timestamp}")               
    #             now_time = None
    #     else:
    #         now_time = None

    #     # Печать результатов
    #     print(f"\nAsset Id: {asset_id}. Время ордера: {now_time}\nСтатус ответа: 200\nДанные ордера:\n{order_details}\n")
 
    # async def process_order(self, order_data, asset_id):
    #     if not order_data:
    #         return

    #     # Проверяем успешность ордера
    #     if order_data.get("status") != "FILLED":
    #         self.log_info_list.append(f"Asset Id: {asset_id}. Ордер {order_data.get('orderId')} не выполнен успешно. Статус: {order_data.get('status')}")
    #         return

    #     self.print_order_data(order_data, asset_id)   

    #     token = order_data.get("symbol", "").upper().replace("USDT", "")
    #     if not token:
    #         self.log_info_list.append("Не удалось извлечь символ из респонса ордера")

    #     # Извлекаем тип операции и общую сумму
    #     side = order_data.get("side")
    #     cummulative_quote_qty = float(order_data.get("cummulativeQuoteQty", 0.0))

    # async def place_order_template(self, session, trade_item):
    #     """
    #     Шаблон для размещения ордера на Binance Spot (и потенциально Futures).
    #     """
    #     resp, asset_id = None, trade_item.get("asset_id")
    #     symbol = trade_item.get("symbol")
    #     token = symbol.replace("USDT", "")
    #     token_data = self.cashe_data_book_dict[asset_id].get(token, {})
    #     qty_precision = token_data.get("qty_precision", 0)
    #     has_futures = trade_item.get("futures", False)
    #     bin_publik_key = trade_item.get("BINANCE_API_PUBLIC_KEY")
    #     bin_private_key = trade_item.get("BINANCE_API_PRIVATE_KEY")    

    #     # Получаем данные для ордера
    #     usdt_order_size = Decimal(trade_item.get("usdt_order_size", 0))
    #     last_price = await self.get_last_price_template(session, symbol, has_futures)

    #     if not (last_price and usdt_order_size > 0):
    #         self.general_error_logger_list.append("Не удалось получить последнюю цену или некорректный размер ордера. Пропуск торговли.")
    #         return None

    #     last_price = Decimal(last_price)

    #     # Рассчитываем количество
    #     qty_size = usdt_order_size / last_price

    #     if not has_futures:
    #         # Обрабатываем спот-ордер
    #         side = trade_item.get("side", None)
            
    #         if side == "SELL":
    #             # Проверяем доступное количество для SELL
    #             cur_spot_quote_amount = Decimal(token_data.get("cur_spot_quote_amount", 0))
    #             if qty_size > cur_spot_quote_amount:
    #                 self.cashe_data_book_dict[asset_id][token]["cur_usdt_supply"] = token_data.get("start_usdt_supply", 0)
    #                 qty_size = cur_spot_quote_amount
    #                 self.general_error_logger_list.append(f"Размер SELL уменьшен до доступного количества: {float(qty_size)}")

    #         size = round(float(qty_size), qty_precision)

    #         # Размещение спотового ордера
    #         resp = await self.place_binance_market_order(
    #             session=session,
    #             symbol=symbol,
    #             size=size,
    #             side=side,
    #             asset_id=asset_id,
    #             bin_publik_key=bin_publik_key,
    #             bin_private_key=bin_private_key,
    #             quoteType='q'
    #         )
    #     else:
    #         # Заготовка для фьючерсных ордеров
    #         pass

    #     return resp, asset_id, has_futures

    # async def place_orders_gather(self, session, trades):
    #     """Размещает ордера."""
    #     tasks = [self.place_order_template(session, trade) for trade in trades]
    #     if tasks:
    #         return await asyncio.gather(*tasks, return_exceptions=True)
    #     return []
# from decimal import Decimal, getcontext, ROUND_DOWN
# # Устанавливаем глобальную точность Decimal
# getcontext().prec = 20