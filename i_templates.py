import asyncio
from h_control_data import DataController
import inspect

class TEMP(DataController):
    def __init__(self):
        super().__init__()
        self._decorate_methods_with_logging()

    def _decorate_methods_with_logging(self):
        """Оборачивает методы в декоратор логирования исключений."""
        methods = [
            name for name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not name.startswith("__")
        ]
        for method_name in methods:
            original_method = getattr(self, method_name)
            setattr(self, method_name, self.log_exceptions_decorator(original_method))
        
    async def process_order_temp(self, order_answer, asset_id, symbol, side):
        def orders_logger_handler():
            if order_answer:
                specific_key_list = ["orderId", "symbol", "positionSide", "side", "executedQty", "avgPrice"]
                try:
                    now_time = self.get_date_time_now(self.tz_location)
                    order_details = "\n".join(f"{k}: {v}" for k, v in order_answer.items() if k in specific_key_list)
                    order_answer_str = f'Время создания ордера: {now_time}\n{order_details}'
                except Exception as ex:
                    self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")            

                # Проверка статуса ордера
                if order_answer.get('status') in ['FILLED', 'NEW', 'PARTIALLY_FILLED']:
                    self.log_info_loger(f"Asset Id: {asset_id}. Символ: {symbol}. {order_answer_str}", True)
                    return True

            # Логирование ошибки
            self.log_error_loger(f"Asset Id: {asset_id}. При попытке создания ордера возникла ошибка. Текст ответа:\n {order_answer}. Символ: {symbol}")
            return False
        
        # Обработка полученных данных
        side = order_answer.get("side", side).upper()
        executed_qty = float(order_answer.get("executedQty", 0.0))
        avg_price = float(order_answer.get("avgPrice", 0.0))

        # Извлечение информации с безопасным доступом
        asset_data = self.cashe_data_book_dict.get(asset_id, {}).get(symbol, {}).get(side, {})
        is_opening = asset_data.get("is_opening", False)
        is_closing = asset_data.get("is_closing", False)

        async with self.async_lock:
            
            # Если ордер не был успешно обработан, сбрасываем флаги
            if not orders_logger_handler():
                if is_opening:
                    self.cashe_data_book_dict[asset_id][symbol][side]["in_position"] = False
            else:
                # Обновление данных в зависимости от типа ордера
                if is_opening:
                    self.cashe_data_book_dict[asset_id][symbol][side]["in_position"] = True            
                    self.cashe_data_book_dict[asset_id][symbol][side]["comul_qty"] = executed_qty
                    self.cashe_data_book_dict[asset_id][symbol][side]["entry_point"] = avg_price
                    self.busy_symbols_set.add(symbol)

                elif is_closing:
                    self.cashe_data_book_dict[asset_id][symbol][side]["in_position"] = False          
                    self.cashe_data_book_dict[asset_id][symbol][side]["comul_qty"] = 0.0
                    self.cashe_data_book_dict[asset_id][symbol][side]["entry_point"] = 0.0             
                    self.busy_symbols_set.discard(symbol)
                    self.hot_symbols[asset_id] = ""

            # Сброс флагов
            self.cashe_data_book_dict[asset_id][symbol][side]["is_opening"] = False
            self.cashe_data_book_dict[asset_id][symbol][side]["is_closing"] = False

    # /////////////
    async def hedg_temp(self, session):
        for asset_id, asset in self.assets_dict.items():  
            api_key = asset.get("BINANCE_API_PUBLIC_KEY")
            api_secret = asset.get("BINANCE_API_PRIVATE_KEY") 
            true_hedg = True
            await self.set_hedge_mode(session, true_hedg, asset_id, api_key, api_secret)

    async def place_order_template(self, session, **trade):
        asset_id, symbol, margin_type, leverage, qty, side, position_side, api_key, api_secret = trade.get("asset_id"), trade.get("symbol"), trade.get("margin_type"), trade.get("leverage"), trade.get("qty"), trade.get("side"), trade.get("position_side"), trade.get("api_key"), trade.get("api_secret")

        # set_margin_type:
        await self.set_margin_type(session, asset_id, symbol, margin_type, api_key, api_secret)

        # set_leverage:
        await self.set_leverage(session, asset_id, symbol, leverage, api_key, api_secret)

        # make_order:
        return await self.make_order(session, asset_id, api_key, api_secret, symbol, qty, side, position_side)

    async def place_orders_gather(self, session, trades):
        """Размещает ордера."""
        tasks = [self.place_order_template(session, trade) for trade in trades]
        if tasks:
            return await asyncio.gather(*tasks, return_exceptions=True)
        return []