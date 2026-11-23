"""
app.py — «Máquina del tiempo modular» (aplicación web, Opción B del Trabajo 18)
================================================================================

Trabajo 18 · Calendarios y aritmética modular: ¿qué día de la semana fue?
Trabajo de aplicaciones · Temas 1 y 2 · Curso 2026–2027 · Universidad Miguel Hernández

Autores:  Oscar Lidon Garcia  ·  Zhengjie Zhan

Ejecutar en local:      streamlit run app.py
Publicar con enlace:    Streamlit Community Cloud (ver README.md)
"""

import calendar as _cal
import datetime as dt
import random
import time

import pandas as pd
import streamlit as st

import calendario as C

AUTORES = ["Oscar Lidon Garcia", "Zhengjie Zhan"]

st.set_page_config(page_title="Máquina del tiempo modular", page_icon="", layout="wide")


# ---------------------------------------------------------------------------
# Utilidades de presentación
# ---------------------------------------------------------------------------

def fecha_txt(y, m, d):
    return f"{d} de {C.MESES[m - 1]} de {y}"


def mostrar_pasos(pasos, titulo="Pasos del cálculo"):
    st.markdown(f"**{titulo}**")
    st.markdown("\n".join(f"- {p}" for p in pasos))


def selector_fecha(prefijo, y0=1969, m0=7, d0=20, ymin=1, ymax=9999):
    for k, v in (("d", d0), ("m", m0), ("y", y0)):
        st.session_state.setdefault(prefijo + k, v)
    c1, c2, c3 = st.columns(3)
    d = c1.number_input("Día", 1, 31, key=prefijo + "d")
    m = c2.selectbox("Mes", list(range(1, 13)), key=prefijo + "m",
                     format_func=lambda i: f"{i} · {C.MESES[i - 1]}")
    y = c3.number_input("Año", ymin, ymax, key=prefijo + "y")
    return int(y), int(m), int(d)


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

def pagina_inicio():
    st.title("Máquina del tiempo modular")
    st.subheader("Trabajo 18 · Calendarios y aritmética modular: ¿qué día de la semana fue?")
    st.markdown("**Autores:** " + " · ".join(AUTORES))
    st.caption("Trabajo de aplicaciones · Temas 1 y 2 (aritmética entera y modular) · "
               "Curso 2026–2027 · Universidad Miguel Hernández")
    st.divider()
    st.markdown("""
Esta aplicación usa **congruencias módulo 7**, la **división entera** y los restos para:

| Sección | Qué hace |
|---|---|
|  **Día de la semana** | Aplica la **congruencia de Zeller** a cualquier fecha y muestra cada paso; lo comprueba con un segundo método. |
|  **365 ≡ 1 (mod 7)** | Explica por qué cada año la misma fecha cae un día más tarde (dos si hay un 29 de febrero). |
|  **Pascua** | Aplica el **algoritmo de Gauss** y explica qué significa cada resto. |
|  **Reforma gregoriana** | Explica la reforma de 1582, el salto de 10 días y su efecto en los cálculos; incluye un conversor juliano gregoriano. |
|  **Entrenamiento mental** | Un juego para aprender a calcular de cabeza el día de la semana (método *Doomsday* de Conway). |
|  **¿Cómo funciona?** | El fundamento matemático de todo lo anterior. |

Usa el menú de la izquierda para navegar.
""")


def pagina_zeller():
    st.header("¿Qué día de la semana fue?  — Congruencia de Zeller")
    st.latex(r"h \equiv q + \left\lfloor \frac{13(m+1)}{5} \right\rfloor + K + \left\lfloor \frac{K}{4} "
             r"\right\rfloor + \left\lfloor \frac{J}{4} \right\rfloor + 5J \pmod 7 \quad\text{(gregoriano)}")
    st.latex(r"h \equiv q + \left\lfloor \frac{13(m+1)}{5} \right\rfloor + K + \left\lfloor \frac{K}{4} "
             r"\right\rfloor + 5 + 6J \pmod 7 \quad\text{(juliano)}")

    st.markdown("""
**Variables de la fórmula**

| Variable | Significado |
|---|---|
| h | Día de la semana |
| q | Día del mes |
| m | Mes |
| K | Últimos dos dígitos del año |
| J | Primeros dos dígitos del año |

**Valores de h:** 0 = sábado, 1 = domingo, 2 = lunes, 3 = martes, 4 = miércoles, 5 = jueves, 6 = viernes.

Para enero y febrero se toma m = 13 y m = 14 y se usa el año anterior para calcular K y J.
""")

    ejemplos = {"(elige un ejemplo histórico)": None,
                "Llegada de Colón a América — 12/10/1492": (1492, 10, 12),
                "Último día juliano en España — 4/10/1582": (1582, 10, 4),
                "Primer día gregoriano — 15/10/1582": (1582, 10, 15),
                "Muerte de Cervantes — 22/4/1616": (1616, 4, 22),
                "Toma de la Bastilla — 14/7/1789": (1789, 7, 14),
                "Constitución de Cádiz — 19/3/1812": (1812, 3, 19),
                "Llegada a la Luna — 20/7/1969": (1969, 7, 20),
                "Constitución española — 6/12/1978": (1978, 12, 6),
                "Caída del muro de Berlín — 9/11/1989": (1989, 11, 9),
                "Efecto 2000 — 1/1/2000": (2000, 1, 1)}
    def cargar_ejemplo():
        f = ejemplos[st.session_state.zej]
        if f:
            st.session_state.zy, st.session_state.zm, st.session_state.zd = f

    st.selectbox("Ejemplos", list(ejemplos), key="zej", on_change=cargar_ejemplo)
    y, m, d = selector_fecha("z")
    cal = C.AUTO

    try:
        r = C.zeller(y, m, d, cal)
    except ValueError as e:
        st.error(str(e))
        return
    cal_usado = C.validar_fecha(y, m, d, cal)
    st.success(f"### El {fecha_txt(y, m, d)} ({cal_usado}) fue **{r.valor.upper()}**")

    col1, col2 = st.columns([3, 2])
    with col1:
        mostrar_pasos(r.pasos, "Zeller, paso a paso")
    with col2:
        st.markdown("**Comprobación por otro camino (número de día juliano)**")
        n = C.jdn(y, m, d, cal_usado)
        st.markdown(f"JDN = {n:,}".replace(",", ".") + f";  {n} mod 7 = {n % 7}  "
                    f"(0 = lunes) ⇒ **{C.dia_semana_por_jdn(y, m, d, cal_usado)}** ")
        b = C.explicar_bisiesto(y, cal_usado)
        with st.expander(f"¿Es {y} bisiesto?"):
            st.markdown("\n".join(f"- {p}" for p in b.pasos))
    with st.expander("¿Por qué ⌊13(m+1)/5⌋?"):
        st.markdown("""
Contando desde marzo, los meses tienen 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31 días.
Cada mes de 31 días adelanta el día de la semana del mes siguiente en 31 ≡ 3 (mod 7) y cada mes de 30 lo adelanta en 30 ≡ 2 (mod 7).
El término ⌊13(m+1)/5⌋ crece 2 o 3 unidades de un mes al siguiente siguiendo justo ese patrón (13/5 = 2,6 ≈ 30,6 − 28).
Por eso **enero y febrero se tratan como meses 13 y 14 del año anterior**: así el día irregular (29 de febrero)
queda al final y no rompe el patrón.
""")
        filas = [{"m": mm, "Mes": C.MESES[(mm - 1) % 12] if mm <= 12 else C.MESES[mm - 13],
                  "⌊13(m+1)/5⌋": (13 * (mm + 1)) // 5,
                  "mod 7": ((13 * (mm + 1)) // 5) % 7} for mm in range(3, 15)]
        st.dataframe(pd.DataFrame(filas), hide_index=True)


def pagina_anual():
    st.header("Desplazamiento de los días de la semana (módulo 7)")
    st.markdown("""
Una semana tiene 7 días, por lo que utilizamos el módulo 7 para calcular el desplazamiento de los días.

* **Año normal:** 365 = 7·52 + 1 → 365 ≡ 1 (mod 7). El día de la semana avanza 1 día.
* **Año bisiesto:** 366 = 7·52 + 2 → 366 ≡ 2 (mod 7). El día de la semana avanza 2 días, si el intervalo incluye el 29 de febrero.

Por tanto, si una fecha cae en el día *d* de la semana, la misma fecha del año siguiente cae en *d* + 365 ≡ *d* + 1 (mod 7): **un día más tarde** (o *d* + 2 si entre las dos fechas hay un 29 de febrero).

El desplazamiento depende de si el 29 de febrero se encuentra entre las dos fechas, no simplemente de si el año es bisiesto.
""")
    y, m, d = selector_fecha("a", 2023, 3, 14, 1583, 9990)
    n = st.slider("Número de años", 4, 30, 10)
    try:
        C.validar_fecha(y, m, d, C.GREGORIANO)
    except ValueError as e:
        st.error(str(e))
        return
    st.dataframe(pd.DataFrame(C.desplazamiento_anual(y, m, d, n)), hide_index=True, width="stretch")


def gauss_lineas(y, cal):
    """Algoritmo de Gauss: lista de (línea de cálculo, [explicaciones]) y fecha final (año, mes, día)."""
    jul = cal == C.JULIANO
    a, b, c = y % 19, y % 4, y % 7
    L = [
        (f"a = {y} mod 19 = {a}",
         [f"a = {a} → Posición del año en el ciclo de Metón: cada 19 años las fases de la Luna vuelven a caer "
          f"en las mismas fechas, así que solo importa el resto de dividir entre 19 (un valor entre 0 y 18)."]),
        (f"b = {y} mod 4 = {b}",
         [f"b = {b} → Lugar del año dentro del ciclo de 4 años de los bisiestos (b = 0 es un año múltiplo de 4)."]),
        (f"c = {y} mod 7 = {c}",
         [f"c = {c} → Como 365 ≡ 1 (mod 7), cada año las fechas avanzan un día de la semana; c lleva esa cuenta "
          f"módulo 7 y servirá para encontrar el domingo."]),
    ]
    if jul:
        M, N = 15, 6
        L.append(("Calendario juliano: M = 15 y N = 6",
                  ["M = 15, N = 6 → En el calendario juliano no hay correcciones de siglo, así que M y N son "
                   "constantes y no hacen falta k, p ni q."]))
    else:
        k = y // 100
        p = (13 + 8 * k) // 25
        q = k // 4
        M = (15 - p + k - q) % 30
        N = (4 + k - q) % 7
        L.append((f"k = ⌊{y}/100⌋ = {k};  p = ⌊(13 + 8k)/25⌋ = ⌊{13 + 8 * k}/25⌋ = {p};  q = ⌊k/4⌋ = {q}",
                  [f"k = {k} → Siglo del año (división entera entre 100: el {y} pertenece al siglo {k + 1}). "
                   f"Es la base de las correcciones del calendario gregoriano.",
                   f"p = {p} → Corrección lunar: el ciclo de Metón no es exacto y la Luna se retrasa unos 8 días "
                   f"cada 2 500 años; p acumula esos días siglo a siglo.",
                   f"q = {q} → Corrección solar: de los k años seculares solo los múltiplos de 400 son bisiestos, "
                   f"así que k − q mide los bisiestos seculares suprimidos."]))
        L.append((f"M = (15 − p + k − q) mod 30 = ({15 - p + k - q}) mod 30 = {M}",
                  [f"M = {M} → Corrección del siglo para la Luna: parte del valor base 15, resta p (corrección lunar) "
                   f"y suma k − q (corrección solar). Es módulo 30 porque un mes lunar dura casi 30 días."]))
        L.append((f"N = (4 + k − q) mod 7 = ({4 + k - q}) mod 7 = {N}",
                  [f"N = {N} → Corrección del día de la semana por los bisiestos de siglo suprimidos. "
                   f"Es módulo 7 porque se trata de días de la semana."]))

    d = (19 * a + M) % 30
    luna = (3, 21 + d) if 21 + d <= 31 else (4, 21 + d - 31)
    L.append((f"d = (19a + M) mod 30 = (19·{a} + {M}) mod 30 = {19 * a + M} mod 30 = {d}",
              [f"d = {d} → Días que pasan desde el 21 de marzo hasta la luna llena pascual: "
               f"esa luna llena cae el {luna[1]} de {C.MESES[luna[0] - 1]}.",
               f"El factor 19 viene de que cada año las fases de la Luna se adelantan unos 11 días "
               f"(19 ≡ −11 mod 30)."]))
    e = (2 * b + 4 * c + 6 * d + N) % 7
    L.append((f"e = (2b + 4c + 6d + N) mod 7 = (2·{b} + 4·{c} + 6·{d} + {N}) mod 7 = "
              f"{2 * b + 4 * c + 6 * d + N} mod 7 = {e}",
              [f"e = {e} → Días extra hasta el domingo: tras esa luna llena, el domingo siguiente llega "
               f"e + 1 = {e + 1} días después (e va de 0 a 6).",
               f"Los coeficientes 2, 4 y 6 convierten los bisiestos (b), el año (c) y la fecha de la luna llena (d) "
               f"en días de la semana, y N añade la corrección del siglo."]))

    total = 22 + d + e
    if total <= 31:
        mes, dia = 3, total
        sub = [f"22 + d + e → Contando desde el 1 de marzo, la luna llena es el 21 + d y el domingo llega "
               f"e + 1 días después, es decir, el día 22 + d + e.",
               f"{total} ≤ 31 → Sigue siendo marzo: {dia} de marzo."]
    else:
        mes, dia = 4, d + e - 9
        sub = [f"22 + d + e → Contando desde el 1 de marzo, la luna llena es el 21 + d y el domingo llega "
               f"e + 1 días después, es decir, el día 22 + d + e.",
               f"{total} > 31 → Nos pasamos de marzo; restando los 31 días de marzo queda d + e − 9 = {dia} de abril."]
    L.append((f"22 + d + e = 22 + {d} + {e} = {total}", sub))

    if not jul and d == 29 and e == 6:
        mes, dia = 4, 19
        L.append(("Excepción de Gauss: d = 29 y e = 6",
                  ["Sin la excepción saldría el 26 de abril, fecha imposible (la Pascua nunca pasa del 25 de abril), "
                   "así que se sustituye por el 19 de abril."]))
    elif not jul and d == 28 and e == 6 and (11 * M + 11) % 30 < 19:
        mes, dia = 4, 18
        L.append((f"Excepción de Gauss: d = 28, e = 6 y (11M + 11) mod 30 = {(11 * M + 11) % 30} < 19",
                  ["Sin la excepción saldría el 25 de abril; en este caso Gauss lo sustituye por el 18 de abril."]))
    L.append((f"Domingo de Pascua: **{dia} de {C.MESES[mes - 1]} de {y}** ({cal})", []))
    return L, (y, mes, dia)


def mostrar_gauss(y, cal, g):
    """Muestra el algoritmo de Gauss con objetivo y cada línea explicada."""
    st.markdown("**Algoritmo de Gauss**")
    st.markdown(f"**Objetivo:** calcular la fecha del Domingo de Pascua del año {y}, es decir, el primer domingo "
                f"después de la primera luna llena que cae el 21 de marzo o después. Gauss lo consigue solo con "
                f"restos (mod) y divisiones enteras: primero calcula dónde está la Luna (d), después cuántos días "
                f"faltan hasta el domingo (e) y con ambos obtiene el día.")
    L, fecha = gauss_lineas(y, cal)
    if fecha != g.valor:  # seguridad: si no coincidiera, se muestran los pasos básicos
        mostrar_pasos(g.pasos[1:], "")
        return
    lineas = []
    for texto, subs in L:
        lineas.append(f"- {texto}")
        lineas += [f"    - {t}" for t in subs]
    st.markdown("\n".join(lineas))


def pagina_pascua():
    st.header("Fecha de Pascua — algoritmo de Gauss")
    st.markdown("""
**Regla (Concilio de Nicea, 325):** la Pascua es el **primer domingo después de la primera luna llena
que cae el 21 de marzo o después** (equinoccio eclesiástico). Por eso siempre está entre el **22 de marzo y el 25 de abril**.
El algoritmo usa tres ciclos, cada uno con su resto:
* **mod 19:** ciclo de Metón (19 años solares ≈ 235 meses lunares) → fase de la Luna.
* **mod 4** y **mod 7:** bisiestos y días de la semana → para llegar al domingo.
* **mod 30:** la «edad» de la Luna (un mes lunar ≈ 29,5 días).
""")
    y = int(st.number_input("Año", 1, 9999, dt.date.today().year, key="py"))
    cal = C.AUTO
    g = C.pascua_gauss(y, cal)
    cal_usado = g.pasos[0].split("calendario ")[1].rstrip(".")
    _, mm, dd = g.valor
    st.success(f"### Domingo de Pascua {y}: **{dd} de {C.MESES[mm - 1]}** (calendario {cal_usado})")

    mostrar_gauss(y, cal_usado, g)
    dia = C.zeller(*g.valor, calendario=cal_usado).valor
    st.markdown(f"Zeller confirma que el {dd} de {C.MESES[mm - 1]} de {y} es **{dia}**.")


def pagina_reforma():
    st.header("La reforma gregoriana (1582)")
    st.markdown("""
**El problema.** El calendario juliano (Julio César, 46 a. C.) pone un bisiesto cada 4 años, de modo que el año medio dura
365,25 días. El año trópico (de equinoccio a equinoccio) dura unos **365,2422** días. El error es de
0,0078 días/año ≈ **1 día cada 128 años**. Hacia 1582 el equinoccio de primavera había retrocedido al 11 de marzo,
y la regla de la Pascua, que se basa en el 21 de marzo, se iba desfasando.

**La solución (bula *Inter gravissimas* de Gregorio XIII, 24-2-1582):**
1. **Se suprimieron 10 días:** al **jueves 4 de octubre de 1582** le siguió el **viernes 15 de octubre de 1582**.
   El día de la semana **no** se interrumpió (jueves → viernes); solo saltó la numeración.
2. **Nueva regla de bisiestos:** los años seculares (múltiplos de 100) solo son bisiestos si son múltiplos de 400.
   En 400 años hay 97 bisiestos en lugar de 100 ⇒ año medio = 365 + 97/400 = **365,2425** días
   (error ≈ 1 día cada ~3 200 años).
3. Se reformó el cálculo de la luna pascual (correcciones solar y lunar, que son la *M* y la *N* de Gauss).

**Efecto en los cálculos:**
* La congruencia de Zeller cambia en los términos del siglo: ⌊J/4⌋ + 5J (gregoriano) frente a 5 + 6J (juliano).
  Restando, la diferencia es J − ⌊J/4⌋ − 5 ≡ J − ⌊J/4⌋ − 2 (mod 7), que es **exactamente el desfase en días**
  entre los dos calendarios.
* En el algoritmo de Gauss, *M* y *N* dejan de ser constantes (15 y 6) y dependen del siglo.
* Cada país adoptó la reforma en una fecha distinta: España, Italia y Portugal en 1582; Gran Bretaña y sus colonias en 1752
  (2 sep → 14 sep); Rusia en 1918; Grecia en 1923. Cervantes (España) y Shakespeare (Inglaterra) murieron
  ambos «el 23 de abril de 1616», pero **no el mismo día**: compruébalo abajo.
""")
    st.subheader("Desfase juliano–gregoriano por siglos")
    st.dataframe(pd.DataFrame([{"Siglo (año)": s * 100,
                                "¿Bisiesto en juliano?": "sí",
                                "¿Bisiesto en gregoriano?": "sí" if C.es_bisiesto(s * 100) else "no",
                                "Desfase desde el 1 de marzo (días)": C.desfase_juliano_gregoriano(s * 100)}
                               for s in range(15, 22)]), hide_index=True)

    st.subheader("Conversor juliano gregoriano")
    c0, _ = st.columns([2, 3])
    origen = c0.radio("La fecha está en el calendario…", [C.JULIANO, C.GREGORIANO], horizontal=True)
    y, m, d = selector_fecha("r", 1616, 4, 23)
    try:
        y2, m2, d2 = C.convertir_calendario(y, m, d, origen)
    except ValueError as e:
        st.error(str(e))
        return
    destino = C.GREGORIANO if origen == C.JULIANO else C.JULIANO
    n = C.jdn(y, m, d, origen)
    st.success(f"{fecha_txt(y, m, d)} ({origen})  =  **{fecha_txt(y2, m2, d2)} ({destino})** — "
               f"{C.zeller(y, m, d, origen).valor}")
    st.caption(f"Método: se pasa la fecha a número de día juliano (JDN = {n}) y se vuelve al otro calendario. "
               f"Cervantes murió el 22 de abril de 1616 (gregoriano, enterrado el 23) y Shakespeare el 23 de abril "
               f"de 1616 juliano = 3 de mayo gregoriano.")


# --------------------------- Juego de entrenamiento -------------------------

def nueva_pregunta():
    nivel = st.session_state.get("nivel", "Medio (1900–2099)")
    rangos = {"Fácil (año actual)": (dt.date.today().year, dt.date.today().year),
              "Medio (1900–2099)": (1900, 2099), "Difícil (1800–2199)": (1800, 2199)}
    a, b = rangos[nivel]
    y = random.randint(a, b)
    m = random.randint(1, 12)
    d = random.randint(1, C.dias_del_mes(y, m))
    st.session_state.pregunta = (y, m, d)
    st.session_state.respondida = None
    st.session_state.t0 = time.time()


def pagina_juego():
    st.header("Entrenamiento del cálculo mental — método «Doomsday»")
    ss = st.session_state
    for k, v in (("aciertos", 0), ("intentos", 0), ("racha", 0), ("mejor_racha", 0), ("tiempos", [])):
        ss.setdefault(k, v)

    with st.expander("Tarjeta del método mental (léela antes de jugar)", expanded=ss.intentos == 0):
        st.markdown("""
**Idea (J. H. Conway, 1973):** en cada año hay unas fechas fáciles de recordar que **siempre caen el mismo día de la semana**,
el *doomsday* («día del juicio») del año. Basta con calcular ese día y contar desde la fecha ancla más cercana.

Numeramos los días con **domingo = 0, lunes = 1, …, sábado = 6** y trabajamos **módulo 7**.

**1. Ancla del siglo:** 1800 → viernes (5) · **1900 → miércoles (3)** · **2000 → martes (2)** · 2100 → domingo (0).

**2. Doomsday del año** (y = dos últimas cifras):  y = 12·a + b,  c = ⌊b/4⌋  \n  doomsday ≡ ancla + a + b + c (mod 7).
  *¿Por qué?* Cada año suma 1 (365 ≡ 1) y cada bisiesto suma 1 más; 12 años suman 12 + 3 = 15 ≡ 1 (mod 7).

**3. Fechas ancla (todas caen en el doomsday):**

| Mes | Ene | Feb | Mar | Abr | May | Jun | Jul | Ago | Sep | Oct | Nov | Dic |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Día | 3 (4 en bisiesto) | 28 (29 en bisiesto) | 14 (π) | 4 | 9 | 6 | 11 | 8 | 5 | 10 | 7 | 12 |

Truco: 4/4, 6/6, 8/8, 10/10, 12/12 y «trabajo de **9 a 5** en el **7-Eleven**» (9/5, 5/9, 11/7, 7/11).

**4. Contar:** día de la semana ≡ doomsday + (día − día ancla) (mod 7).
""")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aciertos", f"{ss.aciertos}/{ss.intentos}")
    c2.metric("Racha", ss.racha)
    c3.metric("Mejor racha", ss.mejor_racha)
    c4.metric("Tiempo medio", f"{sum(ss.tiempos) / len(ss.tiempos):.1f} s" if ss.tiempos else "—")

    st.selectbox("Nivel", ["Fácil (año actual)", "Medio (1900–2099)", "Difícil (1800–2199)"],
                 index=1, key="nivel", on_change=nueva_pregunta)
    if "pregunta" not in ss:
        nueva_pregunta()
    y, m, d = ss.pregunta
    st.markdown(f"## ¿Qué día de la semana es el **{fecha_txt(y, m, d)}**?")

    with st.expander("Pista"):
        an = C.ANCLA_SIGLO[y // 100]
        st.markdown(f"Ancla del siglo: **{C.DIAS_DOM0[an]}**. Día ancla de {C.MESES[m - 1]}: "
                    f"**{C.ancla_mes(y, m)}**. ¿Es bisiesto? **{'sí' if C.es_bisiesto(y) else 'no'}**.")

    if ss.respondida is None:
        cols = st.columns(7)
        for i, nombre in enumerate(["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]):
            if cols[i].button(nombre.capitalize(), width="stretch", key=f"b{i}"):
                correcto = C.zeller(y, m, d, C.GREGORIANO).valor
                ss.intentos += 1
                ss.tiempos.append(time.time() - ss.t0)
                if nombre == correcto:
                    ss.aciertos += 1
                    ss.racha += 1
                    ss.mejor_racha = max(ss.mejor_racha, ss.racha)
                else:
                    ss.racha = 0
                ss.respondida = nombre
                st.rerun()
    else:
        correcto = C.zeller(y, m, d, C.GREGORIANO).valor
        if ss.respondida == correcto:
            st.success(f"¡Correcto! Es **{correcto}** ({ss.tiempos[-1]:.1f} s).")
        else:
            st.error(f"Has dicho {ss.respondida}; es **{correcto}**.")
        mostrar_pasos(C.doomsday(y, m, d).pasos, "Solución con el método mental")
        st.button("Siguiente fecha ", on_click=nueva_pregunta, type="primary")

    if st.button("Reiniciar marcador"):
        for k in ("aciertos", "intentos", "racha", "mejor_racha"):
            ss[k] = 0
        ss.tiempos = []
        nueva_pregunta()
        st.rerun()


def pagina_como_funciona():
    st.header("¿Cómo funciona?")
    st.markdown(r"""
### 1. División entera y congruencias
Para enteros $a$ y $n>0$ existen $q$ y $r$ únicos con $a = n\,q + r$, $0 \le r < n$. Escribimos $q=\lfloor a/n\rfloor$ y $r = a \bmod n$.
Decimos $a \equiv b \pmod n$ si $n \mid (a-b)$. Las congruencias respetan la suma y el producto, así que **podemos reducir
módulo 7 en cualquier momento** sin cambiar el resultado. Por eso los días de la semana son los elementos de $\mathbb{Z}_7$.

### 2. ¿Por qué cada año un día más?
$365 = 7\cdot 52 + 1 \Rightarrow 365 \equiv 1 \pmod 7$, y $366 \equiv 2 \pmod 7$. Si la fecha $F$ cae en el día $d$,
la misma fecha un año después cae en $d+1$ (o $d+2$ si en medio hay un 29 de febrero).

### 3. Congruencia de Zeller (1882)
Se cuenta cuántos días han pasado desde un origen y solo nos quedamos con el resto módulo 7:
* $q$: el día del mes, que suma directamente.
* $\lfloor 13(m+1)/5\rfloor$: los días acumulados por los meses anteriores (desde marzo), reducidos módulo 7.
* $K$: un día por cada año del siglo (por $365\equiv 1$).
* $\lfloor K/4\rfloor$: un día extra por cada bisiesto del siglo.
* Términos del siglo: un siglo gregoriano tiene $36524$ días, y $36524 \equiv 5 \pmod 7$, de ahí el $5J$. Cada 400 años hay un bisiesto más, de ahí el $\lfloor J/4\rfloor$.
  Un siglo juliano tiene $36525 \equiv 6 \pmod 7$, de ahí el $6J$.
* El resultado $h\in\{0,\dots,6\}$ se interpreta como $0=$ sábado, $1=$ domingo, …, $6=$ viernes.

### 4. Algoritmo de Gauss para la Pascua (1800)
| Resto | Significado |
|---|---|
| $a = Y \bmod 19$ | Lugar del año en el **ciclo de Metón**: cada 19 años las fases lunares vuelven a caer en las mismas fechas. |
| $b = Y \bmod 4$, $c = Y \bmod 7$ | Bisiestos y avance del día de la semana. |
| $d = (19a+M)\bmod 30$ | Días entre el 21 de marzo y la luna llena pascual (la Luna se adelanta unos 11 días cada año: $19a \equiv -11a \pmod{30}$). |
| $e = (2b+4c+6d+N)\bmod 7$ | Días desde la luna llena hasta el **domingo** siguiente. |
| Fecha | $22+d+e$ de marzo, o $d+e-9$ de abril. |

$M$ y $N$ son correcciones del siglo: $k=\lfloor Y/100\rfloor$, $p=\lfloor (13+8k)/25\rfloor$, $q=\lfloor k/4\rfloor$,
$M=(15-p+k-q)\bmod 30$, $N=(4+k-q)\bmod 7$ ($M=15$, $N=6$ en el juliano).
**Excepciones:** si $d=29,\ e=6$ → 19 de abril; si $d=28,\ e=6$ y $(11M+11)\bmod 30<19$ → 18 de abril.

### 5. Método mental (Doomsday)
Combina lo anterior: el ancla del siglo es el término de Zeller del siglo, el paso $a+b+\lfloor b/4\rfloor$ es el término $K+\lfloor K/4\rfloor$ reducido
(usando $12 \cdot 365 + 3 \equiv 1 \pmod 7$), y las fechas ancla sustituyen al término del mes.

### 6. ¿Cómo sabemos que la app no se equivoca?
El archivo `test_calendario.py` comprueba de forma automática que:
* Zeller coincide con la librería `datetime` de Python en **todos los días** del 1-1-1583 al 31-12-2400 (más de 300 000 fechas).
* El método mental coincide en todos los días de 1800 a 2199.
* La Pascua de Gauss cae siempre en domingo y entre el 22-III y el 25-IV,
  y coincide con la librería `dateutil`.
""")


# ---------------------------------------------------------------------------
# Navegación
# ---------------------------------------------------------------------------

PAGINAS = {
    "Inicio": pagina_inicio,
    "Día de la semana (Zeller)": pagina_zeller,
    "365 ≡ 1 (mod 7)": pagina_anual,
    "Pascua (Gauss)": pagina_pascua,
    "Reforma gregoriana": pagina_reforma,
    "Entrenamiento mental": pagina_juego,
    "¿Cómo funciona?": pagina_como_funciona,
}

with st.sidebar:
    st.markdown("## Máquina del tiempo modular")
    st.caption("Trabajo 18 · UMH · 2026–2027")
    st.markdown("**Autores**  \n" + "  \n".join(AUTORES))
    st.divider()
    pagina = st.radio("Secciones", list(PAGINAS), label_visibility="collapsed")

PAGINAS[pagina]()