import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from sklearn.linear_model import LinearRegression
from Easy_Trading import Basic_funcs
from datetime import datetime
import time
from scipy import stats

# Name     : Ru fe
# Type     : Forex Hedged USD
# Server   : MetaQuotes-Demo
# Login    : 63329463
# Password : odts6pdi
# Investor : cx6aoihi


nombre = 63329463
clave = 'odts6pdi'
servidor = 'MetaQuotes-Demo'
path = r"C:\Program Files\MetaTrader\terminal64.exe"

bfs = Basic_funcs(nombre, clave, servidor, path)



def regressor_robot():
    while True:
        print('\n\n')
        rates_frame = bfs.extract_data('EURUSD', mt5.TIMEFRAME_M1, 1000)

        rates_frame['minutes'] = range(1000)
        y = rates_frame['open']
        X = rates_frame[['minutes']]
        model = LinearRegression().fit(X, y)
        rates_frame['predict'] = model.predict(X)

        # print(f'{rates_frame.head() = }')
        print(f'{model.coef_ = }')
        params = np.append(model.intercept_, model.coef_)
        predictions = model.predict(X)
        # print(f'{params = }')
        # print(f'{predictions = }')
        # newX = pd.DataFrame({"Constant": np.ones(len(X))}).join(pd.DataFrame(X))
        # MSE = (sum((y - predictions) ** 2)) / (len(newX) - len(newX.columns))
        newX = np.append(np.ones((len(X), 1)), X, axis=1)
        MSE = (sum((y - predictions) ** 2)) / (len(newX) - len(newX[0]))

        print(f'{MSE = }')
        # print(f'{newX.shape = }')
        # print(f'{np.append(np.ones((len(X), 1)), X, axis=1).shape = }')
        # print(f'{len(newX.columns) = }')

        var_b = MSE * (np.linalg.inv(np.dot(newX.T, newX)).diagonal())
        sd_b = np.sqrt(var_b)
        ts_b = params / sd_b

        # p_values = [2 * (1 - stats.t.cdf(np.abs(i), (len(newX) - len(newX.columns)))) for i in ts_b]
        p_values = [2 * (1 - stats.t.cdf(np.abs(i), (newX.shape[0] - newX.shape[1]))) for i in ts_b]

        sd_b = np.round(sd_b, 3)
        ts_b = np.round(ts_b, 3)
        p_values = np.round(p_values, 3)
        # print(f'{sd_b = }')
        # print(f'{ts_b = }')
        print(f'{p_values = }')

        # "sl": mt5.symbol_info_tick(par).ask if tipo_operacion == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(par).bid,
        # "tp": mt5.symbol_info_tick(par).ask if tipo_operacion == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(par).bid,
        if model.coef_ > 0 and p_values[1] < 0.05:
            df1 = bfs.get_all_positions()
            len_d_pos = len(df1)
            if len_d_pos > 0 and df1['type'].unique().tolist() == 1:
                bfs.close_all_open_operations('EURUSD')

                bfs.open_operations('EURUSD', 0.01, mt5.ORDER_TYPE_BUY, nombre_bot='regressor_robot',
                                    tp = mt5.symbol_info_tick('EURUSD').ask + 0.0005,
                                    sl = mt5.symbol_info_tick('EURUSD').ask - 0.0005)
            elif len_d_pos > 0 and df1['type'].unique().tolist() == 0:
                print('Ya existe una operación de compra abierta')
            else:
                bfs.open_operations('EURUSD', 0.01, mt5.ORDER_TYPE_BUY, nombre_bot='regressor_robot',
                                    tp = mt5.symbol_info_tick('EURUSD').ask + 0.0005,
                                    sl = mt5.symbol_info_tick('EURUSD').ask - 0.0005)

        elif model.coef_ < 0 and p_values[1] < 0.05:
            df1 = bfs.get_all_positions()
            len_d_pos = len(df1)
            if len_d_pos > 0 and df1['type'].unique().tolist() == 0:
                bfs.close_all_open_operations('EURUSD')
                bfs.open_operations('EURUSD', 0.01, mt5.ORDER_TYPE_SELL, nombre_bot='regressor_robot',
                                    tp = mt5.symbol_info_tick('EURUSD').bid - 0.0005,
                                    sl = mt5.symbol_info_tick('EURUSD').bid + 0.0005)
            elif len_d_pos > 0 and df1['type'].unique().tolist() == 1:
                print('Ya existe una operación de venta abierta')
            else:
                bfs.open_operations('EURUSD', 0.01, mt5.ORDER_TYPE_SELL, nombre_bot='regressor_robot',
                                    tp = mt5.symbol_info_tick('EURUSD').bid - 0.0005,
                                    sl = mt5.symbol_info_tick('EURUSD').bid + 0.0005)
        else:
            df1 = bfs.get_all_positions()
            len_d_pos = len(df1)
            if len_d_pos > 0 and p_values[1] > 0.05:
                bfs.close_all_open_operations('EURUSD')
        print(f'sleeping for {((60) - datetime.now().second - datetime.now().microsecond / 1000000)} seconds')
        time.sleep((60) - datetime.now().second - datetime.now().microsecond / 1000000)


regressor_robot()
