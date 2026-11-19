"""Pruebas de corrección de calendario.py  (ejecutar:  python -m pytest  o  python test_calendario.py)
Autores: Oscar Lidon Garcia, Zhengjie Zhan
"""
import datetime as dt
import random

from calendario import (GREGORIANO, JULIANO, DIAS_DOM0, zeller, dia_semana_por_jdn, doomsday,
                        pascua_gauss, pascua_meeus, convertir_calendario, es_bisiesto,
                        desfase_juliano_gregoriano, validar_fecha)

try:
    from dateutil.easter import easter, EASTER_JULIAN, EASTER_WESTERN
except ImportError:  # dateutil es opcional
    easter = None

NOMBRE_PY = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def test_zeller_contra_datetime():
    """Zeller (gregoriano) == datetime.weekday() para todos los días de 1583 a 2400."""
    d = dt.date(1583, 1, 1)
    fin = dt.date(2400, 12, 31)
    while d <= fin:
        assert zeller(d.year, d.month, d.day, GREGORIANO).valor == NOMBRE_PY[d.weekday()], d
        d += dt.timedelta(days=1)


def test_zeller_juliano_contra_jdn():
    rnd = random.Random(1)
    for _ in range(5000):
        y, m = rnd.randint(1, 1582), rnd.randint(1, 12)
        d = rnd.randint(1, 28)
        assert zeller(y, m, d, JULIANO).valor == dia_semana_por_jdn(y, m, d, JULIANO)


def test_fechas_historicas():
    assert zeller(1582, 10, 4).valor == "jueves"       # último día juliano
    assert zeller(1582, 10, 15).valor == "viernes"     # primer día gregoriano
    assert zeller(1492, 10, 12).valor == "viernes"     # llegada de Colón (juliano)
    assert zeller(1969, 7, 20).valor == "domingo"      # llegada a la Luna
    assert zeller(1616, 4, 23).valor == "sábado"       # muerte de Cervantes (gregoriano)
    assert zeller(2000, 1, 1).valor == "sábado"


def test_hueco_de_la_reforma():
    for d in range(5, 15):
        try:
            validar_fecha(1582, 10, d)
            assert False, "debería fallar"
        except ValueError:
            pass


def test_doomsday_contra_datetime():
    d = dt.date(1800, 1, 1)
    while d <= dt.date(2199, 12, 31):
        assert doomsday(d.year, d.month, d.day).valor == NOMBRE_PY[d.weekday()], d
        d += dt.timedelta(days=1)


def test_pascua_gauss_igual_meeus():
    for y in range(1583, 5000):
        assert pascua_gauss(y, GREGORIANO).valor == pascua_meeus(y, GREGORIANO).valor, y
    for y in range(1, 2500):
        assert pascua_gauss(y, JULIANO).valor == pascua_meeus(y, JULIANO).valor, y


def test_pascua_es_domingo_y_en_rango():
    for y in range(1583, 4100):
        _, m, d = pascua_gauss(y).valor
        assert dt.date(y, m, d).weekday() == 6
        assert (3, 22) <= (m, d) <= (4, 25)


def test_pascua_casos_conocidos():
    assert pascua_gauss(1981).valor == (1981, 4, 19)   # excepción d = 29, e = 6
    assert pascua_gauss(1954).valor == (1954, 4, 18)   # excepción d = 28, e = 6
    assert pascua_gauss(2026).valor == (2026, 4, 5)
    assert pascua_gauss(2027).valor == (2027, 3, 28)


def test_pascua_contra_dateutil():
    if easter is None:
        return
    for y in range(1583, 4100):
        e = easter(y, EASTER_WESTERN)
        assert pascua_gauss(y).valor == (e.year, e.month, e.day)
    for y in range(326, 1583):
        e = easter(y, EASTER_JULIAN)  # dateutil la devuelve en juliano
        assert pascua_gauss(y, JULIANO).valor == (e.year, e.month, e.day)


def test_conversion_reforma():
    assert convertir_calendario(1582, 10, 4, JULIANO) == (1582, 10, 14)
    assert convertir_calendario(1582, 10, 15, GREGORIANO) == (1582, 10, 5)
    assert desfase_juliano_gregoriano(1600) == 10
    assert desfase_juliano_gregoriano(2026) == 13


def test_bisiestos():
    assert es_bisiesto(2000) and es_bisiesto(2024) and not es_bisiesto(1900)
    assert es_bisiesto(1900, JULIANO)


if __name__ == "__main__":
    import sys
    fallos = 0
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_"):
            try:
                f()
                print(f"OK    {nombre}")
            except AssertionError as e:
                fallos += 1
                print(f"FALLO {nombre}: {e}")
    sys.exit(1 if fallos else 0)
