from ExtraccionDatosFxcmpy import ExtraccionFxcmpy
from ExtraccionDatosOanda import ExtraccionOanda
from distancia_a_soporte_y_resistencia import distancias
from ADX import ADX
from RSI import RSI
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.pricing as pricing
import time
import pandas as pd
import pyautogui
import cv2

import random


def r(num, rand):
    return num + rand * random.random()


'''
click on the center of an image with a bit of random.
eg, if an image is 100*100 with an offset of 5 it may click at 52,50 the first time and then 55,53 etc
Usefull to avoid anti-bot monitoring while staying precise.
this function doesn't search for the image, it's only ment for easy clicking on the images.
input :
image : path to the image file (see opencv imread for supported types)
pos : array containing the position of the top left corner of the image [x,y]
action : button of the mouse to activate : "left" "right" "middle", see pyautogui.click documentation for more info
time : time taken for the mouse to move from where it was to the new position
'''


def click_image(image, pos, action, timestamp, offset=5):
    img = cv2.imread(image)
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + r(width / 2, offset), pos[1] + r(height / 2, offset),
                     timestamp)
    pyautogui.click(button=action)


def ejecutar():
    click_image("horario.jpg", (1805, 132), "left", 0.05)
    time.sleep(0.1)
    click_image("1minuto.jpg", (1517, 220), "left", 0.05)
    click_image("imagen compra.jpg", (1801, 379), "left", 0.05)
    time.sleep(0.05)
    click_image("imagen venta.jpg", (1804, 513), "left", 0.05)


def run(tiempo_de_ejecucion_minutos, primera_divisa, segunda_divisa):
    print("comenzando")
    datos_operaciones = pd.Dataframe()
    timeout = time.time() + (tiempo_de_ejecucion_minutos * 60)
    divisa = f"{primera_divisa}_{segunda_divisa}"
    proceso_1_min = ExtraccionFxcmpy(500, "m1", f"{primera_divisa}/{segunda_divisa}")
    proceso_5_min = ExtraccionOanda(120, "M5", f"{primera_divisa}_{segunda_divisa}")
    proceso_1_min.start()
    proceso_5_min.start()
    time.sleep(30)
    datos_1min = pd.read_csv("datos_m1.csv", index_col="date")
    resistencia_mayor_1m = datos_1min["h"].rolling(150).max().dropna()
    resistencia_menor_1m = datos_1min["c"].rolling(150).max().dropna()
    resistencia_punto_mayor_1m = resistencia_mayor_1m.iloc[-1]
    resistencia_punto_menor_1m = resistencia_menor_1m.iloc[-1]
    # Se calcula rango de resistencia en las últimas 150 velas a 1 minuto
    for data in range(-150, 0):
        precio_h = datos_1min['h'].iloc[data]
        precio_o = datos_1min['o'].iloc[data]
        precio_c = datos_1min['c'].iloc[data]
        if precio_h > resistencia_punto_menor_1m > precio_c:
            if precio_c >= precio_o:
                resistencia_punto_menor_1m = precio_c
            elif precio_c < precio_o < resistencia_punto_menor_1m:
                resistencia_punto_menor_1m = precio_o
    soporte_menor_1m = datos_1min["l"].rolling(150).min().dropna()
    soporte_mayor_1m = datos_1min["c"].rolling(150).min().dropna()
    soporte_punto_menor_1m = soporte_menor_1m.iloc[-1]
    soporte_punto_mayor_1m = soporte_mayor_1m.iloc[-1]
    # Se calcula rango de soporte en las últimas 150 velas a 1 minuto
    for data in range(-50, 0):
        precio_l = datos_1min['l'].iloc[data]
        precio_o = datos_1min['o'].iloc[data]
        precio_c = datos_1min['c'].iloc[data]
        if precio_l < soporte_punto_mayor_1m < precio_c:
            if precio_c <= precio_o:
                soporte_punto_mayor_1m = precio_c
            elif precio_c > precio_o > soporte_punto_mayor_1m:
                soporte_punto_mayor_1m = precio_o
    datos_5min = pd.read_csv("datos_M5.csv", index_col="time")
    resistencia_mayor_5m = datos_5min["h"].rolling(50).max().dropna()
    resistencia_menor_5m = datos_5min["c"].rolling(50).max().dropna()
    resistencia_punto_mayor_5m = resistencia_mayor_5m.iloc[-1]
    resistencia_punto_menor_5m = resistencia_menor_5m.iloc[-1]
    # rango de resistencia a 5 minutos en las últimas 50 velas
    for data in range(50, 0):
        precio_h = datos_5min['h'].iloc[data]
        precio_o = datos_5min['o'].iloc[data]
        precio_c = datos_5min['c'].iloc[data]
        if precio_h > resistencia_punto_menor_5m > precio_c:
            if precio_c >= precio_o:
                resistencia_punto_menor_5m = precio_c
            elif precio_c < precio_o < resistencia_punto_menor_5m:
                resistencia_punto_menor_5m = precio_o
    soporte_menor_5m = datos_5min["l"].rolling(50).min().dropna()
    soporte_mayor_5m = datos_5min["c"].rolling(50).min().dropna()
    soporte_punto_menor_5m = soporte_menor_5m.iloc[-1]
    soporte_punto_mayor_5m = soporte_mayor_5m.iloc[-1]
    # rango de soporte a 5 minutos en las últimas 50 velas
    for data in range(-50, 0):
        precio_l = datos_5min['l'].iloc[data]
        precio_o = datos_5min['o'].iloc[data]
        precio_c = datos_5min['c'].iloc[data]
        if precio_l < soporte_punto_mayor_5m < precio_c:
            if precio_c <= precio_o:
                soporte_punto_mayor_5m = precio_c
            elif precio_c > precio_o > soporte_punto_mayor_5m:
                soporte_punto_mayor_5m = precio_o
    params = {"count": 500, "granularity": "S5"}  # granularity can be in seconds S5 -
    # S30, minutes M1 - M30, hours H1 - H12, days D, weeks W or months M
    client = oandapyV20.API(access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                            environment="practice")
    account_id = "101-011-12930479-001"
    candles = instruments.InstrumentsCandles(instrument=divisa, params=params)
    client.request(candles)
    ohlc_dict = candles.response["candles"]
    ohlc = pd.DataFrame(ohlc_dict)
    datos_5s = ohlc.mid.dropna().apply(pd.Series)
    datos_5s["volume"] = ohlc["volume"]
    datos_5s.index = ohlc["time"]
    datos_5s = datos_5s.apply(pd.to_numeric)
    live_data = []  # precios que recorre el par de divisa en el timeframe seleccionado
    live_price_request = pricing.PricingInfo(accountID=account_id, params={"instruments": divisa})
    rango_precios = []
    while time.time() <= timeout:
        try:
            if f"{(int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1):02}" != \
                    datos_1min.iloc[-1].name[14:16]:
                datos_1min = pd.read_csv("datos_m1.csv", index_col="date")
                resistencia_mayor_1m = datos_1min["h"].rolling(150).max().dropna()
                resistencia_menor_1m = datos_1min["c"].rolling(150).max().dropna()
                resistencia_punto_mayor_1m = resistencia_mayor_1m.iloc[-1]
                resistencia_punto_menor_1m = resistencia_menor_1m.iloc[-1]
                for data in range(-150, 0):
                    precio_h = datos_1min['h'].iloc[data]
                    precio_o = datos_1min['o'].iloc[data]
                    precio_c = datos_1min['c'].iloc[data]
                    if precio_h > resistencia_punto_menor_1m > precio_c:
                        if precio_c >= precio_o:
                            resistencia_punto_menor_1m = precio_c
                        elif precio_c < precio_o < resistencia_punto_menor_1m:
                            resistencia_punto_menor_1m = precio_o
                soporte_menor_1m = datos_1min["l"].rolling(150).min().dropna()
                soporte_mayor_1m = datos_1min["c"].rolling(150).min().dropna()
                soporte_punto_menor_1m = soporte_menor_1m.iloc[-1]
                soporte_punto_mayor_1m = soporte_mayor_1m.iloc[-1]
                for data in range(-50, 0):
                    precio_l = datos_1min['l'].iloc[data]
                    precio_o = datos_1min['o'].iloc[data]
                    precio_c = datos_1min['c'].iloc[data]
                    if precio_l < soporte_punto_mayor_1m < precio_c:
                        if precio_c <= precio_o:
                            soporte_punto_mayor_1m = precio_c
                        elif precio_c > precio_o > soporte_punto_mayor_1m:
                            soporte_punto_mayor_1m = precio_o
            if ((int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 1 or (
                    int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[15:16])) == 6) and \
                    (datos_5min.iloc[-1].name[
                     14:16] != f"{int(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))[14:16]) - 1}"):
                datos_5min = pd.read_csv("datos_M5.csv", index_col="time")
                resistencia_mayor_5m = datos_5min["h"].rolling(50).max().dropna()
                resistencia_menor_5m = datos_5min["c"].rolling(50).max().dropna()
                resistencia_punto_mayor_5m = resistencia_mayor_5m.iloc[-1]
                resistencia_punto_menor_5m = resistencia_menor_5m.iloc[-1]
                # rango de resistencia a 5 minutos en las últimas 50 velas
                for data in range(50, 0):
                    precio_h = datos_5min['h'].iloc[data]
                    precio_o = datos_5min['o'].iloc[data]
                    precio_c = datos_5min['c'].iloc[data]
                    if precio_h > resistencia_punto_menor_5m > precio_c:
                        if precio_c >= precio_o:
                            resistencia_punto_menor_5m = precio_c
                        elif precio_c < precio_o < resistencia_punto_menor_5m:
                            resistencia_punto_menor_5m = precio_o
                soporte_menor_5m = datos_5min["l"].rolling(50).min().dropna()
                soporte_mayor_5m = datos_5min["c"].rolling(50).min().dropna()
                soporte_punto_menor_5m = soporte_menor_5m.iloc[-1]
                soporte_punto_mayor_5m = soporte_mayor_5m.iloc[-1]
                # rango de soporte a 5 minutos en las últimas 50 velas
                for data in range(-50, 0):
                    precio_l = datos_5min['l'].iloc[data]
                    precio_o = datos_5min['o'].iloc[data]
                    precio_c = datos_5min['c'].iloc[data]
                    if precio_l < soporte_punto_mayor_5m < precio_c:
                        if precio_c <= precio_o:
                            soporte_punto_mayor_5m = precio_c
                        elif precio_c > precio_o > soporte_punto_mayor_5m:
                            soporte_punto_mayor_5m = precio_o
            starttime = time.time()
            timeout2 = starttime + 5
            while starttime <= timeout2:  # Se cuenta 5 segundos de extraccion de datos para luego filtrar
                live_price_data = client.request(live_price_request)
                live_data.append(live_price_data)
                starttime = time.time()
            for i in range(len(live_data) - 1):  # Se saca la media entre el Bid y el ask para tener el precio real
                precio = (float(live_data[i]["prices"][0]["closeoutBid"])
                          + float(live_data[i]["prices"][0]["closeoutAsk"])) / 2
                rango_precios.append(precio)
            last_data_row = pd.DataFrame(index=[live_data[-1]["time"]], columns=["o", "h", "l", "c"])
            last_data_row['o'] = round(rango_precios[0], 6)
            last_data_row['h'] = round(max(rango_precios), 6)
            last_data_row['l'] = round(min(rango_precios), 6)
            last_data_row['c'] = round(rango_precios[-1], 6)
            datos_5s = datos_5s.append(last_data_row, sort=False)
            datos_5s = datos_5s.iloc[-500:]
            ejecutar()
            adx_5min = ADX(datos_5min, 14)
            adx_1min = ADX(datos_1min, 21)
            adx_5s = ADX(datos_5s, 14)
            rsi_21 = RSI(datos_5s, 21)
            dentro_resistencia_1min = "Y" if (resistencia_punto_mayor_1m > datos_5s['c'].iloc[-1] >
                                              resistencia_punto_menor_1m) else "N"
            dentro_soporte_1min = "Y" if (soporte_punto_menor_1m < datos_5s['c'].iloc[-1] < soporte_punto_mayor_1m) \
                else "N"
            dentro_resistencia_5min = "Y" if (resistencia_punto_mayor_5m > datos_5s['c'].iloc[-1] >
                                              resistencia_punto_menor_5m) else "N"
            dentro_soporte_5min = "Y" if (soporte_punto_menor_5m < datos_5s['c'].iloc[-1] < soporte_punto_mayor_5m) \
                else "N"
            corte_alcista_adx = "Y" if (adx_5s["DI+"].iloc[-2] < adx_5s["DI-"].iloc[-2] and
                                        adx_5s["DI+"].iloc[-1] > adx_5s["DI-"].iloc[-1]) else "N"
            corte_bajista_adx = "Y" if (adx_5s["DI-"].iloc[-2] < adx_5s["DI+"].iloc[-2] and
                                        adx_5s["DI-"].iloc[-1] > adx_5s["DI+"].iloc[-1]) else "N"
            ganada_perdida = input("fue ganadora?: ")
            datos_operaciones["ADX 5min"] += adx_5min["ADX"].iloc[-1]
            datos_operaciones["DI- 5min"] += adx_5min["DI-"].iloc[-1]
            datos_operaciones["DI+ 5min"] += adx_5min["DI+"].iloc[-1]
            datos_operaciones["ADX 1min"] += adx_1min["ADX"].iloc[-1]
            datos_operaciones["DI- 1min"] += adx_1min["DI-"].iloc[-1]
            datos_operaciones["DI+ 1min"] += adx_1min["DI+"].iloc[-1]
            datos_operaciones["rsi 5s"] += rsi_21.iloc[-1]
            datos_operaciones["resistencia 1m"] += dentro_resistencia_1min
            datos_operaciones["soporte 1m"] += dentro_soporte_1min
            datos_operaciones["resistencia 5m"] += dentro_resistencia_5min
            datos_operaciones["soporte 5m"] += dentro_soporte_5min
            datos_operaciones["corte alcista"] += corte_alcista_adx
            datos_operaciones["corte bajista"] += corte_bajista_adx
            datos_operaciones["ganadora?"] += ganada_perdida
            live_data.clear()
            rango_precios.clear()
        except:
            print("hubo error, verificar si la ejecucion continua")



if __name__ == "__main__":
    primera_divisa = input("introduzca la primera divisa: ")
    segunda_divisa = input("introduzca la segunda divisa: ")
    mes = input("introduzca el mes de inicio: ")
    dia = input("introduzca el dia de inicio: ")
    hora = input("introduzca la hora de inicio (militar): ")
    minuto = input("introduzca el minuto de inicio: ")
    tiempo = int(input("introduzca el tiempo de ejecucion en minutos: "))
    while time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) != f'2020-{mes}-{dia} {hora}:{minuto}:00':
        pass
    run(tiempo, primera_divisa, segunda_divisa)
