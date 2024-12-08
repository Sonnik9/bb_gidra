import asyncio
import pandas as pd
from e_bapi import BINANCE_API
# import os
import inspect

class KlineFetcher(BINANCE_API):
    def __init__(self) -> None:
        super().__init__()

        # Декорируем методы с логированием исключений
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")  # Исключаем специальные методы
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

    async def fetch_klines_for_symbols(self, session, asset_id, symbols, interval, fetch_limit=1, suffix="", api_key=None):
        """
        Асинхронно получает свечи для списка символов и обновляет их в словаре.
        """
        async def fetch_kline(symbol):
            try:
                return symbol, await self.get_klines(session, symbol, interval, fetch_limit, api_key)
            except Exception as e:
                self.log_error_loger(f"Error fetching klines for {symbol}: {e}")
                return symbol, None

        # Создаем задачи и выполняем их параллельно
        tasks = [fetch_kline(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Обновляем словарь клиньев
        for symbol, new_klines in results:
            symbol = f"{symbol}{suffix}"
            if isinstance(new_klines, pd.DataFrame) and not new_klines.empty:
                # Если fetch_limit == 1, обновляем последний элемент
                if fetch_limit == 1 and symbol in self.klines_data_dict.get(asset_id, {}):
                    last_index = self.klines_data_dict[asset_id][symbol].index[-1]
                    self.klines_data_dict[asset_id][symbol].at[last_index, "High"] = new_klines["High"].iloc[-1]
                    self.klines_data_dict[asset_id][symbol].at[last_index, "Low"] = new_klines["Low"].iloc[-1]
                    self.klines_data_dict[asset_id][symbol].at[last_index, "Open"] = new_klines["Open"].iloc[-1]
                    self.klines_data_dict[asset_id][symbol].at[last_index, "Close"] = new_klines["Close"].iloc[-1]
                else:
                    self.klines_data_dict.setdefault(asset_id, {})[symbol] = new_klines
            else:
                self.log_error_loger(f"Invalid klines data for {symbol}: {type(new_klines)}, content: {new_klines}")


class INDICATORS(KlineFetcher):
    def __init__(self) -> None:
        super().__init__()
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

    def calculate_bollinger_middle(self, df, bb_period):
        df['bb_middle'] = df['Close'].rolling(window=bb_period).mean()
        return df

    def calculate_bollinger_bands(self, df, bb_period, bollinger_std, suffix=''):
        std_col = f'std{suffix}'
        upper_col = f'bb_upper{suffix}'
        lower_col = f'bb_lower{suffix}'
        # print(f"bollinger_std: {bollinger_std}")
        df['bb_middle'] = df['Close'].rolling(window=bb_period).mean()
        df[std_col] = df['Close'].rolling(window=bb_period).std()
        df[upper_col] = df['bb_middle'] + (bollinger_std * df[std_col])
        df[lower_col] = df['bb_middle'] - (bollinger_std * df[std_col])
        return df
    
    def check_rate(self, rate, min_rate, strategy_number):
        if rate <= min_rate:
            self.log_error_loger(
                f"Коэффициент сратегии № {strategy_number} должен быть больше {min_rate}!"
            )
            self.stop_bot = True
            return False
        return True

    async def calculate_signals(self, df, strategy_number, bb_period, basik_std, sl_rate=None, tp_rate=None):

        if len(df) < bb_period:
            self.log_error_loger(f"Недостаточно данных для расчета. Требуется минимум {bb_period} строк.")
            return {}
        bb_period = bb_period - 5

        signals_dict = {}
        last_close_price = df["Close"].iloc[-1]        
        prelast_close_price = df["Close"].iloc[-2]
        # if self.hot_symbols["1"]:
        #     print(df)
        #     print(f"symbol: {self.hot_symbols["1"]}")
        #     print(f"last_close_price: {last_close_price}")
        #     print(f"prelast_close_price: {prelast_close_price}")

        df = self.calculate_bollinger_middle(df, bb_period)
        # df = self.calculate_bollinger_bands(df, bb_period, basik_std)

        if strategy_number == 1:
            if sl_rate is not None:
                if not self.check_rate(self, sl_rate, 0, strategy_number):
                    return {}
                
                sl_suffix = f'_sl_{sl_rate}'
                df = self.calculate_bollinger_bands(df, bb_period, basik_std * sl_rate, suffix=sl_suffix)

                signals_dict.update(
                    {
                        "sl_short": (last_close_price > df[f'bb_upper{sl_suffix}'].iloc[-1]),
                        "sl_long": (last_close_price < df[f'bb_lower{sl_suffix}'].iloc[-1]),
                    }
                )
                
            if tp_rate is not None:
                if not self.check_rate(self, tp_rate, 0, strategy_number):
                    return {}
                
                tp_suffix = f'_tp_{tp_rate}'            
                df = self.calculate_bollinger_bands(df, bb_period, basik_std * tp_rate, suffix=tp_suffix)

                signals_dict.update(
                    {
                        "tp_long": (last_close_price > df[f'bb_upper{tp_suffix}'].iloc[-1]),
                        "tp_short": (last_close_price < df[f'bb_lower{tp_suffix}'].iloc[-1]),
                    }

                )

            signals_dict.update(
                {
                    "middle_long_cross": (last_close_price > df['bb_middle'].iloc[-1]) and 
                                        (prelast_close_price < df['bb_middle'].iloc[-2]),
                    "middle_short_cross": (last_close_price < df['bb_middle'].iloc[-1]) and 
                                        (prelast_close_price > df['bb_middle'].iloc[-2]),
                }
            )        

            if sl_rate and tp_rate:
                return signals_dict

        elif strategy_number == 2:
            if sl_rate is not None:
                if not self.check_rate(self, sl_rate, 1, strategy_number):
                    return {}              
               
                sl_suffix = f'_sl_{sl_rate}'
                df = self.calculate_bollinger_bands(df, bb_period, basik_std * sl_rate, suffix=sl_suffix)

                signals_dict.update(
                    {
                        "sl_short": (last_close_price > df[f'bb_upper{sl_suffix}'].iloc[-1]),
                        "sl_long": (last_close_price < df[f'bb_lower{sl_suffix}'].iloc[-1]),
                    }
                )   

        df = self.calculate_bollinger_bands(df, bb_period, basik_std)
        signals_dict.update(
            {
                "upper_cross": (last_close_price > df[f'bb_upper'].iloc[-1]),
                "lower_cross": (last_close_price < df[f'bb_lower'].iloc[-1])
            }
        )

        return signals_dict

class Strategiess(INDICATORS):
    def __init__(self):
        super().__init__()
     
        # Декорируем методы с логированием исключений
        methods_to_wrap = [
            method_name for method_name, _ in inspect.getmembers(self, predicate=inspect.ismethod)
            if not method_name.startswith("__")
        ]
        for method_name in methods_to_wrap:
            setattr(self, method_name, self.log_exceptions_decorator(getattr(self, method_name)))

    async def _handle_retrade(self, asset_id, symbol, position_type):
        """
        Обрабатывает противоположное действие при уникальном сигнале "retrade".
        """
        opposite_position_type = "SHORT" if position_type == "LONG" else "LONG"

        async with self.async_lock:
            self.cashe_data_book_dict[asset_id][symbol][opposite_position_type]["is_opening"] = True

        # Логируем событие retrade
        self.log_info_loger(
            f"Asset Id: {asset_id}. Symbol: {symbol}. Opening position in opposite direction. "
            f"Time: {self.get_date_time_now(self.tz_location)}", 
            True
        )

    async def process_position(self, position_type, action, signal_reason, asset_id, symbol, unik_action=None):
        """
        Обрабатывает действия с позициями (открытие/закрытие).
        """
        # Проверяем конфликт символов в горячих символах
        async with self.async_lock:
            if self.hot_symbols and any(asset_id != ass_id and symbol == s for ass_id, s in self.hot_symbols.items()):
                return

            # Обновляем состояние сигналов и данных
            self.is_any_signal = True
            self.hot_symbols[asset_id] = symbol
            self.cashe_data_book_dict[asset_id][symbol][position_type][action] = True

        # Логируем основное событие
        self.log_info_loger(
            f"Asset Id: {asset_id}. Symbol: {symbol}. {signal_reason}. Time: {self.get_date_time_now(self.tz_location)}"
        )

        # Обрабатываем уникальное действие, если указано
        if unik_action == "retrade":
            await self._handle_retrade(asset_id, symbol, position_type)
   
    async def strategy_1(self, signals_dict, asset_id, symbol):
        """
        Реализация стратегии 1.
        """
        print(signals_dict)
        in_position_long = self.cashe_data_book_dict[asset_id][symbol]["LONG"]["in_position"]
        in_position_short = self.cashe_data_book_dict[asset_id][symbol]["SHORT"]["in_position"]
        is_tp = self.cashe_data_book_dict[asset_id][symbol]["tp_rate"]
        is_sl = self.cashe_data_book_dict[asset_id][symbol]["sl_rate"]

        # Обработка длинных позиций
        if in_position_long:
            if is_tp and signals_dict["tp_long"]:
                await self.process_position(
                    "LONG", "is_closing", "Закрываем лонг по тейк-профиту", asset_id, symbol
                )
            elif signals_dict["upper_cross"]:
                await self.process_position(
                    "LONG", "is_closing", "Закрываем лонг по пересечению с верхней линией", asset_id, symbol
                )
            elif is_sl and signals_dict["sl_long"]:
                await self.process_position(
                    "LONG", "is_closing", "Закрываем лонг по стоп-лоссу", asset_id, symbol
                )

        # Обработка коротких позиций
        if in_position_short:
            if is_tp and signals_dict["tp_short"]:
                await self.process_position(
                    "SHORT", "is_closing", "Закрываем шорт по тейк-профиту", asset_id, symbol
                )
            elif signals_dict["lower_cross"]:
                await self.process_position(
                    "SHORT", "is_closing", "Закрываем шорт по пересечению с нижней линией", asset_id, symbol
                )
            elif is_sl and signals_dict["sl_short"]:
                await self.process_position(
                    "SHORT", "is_closing", "Закрываем шорт по стоп-лоссу", asset_id, symbol
                )

        # Открытие новых позиций
        if signals_dict["middle_long_cross"] or signals_dict["middle_short_cross"]:
            # print("is candidate to open pos")
            if not in_position_long:
                await self.process_position(
                    "LONG", "is_opening", "Открываем новую лонг позицию", asset_id, symbol
                )
            if not in_position_short:
                await self.process_position(
                    "SHORT", "is_opening", "Открываем новую шорт позицию", asset_id, symbol
                )

    async def strategy_2(self, signals_dict, asset_id, symbol):
        """
        Реализация стратегии 2.
        """
        in_position_long = self.cashe_data_book_dict[asset_id][symbol]["LONG"]["in_position"]
        in_position_short = self.cashe_data_book_dict[asset_id][symbol]["SHORT"]["in_position"]
        is_sl = self.cashe_data_book_dict[asset_id][symbol]["sl_rate"]

        if in_position_long:  # Активна длинная позиция
            if signals_dict["upper_cross"]:
                await self.process_position(
                    "LONG", "is_closing", "Закрываем Лонг по пересечению с верхней линией", asset_id, symbol, "retrade"
                )
            elif is_sl and signals_dict["sl_long"]:
                await self.process_position(
                    "LONG", "is_closing", "Закрываем Лонг по стоп-лоссу", asset_id, symbol
                )
        elif in_position_short:  # Активна короткая позиция
            if signals_dict["lower_cross"]:
                await self.process_position(
                    "SHORT", "is_closing", "Закрываем Шорт по пересечению с нижней линией", asset_id, symbol, "retrade"
                )
            elif is_sl and signals_dict["sl_short"]:
                await self.process_position(
                    "SHORT", "is_closing", "Закрываем Шорт по стоп-лоссу", asset_id, symbol
                )
        else:  # Позиции отсутствуют
            if signals_dict["lower_cross"]:
                await self.process_position(
                    "LONG", "is_opening", "Открываем Лонг", asset_id, symbol
                )
            elif signals_dict["upper_cross"]:
                await self.process_position(
                    "SHORT", "is_opening", "Открываем Шорт", asset_id, symbol
                )

    async def strategy_executer(self, strategy_num, signals_dict, asset_id, symbol):
        """
        Выполняет указанную стратегию.
        """
        if strategy_num == 1:
            await self.strategy_1(signals_dict, asset_id, symbol)
        elif strategy_num == 2:
            await self.strategy_2(signals_dict, asset_id, symbol)
        else:
            self.log_error_loger(f"Ошибка: неизвестная стратегия: {strategy_num}", True)