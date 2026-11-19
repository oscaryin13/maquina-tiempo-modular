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


def selector_calendario(prefijo):
    op = st.radio("Calendario", [C.AUTO, C.GREGORIANO, C.JULIANO], horizontal=True, key=prefijo + "cal",
                  format_func=lambda s: {"auto": "Automático (el vigente en España)",
                                         "gregoriano": "Gregoriano", "juliano": "Juliano"}[s])
    return op


def mini_calendario(y, m, d, cal):
    """Hoja del mes con el día marcado (lunes primero)."""
    primero = C.dia_semana_por_jdn(y, m, 1, cal)
    orden = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    offset = orden.index(primero)
    n = C.dias_del_mes(y, m, cal)
    celdas = [""] * offset + [str(i) for i in range(1, n + 1)]
    if y == 1582 and m == 10 and cal == C.GREGORIANO:  # mes de la reforma
        celdas = [""] * orden.index("lunes") + ["1", "2", "3", "4"] + [str(i) for i in range(15, 32)]
    while len(celdas) % 7:
        celdas.append("")
    filas = [celdas[i:i + 7] for i in range(0, len(celdas), 7)]
    df = pd.DataFrame(filas, columns=["L", "M", "X", "J", "V", "S", "D"])

    def marcar(v):
        return "background-color:#ffd54f;font-weight:bold" if v == str(d) else ""
    st.dataframe(df.style.map(marcar), hide_index=True, width="stretch")


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
    hoy = dt.date.today()
    st.info(f"Hoy es **{C.zeller(hoy.year, hoy.month, hoy.day).valor}**, {fecha_txt(hoy.year, hoy.month, hoy.day)}. "
            f"Lo ha calculado la congruencia de Zeller, no el reloj del ordenador.")
    st.markdown("""
Esta aplicación usa **congruencias módulo 7**, la **división entera** y los restos para:

| Sección | Qué hace |
|---|---|
|  **Día de la semana** | Aplica la **congruencia de Zeller** a cualquier fecha y muestra cada paso; lo comprueba con un segundo método. |
|  **365 ≡ 1 (mod 7)** | Explica por qué cada año la misma fecha cae un día más tarde (dos si hay un 29 de febrero). |
|  **Pascua** | Aplica los **algoritmos de Gauss y de Meeus** y explica qué significa cada resto. |
|  **Reforma gregoriana** | Explica la reforma de 1582, el salto de 10 días y su efecto en los cálculos; incluye un conversor juliano gregoriano. |
|  **Entrenamiento mental** | Un juego para aprender a calcular de cabeza el día de la semana (método *Doomsday* de Conway). |
|  **Ejemplos resueltos** | Los ejemplos hechos a mano en la ficha técnica, para cotejarlos con la app. |
|  **¿Cómo funciona?** | El fundamento matemático de todo lo anterior. |

Usa el menú de la izquierda para navegar.
""")


def pagina_zeller():
    st.header("¿Qué día de la semana fue?  — Congruencia de Zeller")
    st.latex(r"h \equiv q + \left\lfloor \frac{13(m+1)}{5} \right\rfloor + K + \left\lfloor \frac{K}{4} "
             r"\right\rfloor + \left\lfloor \frac{J}{4} \right\rfloor + 5J \pmod 7 \quad\text{(gregoriano)}")
    st.latex(r"h \equiv q + \left\lfloor \frac{13(m+1)}{5} \right\rfloor + K + \left\lfloor \frac{K}{4} "
             r"\right\rfloor + 5 + 6J \pmod 7 \quad\text{(juliano)}")

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
    cal = selector_calendario("z")

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
        st.markdown(f"**{C.MESES[m - 1].capitalize()} de {y}** ({cal_usado})")
        mini_calendario(y, m, d, cal_usado)
        st.markdown("**Comprobación por otro camino (número de día juliano)**")
        n = C.jdn(y, m, d, cal_usado)
        st.markdown(f"JDN = {n:,}".replace(",", ".") + f";  {n} mod 7 = {n % 7}  "
                    f"(0 = lunes) ⇒ **{C.dia_semana_por_jdn(y, m, d, cal_usado)}** ")
        b = C.explicar_bisiesto(y, cal_usado)
        with st.expander(f"¿Es {y} bisiesto?"):
            st.markdown("\n".join(f"- {p}" for p in b.pasos))
        if cal_usado == C.JULIANO:
            gy, gm, gd = C.convertir_calendario(y, m, d, C.JULIANO)
            st.info(f"En el calendario gregoriano (proléptico) ese mismo día sería el {fecha_txt(gy, gm, gd)}.")
        elif (y, m, d) >= (1, 3, 1):
            jy, jm, jd = C.convertir_calendario(y, m, d, C.GREGORIANO)
            st.caption(f"En el calendario juliano ese mismo día era el {fecha_txt(jy, jm, jd)}.")

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
    st.header("365 ≡ 1 (mod 7): cada año, un día más")
    st.markdown("""
Una semana tiene 7 días. Al dividir los días de un año entre 7:

* **Año normal:** 365 = 7·52 + **1**  ⇒  365 ≡ 1 (mod 7)
* **Año bisiesto:** 366 = 7·52 + **2**  ⇒  366 ≡ 2 (mod 7)

Si una fecha cae un día *d* de la semana, la misma fecha del año siguiente cae, por tanto, en
*d* + 365 ≡ *d* + 1 (mod 7): **un día más tarde**. Si entre las dos fechas hay un 29 de febrero, el salto es de **dos**.
Ojo: lo que importa es si el 29 de febrero queda *entre* las dos fechas, no si el año es bisiesto.
Para un cumpleaños en marzo de 2023, el salto a 2024 es de 2; para uno en enero de 2024, el salto de 2024 a 2025 es de 1.
""")
    y, m, d = selector_fecha("a", 2023, 3, 14, 1583, 9990)
    n = st.slider("Número de años", 4, 30, 10)
    try:
        C.validar_fecha(y, m, d, C.GREGORIANO)
    except ValueError as e:
        st.error(str(e))
        return
    st.dataframe(pd.DataFrame(C.desplazamiento_anual(y, m, d, n)), hide_index=True, width="stretch")
    st.markdown("""
**Consecuencias:**
* En 4 años julianos hay 4·365 + 1 = 1461 días; 1461 = 7·208 + 5 ⇒ el calendario **no** se repite cada 4 años.
* En 28 años julianos hay 28·365 + 7 = 10227 días = 7·1461 ≡ 0 (mod 7): el calendario juliano se repite cada **28 años** (ciclo solar).
* En 400 años gregorianos hay 400·365 + 97 = 146097 días = 7·20871 ≡ 0 (mod 7): el calendario gregoriano se repite exactamente cada **400 años**.
""")
    st.markdown("**Años con el mismo calendario que el elegido** (misma fecha del 1 de enero y mismo tipo de año):")
    base_dia = C.dia_semana_por_jdn(y, 1, 1, C.GREGORIANO)
    iguales = [a for a in range(y - 40, y + 41) if a != y and a >= 1583
               and C.es_bisiesto(a) == C.es_bisiesto(y) and C.dia_semana_por_jdn(a, 1, 1, C.GREGORIANO) == base_dia]
    st.write(", ".join(map(str, iguales)) or "—")


def pagina_pascua():
    st.header("Fecha de Pascua — algoritmos de Gauss")
    st.markdown("""
**Regla (Concilio de Nicea, 325):** la Pascua es el **primer domingo después de la primera luna llena
que cae el 21 de marzo o después** (equinoccio eclesiástico). Por eso siempre está entre el **22 de marzo y el 25 de abril**.
El algoritmo usa tres ciclos, cada uno con su resto:
* **mod 19:** ciclo de Metón (19 años solares ≈ 235 meses lunares) → fase de la Luna.
* **mod 4** y **mod 7:** bisiestos y días de la semana → para llegar al domingo.
* **mod 30:** la «edad» de la Luna (un mes lunar ≈ 29,5 días).
""")
    c1, c2 = st.columns(2)
    y = int(c1.number_input("Año", 1, 9999, dt.date.today().year, key="py"))
    cal = c2.radio("Calendario", [C.AUTO, C.GREGORIANO, C.JULIANO], horizontal=True, key="pcal",
                   format_func=lambda s: {"auto": "Automático (juliano hasta 1582)",
                                          "gregoriano": "Gregoriano (Iglesia católica)",
                                          "juliano": "Juliano (Iglesias ortodoxas)"}[s])
    g = C.pascua_gauss(y, cal)
    me = C.pascua_meeus(y, cal)
    cal_usado = g.pasos[0].split("calendario ")[1].rstrip(".")
    _, mm, dd = g.valor
    st.success(f"### Domingo de Pascua {y}: **{dd} de {C.MESES[mm - 1]}** (calendario {cal_usado})")

    col1, col2 = st.columns(2)
    with col1:
        mostrar_pasos(g.pasos[1:], "Algoritmo de Gauss")
    with col2:
        mostrar_pasos(me.pasos[1:], "Algoritmo de Meeus (comprobación)")
        if g.valor == me.valor:
            st.markdown("**Los dos algoritmos coinciden.**")
        else:
            st.error("Los algoritmos no coinciden (no debería ocurrir).")
        dia = C.zeller(*g.valor, calendario=cal_usado).valor
        st.markdown(f"Zeller confirma que el {dd} de {C.MESES[mm - 1]} de {y} es **{dia}**.")

    st.subheader("Fiestas móviles de ese año")
    st.dataframe(pd.DataFrame([{"Fiesta": n, "Fecha": fecha_txt(*f),
                                "Día": C.zeller(*f, calendario=cal_usado).valor}
                               for n, f in C.fiestas_moviles(y, cal_usado)]), hide_index=True)

    st.subheader("Pascua de varios años")
    a, b = st.slider("Intervalo", 1583, 2200, (2020, 2035))
    filas = []
    for yy in range(a, b + 1):
        gg = C.pascua_gauss(yy, C.GREGORIANO)
        jj = C.pascua_gauss(yy, C.JULIANO)
        jg = C.convertir_calendario(*jj.valor, C.JULIANO)
        A, B, Cc = yy % 19, yy % 4, yy % 7
        filas.append({"Año": yy, "a=Y mod 19": A, "b=Y mod 4": B, "c=Y mod 7": Cc,
                      "Católica (greg.)": f"{gg.valor[2]}/{gg.valor[1]}",
                      "Ortodoxa (fecha gregoriana)": f"{jg[2]}/{jg[1]}",
                      "¿Coinciden?": "sí" if (jg[1], jg[2]) == gg.valor[1:] else ""})
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")


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


def pagina_ejemplos():
    st.header("Ejemplos resueltos a mano (para cotejar con la ficha técnica)")
    st.markdown("Estos son los ejemplos que hemos resuelto a mano. La app los recalcula en tiempo real: "
                "los resultados deben coincidir con los de la ficha técnica.")
    st.subheader("1. Zeller — 12 de octubre de 1492 (calendario juliano)")
    mostrar_pasos(C.zeller(1492, 10, 12).pasos, "")
    st.subheader("2. Zeller con enero — 1 de enero de 2000 (gregoriano)")
    mostrar_pasos(C.zeller(2000, 1, 1).pasos, "")
    st.subheader("3. Pascua de 2026 — algoritmo de Gauss")
    mostrar_pasos(C.pascua_gauss(2026).pasos, "")
    st.subheader("4. Pascua de 1981 — caso excepcional de Gauss")
    mostrar_pasos(C.pascua_gauss(1981).pasos, "")
    st.subheader("5. Método mental — 20 de julio de 1969")
    mostrar_pasos(C.doomsday(1969, 7, 20).pasos, "")


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
El **algoritmo de Meeus** obtiene lo mismo sin excepciones y la app lo usa como comprobación.

### 5. Método mental (Doomsday)
Combina lo anterior: el ancla del siglo es el término de Zeller del siglo, el paso $a+b+\lfloor b/4\rfloor$ es el término $K+\lfloor K/4\rfloor$ reducido
(usando $12 \cdot 365 + 3 \equiv 1 \pmod 7$), y las fechas ancla sustituyen al término del mes.

### 6. ¿Cómo sabemos que la app no se equivoca?
El archivo `test_calendario.py` comprueba de forma automática que:
* Zeller coincide con la librería `datetime` de Python en **todos los días** del 1-1-1583 al 31-12-2400 (más de 300 000 fechas).
* El método mental coincide en todos los días de 1800 a 2199.
* Gauss y Meeus dan la misma Pascua desde el año 1 hasta el 5000, siempre en domingo y entre el 22-III y el 25-IV,
  y coinciden con la librería `dateutil`.

### Referencias
- Zeller, C. (1882). Die Grundaufgaben der Kalenderrechnung auf neue und vereinfachte Weise gelöst. *Württembergische Vierteljahrshefte für Landesgeschichte*, 5, 313–314.
- Gauss, C. F. (1800). Berechnung des Osterfestes. *Monatliche Correspondenz zur Beförderung der Erd- und Himmels-Kunde*, 2, 121–130.
- Meeus, J. (1991). *Astronomical Algorithms*. Willmann-Bell.
- Berlekamp, E. R., Conway, J. H., & Guy, R. K. (1982). *Winning Ways for your Mathematical Plays* (Vol. 2). Academic Press.
- Richards, E. G. (2013). Calendars. En S. E. Urban & P. K. Seidelmann (Eds.), *Explanatory Supplement to the Astronomical Almanac* (3.ª ed.). University Science Books.
- Gregorio XIII (1582). Bula *Inter gravissimas*.
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
    "Ejemplos resueltos": pagina_ejemplos,
    "¿Cómo funciona?": pagina_como_funciona,
}

with st.sidebar:
    st.markdown("## Máquina del tiempo modular")
    st.caption("Trabajo 18 · UMH · 2026–2027")
    st.markdown("**Autores**  \n" + "  \n".join(AUTORES))
    st.divider()
    pagina = st.radio("Secciones", list(PAGINAS), label_visibility="collapsed")

PAGINAS[pagina]()
