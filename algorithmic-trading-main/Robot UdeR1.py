import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from sklearn.linear_model import LinearRegression
from Easy_Trading import Basic_funcs
from datetime import datetime
import time
from scipy import stats
from logger_tt import logger, setup_logging

setup_logging()
nombre = 63329463
clave = 'odts6pdi'
servidor = 'MetaQuotes-Demo'
path = r"C:\Program Files\MetaTrader\terminal64.exe"


# bfs = Basic_funcs(nombre, clave, servidor, path)


class Robots_URosario():

    def __init__(self, nombre, clave, servidor, path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path
        self.bfs = Basic_funcs(nombre, clave, servidor, path)

    def strategy(self, rates_frame, volumen=0.01, instrument='EURUSD', perc_tp=0.01, perc_sl=0.01):
        """
        This function implements a simple trading strategy based on the linear regression model.
        The strategy is as follows:
        - if the regression line is rising, then we open a long position;
        - if the regression line is falling, then we open a short position;
        - if the regression line is horizontal, then we do nothing;
        - if the regression line is rising and the price is above the regression line, then we do nothing;
        - if the regression line is falling and the price is below the regression line, then we do nothing.

        Mathematical details:
        - the regression line is calculated using the least squares method;
        - the slope of the regression line is calculated using the Pearson correlation coefficient;
        - the p-value of the correlation coefficient is used to determine the statistical significance of the slope;
        - if the p-value is less than 0.05, then the slope is considered statistically significant;
        - if the slope is statistically significant and positive, then we open a long position;
        - if the slope is statistically significant and negative, then we open a short position;
        - if the slope is not statistically significant, then we do nothing.

        :param rates_frame: dataframe with historical data of the instrument
        :param volumen: volumen of the operation
        :param instrument: instrument to trade
        :param perc_tp: percentage of take profit
        :param perc_sl: percentage of stop loss
        :return: None
        """
        y = rates_frame['open']
        X = rates_frame[['minutes']]
        model = LinearRegression().fit(X, y)
        rates_frame['predict'] = model.predict(X)

        params = np.append(model.intercept_, model.coef_)
        predictions = model.predict(X)
        newX = np.append(np.ones((len(X), 1)), X, axis=1)
        MSE = (sum((y - predictions) ** 2)) / (len(newX) - len(newX[0]))
        logger.info(f'{model.coef_ = }')
        logger.info(f'{MSE = }')

        var_b = MSE * (np.linalg.inv(np.dot(newX.T, newX)).diagonal())
        sd_b = np.sqrt(var_b)
        ts_b = params / sd_b

        p_values = [2 * (1 - stats.t.cdf(np.abs(i), (newX.shape[0] - newX.shape[1]))) for i in ts_b]

        sd_b = np.round(sd_b, 3)
        ts_b = np.round(ts_b, 3)
        p_values = np.round(p_values, 3)
        logger.info(f'{p_values = }')

        # if model.coef_ > 0 and p_values[1] < 0.05 and rates_frame['open'].iloc[-1] > rates_frame['predict'].iloc[-1]:
        if model.coef_ > 0 and p_values[1] < 0.05:
            df1 = self.bfs.get_all_positions()
            len_d_pos = len(df1)
            if len_d_pos > 0 and df1['type'].unique().tolist() == 1:
                self.bfs.close_all_open_operations(instrument)

                self.bfs.open_operations(instrument, volumen, mt5.ORDER_TYPE_BUY, nombre_bot='regressor_robot',
                                         tp=mt5.symbol_info_tick(instrument).ask + perc_tp * mt5.symbol_info_tick(
                                             instrument).ask,
                                         sl=mt5.symbol_info_tick(instrument).ask - perc_sl * mt5.symbol_info_tick(
                                             instrument).ask
                                         )
            elif len_d_pos > 0 and df1['type'].unique().tolist() == 0:
                logger.info('Ya existe una operación de compra abierta')
            else:
                self.bfs.open_operations(instrument, volumen, mt5.ORDER_TYPE_BUY, nombre_bot='regressor_robot',
                                         tp=mt5.symbol_info_tick(instrument).ask + perc_tp * mt5.symbol_info_tick(
                                             instrument).ask,
                                         sl=mt5.symbol_info_tick(instrument).ask - perc_sl * mt5.symbol_info_tick(
                                             instrument).ask
                                         )

        elif model.coef_ < 0 and p_values[1] < 0.05:
            df1 = self.bfs.get_all_positions()
            len_d_pos = len(df1)
            if len_d_pos > 0 and df1['type'].unique().tolist() == 0:
                self.bfs.close_all_open_operations(instrument)
                self.bfs.open_operations(instrument, volumen, mt5.ORDER_TYPE_SELL, nombre_bot='regressor_robot',
                                         tp=mt5.symbol_info_tick(instrument).bid - perc_tp * mt5.symbol_info_tick(
                                             instrument).bid,
                                         sl=mt5.symbol_info_tick(instrument).bid + perc_sl * mt5.symbol_info_tick(
                                             instrument).bid
                                         )
            elif len_d_pos > 0 and df1['type'].unique().tolist() == 1:
                logger.info('Ya existe una operación de venta abierta')
            else:
                self.bfs.open_operations(instrument, volumen, mt5.ORDER_TYPE_SELL, nombre_bot='regressor_robot',
                                         tp=mt5.symbol_info_tick(instrument).bid - perc_tp * mt5.symbol_info_tick(
                                             instrument).bid,
                                         sl=mt5.symbol_info_tick(instrument).bid + perc_sl * mt5.symbol_info_tick(
                                             instrument).bid
                                         )
        else:
            df1 = self.bfs.get_all_positions()
            len_d_pos = len(df1)
            if len_d_pos > 0 and p_values[1] > 0.05:
                self.bfs.close_all_open_operations(instrument)

    def robotuder1(self, df2, volumen, par, perc_tp, perc_sl):
        """
        This function is the main function of the robot. It is responsible for calling the functions that will be executed
        in the robot.
        """

        df_pos = self.bfs.get_all_positions()

        '''Intertrade Management'''
        if len(df_pos) > 0:
            lista_operaciones = df_pos['ticket'].unique().tolist()
            for ticket in lista_operaciones:
                temp = df_pos[df_pos['ticket'] == ticket]
                profit_actual = temp['profit'].iloc[0]
                balance, profit_account, equity, free_margin = self.bfs.info_account()

                if (profit_actual >= equity * perc_tp) or (profit_actual <= equity * perc_sl):
                    self.bfs.close_all_open_operations()

                else:
                    logger.info('No se ha cumplido la condición para cerrar posiciones')
        else:
            logger.info('No existen posiciones abiertas')

        '''Strategy'''
        self.strategy(df2, volumen, par, perc_tp, perc_sl)
        # logger.info(f'sleeping for {((60) - datetime.now().second - datetime.now().microsecond / 1000000)} seconds')
        # time.sleep((60) - datetime.now().second - datetime.now().microsecond / 1000000)

    def handler_robot(self, lista, periodo, cantidad, volumen, perc_tp, perc_sl):
        mt5.initialize(login=nombre, password=clave, server=servidor, path=path)
        if lista == []:
            symbols = mt5.symbols_get()
            lista = [s.name for s in symbols]

        while True:
            # for par in lista:
            #     # df = self.extraer_datos(par, periodo, cantidad)
            #     df = self.bfs.extract_data(par, periodo, cantidad)
            #     # df2 = self.calcular_media_movil(df, N)
            #     # self.robotuder1(df2, volumen, par, perc_tp, perc_sl)
            #     self.robotuder1(df, volumen, par, perc_tp, perc_sl)
            # logger.info(f'sleeping for {((60) - datetime.now().second - datetime.now().microsecond / 1000000)} seconds')
            # time.sleep((60) - datetime.now().second - datetime.now().microsecond / 1000000)

            # In parallel
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for par in lista:
                    # executor.submit(self.robotuder1, self.bfs.extract_data(par, periodo, cantidad), volumen, par,
                    #                 perc_tp, perc_sl)
                    executor.submit(self.robotuder1, self.bfs.extract_data(par, periodo, cantidad), volumen, par,
                                    perc_tp, perc_sl)

            logger.info(f'sleeping for {((60) - datetime.now().second - datetime.now().microsecond / 1000000)} seconds')
            time.sleep((60) - datetime.now().second - datetime.now().microsecond / 1000000)

            # # Optimized to take trades once a minute but check tp and sl every second
            # for par in lista:
            #     df = self.bfs.extract_data(par, periodo, cantidad)
            #     self.robotuder1(df, volumen, par, perc_tp, perc_sl)

            print()


ur = Robots_URosario(nombre, clave, servidor, path)

lista = ['EURUSD', 'GBPAUD', 'XAUUSD', 'USDJPY']
# lista = []
ur.handler_robot(lista, mt5.TIMEFRAME_M1, cantidad=12, volumen=1.0, perc_tp=0.0005, perc_sl=0.0005)
