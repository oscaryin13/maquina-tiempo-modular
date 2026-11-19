# 🕰️ Máquina del tiempo modular

**Trabajo 18 · Calendarios y aritmética modular: ¿qué día de la semana fue?**
Trabajo de aplicaciones · Temas 1 y 2 · Curso 2026–2027 · Universidad Miguel Hernández
Producto final: **Opción B (aplicación)**

**Autores:** Oscar Lidon Garcia · Zhengjie Zhan

---

## Qué hace la aplicación

| Sección | Qué pide la ficha | Qué hace la app |
|---|---|---|
| 🗓️ Día de la semana | Aplicar la congruencia de Zeller a fechas históricas y comprobar el resultado | Zeller paso a paso (gregoriano y juliano), con 10 fechas históricas precargadas, comprobación por el número de día juliano y hoja del mes |
| 📈 365 ≡ 1 (mod 7) | Deducir por qué cada año la misma fecha cae un día más tarde (dos si hay un 29 de febrero) | Tabla año a año con el salto módulo 7 y su motivo; ciclos de 28 y 400 años |
| 🐣 Pascua | Gauss (o Meeus) para varios años, explicando cada resto | Gauss y Meeus en paralelo con cada resto explicado, excepciones de Gauss, fiestas móviles y tabla de varios años (católica y ortodoxa) |
| ⛪ Reforma gregoriana | Explicar la reforma y su efecto en los cálculos | Explicación, tabla de desfases por siglos, conversor juliano ↔ gregoriano y control del hueco del 5 al 14 de octubre de 1582 |
| 🎮 Entrenamiento mental | Juego de entrenamiento del cálculo mental | Juego con el método *Doomsday*: 3 niveles, marcador, racha, tiempo, pista y solución paso a paso |
| ✍️ Ejemplos resueltos | Ejemplo a mano que coincida con la app | Los ejemplos de la ficha técnica recalculados por la app |
| ❓ ¿Cómo funciona? | Sección obligatoria | Fundamento matemático y referencias |

## Archivos

```
app.py               Interfaz web (Streamlit)
calendario.py        Núcleo matemático: Zeller, Gauss, Meeus, JDN, Doomsday, bisiestos
test_calendario.py   Pruebas automáticas de corrección
requirements.txt     Dependencias
capturas/            Capturas de pantalla para la ficha técnica
```

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py          # se abre en http://localhost:8501
python calendario.py          # demostración por consola, sin interfaz
python test_calendario.py     # pruebas de corrección
```

## Publicar con un enlace (gratis) — Streamlit Community Cloud

1. Cread un repositorio **público** en GitHub y subid estos archivos (al menos `app.py`, `calendario.py` y `requirements.txt`).
2. Entrad en <https://share.streamlit.io> con la cuenta de GitHub → **Create app** → elegid el repositorio, la rama `main` y el archivo `app.py`.
3. En *App URL* poned un nombre, p. ej. `maquina-tiempo-modular`, y pulsad **Deploy**.
4. El enlace queda así: `https://maquina-tiempo-modular.streamlit.app`. Comprobad antes de entregarlo que se abre en una ventana de incógnito.

> Las apps gratuitas se «duermen» si nadie las abre en unos días; basta con abrir el enlace y pulsar *Wake up*.
> Abridla de vez en cuando durante el periodo de evaluación.

## Verificación

`test_calendario.py` comprueba que:
- Zeller coincide con `datetime` de Python en **todos** los días del 1-1-1583 al 31-12-2400.
- Zeller juliano coincide con el número de día juliano (5000 fechas aleatorias).
- El método mental coincide en todos los días de 1800 a 2199.
- Gauss = Meeus para los años 1–5000; la Pascua siempre cae en domingo, entre el 22-III y el 25-IV, y coincide con `dateutil.easter`.
- Fechas de referencia: 4-X-1582 jueves → 15-X-1582 viernes; Pascua de 1981 = 19-IV y de 1954 = 18-IV (excepciones de Gauss).

## Uso de IA (hay que declararlo en la ficha técnica)

La app se ha desarrollado con ayuda de **Claude (Anthropic)**. Hay que indicar en la ficha técnica para qué se usó
(generación del código Python y de la interfaz) y la lista de las instrucciones (prompts) principales.
