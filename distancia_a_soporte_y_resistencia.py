import pandas as pd


def distancias(ultimo_precio, soporte_1min, soporte_5min, resistencia_1min, resistencia_5min):
    return (ultimo_precio - soporte_1min, ultimo_precio - soporte_5min, resistencia_1min - ultimo_precio,
            resistencia_5min - ultimo_precio)
