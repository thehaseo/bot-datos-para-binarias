import pandas as pd


def distancias(ultimo_precio, soporte_1_min, soporte_5_min, resistencia_1_min, resistencia_5_min):
    return (ultimo_precio - soporte_1_min, ultimo_precio - soporte_5_min, resistencia_1_min - ultimo_precio,
            resistencia_5_min - ultimo_precio)
