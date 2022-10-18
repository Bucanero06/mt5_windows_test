import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from logger_tt import logger

nombre = 63329463
clave = 'odts6pdi'
servidor = 'MetaQuotes-Demo'
path = r"C:\Program Files\MetaTrader\terminal64.exe"


class Basic_funcs():

    def __init__(self, nombre, clave, servidor, path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path

    @staticmethod
    def info_account():

        '''Desarrollada por Max'''

        mt5.initialize(login=nombre, password=clave, server=servidor, path=path)
        cuentaDict = mt5.account_info()._asdict()
        balance = cuentaDict["balance"]
        profit_account = cuentaDict["profit"]
        equity = cuentaDict["equity"]
        free_margin = cuentaDict["margin_free"]

        return balance, profit_account, equity, free_margin

    @staticmethod
    def extract_data(par, periodo, cantidad):
        '''
        Función para extraer los datos de MT5 y convertitlos en un DataFrame

        # Parámetros
        
        - par: Activo a extraer
        - periodo: M1, M5...etc
        - cantidad: Entero con el número de registros a extraer

        '''
        # mt5.initialize(login = nombre, password = clave, server = servidor, path = path)
        if not mt5.initialize(login=nombre, password=clave, server=servidor, path=path):
            logger.error("initialize() failed")
            mt5.shutdown()

        # request connection status and parameters
        # get data on MetaTrader 5 version
        rates = mt5.copy_rates_from_pos(par, periodo, 0, cantidad)
        tabla = pd.DataFrame(rates)
        if len(tabla) == 0:
            return None
        tabla['time'] = pd.to_datetime(tabla['time'], unit='s')
        tabla['minutes'] = range(cantidad)

        # logger.info(f'Los datos de {par} han sido extraidos correctamente')
        return tabla

    @staticmethod
    def open_operations(par, volumen, tipo_operacion, nombre_bot, sl=None, tp=None):

        if (sl == None) and (tp == None):

            orden = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": par,
                "volume": volumen,
                "type": tipo_operacion,
                "magic": 202204,
                "comment": nombre_bot,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "price": mt5.symbol_info_tick(
                    par).ask if tipo_operacion == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(par).bid,

            }
            # mt5.order_send(orden)
            a = mt5.order_send(orden)
            logger.info(a)
            # logger.info('Se ejecutó una', tipo_operacion, 'con un volumen de', volumen)
            logger.info(f'Se ejecutó una {tipo_operacion} con un volumen de {volumen}')

        elif (sl == None) and (tp != None):
            orden = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": par,
                "tp": tp,
                "volume": volumen,
                "type": tipo_operacion,
                "magic": 202204,
                "comment": nombre_bot,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "price": mt5.symbol_info_tick(
                    par).ask if tipo_operacion == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(par).bid,

            }

            # mt5.order_send(orden)
            a = mt5.order_send(orden)
            logger.info(a)
            # logger.info('Se ejecutó una', tipo_operacion, 'con un volumen de', volumen)
            logger.info(f'Se ejecutó una {tipo_operacion} con un volumen de {volumen}')

        elif (sl != None) and (tp == None):
            orden = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": par,
                "sl": sl,
                "volume": volumen,
                "type": tipo_operacion,
                "magic": 202204,
                "comment": nombre_bot,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "price": mt5.symbol_info_tick(
                    par).ask if tipo_operacion == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(par).bid,

            }

            # mt5.order_send(orden)
            a = mt5.order_send(orden)
            logger.info(a)

        elif (sl != None) and (tp != None):
            orden = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": par,
                "sl": sl,
                "tp": tp,
                "volume": volumen,
                "type": tipo_operacion,
                "magic": 202204,
                "comment": nombre_bot,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "price": mt5.symbol_info_tick(
                    par).ask if tipo_operacion == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(par).bid,

            }

            # mt5.order_send(orden)
            a = mt5.order_send(orden)
            logger.info(a)
            # logger.info('Se ejecutó una', tipo_operacion, 'con un volumen de', volumen)
            logger.info(f'Se ejecutó una {tipo_operacion} con un volumen de {volumen}')

    def close_all_open_operations(self, par=None):

        df_open_positions = self.get_all_positions()
        len_d_pos = len(df_open_positions)
        if len_d_pos > 0:
            if par == None:
                lista_ops = df_open_positions['ticket'].unique().tolist()
            else:
                df_open_positions = df_open_positions[df_open_positions['symbol'] == par]
                lista_ops = df_open_positions['ticket'].unique().tolist()

            for operacion in lista_ops:
                df_operacion = df_open_positions[df_open_positions['ticket'] == operacion]
                price_close = mt5.symbol_info_tick(df_operacion['symbol'].item()).bid
                tipo_operacion = df_operacion['type'].item()
                simbolo_operacion = df_operacion['symbol'].item()
                volumen_operacion = df_operacion['volume'].item()
                # 1 Sell / 0 Buy
                if tipo_operacion == 1:
                    tip_op = mt5.ORDER_TYPE_BUY
                    close_request = {
                        'action': mt5.TRADE_ACTION_DEAL,
                        'symbol': simbolo_operacion,
                        'volume': volumen_operacion,
                        'type': tip_op,
                        'position': operacion,
                        'price': price_close,
                        'comment': 'Cerrar posiciones',
                        'type_filling': mt5.ORDER_FILLING_FOK
                    }

                    mt5.order_send(close_request)
                if tipo_operacion == 0:
                    tip_op = mt5.ORDER_TYPE_SELL
                    close_request = {
                        'action': mt5.TRADE_ACTION_DEAL,
                        'symbol': simbolo_operacion,
                        'volume': volumen_operacion,
                        'type': tip_op,
                        'position': operacion,
                        'price': price_close,
                        'comment': 'Cerrar posiciones',
                        'type_filling': mt5.ORDER_FILLING_FOK
                    }

                    mt5.order_send(close_request)

    @staticmethod
    def get_opened_positions(par=None):
        '''
        Función auxiliar 1. Sirve para obtener las posiciones abiertas para cada uno de los pares
        en cada timeframe
        
        '''

        try:
            # mt5.initialize( login = name, server = serv, password = key, path = path)
            if not mt5.initialize(login=nombre, password=clave, server=servidor, path=path):
                logger.error("initialize() failed")
                mt5.shutdown()
            o_pos = mt5.positions_get()
            df_pos = pd.DataFrame(list(o_pos), columns=o_pos[0]._asdict().keys())
            if par == None:
                df_pos_temp = df_pos
            else:
                df_pos_temp = df_pos[df_pos['symbol'] == par]

            len_d_pos = len(df_pos_temp)
            logger.info("Se logró obtener la historia correctamente")


        except:
            len_d_pos = 0
            df_pos_temp = pd.DataFrame()
            # logger.warning("No se logró obtener la historia correctamente")

        return len_d_pos, df_pos_temp

    @staticmethod
    def get_all_positions():
        '''
        Función auxiliar 2. Sirve para obtener las posiciones abiertas para cada uno de los pares en cada timeframe
        '''
        try:
            # mt5.initialize( login = name, server = serv, password = key, path = path)
            if not mt5.initialize(login=nombre, password=clave, server=servidor, path=path):
                logger.error("initialize() failed")
                mt5.shutdown()
            o_pos = mt5.positions_get()
            df_pos = pd.DataFrame(list(o_pos), columns=o_pos[0]._asdict().keys())
            # logger.info("Se logró obtener la historia correctamente")
            logger.info(f'Se logró obtener la historia correctamente. Se encontraron {len(df_pos)} posiciones abiertas')

        except:
            df_pos = pd.DataFrame()
            # logger.warning("No se logró obtener la historia correctamente")

        return df_pos

    @staticmethod
    def send_to_breakeven(df_pos_temp: pd.DataFrame, perc_rec: float):
        if df_pos_temp.empty:
            print('No hay operaciones aún')
        if not df_pos_temp.empty:
            for symb in df_pos_temp['symbol'].unique().tolist():
                df_symbol_pos = df_pos_temp[df_pos_temp['symbol'] == symb]
                if not df_symbol_pos.empty:
                    ticket = df_symbol_pos['ticket'].iloc[0]
                    op_price = df_symbol_pos['price_open'].iloc[0]
                    c_tp = df_symbol_pos['tp'].iloc[0]
                    typ_op = df_symbol_pos['type'].iloc[0]
                    c_price = df_symbol_pos['price_current'].iloc[0]

                    # 1 Sell / 0 Buy
                    if typ_op == 1:
                        # action = mt5.ORDER_TYPE_BUY
                        dist = op_price - c_tp
                        lim_price = op_price - perc_rec * dist

                        if c_price <= lim_price:
                            modify_order_request = {
                                "action": mt5.TRADE_ACTION_SLTP,
                                "symbol": symb,
                                "position": ticket.item(),
                                "type": mt5.ORDER_TYPE_BUY,
                                "sl": op_price.item(),
                                "tp": c_tp,
                                "comment": "Change stop loss",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC
                            }
                            mt5.order_send(modify_order_request)
                    if typ_op == 0:
                        # action = mt5.ORDER_TYPE_SELL
                        dist = c_tp - op_price
                        lim_price = op_price + perc_rec * dist

                        if c_price >= lim_price:
                            modify_order_request = {
                                "action": mt5.TRADE_ACTION_SLTP,
                                "symbol": symb,
                                "position": ticket.item(),
                                "type": mt5.ORDER_TYPE_SELL,
                                "sl": op_price.item(),
                                "tp": c_tp,
                                "comment": "Change stop loss",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC
                            }
                            mt5.order_send(modify_order_request)

    def calculate_position_size(self, symbol, tradeinfo, per_to_risk):

        mt5.symbol_select(symbol, True)
        symbol_info_tick = mt5.symbol_info_tick(symbol)
        symbol_info = mt5.symbol_info(symbol)

        current_price = (symbol_info_tick.bid + symbol_info_tick.ask) / 2
        sl = tradeinfo
        tick_size = symbol_info.trade_tick_size

        balance = mt5.account_info().balance
        risk_per_trade = per_to_risk
        ticks_at_risk = abs(current_price - sl) / tick_size
        tick_value = symbol_info.trade_tick_value

        position_size = round((balance * risk_per_trade) / (ticks_at_risk * tick_value), 2)

        logger.info(f'El tamaño de la posición {symbol} es: {position_size}')

        return position_size
