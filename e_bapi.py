import time
import hmac
import hashlib
import pandas as pd
from d_utils import UTILS
import os
import inspect

class BINANCE_API(UTILS):
    def __init__(self):
        super().__init__()       
        self.create_order_url = self.cancel_order_url = 'https://fapi.binance.com/fapi/v1/order'
        self.change_trade_mode = 'https://fapi.binance.com/fapi/v1/positionSide/dual'
        self.exchangeInfo_url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
        self.klines_url = 'https://fapi.binance.com/fapi/v1/klines'
        self.set_margin_type_url = 'https://fapi.binance.com/fapi/v1/marginType'
        self.set_leverage_url = 'https://fapi.binance.com/fapi/v1/leverage'
        self.positions_url = 'https://fapi.binance.com/fapi/v2/positionRisk'
        self.positions2_url = 'https://fapi.binance.com/fapi/v2/account'
        self.all_tikers_url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
        self.get_all_orders_url = 'https://fapi.binance.com/fapi/v1/allOrders'
        self.cancel_all_orders_url = 'https://fapi.binance.com/fapi/v1/allOpenOrders'
        self.balance_url = 'https://fapi.binance.com/fapi/v2/balance'

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

    def get_signature(self, params, api_secret):
        params['timestamp'] = int(time.time() * 1000)
        params_str = '&'.join([f'{k}={v}' for k, v in params.items()])
        signature = hmac.new(bytes(api_secret, 'utf-8'), params_str.encode('utf-8'), hashlib.sha256).hexdigest()
        params['signature'] = signature
        return params
    
    # publis methods:    
    async def get_exchange_info(self, session):
        params = {'recvWindow': 20000}
        try:    
            async with session.get(self.exchangeInfo_url, params=params) as response:            
                if response.status != 200:
                    self.log_error_loger(f"Failed to fetch positions: {response.status}")
                return await response.json()  
        except Exception as ex:
            self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")

    async def get_all_tickers(self, session):
        params = {'recvWindow': 20000}
        try:
            async with session.get(self.all_tikers_url, params=params) as response:            
                if response.status != 200:
                    self.log_error_loger(f"Failed to fetch positions: {response.status}")
                return await response.json()  
        except Exception as ex:
            self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")

    async def get_klines(self, session, symbol, interval, limit, api_key=None):
        """
        Загружает данные свечей (klines) для заданного символа.
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        headers = {}
        if api_key:
            headers["X-MBX-APIKEY"] = api_key  # Добавляем ключ в заголовки

        try:
            async with session.get(self.klines_url, params=params, headers=headers) as response:
                if response.status != 200:
                    self.log_error_loger(f"Failed to fetch klines: {response.status}, symbol: {symbol}")
                    return pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

                klines = await response.json()
                if not klines:
                    return pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

            # Преобразование данных в DataFrame
            data = pd.DataFrame(klines).iloc[:, :6]
            data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
            data['Time'] = pd.to_datetime(data['Time'], unit='ms')  # Преобразуем метки времени
            data.set_index('Time', inplace=True)
            return data.astype(float)

        except Exception as ex:
            self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name}")
        return pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

    # private methods:        
    async def fetch_positions(self, session, api_key, api_secret):
        params = self.get_signature({'recvWindow': 20000}, api_secret)
        headers = {
            'X-MBX-APIKEY': api_key
        }
        async with session.get(self.positions2_url, headers=headers, params=params) as response:
            if response.status != 200:
                self.log_error_loger(f"Failed to fetch positions: {response.status}")
            return await response.json()        
                
    async def set_hedge_mode(self, session, true_hedg, asset_id, api_key, api_secret):
        try:
            params = {
                'dualSidePosition': 'true' if true_hedg else 'false',            
            }
            headers = {
                'X-MBX-APIKEY': api_key
            }
            params = self.get_signature(params, api_secret)
            async with session.post(self.change_trade_mode, headers=headers, params=params) as response:
                if response.status != 200:
                    self.log_error_loger(f"Asset Id: {asset_id}. Failed to set position mode: {response.status}")
                resp_j = await response.json()
                self.log_info_loger(f"Asset Id: {asset_id}. {resp_j}", True)
        except Exception as ex:
            self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")
        
        return {}        
    
    async def set_margin_type(self, session, asset_id, symbol, margin_type, api_key, api_secret):
        try:
            params = {
                'symbol': symbol,
                'marginType': margin_type,
                'recvWindow': 20000,
                'newClientOrderId': 'CHANGE_MARGIN_TYPE'
            }
            headers = {
                'X-MBX-APIKEY': api_key
            }
            params = self.get_signature(params, api_secret)
            async with session.post(self.set_margin_type_url, headers=headers, params=params) as response:
                await self.requests_logger(response, asset_id, "set_margin_type", symbol)
        except Exception as ex:
            self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")

        return {}

    async def set_leverage(self, session, asset_id, symbol, lev_size, api_key, api_secret):
        try:
            params = {
                'symbol': symbol,
                'recvWindow': 20000,
                'leverage': lev_size
            }
            headers = {
                'X-MBX-APIKEY': api_key
            }
            params = self.get_signature(params, api_secret)
            async with session.post(self.set_leverage_url, headers=headers, params=params) as response:
                await self.requests_logger(response, asset_id, "set_leverage", symbol)
            
        except Exception as ex:
            self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")
            
        return {}    

    async def make_order(self, session, asset_id, api_key, api_secret, symbol, qty, side, position_side, market_type="MARKET"):
        # print("Параметры запроса:...")
        # print(asset_id, api_key, api_secret, symbol, qty, side, position_side)
        try:
            params = {
                "symbol": symbol,
                "side": side,
                "type": market_type,
                "quantity": abs(qty),
                "positionSide": position_side,
                "recvWindow": 20000,
                "newOrderRespType": 'RESULT'
            }
            headers = {
                'X-MBX-APIKEY': api_key
            }           

            params = self.get_signature(params, api_secret)
            async with session.post(self.create_order_url, headers=headers, params=params) as response:
                return await self.requests_logger(response, asset_id, "place_order", symbol, position_side)
             
        except Exception as ex:
            self.log_error_loger(f"{ex} in {inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}")

        return {}, asset_id, symbol, position_side