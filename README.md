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
