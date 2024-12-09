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
            
    async def process_order_temp(self, order_answer, asset_id, symbol, positionSide):
        """Обработка временного ордера и обновление состояния данных."""

        def orders_logger_handler() -> bool:
            """Обработка логирования результатов ордера."""
            if not order_answer:
                self.log_error_loger(
                    f"Asset Id: {asset_id}. Ошибка создания ордера. Ответ:\n{order_answer}. Символ: {symbol}"
                )
                return False

            try:
                now_time = self.get_date_time_now(self.tz_location)
                specific_keys = ["orderId", "symbol", "positionSide", "side", "executedQty", "avgPrice"]
                order_details = "\n".join(f"{k}: {order_answer[k]}" for k in specific_keys if k in order_answer)
                order_answer_str = f'Время создания ордера: {now_time}\n{order_details}'
            except Exception as ex:
                self.log_error_loger(
                    f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}"
                ) 
                return False

            if order_answer.get('status') in ['FILLED', 'NEW', 'PARTIALLY_FILLED']:
                self.log_info_loger(f"Asset Id: {asset_id}. Символ: {symbol}. {order_answer_str}", True)
                return True

            self.log_error_loger(
                f"Asset Id: {asset_id}. Ошибка статуса ордера. Ответ:\n{order_answer}. Символ: {symbol}"
            )
            return False

        # Извлечение данных из ордера
        # side = order_answer.get("side", side).upper()
        positionSide = order_answer.get("positionSide", positionSide).upper()
        executed_qty = float(order_answer.get("executedQty", 0.0))
        avg_price = float(order_answer.get("avgPrice", 0.0))

        # Получение данных символа
        asset_data = self.cashe_data_book_dict.get(asset_id, {}).get(symbol, {}).get(positionSide, {})
        is_opening = asset_data.get("is_opening", False)
        # print(f"is_opening, 59: {is_opening}")
        is_closing = asset_data.get("is_closing", False)
        # print(f"is_closing, 61: {is_closing}")

        async with self.async_lock:
            # Обработка ордера
            if not orders_logger_handler():
                if is_opening:
                    print("not orders_logger_handler()")
                    asset_data["in_position"] = False
            else:
                # Обновление данных позиции
                if is_opening:
                    # print("is_opening template")
                    asset_data.update({
                        "in_position": True,
                        "entry_point": avg_price,
                        "comul_qty": abs(executed_qty),                    
                        "is_opening": False,
                        "is_closing": False
                    })
                    # self.busy_symbols_set.add(symbol)
                    # print("self.busy_symbols_set.add(symbol)")

                elif is_closing:
                    # print("is_closing template")
                    asset_data.update({
                        "in_position": False,
                        "entry_point": 0.0,
                        "comul_qty": 0.0,                    
                        "is_opening": False,
                        "is_closing": False
                    })

            # Очистка символов, если ни одна позиция не открыта
            long_in_position = self.cashe_data_book_dict[asset_id][symbol]["LONG"]["in_position"]
            short_in_position = self.cashe_data_book_dict[asset_id][symbol]["SHORT"]["in_position"]
            if not (long_in_position or short_in_position):
                print(f"{symbol} is discard")
                # self.busy_symbols_set.discard(symbol)
                self.hot_symbols[asset_id] = ""
                asset_data["entry_point"] = 0.0
                asset_data["comul_qty"] = 0.0
                asset_data["is_opening"] = False
                asset_data["is_closing"] = False

    # /////////////
    async def hedg_temp(self, session):
        for asset_id, asset in self.assets_dict.items():  
            api_key = asset.get("BINANCE_API_PUBLIC_KEY")
            api_secret = asset.get("BINANCE_API_PRIVATE_KEY") 
            true_hedg = True
            await self.set_hedge_mode(session, true_hedg, asset_id, api_key, api_secret)

    async def place_order_template(self, session, trade):
        asset_id, symbol, margin_type, leverage, qty, side, position_side, api_key, api_secret = trade.get("asset_id"), trade.get("symbol"), trade.get("margin_type"), trade.get("leverage"), trade.get("qty"), trade.get("side"), trade.get("position_side"), trade.get("api_key"), trade.get("api_secret")

        # set_margin_type:
        await self.set_margin_type(session, asset_id, symbol, margin_type, api_key, api_secret)

        # set_leverage:
        await self.set_leverage(session, asset_id, symbol, leverage, api_key, api_secret)

        # make_order:
        return await self.make_order(session, asset_id, api_key, api_secret, symbol, qty, side, position_side)

    async def place_orders_gather(self, session, trades):
        """Размещает ордера."""
        # print(f"trades: {trades}")
        tasks = [self.place_order_template(session, trade) for trade in trades]
        if tasks:
            return await asyncio.gather(*tasks, return_exceptions=True)
        return []