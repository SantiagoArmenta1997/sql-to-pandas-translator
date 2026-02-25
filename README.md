# 📊 SQL to Pandas Translator (v1.final)

**Transforma tus consultas SQL complejas en código Python eficiente de forma automática.**

Este proyecto nace de la necesidad de agilizar la transición entre el análisis de datos tradicional en bases de datos y el análisis avanzado en Python. No es un simple reemplazo de texto; es un motor lógico que interpreta la intención de tu SQL para generar scripts de Pandas optimizados.

---

## 🌟 Características Principales

- **Agregaciones Inteligentes**: Traduce `COUNT`, `SUM`, `AVG` y más, utilizando el método `.agg()` de Pandas para mantener el código limpio.
- **Manejo de Subqueries**: Resuelve subconsultas correlacionadas en el `SELECT` mediante lógica de pre-procesamiento y `merges`.
- **Limpieza Automática de Alias**: Olvídate de los errores por prefijos como `o.` o `c.`. El traductor limpia los nombres de las tablas para que coincidan con tus DataFrames.
- **Filtros LIKE Potentes**: Convierte `LIKE 'A%'`, `'%B'` o `'%C%'` en sus equivalentes exactos de `.str.startswith`, `.str.endswith` y `.str.contains`.
- **Renombrado Dinámico**: Aplica los alias de SQL (`AS alias`) automáticamente para que tu resultado final esté listo para reportar.

---

## 🛠️ Cómo funciona

1. **Entrada**: Copia tu Query de SQL (T-SQL / Estándar).
2. **Traducción**: El motor descompone el SQL y lo mapea a funciones de Pandas.
3. **Salida**: Obtienes un script de Python listo para copiar y pegar, dividido en pasos lógicos.



---

## 🧪 Casos de Uso Soportados (Pruebas v1.final)

### 1. Reportes de Ventas (Joins + GroupBy)
Maneja uniones de tablas y cálculos agrupados por categorías, generando un código que primero une, luego filtra y finalmente agrega.

### 2. Cruce de Datos Complejos (Subqueries)
Ideal para cuando necesitas traer un dato específico de otra tabla sin hacer un Join masivo, utilizando subconsultas en el SELECT.

### 3. Segmentación de Clientes (Strings + Alias)
Perfecto para filtrar nombres o correos por patrones de texto y renombrar columnas para una mejor presentación.

---

## ⚠️ Notas de Uso

* **Nombres de DataFrames**: El código generado asume que tus DataFrames en Python se llaman igual que tus tablas en SQL (ej. `customers`, `orders`).
* **Dependencias**: El código generado requiere `pandas`. El traductor en sí utiliza `sqlglot`.
* **Sensibilidad a Mayúsculas**: Recuerda que Pandas diferencia entre mayúsculas y minúsculas en los filtros de texto.

---

## 🤝 Feedback y Bug Hunting

¡Esta es la versión **v1.final** y quiero ponerla a prueba! 
Si encuentras un Query que rompa el traductor o genere un error de Python, por favor házmelo saber. Mi objetivo es que este motor sea capaz de manejar cualquier consulta analítica estándar.

---
**Desarrollado con 🐍 y ❤️ para la comunidad de datos.**