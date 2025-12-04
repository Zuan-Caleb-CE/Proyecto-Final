Descripción 
Aplicación de Python que carga un dataset CSV, lo normaliza y ofrece una interfaz gráfica (Tkinter) para: agregar registros, consultar, aplicar filtros interactivos y generar gráficos dinámicos dentro de la misma interfaz (scatter, boxplot, histogramas, barras, pastel, líneas).  Y utilidades de usabilidad (cargador, temas, animaciones, sonidos si están disponibles). 

Proyecto_final.py

Objetivos cubiertos (resumen)

Integrar interfaces gráficas con Tkinter para gestionar, analizar y visualizar datos. 

Cada funcionalidad (agregar, consultar, filtrar, visualizar estadísticas) se presenta en ventanas/Toplevel independientes desde la ventana principal. 

Filtros interactivos mediante comboboxes, checkboxes y botones; resultados mostrados en la interfaz. 

Generación de gráficos embebidos con Matplotlib + FigureCanvasTkAgg; opción de actualizar gráficos según filtros. 

Estructura del DataFrame

las siguientes columnas son con las que se trabajaron:

ID (del vehiculo)

Categoría (buseta, minibus)

Ruta

Kilometro(Km)

Hora del primer despacho y del ultimo despacho

Frecuencia hora valle y hora pico

Terminal

Empresa 

Nota: todas columnas propias del CSV con el que se esta trabajando

"Filtros (obligatorios e interactivos)"

Filtros básicos (obligatorios).
Filtro por terminales.
Filtro por lugares.

Interactividad en GUI

Los filtros se aplican con Comboboxes y Botones en Tkinter.

Los resultados aparecen en otra ventana y como tablas de Pandas renderizadas en widgets o labels. 

Visualización y personalización de gráficos

Tipos de gráficos requeridos e implementados:

Dispersión (scatter): Capacidad minima vs Capacidad maxima.

Boxplot (gráfico de caja): hora pico vs hora valle.

Histograma: distribución de longitudes Km.

Adicionales: barras, líneas (Frecuencia de terminales).

Selección de colores: permitir al usuario elegir entre al menos 2 paletas predefinidas antes de dibujar el gráfico (El modo clraro y oscuro).

Los gráficos se insertan en Tkinter con FigureCanvasTkAgg y se regeneran cuando se aplican filtros.

Ventana principal (inicio)

Ventana redimensionable con imagen alusiva (logo) y botones para navegar:

Agregar vehiculo / registro.

Consultar / Buscar producto (Lugares o terminales).

Aplicar filtros (Explicados anteriormente).

Visualizar estadísticas / gráficos.

En el código: ventana es la ventana principal y tiene botones que abren Toplevels con cada funcionalidad.

Adición de un vehiculo
Formulario con todos los campos del DataFrame, validaciones básicas (numéricas y de formato).

Requiere autenticación simple (modal) antes de guardar (ejemplo: usuario admin, contraseña 1234 para pruebas).

Al guardar, la fila se agrega al DataFrame global y se persiste al CSV (y se exporta a Excel al finalizar ejecución).

Actualiza df y df_filtrado en memoria y reescribe el CSV .

Estadísticas

Módulo para generar al menos 3 estadísticas relevantes.

Representación con barras, líneas y pastel en ventanas Tkinter separadas. El script ya contiene plantillas para estadísticas por empresa / global.

Requisitos / Instalación

Python 3.8+

Paquetes (instalar via pip):

pip install pandas matplotlib pillow numpy

Ejecutar desde la carpeta que contiene el CSV (o ajustar ruta): el script espera 8._RUTAS_TRANSPORTE_URBANO_20251011.csv junto a Proyecto_final.py. Puedes cambiar csv_filename dentro del script.

Cómo ejecutar

Desde la terminal, en la carpeta del proyecto:

python Proyecto_final.py

La ventana principal aparecerá; usa los botones para navegar.

Para probar guardar un nuevo registro, usa  Agregar vehiculo y luego credenciales de prueba (admin / 1234) si la autenticación está activa.

Proyecto_final.py — código principal. 

Proyecto_final

data/ — CSV original y versiones (ej.: 8._RUTAS_...csv).

resources/ — imágenes (logobus.png), iconos.

docs/ — diseño en Figma/Draw.io, manual de usuario.

README.md — este archivo XD.

Código Python comentado y organizado.

Interfaz Tkinter funcional con filtros y gráficos.

Diseño preliminar en herramienta de prototipado.

Manual de usuario (explicar cada ventana y botones).

Enlace al repositorio GitHub con todo el proyecto y documentación.

Autores:
Zuan Caleb Catata Echeverri Ing. Biomedica
Jacobo Ropero Ramirez Ing. Electronica
