import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

df = pd.read_csv("8._RUTAS_TRANSPORTE_URBANO_20251011.csv", index_col="codigo")
print(df.columns)

df_filtrado = df.fillna({"empresa":"BUSETAS AUTONOMA"
                         ,"capacidad_minima" : df["capacidad_minima"].mean(),
                         'capacidad_maxima':df["capacidad_maxima"].mean(),
                        'frecuencia_de_despacho_hora_pico': "00",
                        'hora_primer_despacho': "05:00:00 a.m.",
                        'hora_ultimo_despacho': "08:30:00 p.m",})

df_filtrado["empresa_limpia"] = df_filtrado["empresa"].str.replace("OPERACIÓN AUTORIZADA A ", "", regex=False)

df_filtrado = df_filtrado.dropna()

print(df_filtrado.describe())

print(df_filtrado)


#añadido de metadatos
if 'id' not in df.columns:
    df = df.copy()                         
    df['id'] = range(1, len(df) + 1)        
    print("se añadio la columna'id'")
else:
    print("'id' ya existe")


bloqueado = False      # Para controlar la activación/desactivación

def a():
    print("algo")

def allempresas():
    print("MOSTRAR TODAS LAS EMPRESAS")

def cerrar_y_volver(ventana_actual):
    # Cerrar la ventana secundaria
    if ventana_actual is not None:
        try:
            ventana_actual.destroy()
        except:
            pass

def invempresas(nombre):

    # Cerrar SOLO ventanas secundarias, excepto la principal
    for w in ventana.winfo_children():
        if isinstance(w, tk.Toplevel):
            try:
                w.destroy()
            except:
                pass
    # Ocultar ventana principal
    ventana.withdraw()
    # --- Filtrar empresa ---
    df_emp = df_filtrado[df_filtrado["empresa_limpia"] == nombre]

    if df_emp.empty:
        tk.messagebox.showerror("Error", "No hay datos para esta empresa")
        ventana.deiconify()
        return

    # --- Crear ventana ---
    ven_emp = tk.Toplevel(ventana)
    ven_emp.title(f"Estadísticas — {nombre}")
    ven_emp.geometry("750x700")
    ven_emp.config(bg="#F5F5F5")
    ven_emp.transient(ventana)
    ven_emp.grab_set()

    # ============================================================
    #                  SCROLLBAR Y CANVAS
    # ============================================================
    contenedor = tk.Frame(ven_emp)
    contenedor.pack(fill="both", expand=True)

    canvas = tk.Canvas(contenedor, bg="#F5F5F5")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    # Para permitir scroll dentro del frame → truco oficial de Tkinter
    frame_scroll = tk.Frame(canvas, bg="#F5F5F5")
    canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_scroll.bind("<Configure>", actualizar_scroll)

    # ============================================================
    #                        CONTENIDO
    # ============================================================

    # --------- Título ---------
    lbl_titulo = tk.Label(
        frame_scroll,
        text=f"Empresa: {nombre}",
        font=("Arial", 18, "bold"),
        bg="#F5F5F5"
    )
    lbl_titulo.pack(pady=20)

    # --------- Gráfica ---------
    conteo_term = df_emp["terminal"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    conteo_term.plot(kind="bar", color="skyblue", ax=ax)

    ax.set_title(f"Frecuencia de terminales — {nombre}", fontsize=10)
    ax.set_xlabel("Terminal")
    ax.set_ylabel("Cantidad")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    ax.grid(alpha=0.3)

    frame_graf = tk.Frame(frame_scroll, bg="#F5F5F5")
    frame_graf.pack(pady=10)

    canvas_graf = FigureCanvasTkAgg(fig, master=frame_graf)
    canvas_graf.draw()
    canvas_graf.get_tk_widget().pack()

    # --------- Estadísticas numéricas ---------
    cant = len(df_emp)
    cap_max = df_emp["capacidad_maxima"].mean()
    cap_min = df_emp["capacidad_minima"].mean()
    frec_pico = df_emp["frecuencia_de_despacho_hora_pico"].mean()
    frec_valle = df_emp["frecuencia_despacho_hora_valle"].mean()

    texto = (
        f"• Vehículos registrados: {cant}\n\n"
        f"• Capacidad Máxima promedio: {round(cap_max, 2)}\n\n"
        f"• Capacidad Mínima promedio: {round(cap_min, 2)}\n\n"
        f"• Frecuencia hora pico promedio: {round(frec_pico, 2)}\n\n"
        f"• Frecuencia hora valle promedio: {round(frec_valle, 2)}"
    )

    frame_info = tk.Frame(frame_scroll, bg="white", bd=1, relief="solid")
    frame_info.pack(padx=30, pady=20, fill="x")

    lbl_info = tk.Label(frame_info, text=texto, font=("Arial", 12),
                        bg="white", justify="left", anchor="w")
    lbl_info.pack(padx=20, pady=20)

    # --------- Botón volver ---------
    btn_volver = tk.Button(
        frame_scroll,
        text="Volver al menú principal",
        font=("Arial", 12),
        width=25,
        height=2,
        bg="#D9EAF7",
        command=lambda: cerrar_y_volver(ven_emp)
    )
    btn_volver.pack(pady=20)

# -------------------------------------------------------------------
# ----- VENTANA DE SELECCION DE ESTADISTICAS ------------------------
# -------------------------------------------------------------------
def estats():
    est_dec = tk.Toplevel(ventana)
    est_dec.columnconfigure(0, weight=1)
    est_dec.columnconfigure(1, weight=1)
    est_dec.title("Estadísticas de vehículos")
    est_dec.geometry("450x300")

    empresas = ["UNITRANSA S.A.", "TRANSCOLOMBIA S.A.", "COTRANDER",
                "LUSITANIA S.A.", "ORIENTAL DE TRANSPORTES S.A.",
                "TRANSPORTES SAN JUAN S.A.", "TRANSPORTES PIEDECUESTA S.A."]

    list_emp = ttk.Combobox(est_dec, values=empresas, width=35, state="disabled")
    list_emp.set("Seleccione una empresa...")
    list_emp.grid(row=2, column=0, pady=10, columnspan=2)

    btn_ver = tk.Button(est_dec, text="Ver Empresa", width=20,
                        command=lambda: invempresas(list_emp.get()))

    def toggle():
        if list_emp.instate(["disabled"]):   # ← CORREGIDO
            list_emp.config(state="readonly")
            btn_all.config(state="disabled")
            btn_ver.config(state=tk.NORMAL)
        else:
            list_emp.config(state="disabled")
            btn_all.config(state="normal")
            btn_ver.config(state=tk.DISABLED)

    btn_all = tk.Button(est_dec, text="Todas las Empresas", width=20, command=allempresas)
    btn_all.grid(row=1, column=1)

    btn_inv = tk.Button(est_dec, text="Empresa Individual", width=20, command=toggle)
    btn_inv.grid(row=1, column=0)

    btn_ver.grid(row=4, column=0, columnspan=2, pady=10)

    boton_cancelar = tk.Button(est_dec, text="Cancelar", width=20, height=2, command=est_dec.destroy)
    boton_cancelar.grid(row=5, column=0, columnspan=2, pady=5, padx=10)

# -------------------------------------------------------------------
# -----  V E N T A N A   P R I N C I P A L ---------------------------
# -------------------------------------------------------------------
ventana = tk.Tk()
ventana.title("Menu Principal")
ventana.geometry("400x450")
ventana.config(bg="white")

# Centrar los elementos
ventana.columnconfigure(0, weight=1)
ventana.columnconfigure(1, weight=1)

labelprin = tk.Label(ventana, text="Transporte Urbano", bg="lightgrey", font=("Arial", 20))
labelprin.grid(row=0, column=0, columnspan=2, pady=10)

# Imagen
try: #por si no encuentra la imagen
    imagen = Image.open(r"logobus.png") #ruta de la imagen
    imagen = imagen.resize((200, 200)) #redimensiona la imagen
    imagen_tk = ImageTk.PhotoImage(imagen)#convierte la imagen para tkinter

    label_imagen = tk.Label(ventana, image=imagen_tk)#pone la imagen en un label
    label_imagen.image = imagen_tk #mantiene una referencia para que no se borre
    label_imagen.grid(row=1, column=0, columnspan=2, pady=10) #coloca el label en la ventana
except FileNotFoundError:# para evitar que se mate si no encuentra la imagen
    print("Error: The file 'logobus.png' was not found. Please ensure the file is in the correct location.")#saca un error en consola, en ingles porque es un error tecnico
    label_imagen = tk.Label(ventana, text="Imagen no disponible", font=("Arial", 12), bg="lightgrey")#pone un label de texto en vez de la imagen avisando que no se encontro
    label_imagen.grid(row=1, column=0, columnspan=2, pady=10)#coloca el label en la ventana

# Botones principales
btn_estads = tk.Button(text="Estaditicas de Vehiculos", width=20, height=2, command=estats)
btn_agregar = tk.Button(text="Agregar vehiculo", width=20, height=2, command=a)
btn_visual = tk.Button(text="Visualización de rutas", width=20, height=2, command=a)

btn_estads.grid(row=4, column=0, pady=10, padx=5)
btn_agregar.grid(row=5, column=0, pady=10, padx=5)
btn_visual.grid(row=4, column=1, pady=10, padx=5)

# -------------------------------------------------------------
# Ventana de salir
# -------------------------------------------------------------
def cerrar():
    ventana.quit()
    ventana.destroy()

def salir():
    sal = tk.Toplevel(ventana)
    sal.title("Salir")
    sal.geometry("350x150")
    sal.transient(ventana)
    sal.grab_set()

    lbl_salir = tk.Label(sal, text="¿Seguro que deseas salir?")
    lbl_salir.grid(row=0, column=0, columnspan=2, pady=20)

    boton_si = tk.Button(sal, text="Sí", width=20, height=2, command=cerrar)
    boton_si.grid(row=1, column=0, padx=10)

    boton_no = tk.Button(sal, text="No", width=20, height=2, command=sal.destroy)
    boton_no.grid(row=1, column=1, padx=10)

btn_salir = tk.Button(text="Salir", width=20, height=2, command=salir)
btn_salir.grid(row=5, column=1, pady=10, padx=5)

def cerrar_y_volver(ventana_actual):
    ventana_actual.destroy()
    ventana.deiconify()     # Vuelve a mostrar el menú principal

def cerrar_ventana(vent):
    vent.destroy()

ventana.mainloop()

#creacion archivo excel; lo ultimito
df.to_excel("Excel_RUTAS_TRANSPORTE_URBANO.xlsx", index=False)
print("Guardado Excel_RUTAS_TRANSPORTE_URBANO.xlsx")

cant_total = len(df_filtrado)
prom_gen_max = df_filtrado["capacidad_maxima"].mean()
prom_gen_min = df_filtrado["capacidad_minima"].mean()
prom_frec_pico = df_filtrado["frecuencia_de_despacho_hora_pico"].mean()
prom_frec_valle = df_filtrado["frecuencia_despacho_hora_valle"].mean()

df_filtrado["long_km"] = pd.to_numeric(df_filtrado["long_km"], errors="coerce") # convierte los numeros que estan guardados como string a numeros operables
prom_km = df_filtrado["long_km"].mean()

mindf = {
    "Cantidad de veiculos registrados" : cant_total,
    "Promedio Capacidad Maxima" : round(prom_gen_max,2),
    "Promedio Capacidad Minima" : round(prom_gen_min,2),
    "Promedio Frecuencia de despacho en hora pico" : round(prom_frec_pico,2),
    "Promedio Frecuencia de despacho en hora valle" : round(prom_frec_valle,2),
    "Promedio de Kilometros" : round(prom_km, 2)
}
minidata = pd.DataFrame([mindf])
minidata

df_empr1 = df_filtrado[df_filtrado["empresa"] == "OPERACIÓN AUTORIZADA A UNITRANSA S.A."]

nombre_emp = df_empr1["empresa"].iloc[0]
print("Empresa:", nombre_emp)

cant = len(df_empr1)
cap_max = df_empr1["capacidad_maxima"].mean()
cap_min = df_empr1["capacidad_minima"].mean()
frec_pico = df_empr1["frecuencia_de_despacho_hora_pico"].mean()
frec_valle = df_empr1["frecuencia_despacho_hora_valle"].mean()

print(f"La cantidad de veiculos registrado de la empresa {nombre_emp} es: {cant}")
print(f"El promedio de la \"Capacidad Maxima\" de la empresa {nombre_emp} es: {round(cap_max, 2)}")
print(f"El promedio de la \"Capacidad Minima\" de la empresa {nombre_emp} es: {round(cap_min, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora pico\" de la empresa {nombre_emp} es: {round(frec_pico, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora valle\" de la empresa {nombre_emp} es: {round(frec_valle, 2)}")

conteo_term = df_empr1["terminal"].value_counts()

conteo_term.plot(kind="bar", figsize=(10,5), color="skyblue")

# Personalizar la gráfica
plt.title(f"Frecuencia de terminales de la empresa {nombre_emp}")
plt.xlabel("Terminal")
plt.ylabel("Cantidad")
plt.xticks(rotation=45, ha="right")  # rotar nombres para que se lean mejor
plt.tight_layout()
plt.grid()
#plt.show()

df_empr3 = df_filtrado[df_filtrado["empresa"] == "OPERACIÓN AUTORIZADA A TRANSCOLOMBIA S.A."]

nombre_emp = df_empr3["empresa"].iloc[0]
print("Empresa:", nombre_emp)

cant = len(df_empr3)
cap_max = df_empr3["capacidad_maxima"].mean()
cap_min = df_empr3["capacidad_minima"].mean()
frec_pico = df_empr3["frecuencia_de_despacho_hora_pico"].mean()
frec_valle = df_empr3["frecuencia_despacho_hora_valle"].mean()

print(f"La cantidad de veiculos registrado de la empresa {nombre_emp} es: {cant}")
print(f"El promedio de la \"Capacidad Maxima\" de la empresa {nombre_emp} es: {round(cap_max, 2)}")
print(f"El promedio de la \"Capacidad Minima\" de la empresa {nombre_emp} es: {round(cap_min, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora pico\" de la empresa {nombre_emp} es: {round(frec_pico, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora valle\" de la empresa {nombre_emp} es: {round(frec_valle, 2)}")

conteo_term = df_empr3["terminal"].value_counts()

conteo_term.plot(kind="bar", figsize=(10,5), color="skyblue")

plt.title(f"Frecuencia de terminales de la empresa {nombre_emp}")
plt.xlabel("Terminal")
plt.ylabel("Cantidad")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid()
#plt.show()

df_empr4 = df_filtrado[(df_filtrado["empresa"] == "OPERACIÓN AUTORIZADA A COTRANDER") | (df_filtrado["empresa"] == "COTRANDER")]

nombre_emp = df_empr4["empresa"].iloc[0]
print("Empresa:", nombre_emp)

cant = len(df_empr4)
cap_max = df_empr4["capacidad_maxima"].mean()
cap_min = df_empr4["capacidad_minima"].mean()
frec_pico = df_empr4["frecuencia_de_despacho_hora_pico"].mean()
frec_valle = df_empr4["frecuencia_despacho_hora_valle"].mean()

print(f"La cantidad de veiculos registrado de la empresa {nombre_emp} es: {cant}")
print(f"El promedio de la \"Capacidad Maxima\" de la empresa {nombre_emp} es: {round(cap_max, 2)}")
print(f"El promedio de la \"Capacidad Minima\" de la empresa {nombre_emp} es: {round(cap_min, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora pico\" de la empresa {nombre_emp} es: {round(frec_pico, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora valle\" de la empresa {nombre_emp} es: {round(frec_valle, 2)}")

conteo_term = df_empr4["terminal"].value_counts()

conteo_term.plot(kind="bar", figsize=(10,5), color="skyblue")

plt.title(f"Frecuencia de terminales de la empresa {nombre_emp}")
plt.xlabel("Terminal")
plt.ylabel("Cantidad")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid()
#plt.show()

df_empr5 = df_filtrado[df_filtrado["empresa"] == "LUSITANIA S.A."]

nombre_emp = df_empr5["empresa"].iloc[0]
print("Empresa:", nombre_emp)

cant = len(df_empr5)
cap_max = df_empr5["capacidad_maxima"].mean()
cap_min = df_empr5["capacidad_minima"].mean()
frec_pico = df_empr5["frecuencia_de_despacho_hora_pico"].mean()
frec_valle = df_empr5["frecuencia_despacho_hora_valle"].mean()

print(f"La cantidad de veiculos registrado de la empresa {nombre_emp} es: {cant}")
print(f"El promedio de la \"Capacidad Maxima\" de la empresa {nombre_emp} es: {round(cap_max, 2)}")
print(f"El promedio de la \"Capacidad Minima\" de la empresa {nombre_emp} es: {round(cap_min, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora pico\" de la empresa {nombre_emp} es: {round(frec_pico, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora valle\" de la empresa {nombre_emp} es: {round(frec_valle, 2)}")

conteo_term = df_empr5["terminal"].value_counts()

conteo_term.plot(kind="bar", figsize=(10,5), color="skyblue")

plt.title(f"Frecuencia de terminales de la empresa {nombre_emp}")
plt.xlabel("Terminal")
plt.ylabel("Cantidad")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid()
#plt.show()

df_empr6 = df_filtrado[df_filtrado["empresa"] == "ORIENTAL DE TRANSPORTES S.A."]

nombre_emp = df_empr6["empresa"].iloc[0]
print("Empresa:", nombre_emp)

cant = len(df_empr6)
cap_max = df_empr6["capacidad_maxima"].mean()
cap_min = df_empr6["capacidad_minima"].mean()
frec_pico = df_empr6["frecuencia_de_despacho_hora_pico"].mean()
frec_valle = df_empr6["frecuencia_despacho_hora_valle"].mean()

print(f"La cantidad de veiculos registrado de la empresa {nombre_emp} es: {cant}")
print(f"El promedio de la \"Capacidad Maxima\" de la empresa {nombre_emp} es: {round(cap_max, 2)}")
print(f"El promedio de la \"Capacidad Minima\" de la empresa {nombre_emp} es: {round(cap_min, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora pico\" de la empresa {nombre_emp} es: {round(frec_pico, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora valle\" de la empresa {nombre_emp} es: {round(frec_valle, 2)}")

conteo_term = df_empr6["terminal"].value_counts()

conteo_term.plot(kind="bar", figsize=(10,5), color="skyblue")

plt.title(f"Frecuencia de terminales de la empresa {nombre_emp}")
plt.xlabel("Terminal")
plt.ylabel("Cantidad")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid()
#plt.show()

df_empr7 = df_filtrado[df_filtrado["empresa"] == "TRANSPORTES SAN JUAN S.A."]

nombre_emp = df_empr7["empresa"].iloc[0]
print("Empresa:", nombre_emp)

cant = len(df_empr7)
cap_max = df_empr7["capacidad_maxima"].mean()
cap_min = df_empr7["capacidad_minima"].mean()
frec_pico = df_empr7["frecuencia_de_despacho_hora_pico"].mean()
frec_valle = df_empr7["frecuencia_despacho_hora_valle"].mean()

print(f"La cantidad de veiculos registrado de la empresa {nombre_emp} es: {cant}")
print(f"El promedio de la \"Capacidad Maxima\" de la empresa {nombre_emp} es: {round(cap_max, 2)}")
print(f"El promedio de la \"Capacidad Minima\" de la empresa {nombre_emp} es: {round(cap_min, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora pico\" de la empresa {nombre_emp} es: {round(frec_pico, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora valle\" de la empresa {nombre_emp} es: {round(frec_valle, 2)}")

conteo_term = df_empr7["terminal"].value_counts()

conteo_term.plot(kind="bar", figsize=(10,5), color="skyblue")

plt.title(f"Frecuencia de terminales de la empresa {nombre_emp}")
plt.xlabel("Terminal")
plt.ylabel("Cantidad")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid()
#plt.show()

df_empr8 = df_filtrado[df_filtrado["empresa"] == "TRANSPORTES PIEDECUESTA S.A."]

nombre_emp = df_empr8["empresa"].iloc[0]
print("Empresa:", nombre_emp)

cant = len(df_empr8)
cap_max = df_empr8["capacidad_maxima"].mean()
cap_min = df_empr8["capacidad_minima"].mean()
frec_pico = df_empr8["frecuencia_de_despacho_hora_pico"].mean()
frec_valle = df_empr8["frecuencia_despacho_hora_valle"].mean()

print(f"La cantidad de veiculos registrado de la empresa {nombre_emp} es: {cant}")
print(f"El promedio de la \"Capacidad Maxima\" de la empresa {nombre_emp} es: {round(cap_max, 2)}")
print(f"El promedio de la \"Capacidad Minima\" de la empresa {nombre_emp} es: {round(cap_min, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora pico\" de la empresa {nombre_emp} es: {round(frec_pico, 2)}")
print(f"El promedio de la \"Frecuencia de despacho en hora valle\" de la empresa {nombre_emp} es: {round(frec_valle, 2)}")

conteo_term = df_empr8["terminal"].value_counts()

conteo_term.plot(kind="bar", figsize=(10,5), color="skyblue")

plt.title(f"Frecuencia de terminales de la empresa {nombre_emp}")
plt.xlabel("Terminal")
plt.ylabel("Cantidad")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid()
#plt.show()

filava = df_filtrado["empresa"].str.replace("OPERACIÓN AUTORIZADA A ", "", regex=False).str.strip()

# Contar frecuencia de empresas
empresas = filava.value_counts()
promedio_vehiculos = empresas.mean()
print("Promedio de vehículos registrados por empresa:", round(promedio_vehiculos))

# Filtrar empresas que están por encima del promedio
empresas_mayores = empresas[empresas > promedio_vehiculos]
print("\nEmpresas por encima del promedio:\n", empresas_mayores)

# Crear un nuevo DataFrame filtrado y asegurar que sea una copia independiente
df_mayores = df_filtrado[
    df_filtrado["empresa"]
    .str.replace("OPERACIÓN AUTORIZADA A ", "", regex=False)
    .str.strip()
    .isin(empresas_mayores.index)
].copy()  # <-- ESTA ES LA CLAVE

print("\nDataFrame filtrado (empresas mayores al promedio):")
print(df_mayores)

# Convertir columna a numérica sin advertencias
df_mayores["long_km"] = pd.to_numeric(df_mayores["long_km"], errors="coerce")

# Filtrar registros con menos de 30 km
df_long = df_mayores[df_mayores["long_km"] < 30].copy()

print("\nDataFrame final (longitud menor a 30 km):")
print(df_long)


df = pd.read_csv("8._RUTAS_TRANSPORTE_URBANO_20251011.csv", index_col="codigo")
df['long_km'] = (df['long_km'].astype(str) #lo convierte a string para que sea mas facil de trabajar
                 
                 .str.replace(',', '.', regex=False)          #comas -> puntos

                 .str.extract(r"([-+]?[0-9]*\.?[0-9]+)")[0]   #Busca dentro del texto solo numeros
                 #esa cosota significa:
                 #[-+]? → puede tener signo “+” o “-” al inicio.
                 #[0-9]* → puede tener varios dígitos antes del punto.
                 #\.? → puede tener un punto decimal.
                 #[0-9]+ → al menos un dígito después del punto.
                    # el [0] al final toma la columna del resultado del extract,
                    # ya que devuelve un DataFrame.
                 
                 #lo anterior bota texto; esto lo vuelve a float
                 .astype(float, errors='ignore'))
                  #errors evita que se mate el programa si hay algún valor no convertible
                  # (lo deja igual)

#agrupacion por empresa

#agrupa el DataFrame por la columna empresa
                             #dropna=False hace que también incluya filas donde “empresa” está vacía
res = df.groupby('empresa', dropna=False)['long_km'].agg(cantidad='count', promedio_km='mean', desviacion_estandar_km='std') \
    .reset_index()                                  #agg es agreggate; agregar
  #Convierte el índice del groupby en un un DataFrame limpio para imprimir

print(res)   # muestra en consola

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("8._RUTAS_TRANSPORTE_URBANO_20251011.csv", index_col="codigo")
print(df.columns) # saco la database de nuevo

DF = df #para evitar modificar accidentalmente el df
pico = "frecuencia_de_despacho_hora_pico"
valle = "frecuencia_despacho_hora_valle"

#itera dos veces: una para pico y otra para valle
for c in (pico, valle):
    #convierte todos los valores de la columna a texto;
    #por si hay estan vacios o sonnúmeros
    DF[c] = (DF[c].astype(str)
               .str.replace(",", ".", regex=False)            #comas -> puntos
               .str.extract(r"([-+]?[0-9]*\.?[0-9]+)")[0]     ##Busca dentro del texto solo numeros
                 #esa cosota significa:
                 #[-+]? → puede tener signo “+” o “-” al inicio.
                 #[0-9]* → puede tener varios dígitos antes del punto.
                 #\.? → puede tener un punto decimal.
                 #[0-9]+ → al menos un dígito después del punto.
                    # el [0] al final toma la columna del resultado del extract,
                    # ya que devuelve un DataFrame.
             )
    DF[c] = pd.to_numeric(DF[c], errors="coerce")
    #convierte el texto resultante a número

#   escoge las dos columnas       calcula tres cosas por columna; 
#       de interés en un            cantidad (valores no nulos), 
#       DataFrame                    media y desviación estándar
stats_general = DF[[pico, valle]].agg(['count', 'mean', 'std'])\
.T.rename(columns={'count':'cantidad','mean':'promedio','std':'desviacion'})
#transpone la tabla para que     renombra las columnas del resultado 
#las filas sean pico y valle             a nombres en español 
 #(más legible).                   cantidad, promedio, desviacion

print("Estadísticas generales (pico vs valle):")
print(stats_general)

medias = DF[[pico, valle]].mean() #calcula las medias de estos datos
desvs  = DF[[pico, valle]].std() #calcula la desviación estándar,por columna, de pico y valle

x = np.arange(len(medias))           
 #Crea un arreglo [0, 1] igual de largo que medias, sirve como posiciones en X para las barras

etiquetas = ['Pico', 'Valle']   # nombres en el eje x 
anchura = 0.6                   #Ancho de cada barra en el gráfico

plt.figure(figsize=(6,4)) #Crea un lienzo para el gráfico de tamaño 6×4

#Dibuja las barras en las 
#posiciones x con alturas medias
plt.bar(x, medias\
, width=anchura, yerr=desvs, capsize=6) #el tamaño de la tapita encima de la barra
#yerr=desvs añade barras de error verticales 
#con longitud igual a la desviación estándar


plt.xticks(x, etiquetas) #pone ['Pico','Valle'] en el eje x
plt.ylabel('Frecuencia (media)') #nombra el eje Y Frecuencia (media)
plt.title('Media ± desviación estándar: frecuencia despacho (Pico vs Valle)') #titulo del gráfico
plt.grid(axis='y', linestyle='--', alpha=0.3) #dibuja la cuadricula
plt.tight_layout() #ajusta los margenes para que no se corte nada
#plt.show() #muestra el grafico

#filtra el DataFrame y se queda
#solo con las columnas que son numeros     obtiene los nombres de esas columnas
num_cols = DF.select_dtypes(include=[np.number]).columns.tolist()#convierte ese índice de columnas en una lista normal

#crea un diccionario donde cada clave c
counts = {c: DF[c].count() for c in num_cols}#Crea un diccionario que guarda cuántos valores válidos hay
#c es el nombre de num_cols y el valor es el número de elementos no nulos en esa columna

#retorna una lista de claves ordenadas de mayor a menor por su conteo.
sorted_cols = sorted(counts, key=lambda k: counts[k], reverse=True)
#ordena las claves del diccionario counts usando como criterio el valor counts[k]

xcol, ycol = sorted_cols[0], sorted_cols[1]
#toma los dos primeros elementos de la lista ordenada y los asigna al eje X y al eje Y

print(f"Usando columnas para scatter: X = '{xcol}'  ,  Y = '{ycol}'")

#crea un sub-DataFrame con solo dos columnas y elimina todas las filas que tengan
df_sc = DF[[xcol, ycol]].dropna()
#extrae los valores de cada columna como arrays
x = df_sc[xcol].values
y = df_sc[ycol].values

#ajustar linea recta (regresión simple)
m, b = np.polyfit(x, y, 1)
#m,bmin​i∑​(yi​−(mxi​+b))2 <- hace eso

y_fit = m * x + b#para dibujar la línea de tendencia en el gráfico; una lineal normalita

plt.figure(figsize=(6,4))#Crea un lienzo para el gráfico de tamaño 6×4
plt.scatter(x, y, alpha=0.7)
#dibuja los puntos x_i, y_i; alpha=0.7 hace puntos semitransparentes para que no se tapen

#conecta x_i, y_fit_i con una linea
plt.plot(x, y_fit, color='orange', linewidth=2)#Color orange y grosor de 2

#pone los nombres en los ejes con los nombres de las columnas
plt.xlabel(xcol)
plt.ylabel(ycol)

plt.title(f"Scatter: {ycol} vs {xcol} (línea de tendencia)") #titulo del gráfico
plt.grid(True, linestyle='--', alpha=0.3) #dibuja la cuadricula
plt.tight_layout()#ajusta los margenes para que no se corte nada
#plt.show() #muestra la grafica

#es una función de numpy que calcula la correlación
corr = np.corrcoef(x, y)[0,1] if len(x) > 1 else np.nan#si hay más de un dato, calcula la correlacion; sinó, pon NaN
#Esto toma el valor de la posición 0,1 de esa matriz, r=correlación

print(f"Pendiente (m) = {m:.4f} ; intercepto (b) = {b:.4f} ; correlación r = {corr:.4f}")
#4 dígitos después del punto y formato float

longitudes = df_filtrado["long_km"]

plt.figure(figsize=(16, 8))  # tamaño 
plt.hist(longitudes, bins=20, color= "cyan", edgecolor="black")  # bins controla cuántos "bloques" hay
# Títulos y etiquetas
plt.title("Distribución de la longitud de las rutas", fontsize=14) # fontsize gradua el tmaño de los titulos
plt.xlabel("Longitud de la ruta (km)", fontsize=12)
plt.ylabel("Frecuencia", fontsize=12) 
plt.grid()
plt.tight_layout()
#plt.show()