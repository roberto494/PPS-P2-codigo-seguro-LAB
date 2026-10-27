"""Suite de PPS-E2. Todo en verde... ¿significa que el código está bien?"""

import pytest
import math

from descuentos import aplicar_descuento, es_precio_valido


# --- ¿Qué comprueba realmente este test?
def test_ejecuta_sin_reventar():
    aplicar_descuento(100, 10)
    assert True


def test_descuento_correcto():
    assert aplicar_descuento(100, 10) == 90.0
    assert aplicar_descuento(50, 0) == 50.0
    assert aplicar_descuento(80, 100) == 0.0


def test_precio_negativo_se_rechaza():
    with pytest.raises(ValueError):
        aplicar_descuento(-10, 10)

def test_regresion_nan_e_infinitos():
    with pytest.raises(ValueError):
        aplicar_descuento(float('nan'), 10)
    with pytest.raises(ValueError):
        aplicar_descuento(100, float('nan'))
    with pytest.raises(ValueError):
        aplicar_descuento(float('inf'), 10)

# --- Test para la función es_precio_valido (completar cobertura)

def test_es_precio_valido():
    assert es_precio_valido(50) is True
    assert es_precio_valido(-10) is False

# --- TU TEST DE REGRESIÓN (incidencia #17) va aquí debajo.

def test_regresion_indicencia_17():

    with pytest.raises(ValueError):
        aplicar_descuento(100, 150)

    with pytest.raises(ValueError):
        aplicar_descuento(100,  -5)
