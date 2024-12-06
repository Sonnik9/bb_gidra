
from a_init_params import VARIABLES
import os
import inspect

current_file = os.path.basename(__file__)

class Total_Logger(VARIABLES):
    def log_info_loger(self, data, is_print=False):
        self.log_info_list.append(data)
        if is_print:
            print(data)

    def log_error_loger(self, data, is_print=False):
        self.general_error_logger_list.append(data)
        if is_print:
            print(data)

    def log_exception(self, ex):
        """Логирование исключений с указанием точного места ошибки."""
        # Получаем информацию об ошибке
        exception_message = str(ex)
        # Получаем стек вызовов
        stack = inspect.trace()
        
        # Берем последний фрейм, который соответствует месту, где произошла ошибка
        if stack:
            last_frame = stack[-1]
            file_name = last_frame.filename
            line_number = last_frame.lineno
            func_name = last_frame.function
            
            message = f"Error occurred in '{func_name}' at file '{file_name}', line {line_number}: {exception_message}"
            # print(message)
            self.general_error_logger_list.append(message)

    def sync_log_exceptions_decorator(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                self.log_exception(ex)

        return wrapper

    def log_exceptions_decorator(self, func):
        """Универсальный декоратор для логирования исключений."""
        
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as ex:
                async with self.async_lock:
                    self.log_exception(ex)

        return async_wrapper if inspect.iscoroutinefunction(func) else self.sync_log_exceptions_decorator(func)

class Requests_Logger(Total_Logger):
    async def get_status_order_response(self, resp):
        """Проверяет и возвращает данные запроса и статус."""
        try:
            return await resp.json(), resp.status
        except Exception as e:
            print(f"Ошибка при разборе JSON: {e}")
            return None, None
        
    async def log_error(self, asset_id, target, error_text, error_code, symbol=None):
        """Логирует ошибку в ответе."""
        error_dict = {
                "asset_id": asset_id,
                "error_text": error_text,
                "error_code": error_code,
                "target": target
        }
        if symbol:
            error_dict["symbol"] = symbol
        async with self.async_lock:
            self.log_response_list.append(error_dict)

    async def log_request(self, is_success, data, status, asset_id, target, symbol=None):
        """Логирование успешных и ошибочных запросов."""
        log_entry = {
            "id": asset_id,
            "target": target,            
            "request_text" if is_success else "error_text": data,
            "request_code" if is_success else "error_code": status,
        }
        if symbol:
            log_entry["symbol"] = symbol

        if target == "place_order":
            async with self.async_lock:
                (self.log_succ_order_list if is_success else self.log_error_order_list).append(log_entry)
        else:
            async with self.async_lock:
                self.log_response_list.append(log_entry)

    async def requests_logger(self, resp, asset_id, target, symbol=None):
        """Обработка и логирование данных запроса."""
        if resp is None:
            # Логируем ошибку, если resp равен None
            await self.log_error(target, "Response is None", "N/A")
            return None

        resp_j, status = await self.get_status_order_response(resp)

        # Определяем успешность запроса
        is_success = isinstance(resp_j, dict) and status == 200

        # Логируем результат запроса
        await self.log_request(
            is_success,
            resp_j if is_success else await resp.text(),
            status,        
            asset_id,            
            target,
            symbol
        )

        return resp_j, asset_id, symbol