"""
calendario.py — Núcleo matemático de la «Máquina del tiempo modular»
=====================================================================

Trabajo 18 · Calendarios y aritmética modular: ¿qué día de la semana fue?
Trabajo de aplicaciones · Temas 1 y 2 · Curso 2026–2027 · Universidad Miguel Hernández

Autores:
    - Oscar Lidon Garcia
    - Zhengjie Zhan

Este módulo contiene SOLO matemáticas (sin interfaz). Cada función devuelve,
además del resultado, la lista de pasos intermedios (restos, divisiones enteras,
congruencias) para que la aplicación pueda mostrarlos.

Contenidos del Tema 1 que se usan:
    * División entera  a = b·q + r,  0 ≤ r < b   (operadores // y % de Python)
    * Congruencias módulo 7 (días de la semana), módulo 19 (ciclo de Metón),
      módulo 30 y módulo 4 (bisiestos)
    * Congruencia de Zeller
    * Algoritmo de Gauss y algoritmo de Meeus (anónimo gregoriano) para la Pascua
    * Reforma gregoriana de 1582
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Días de la semana en el orden en que los devuelve Zeller: h = 0 → sábado
DIAS_ZELLER = ["sábado", "domingo", "lunes", "martes", "miércoles", "jueves", "viernes"]

# Orden "humano" (domingo = 0), usado en el método mental (Doomsday)
DIAS_DOM0 = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

GREGORIANO = "gregoriano"
JULIANO = "juliano"
AUTO = "auto"

# La reforma: al jueves 4 de octubre de 1582 (juliano) le siguió el
# viernes 15 de octubre de 1582 (gregoriano).
REFORMA_ULTIMO_JULIANO = (1582, 10, 4)
REFORMA_PRIMER_GREGORIANO = (1582, 10, 15)


@dataclass
class Resultado:
    """Resultado de un cálculo con sus pasos intermedios."""
    valor: object
    pasos: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Años bisiestos y validación de fechas
# ---------------------------------------------------------------------------

def es_bisiesto(año: int, calendario: str = GREGORIANO) -> bool:
    """Juliano: múltiplo de 4.
    Gregoriano: múltiplo de 4, salvo los múltiplos de 100 que no lo son de 400."""
    if calendario == JULIANO:
        return año % 4 == 0
    return (año % 4 == 0 and año % 100 != 0) or año % 400 == 0


def explicar_bisiesto(año: int, calendario: str = GREGORIANO) -> Resultado:
    pasos = [f"{año} mod 4 = {año % 4}"]
    if calendario == JULIANO:
        b = año % 4 == 0
        pasos.append("Calendario juliano: es bisiesto ⇔ año ≡ 0 (mod 4).")
    else:
        pasos.append(f"{año} mod 100 = {año % 100}")
        pasos.append(f"{año} mod 400 = {año % 400}")
        pasos.append("Calendario gregoriano: bisiesto ⇔ (año ≡ 0 mod 4 y año ≢ 0 mod 100) "
                     "o año ≡ 0 mod 400.")
        b = es_bisiesto(año, GREGORIANO)
    pasos.append(f"⇒ {año} {'SÍ' if b else 'NO'} es bisiesto en el calendario {calendario}.")
    return Resultado(b, pasos)


def dias_del_mes(año: int, mes: int, calendario: str = GREGORIANO) -> int:
    if mes == 2:
        return 29 if es_bisiesto(año, calendario) else 28
    return 30 if mes in (4, 6, 9, 11) else 31


def calendario_vigente(año: int, mes: int, dia: int) -> str:
    """Calendario en vigor (criterio de los países católicos, p. ej. España)."""
    return JULIANO if (año, mes, dia) <= REFORMA_ULTIMO_JULIANO else GREGORIANO


def validar_fecha(año: int, mes: int, dia: int, calendario: str = AUTO) -> str:
    """Devuelve el calendario que se usará. Lanza ValueError si la fecha no existe."""
    if not 1 <= mes <= 12:
        raise ValueError("El mes debe estar entre 1 y 12.")
    if calendario == AUTO:
        if REFORMA_ULTIMO_JULIANO < (año, mes, dia) < REFORMA_PRIMER_GREGORIANO:
            raise ValueError("Del 5 al 14 de octubre de 1582 no existieron: la reforma "
                             "gregoriana pasó del jueves 4 al viernes 15 de octubre.")
        calendario = calendario_vigente(año, mes, dia)
    if año < 1:
        raise ValueError("Usa años d. C. (año ≥ 1).")
    if not 1 <= dia <= dias_del_mes(año, mes, calendario):
        raise ValueError(f"{MESES[mes - 1].capitalize()} de {año} solo tiene "
                         f"{dias_del_mes(año, mes, calendario)} días en el calendario {calendario}.")
    return calendario


# ---------------------------------------------------------------------------
# Congruencia de Zeller
# ---------------------------------------------------------------------------

def zeller(año: int, mes: int, dia: int, calendario: str = AUTO) -> Resultado:
    """Día de la semana mediante la congruencia de Zeller, paso a paso.

    Gregoriano: h ≡ q + ⌊13(m+1)/5⌋ + K + ⌊K/4⌋ + ⌊J/4⌋ + 5J   (mod 7)
    Juliano:    h ≡ q + ⌊13(m+1)/5⌋ + K + ⌊K/4⌋ + 5 + 6J       (mod 7)

    q = día, m = mes (marzo = 3, …, diciembre = 12, enero = 13, febrero = 14 del año anterior),
    K = año del siglo (Y mod 100), J = siglo (⌊Y/100⌋), h = 0 sábado, 1 domingo, …, 6 viernes.
    """
    cal = validar_fecha(año, mes, dia, calendario)
    pasos: list[str] = []
    pasos.append(f"Fecha: {dia} de {MESES[mes - 1]} de {año} — calendario {cal}.")

    q, m, Y = dia, mes, año
    if m <= 2:
        m += 12
        Y -= 1
        pasos.append(f"1) Enero y febrero se cuentan como meses 13 y 14 del año anterior "
                     f"(así el 29 de febrero queda al final del «año»): m = {m}, Y = {Y}.")
    else:
        pasos.append(f"1) El mes es ≥ 3, no se modifica: m = {m}, Y = {Y}.")

    K, J = Y % 100, Y // 100
    pasos.append(f"2) División entera de Y entre 100: {Y} = 100·{J} + {K} ⇒ J = {J} (siglo), "
                 f"K = {K} (año del siglo).")

    t_mes = (13 * (m + 1)) // 5
    pasos.append(f"3) Término del mes: ⌊13·(m+1)/5⌋ = ⌊13·{m + 1}/5⌋ = ⌊{13 * (m + 1)}/5⌋ = {t_mes}.")
    t_K4 = K // 4
    pasos.append(f"4) Bisiestos del siglo: ⌊K/4⌋ = ⌊{K}/4⌋ = {t_K4}.")

    if cal == GREGORIANO:
        t_J4 = J // 4
        t_J = 5 * J
        suma = q + t_mes + K + t_K4 + t_J4 + t_J
        pasos.append(f"5) Términos del siglo (gregoriano): ⌊J/4⌋ = {t_J4}, 5J = {t_J}.")
        pasos.append(f"6) Suma: q + ⌊13(m+1)/5⌋ + K + ⌊K/4⌋ + ⌊J/4⌋ + 5J = "
                     f"{q} + {t_mes} + {K} + {t_K4} + {t_J4} + {t_J} = {suma}.")
    else:
        t_J = 6 * J
        suma = q + t_mes + K + t_K4 + 5 + t_J
        pasos.append(f"5) Términos del siglo (juliano): 5 + 6J = 5 + {t_J}.")
        pasos.append(f"6) Suma: q + ⌊13(m+1)/5⌋ + K + ⌊K/4⌋ + 5 + 6J = "
                     f"{q} + {t_mes} + {K} + {t_K4} + 5 + {t_J} = {suma}.")

    h = suma % 7
    pasos.append(f"7) Resto módulo 7: {suma} = 7·{suma // 7} + {h} ⇒ h ≡ {h} (mod 7).")
    pasos.append(f"8) Tabla de Zeller: 0 = sáb, 1 = dom, 2 = lun, 3 = mar, 4 = mié, 5 = jue, 6 = vie "
                 f"⇒ h = {h} → **{DIAS_ZELLER[h]}**.")
    return Resultado(DIAS_ZELLER[h], pasos)


# ---------------------------------------------------------------------------
# Número de día juliano (JDN): comprobación independiente y conversión
# ---------------------------------------------------------------------------

def jdn(año: int, mes: int, dia: int, calendario: str = GREGORIANO) -> int:
    """Número de día juliano (días transcurridos desde el 1-1-4713 a. C. juliano)."""
    a = (14 - mes) // 12
    y = año + 4800 - a
    m = mes + 12 * a - 3
    base = dia + (153 * m + 2) // 5 + 365 * y + y // 4
    if calendario == GREGORIANO:
        return base - y // 100 + y // 400 - 32045
    return base - 32083


def jdn_a_fecha(n: int, calendario: str = GREGORIANO) -> tuple[int, int, int]:
    """Inversa de jdn()."""
    if calendario == GREGORIANO:
        a = n + 32044
        b = (4 * a + 3) // 146097
        c = a - 146097 * b // 4
    else:
        b = 0
        c = n + 32082
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    dia = e - (153 * m + 2) // 5 + 1
    mes = m + 3 - 12 * (m // 10)
    año = 100 * b + d - 4800 + m // 10
    return año, mes, dia


def dia_semana_por_jdn(año: int, mes: int, dia: int, calendario: str = AUTO) -> str:
    """Comprobación independiente: JDN ≡ 0 (mod 7) es lunes."""
    cal = validar_fecha(año, mes, dia, calendario)
    return DIAS_DOM0[(jdn(año, mes, dia, cal) + 1) % 7]


def convertir_calendario(año: int, mes: int, dia: int, origen: str) -> tuple[int, int, int]:
    """Convierte una fecha juliana a gregoriana o al revés (mismo día real)."""
    validar_fecha(año, mes, dia, origen)
    destino = GREGORIANO if origen == JULIANO else JULIANO
    return jdn_a_fecha(jdn(año, mes, dia, origen), destino)


def desfase_juliano_gregoriano(año: int) -> int:
    """Días que el calendario juliano va por detrás del gregoriano (válido desde
    el 1 de marzo del año del siglo correspondiente): ⌊S⌋ − ⌊S/4⌋ − 2, S = ⌊año/100⌋."""
    s = año // 100
    return s - s // 4 - 2


# ---------------------------------------------------------------------------
# 365 ≡ 1 (mod 7): desplazamiento de un año al siguiente
# ---------------------------------------------------------------------------

def desplazamiento_anual(año: int, mes: int, dia: int, n_años: int = 8) -> list[dict]:
    """El mismo día/mes durante n_años consecutivos (gregoriano) y cuánto avanza.

    Entre la fecha del año Y y la del año Y+1 hay 365 o 366 días.
    365 = 7·52 + 1 ⇒ 365 ≡ 1 (mod 7)  → avanza 1 día de la semana.
    366 = 7·52 + 2 ⇒ 366 ≡ 2 (mod 7)  → avanza 2 (si entre ambas fechas hay un 29 de febrero).
    """
    filas = []
    anterior = None
    for y in range(año, año + n_años):
        if mes == 2 and dia == 29 and not es_bisiesto(y):
            continue
        n = jdn(y, mes, dia)
        fila = {"Año": y, "Día": DIAS_DOM0[(n + 1) % 7]}
        if anterior is not None:
            dif = n - anterior[1]
            fila["Días desde la fecha anterior"] = str(dif)
            fila["≡ (mod 7)"] = str(dif % 7)
            fila["Motivo"] = ("incluye un 29 de febrero" if dif % 7 == 2
                              else "365 ≡ 1 (mod 7)" if dif == 365 else f"{dif} días")
        else:
            fila["Días desde la fecha anterior"] = "—"
            fila["≡ (mod 7)"] = "—"
            fila["Motivo"] = "fecha inicial"
        filas.append(fila)
        anterior = (y, n)
    return filas


# ---------------------------------------------------------------------------
# Pascua: algoritmo de Gauss
# ---------------------------------------------------------------------------

def pascua_gauss(año: int, calendario: str = AUTO) -> Resultado:
    """Domingo de Pascua por el algoritmo de Gauss (1800, con la corrección de 1816)."""
    if calendario == AUTO:
        calendario = JULIANO if año <= 1582 else GREGORIANO
    if año < 1:
        raise ValueError("Usa años d. C.")
    pasos: list[str] = [f"Año {año} — calendario {calendario}."]

    a, b, c = año % 19, año % 4, año % 7
    pasos.append(f"a = {año} mod 19 = {a}  → posición del año en el ciclo de Metón "
                 f"(19 años solares ≈ 235 lunaciones; la Luna repite fases).")
    pasos.append(f"b = {año} mod 4 = {b}  → posición en el ciclo de bisiestos.")
    pasos.append(f"c = {año} mod 7 = {c}  → como 365 ≡ 1 (mod 7), cada año desplaza un día la semana.")

    if calendario == GREGORIANO:
        k = año // 100
        p = (13 + 8 * k) // 25
        qq = k // 4
        M = (15 - p + k - qq) % 30
        N = (4 + k - qq) % 7
        pasos.append(f"k = ⌊{año}/100⌋ = {k};  p = ⌊(13 + 8k)/25⌋ = ⌊{13 + 8 * k}/25⌋ = {p};  "
                     f"q = ⌊k/4⌋ = {qq}.")
        pasos.append(f"M = (15 − p + k − q) mod 30 = ({15 - p + k - qq}) mod 30 = {M}  "
                     f"→ corrección lunar (p) y solar (k − q) del siglo.")
        pasos.append(f"N = (4 + k − q) mod 7 = ({4 + k - qq}) mod 7 = {N}  "
                     f"→ corrección del día de la semana por los bisiestos suprimidos.")
    else:
        M, N = 15, 6
        pasos.append("Calendario juliano: M = 15 y N = 6 (constantes, sin correcciones de siglo).")

    d = (19 * a + M) % 30
    pasos.append(f"d = (19a + M) mod 30 = (19·{a} + {M}) mod 30 = {19 * a + M} mod 30 = {d}  "
                 f"→ días desde el 21 de marzo hasta la luna llena pascual.")
    e = (2 * b + 4 * c + 6 * d + N) % 7
    pasos.append(f"e = (2b + 4c + 6d + N) mod 7 = (2·{b} + 4·{c} + 6·{d} + {N}) mod 7 = "
                 f"{2 * b + 4 * c + 6 * d + N} mod 7 = {e}  → días hasta el domingo siguiente.")

    total = 22 + d + e
    if total <= 31:
        mes, dia = 3, total
        pasos.append(f"22 + d + e = {total} ≤ 31 ⇒ {dia} de marzo.")
    else:
        mes, dia = 4, d + e - 9
        pasos.append(f"22 + d + e = {total} > 31 ⇒ d + e − 9 = {dia} de abril.")

    if calendario == GREGORIANO:
        if d == 29 and e == 6:
            pasos.append("Excepción de Gauss: d = 29 y e = 6 ⇒ el 26 de abril se sustituye por el 19 de abril.")
            mes, dia = 4, 19
        elif d == 28 and e == 6 and (11 * M + 11) % 30 < 19:
            pasos.append(f"Excepción de Gauss: d = 28, e = 6 y (11M + 11) mod 30 = {(11 * M + 11) % 30} < 19 "
                         f"⇒ el 25 de abril se sustituye por el 18 de abril.")
            mes, dia = 4, 18
    pasos.append(f"⇒ Domingo de Pascua: **{dia} de {MESES[mes - 1]} de {año}** ({calendario}).")
    return Resultado((año, mes, dia), pasos)


# ---------------------------------------------------------------------------
# Pascua: algoritmo de Meeus (anónimo gregoriano / Meeus juliano)
# ---------------------------------------------------------------------------

def pascua_meeus(año: int, calendario: str = AUTO) -> Resultado:
    """Algoritmo de Meeus/Jones/Butcher (gregoriano) y de Meeus (juliano).
    No necesita excepciones."""
    if calendario == AUTO:
        calendario = JULIANO if año <= 1582 else GREGORIANO
    pasos: list[str] = [f"Año {año} — calendario {calendario}."]
    if calendario == GREGORIANO:
        a = año % 19
        b, c = divmod(año, 100)
        d, e = divmod(b, 4)
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i, k = divmod(c, 4)
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        n, p = divmod(h + l - 7 * m + 114, 31)
        pasos += [
            f"a = {año} mod 19 = {a}",
            f"{año} = 100·b + c ⇒ b = {b}, c = {c}",
            f"b = 4·d + e ⇒ d = {d}, e = {e}",
            f"f = ⌊(b + 8)/25⌋ = {f}",
            f"g = ⌊(b − f + 1)/3⌋ = {g}",
            f"h = (19a + b − d − g + 15) mod 30 = {19 * a + b - d - g + 15} mod 30 = {h}  (epacta / luna llena)",
            f"c = 4·i + k ⇒ i = {i}, k = {k}",
            f"l = (32 + 2e + 2i − h − k) mod 7 = {32 + 2 * e + 2 * i - h - k} mod 7 = {l}  (hasta el domingo)",
            f"m = ⌊(a + 11h + 22l)/451⌋ = ⌊{a + 11 * h + 22 * l}/451⌋ = {m}  (corrige los casos excepcionales)",
            f"h + l − 7m + 114 = {h + l - 7 * m + 114} = 31·{n} + {p} ⇒ mes = {n}, día = {p} + 1 = {p + 1}",
        ]
        mes, dia = n, p + 1
    else:
        a, b, c = año % 4, año % 7, año % 19
        d = (19 * c + 15) % 30
        e = (2 * a + 4 * b - d + 34) % 7
        n, p = divmod(d + e + 114, 31)
        pasos += [
            f"a = {año} mod 4 = {a},  b = {año} mod 7 = {b},  c = {año} mod 19 = {c}",
            f"d = (19c + 15) mod 30 = {19 * c + 15} mod 30 = {d}",
            f"e = (2a + 4b − d + 34) mod 7 = {2 * a + 4 * b - d + 34} mod 7 = {e}",
            f"d + e + 114 = {d + e + 114} = 31·{n} + {p} ⇒ mes = {n}, día = {p + 1}",
        ]
        mes, dia = n, p + 1
    pasos.append(f"⇒ Domingo de Pascua: **{dia} de {MESES[mes - 1]} de {año}** ({calendario}).")
    return Resultado((año, mes, dia), pasos)


def fiestas_moviles(año: int, calendario: str = AUTO) -> list[tuple[str, tuple[int, int, int]]]:
    """Fiestas que dependen de la Pascua (se calculan sumando días al JDN)."""
    if calendario == AUTO:
        calendario = JULIANO if año <= 1582 else GREGORIANO
    y, m, d = pascua_gauss(año, calendario).valor
    base = jdn(y, m, d, calendario)
    tabla = [("Miércoles de Ceniza", -46), ("Domingo de Ramos", -7), ("Jueves Santo", -3),
             ("Viernes Santo", -2), ("Domingo de Pascua", 0), ("Lunes de Pascua", 1),
             ("Ascensión", 39), ("Pentecostés", 49), ("Corpus Christi", 60)]
    return [(nombre, jdn_a_fecha(base + desp, calendario)) for nombre, desp in tabla]


# ---------------------------------------------------------------------------
# Método mental: «Doomsday» de John Conway (para el juego)
# ---------------------------------------------------------------------------

# Días "ancla" de cada mes: todos caen el mismo día de la semana que el doomsday del año.
# 4/4, 6/6, 8/8, 10/10, 12/12; 9/5, 5/9, 11/7, 7/11 («trabajo de 9 a 5 en el 7-Eleven»);
# 3/1 (4/1 en bisiesto), 28/2 (29/2 en bisiesto), 14/3 (π).
def ancla_mes(año: int, mes: int) -> int:
    bis = es_bisiesto(año)
    return {1: 4 if bis else 3, 2: 29 if bis else 28, 3: 14, 4: 4, 5: 9, 6: 6,
            7: 11, 8: 8, 9: 5, 10: 10, 11: 7, 12: 12}[mes]


ANCLA_SIGLO = {18: 5, 19: 3, 20: 2, 21: 0}  # 1800 vie, 1900 mié, 2000 mar, 2100 dom (domingo = 0)


def doomsday(año: int, mes: int, dia: int) -> Resultado:
    """Método mental de Conway (calendario gregoriano, 1800–2199)."""
    validar_fecha(año, mes, dia, GREGORIANO)
    siglo = año // 100
    if siglo not in ANCLA_SIGLO:
        raise ValueError("El método mental está preparado para los años 1800–2199.")
    pasos = []
    ancla = ANCLA_SIGLO[siglo]
    pasos.append(f"1) Ancla del siglo {siglo}00: {DIAS_DOM0[ancla]} ({ancla}).  "
                 f"[1800 vie · 1900 mié · 2000 mar · 2100 dom]")
    y = año % 100
    a, b = divmod(y, 12)
    c = b // 4
    pasos.append(f"2) y = {y}.  y = 12·{a} + {b}  ⇒  a = {a}, b = {b}, c = ⌊b/4⌋ = {c}.")
    pasos.append(f"   (12 años = 12 + 3 bisiestos = 15 días ≡ 1 mod 7, por eso cada docena suma 1.)")
    dd = (ancla + a + b + c) % 7
    pasos.append(f"3) Doomsday del año = ({ancla} + {a} + {b} + {c}) mod 7 = "
                 f"{ancla + a + b + c} mod 7 = {dd} → {DIAS_DOM0[dd]}.")
    an = ancla_mes(año, mes)
    pasos.append(f"4) Día ancla de {MESES[mes - 1]}: el {an} (cae en {DIAS_DOM0[dd]}).")
    dif = dia - an
    res = (dd + dif) % 7
    pasos.append(f"5) {dia} − {an} = {dif};  ({dd} + {dif}) mod 7 = {res} → **{DIAS_DOM0[res]}**.")
    return Resultado(DIAS_DOM0[res], pasos)


# ---------------------------------------------------------------------------
# Demostración por consola:  python calendario.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(__doc__.split("Este módulo")[0])
    for fecha in [(1492, 10, 12), (1582, 10, 4), (1582, 10, 15), (1969, 7, 20), (2026, 11, 18)]:
        r = zeller(*fecha)
        print("\n".join(r.pasos), "\n")
    for y in (2026, 2027):
        print("\n".join(pascua_gauss(y).pasos), "\n")
