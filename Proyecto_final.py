import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import unicodedata

df = pd.read_csv("8._RUTAS_TRANSPORTE_URBANO_20251011.csv", index_col="codigo")
print(df.columns)

#normalizar y convertir a numérico las columnas que deben ser números
cols_numericas = [
    "capacidad_minima",
    "capacidad_maxima",
    "frecuencia_de_despacho_hora_pico",
    "frecuencia_despacho_hora_valle",
    "long_km"
]
for col in cols_numericas:
    if col in df.columns:
        #convertir a string, cambiar comas por puntos y extraer el primer número que encuentre
        df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
        df[col] = df[col].str.extract(r'([-+]?\d*\.?\d+)')[0]
        df[col] = pd.to_numeric(df[col], errors="coerce")

#crear diccionario de fillna usando medias numéricas limpias cuando existan
llenar = {"empresa": "BUSETAS AUTONOMA",
          "hora_primer_despacho": "05:00:00 a.m.",
          "hora_ultimo_despacho": "08:30:00 p.m"}

if "capacidad_minima" in df.columns:
    llenar["capacidad_minima"] = df["capacidad_minima"].mean()
if "capacidad_maxima" in df.columns:
    llenar["capacidad_maxima"] = df["capacidad_maxima"].mean()
if "frecuencia_de_despacho_hora_pico" in df.columns:
    llenar["frecuencia_de_despacho_hora_pico"] = df["frecuencia_de_despacho_hora_pico"].mean()
#nota: frecuencia_valle no está en la clave exacta usada para fillna en tu archivo original;
#si existe en df se puede añadir igual que arriba:
if "frecuencia_despacho_hora_valle" in df.columns:
    llenar["frecuencia_despacho_hora_valle"] = df["frecuencia_despacho_hora_valle"].mean()

df_filtrado = df.fillna(llenar)


df_filtrado["empresa_limpia"] = df_filtrado["empresa"].str.replace("OPERACIÓN AUTORIZADA A ", "", regex=False)

df_filtrado = df_filtrado.dropna(subset=['ruta','terminal'], how='all')

print(df_filtrado.describe())

print(df_filtrado)

#extrae las columnas necesarias del DataFrame
lugares = df["ruta"].dropna().unique().tolist()  #elimina valores nulos y convierte a lista

#separa las rutas por el carácter "-" y extrae los lugares únicos
lugares_separados = set()  #usa un conjunto para evitar duplicados
for ruta in lugares:
    lugares_separados.update([lugar.strip() for lugar in ruta.split("-")])  #separa y elimina espacios

lugares = sorted(lugares_separados)  #convierte el conjunto a una lista y la ordena alfabéticamente

#extrae y ordena las terminales
terminales = sorted(set(df["terminal"].dropna().astype(str).str.strip()))  #elimina valores nulos y convierte a lista
terminales.sort()

#imprime las listas
print("Lugares:")
print(lugares)

print("\nTerminales:")
print(terminales)

#añadido de metadatos
if 'id' not in df.columns:
    df = df.copy()                         
    df['id'] = range(1, len(df) + 1)        
    print("se añadio la columna'id'")
else:
    print("'id' ya existe")


bloqueado = False      # Para controlar la activación/desactivación

def solicitar_credenciales(padre):
    #abrir ventana modal para pedir usuario y contraseña
    credenciales_validas = {"admin":"1234"}  #CONTRASEÑA FIJA PARA PRUEBAS
    resultado = [False]  #lista mutable para capturar resultado desde la ventana modal

    ventana_cred = tk.Toplevel(padre)
    ventana_cred.transient(padre)
    ventana_cred.grab_set()
    ventana_cred.title("Autenticación")
    ventana_cred.geometry("320x160")

    usuario_var = tk.StringVar()
    clave_var = tk.StringVar()

    ttk.Label(ventana_cred, text="usuario:").grid(row=0, column=0, pady=(12,6), padx=10, sticky="w")
    entrada_usuario = ttk.Entry(ventana_cred, textvariable=usuario_var, width=30)
    entrada_usuario.grid(row=0, column=1, pady=(12,6), padx=10)

    ttk.Label(ventana_cred, text="contraseña:").grid(row=1, column=0, pady=(6,6), padx=10, sticky="w")
    entrada_clave = ttk.Entry(ventana_cred, textvariable=clave_var, show="*", width=30)
    entrada_clave.grid(row=1, column=1, pady=(6,6), padx=10)

    def comprobar():
        usu = usuario_var.get().strip()
        cla = clave_var.get().strip()
        if credenciales_validas.get(usu) == cla:
            resultado[0] = True
            ventana_cred.destroy()
        else:
            try:
                tk.messagebox.showerror("Error", "usuario o contraseña incorrectos")
            except:
                pass

    btn_aceptar = ttk.Button(ventana_cred, text="Aceptar", command=comprobar)
    btn_aceptar.grid(row=2, column=0, pady=12, padx=10)
    btn_cancel = ttk.Button(ventana_cred, text="Cancelar", command=ventana_cred.destroy)
    btn_cancel.grid(row=2, column=1, pady=12, padx=10)

    entrada_usuario.focus_set()
    ventana_cred.wait_window()  #espera hasta que se cierre la ventana modal
    return resultado[0]


def a(): # El placeholder supremo de la función, se uso para pruebas
    print("algo")


####################################################################3
#################################################################
##ver estadisticas de todas las empresas
#########################################################################3
#########################################################3


def allempresas():
    #mostrar estadisticas agregadas de todas las empresas (arreglo rapido para que no quede bajo la barra de tareas)
    try:
        df_todas = df.copy()
    except Exception as e:
        print("debug: no se pudo copiar df:", e)
        try:
            tk.messagebox.showerror("Error", "No fue posible acceder a los datos.")
        except:
            pass
        return

    #si no hay datos, avisar
    if df_todas.empty:
        try:
            tk.messagebox.showinfo("Información", "No hay registros en el dataset.")
        except:
            pass
        return

    #crear ventana principal con altura reducida para evitar solapamiento con la barra de tareas
    ven_all = tk.Toplevel(ventana)
    ven_all.title("Estadísticas — Todas las empresas")
    ven_all.geometry("980x700")  #ancho x alto reducido para evitar taskbar
    ven_all.minsize(800, 600)
    ven_all.config(bg="#F5F5F5")
    ven_all.transient(ventana)
    ven_all.grab_set()

    #header fijo superior con título y botón volver (siempre visible)
    marco_header = ttk.Frame(ven_all, padding=(8,6))
    marco_header.pack(side="top", fill="x")
    etiqueta_titulo = ttk.Label(marco_header, text="Estadísticas agregadas — Todas las empresas", font=("Arial", 14, "bold"))
    etiqueta_titulo.pack(side="left", padx=(6,0))
    btn_volver_header = tk.Button(
        marco_header,
        text="Volver al menú principal",
        font=("Arial", 10),
        width=20,
        height=1,
        bg="#D9EAF7",
        command=lambda: cerrar_y_volver(ven_all)
    )
    btn_volver_header.pack(side="right", padx=(0,8))

    #área scrollable para contenido (contenido principal debe poder scrollear, header permanece)
    contenedor = tk.Frame(ven_all)
    contenedor.pack(fill="both", expand=True)
    canvas = tk.Canvas(contenedor, bg="#F5F5F5", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    frame_scroll = tk.Frame(canvas, bg="#F5F5F5")
    canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_scroll.bind("<Configure>", actualizar_scroll)

    #función auxiliar para convertir columnas numéricas
    def convertir_numericas_seguras(df_local, candidatos):
        for c in candidatos:
            if c in df_local.columns:
                df_local[c] = (df_local[c].astype(str)
                               .str.replace(",", ".", regex=False)
                               .str.extract(r"([-+]?\d*\.?\d+)")[0])
                df_local[c] = pd.to_numeric(df_local[c], errors="coerce")
        return df_local

    #columnas candidatas para frecuencia y longitudes
    candidatos_freq = [
        "frecuencia_de_despacho_hora_pico", "frecuencia_de_despacho_pico", "frecuencia_pico",
        "frecuencia_despacho_hora_valle", "frecuencia_de_despacho_hora_valle", "frecuencia_valle",
        "frecuencia_despacho_hora_valle"
    ]
    posibles_long = ["long_km", "longitud", "longitud_km", "long_km"]

    #convertir numéricas en el df agregado
    df_todas = convertir_numericas_seguras(df_todas, candidatos_freq)
    df_todas = convertir_numericas_seguras(df_todas, posibles_long)
    df_todas = convertir_numericas_seguras(df_todas, ["capacidad_minima", "capacidad_maxima"])

    #marco rejilla: dos columnas arriba, fila ancha abajo
    marco_graficos = ttk.Frame(frame_scroll)
    marco_graficos.pack(padx=8, pady=6, fill="both", expand=False)
    marco_graficos.columnconfigure(0, weight=1)
    marco_graficos.columnconfigure(1, weight=1)

    #función para renderizar figura dentro de frame
    def render_fig_en_frame(fig, parent_frame):
        try:
            canvas_fig = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas_fig.draw()
            widget = canvas_fig.get_tk_widget()
            widget.pack(fill="both", expand=True)
        except Exception as e:
            print("debug: error renderizando figura en frame:", e)

    #--------- GRAFICO 1 (0,0): scatter (compacto) ----------
    try:
        frame_a = ttk.Frame(marco_graficos, padding=4)
        frame_a.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        num_cols = df_todas.select_dtypes(include=[np.number]).columns.tolist()
        num_cols = [c for c in num_cols if c not in ("id",)]
        if len(num_cols) >= 2:
            conteos = {c: df_todas[c].count() for c in num_cols}
            cols_orden = sorted(conteos, key=lambda k: conteos[k], reverse=True)
            xcol, ycol = cols_orden[0], cols_orden[1]
            df_sc = df_todas[[xcol, ycol]].dropna()
            if len(df_sc) > 1:
                x = df_sc[xcol].values
                y = df_sc[ycol].values
                try:
                    m, b = np.polyfit(x, y, 1)
                    y_fit = m * x + b
                except Exception:
                    y_fit = None
                fig_a, ax_a = plt.subplots(figsize=(3.4,2.4), dpi=100)  #compacto
                ax_a.scatter(x, y, alpha=0.6, s=16)
                if y_fit is not None:
                    ax_a.plot(x, y_fit, color='orange', linewidth=1.0)
                ax_a.set_xlabel(xcol, fontsize=7)
                ax_a.set_ylabel(ycol, fontsize=7)
                ax_a.set_title(f"Dispersión: {ycol} vs {xcol}", fontsize=8)
                ax_a.grid(alpha=0.2, linestyle='--')
                fig_a.tight_layout()
                render_fig_en_frame(fig_a, frame_a)
            else:
                ttk.Label(frame_a, text="no hay suficientes datos numéricos", background="#F5F5F5").pack(expand=True, fill="both")
        else:
            ttk.Label(frame_a, text="menos de 2 columnas numéricas en el dataset", background="#F5F5F5").pack(expand=True, fill="both")
    except Exception as e:
        print("debug: error grafico scatter todas:", e)

    #--------- GRAFICO 2 (0,1): pico vs valle (compacto) ----------
    try:
        frame_b = ttk.Frame(marco_graficos, padding=4)
        frame_b.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        candidatos_pico = ["frecuencia_de_despacho_hora_pico", "frecuencia_de_despacho_pico", "frecuencia_pico", "frecuencia_de_pico"]
        candidatos_valle = ["frecuencia_despacho_hora_valle", "frecuencia_de_despacho_hora_valle", "frecuencia_valle", "frecuencia_de_valle"]

        pico_col = next((c for c in candidatos_pico if c in df_todas.columns), None)
        valle_col = next((c for c in candidatos_valle if c in df_todas.columns), None)

        if pico_col or valle_col:
            valores_pico = df_todas[pico_col].dropna() if pico_col else pd.Series(dtype=float)
            valores_valle = df_todas[valle_col].dropna() if valle_col else pd.Series(dtype=float)

            medias = [valores_pico.mean() if not valores_pico.empty else np.nan,
                      valores_valle.mean() if not valores_valle.empty else np.nan]
            desv = [valores_pico.std() if not valores_pico.empty else np.nan,
                   valores_valle.std() if not valores_valle.empty else np.nan]

            if not all(np.isnan(medias)):
                medias_plot = [0 if np.isnan(m) else m for m in medias]
                desv_plot = [0 if np.isnan(d) else d for d in desv]
                etiquetas = ['Pico', 'Valle']
                x = np.arange(len(etiquetas))
                fig_b, ax_b = plt.subplots(figsize=(3.4,2.4), dpi=100)  #compacto
                ax_b.bar(x, medias_plot, width=0.6, yerr=desv_plot, capsize=4)
                ax_b.set_xticks(x)
                ax_b.set_xticklabels(etiquetas, fontsize=7)
                ax_b.set_ylabel('Frecuencia (media)', fontsize=7)
                ax_b.set_title('Media ± desviación: Pico vs Valle', fontsize=8)
                ax_b.grid(axis='y', alpha=0.2, linestyle='--')
                fig_b.tight_layout()
                render_fig_en_frame(fig_b, frame_b)
            else:
                ttk.Label(frame_b, text="no hay datos para Pico/Valle", background="#F5F5F5").pack(expand=True, fill="both")
        else:
            ttk.Label(frame_b, text="no se encontraron columnas Pico/Valle", background="#F5F5F5").pack(expand=True, fill="both")
    except Exception as e:
        print("debug: error grafico pico/valle todas:", e)

    #--------- GRAFICO 3 (fila inferior, ancho completo): barras de terminales (ancho reducido en alto) ----------
    try:
        frame_c = ttk.Frame(frame_scroll, padding=6)
        frame_c.pack(fill="both", expand=False, padx=6, pady=(6,8))

        if "terminal" in df_todas.columns and not df_todas["terminal"].dropna().empty:
            conteo_term = df_todas["terminal"].value_counts()
            #mostrar solo top N para evitar que la barra sea demasiado alta/ancha
            top_n = 25
            conteo_term_top = conteo_term.iloc[:top_n]
            fig_c, ax_c = plt.subplots(figsize=(9,2.2), dpi=100)  #altura reducida
            conteo_term_top.plot(kind="bar", ax=ax_c)
            ax_c.set_title("Frecuencia de terminales — Todas las empresas (top {})".format(min(top_n, len(conteo_term))), fontsize=9)
            ax_c.set_xlabel("Terminal")
            ax_c.set_ylabel("Cantidad")
            plt.setp(ax_c.get_xticklabels(), rotation=45, ha="right", fontsize=7)
            ax_c.grid(alpha=0.2)
            fig_c.tight_layout()
            render_fig_en_frame(fig_c, frame_c)
        else:
            ttk.Label(frame_c, text="sin datos de terminales en el dataset", background="#F5F5F5").pack(expand=True, fill="both")
    except Exception as e:
        print("debug: error grafico terminales todas:", e)

    #--------- resumen estadístico debajo (compacto) ----------
    try:
        total_reg = len(df_todas)
        cap_max = df_todas["capacidad_maxima"].mean() if "capacidad_maxima" in df_todas.columns else float("nan")
        cap_min = df_todas["capacidad_minima"].mean() if "capacidad_minima" in df_todas.columns else float("nan")
        texto = (
            f"• Registros totales: {total_reg}\n\n"
            f"• Capacidad máxima promedio: {round(cap_max,2) if not pd.isna(cap_max) else 'N/A'}\n\n"
            f"• Capacidad mínima promedio: {round(cap_min,2) if not pd.isna(cap_min) else 'N/A'}"
        )
    except Exception as e:
        print("debug: error calculando resumen todas:", e)
        texto = "No fue posible calcular estadísticas."

    frame_info = tk.Frame(frame_scroll, bg="white", bd=1, relief="solid")
    frame_info.pack(padx=12, pady=8, fill="x")
    lbl_info = tk.Label(frame_info, text=texto, font=("Arial", 11), bg="white", justify="left")
    lbl_info.pack(padx=10, pady=8)

    #acción al cerrar
    def al_cerrar():
        try:
            ven_all.destroy()
        finally:
            try:
                ventana.deiconify()
            except:
                pass

    ven_all.protocol("WM_DELETE_WINDOW", al_cerrar)



##############################################################################3
###############################################################################3
#######################################################################################3

def cerrar_y_volver(ventana_actual):
    # Cerrar la ventana secundaria
    if ventana_actual is not None:
        try:
            ventana_actual.destroy()
        except:
            pass

######################################################################
#######################################################################
########################################################################3

#ver estadisticas de una empresa específica

def invempresas(nombre):
    #cerrar solo ventanas secundarias antes de abrir la nueva
    try:
        for w in ventana.winfo_children():
            if isinstance(w, tk.Toplevel):
                try:
                    w.destroy()
                except:
                    pass
    except Exception as e:
        print("debug: error cerrando toplevels previos:", e)

    #si el nombre es el placeholder o vacío, avisar y no continuar
    if not nombre or nombre.strip() == "" or "Seleccione" in nombre:
        try:
            tk.messagebox.showinfo("Información", "Seleccione una empresa válida antes de ver.")
        except:
            pass
        return

    #normalizar nombre buscado (case-insensitive)
    nombre_buscar = nombre.strip().lower()

    #filtrar de forma segura usando igualdad primero luego contains
    try:
        df_emp = df_filtrado[
            df_filtrado["empresa_limpia"].astype(str).str.strip().str.lower() == nombre_buscar
        ].copy()
    except Exception as e:
        print("debug: error filtrando empresa:", e)
        try:
            tk.messagebox.showerror("Error", f"error interno al filtrar: {e}")
        except:
            pass
        return

    if df_emp.empty:
        try:
            df_emp = df_filtrado[
                df_filtrado["empresa_limpia"].astype(str).str.strip().str.lower().str.contains(
                    re.escape(nombre_buscar)
                )
            ].copy()
        except Exception as e:
            print("debug: error secundario filtrando por contains:", e)
            df_emp = pd.DataFrame()

    if df_emp.empty:
        try:
            tk.messagebox.showerror("Error", "No hay datos para esta empresa")
        except:
            pass
        return

    #crear ventana nueva para mostrar estadísticas (tamaño similar al original)
    ven_emp = tk.Toplevel(ventana)
    ven_emp.title(f"Estadísticas — {nombre}")
    ven_emp.geometry("750x700")
    ven_emp.config(bg="#F5F5F5")
    ven_emp.transient(ventana)
    ven_emp.grab_set()

    #header fijo superior con título y botón volver (siempre visible)
    marco_header = ttk.Frame(ven_emp, padding=(8,6))
    marco_header.pack(side="top", fill="x")

    etiqueta_titulo = ttk.Label(marco_header, text=f"Empresa: {nombre}", font=("Arial", 16, "bold"))
    etiqueta_titulo.pack(side="left", padx=(6,0))

    btn_volver_header = tk.Button(
        marco_header,
        text="Volver al menú principal",
        font=("Arial", 11),
        width=20,
        height=1,
        bg="#D9EAF7",
        command=lambda: cerrar_y_volver(ven_emp)
    )
    btn_volver_header.pack(side="right", padx=(0,10))

    #scrollable canvas para contenido (gráfica + resumen)
    contenedor = tk.Frame(ven_emp)
    contenedor.pack(fill="both", expand=True)

    canvas = tk.Canvas(contenedor, bg="#F5F5F5")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    frame_scroll = tk.Frame(canvas, bg="#F5F5F5")
    canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_scroll.bind("<Configure>", actualizar_scroll)

    #asegurar columnas numéricas convertidas de forma segura
    for col in ("capacidad_maxima", "capacidad_minima", "frecuencia_de_despacho_hora_pico", "frecuencia_despacho_hora_valle"):
        if col in df_emp.columns:
            try:
                df_emp[col] = df_emp[col].astype(str).str.replace(",", ".", regex=False)
                df_emp[col] = pd.to_numeric(df_emp[col].str.extract(r"([-+]?\d*\.?\d+)")[0], errors="coerce")
            except Exception:
                df_emp[col] = pd.to_numeric(df_emp[col], errors="coerce")

    #intentar crear la gráfica de terminales dentro de try para capturar errores
    try:
        frame_graf = tk.Frame(frame_scroll, bg="#F5F5F5")
        frame_graf.pack(pady=10, fill="both", expand=False)

        if "terminal" in df_emp.columns and not df_emp["terminal"].dropna().empty:
            conteo_term = df_emp["terminal"].value_counts()
            fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
            conteo_term.plot(kind="bar", ax=ax)
            ax.set_title(f"Frecuencia de terminales — {nombre}", fontsize=10)
            ax.set_xlabel("Terminal")
            ax.set_ylabel("Cantidad")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            ax.grid(alpha=0.3)

            canvas_graf = FigureCanvasTkAgg(fig, master=frame_graf)
            canvas_graf.draw()
            canvas_graf.get_tk_widget().pack(fill="both", expand=True)
        else:
            ttk.Label(frame_graf, text="sin datos de terminales", background="#F5F5F5").pack(fill="both", expand=True)
    except Exception as e:
        print("debug: error creando grafica terminales:", e)
        try:
            tk.messagebox.showwarning("Advertencia", f"No se pudo generar la gráfica: {e}")
        except:
            pass

    #estadísticas numéricas seguras (round solo si hay valores)
    try:
        cant = len(df_emp)
        cap_max = df_emp["capacidad_maxima"].mean() if "capacidad_maxima" in df_emp.columns else float("nan")
        cap_min = df_emp["capacidad_minima"].mean() if "capacidad_minima" in df_emp.columns else float("nan")
        frec_pico = df_emp["frecuencia_de_despacho_hora_pico"].mean() if "frecuencia_de_despacho_hora_pico" in df_emp.columns else float("nan")
        frec_valle = df_emp["frecuencia_despacho_hora_valle"].mean() if "frecuencia_despacho_hora_valle" in df_emp.columns else float("nan")

        texto = (
            f"• Vehículos registrados: {cant}\n\n"
            f"• Capacidad Máxima promedio: {round(cap_max, 2) if not pd.isna(cap_max) else 'N/A'}\n\n"
            f"• Capacidad Mínima promedio: {round(cap_min, 2) if not pd.isna(cap_min) else 'N/A'}\n\n"
            f"• Frecuencia hora pico promedio: {round(frec_pico, 2) if not pd.isna(frec_pico) else 'N/A'}\n\n"
            f"• Frecuencia hora valle promedio: {round(frec_valle, 2) if not pd.isna(frec_valle) else 'N/A'}"
        )
    except Exception as e:
        print("debug: error calculando estadisticas:", e)
        texto = "No fue posible calcular estadísticas numéricas."

    #panel de información (debajo de la gráfica)
    frame_info = tk.Frame(frame_scroll, bg="white", bd=1, relief="solid")
    frame_info.pack(padx=30, pady=20, fill="x")
    lbl_info = tk.Label(frame_info, text=texto, font=("Arial", 12), bg="white", justify="left", anchor="w")
    lbl_info.pack(padx=20, pady=20)

    #acción al cerrar: asegurar que la ventana principal se revele
    def al_cerrar():
        try:
            ven_emp.destroy()
        finally:
            try:
                ventana.deiconify()
            except:
                pass

    ven_emp.protocol("WM_DELETE_WINDOW", al_cerrar)


#;-;###########################################################################
########################################################################################
#####################################################################################
########################################################################################
###################################################################

def filtrar_por_seleccion(lugar, terminal):
    df_search = df_filtrado.reset_index().copy()

    if lugar and lugar != "Seleccione un lugar...":
        def ruta_contiene(r):
            if not isinstance(r, str):
                return False
            partes = [p.strip().lower() for p in r.split("-")]
            return lugar.strip().lower() in partes

        filtrado = df_search[df_search["ruta"].astype(str).apply(ruta_contiene)].copy()
        lista_resultados = filtrado.to_dict(orient="records")
        return lista_resultados

    elif terminal and terminal != "Seleccione un terminal...":
        terminal_normalizado = terminal.strip().lower()
        filtrado = df_search[
            df_search["terminal"].astype(str).str.strip().str.lower() == terminal_normalizado
        ].copy()
        print("DEBUG: terminales encontrados en el filtrado:")
        for t in filtrado["terminal"]:
            print(f"  '{t}'")
        lista_resultados = filtrado.to_dict(orient="records")
        return lista_resultados

    else:
        return []
"""ññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññ"""
"""ññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññ"""
"""ññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññ"""
def debug_lugares_terminales_vacios():
    print("\n--- DEBUG: Lugares vacíos tras filtrar ---")
    vacios_lugares = []
    for lugar in lugares:
        res = filtrar_por_seleccion(lugar, None)
        if not res:
            print(f"lugar vacío: '{lugar}'")
            vacios_lugares.append(lugar)
    print(f"Total lugares vacíos: {len(vacios_lugares)}")

    print("\n--- DEBUG: Terminales vacíos tras filtrar ---")
    vacios_terminales = []
    for terminal in terminales:
        res = filtrar_por_seleccion(None, terminal)
        if not res:
            print(f"terminal vacío: '{terminal}'")
            vacios_terminales.append(terminal)
    print(f"Total terminales vacíos: {len(vacios_terminales)}")
    print("--- FIN DEBUG ---\n")

debug_lugares_terminales_vacios()

"""ññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññ"""
"""ññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññ"""

#-------------------------------------------------------------
#----- VENTANA DE VISUALIZACION DE RUTAS ------------------------
#####################################################################################3333
##########################################################################################3
#######################################################################################333


def visualizacion_rutas():
    ventana.withdraw()  #esconde la ventana principal para que no se vea

    #crea la nueva ventana
    ventana_visual = tk.Toplevel()
    ventana_visual.title("Visualización de Rutas")
    ventana_visual.geometry("600x400")
    ventana_visual.config(bg="white")

    #frame para el título
    frame_visual = tk.Frame(ventana_visual, bg="white")
    frame_visual.pack(pady=20)

    label_visual = tk.Label(
        frame_visual,
        text="Seleccione una de las dos opciones",
        font=("Arial", 16),
        bg="white",
        justify="center"
    )
    label_visual.pack(pady=10)

    #frame para botones y menús desplegables
    frame_controls = tk.Frame(ventana_visual, bg="white")
    frame_controls.pack(pady=20)

    #botón para activar el menú desplegable de lugares
    btn_lugares = tk.Button(
        frame_controls,
        text="Por Lugares",
        width=20,
        height=2,
        bg="#D9EAF7",
        command=lambda: enable_dropdown("lugares")
    )
    btn_lugares.grid(row=0, column=0, padx=10, pady=5)

    #menú desplegable de lugares
    dropdown_lugares = ttk.Combobox(frame_controls, values=lugares, width=20, state="disabled")
    dropdown_lugares.set("Seleccione un lugar...")
    dropdown_lugares.grid(row=1, column=0, padx=10, pady=5)

    #botón para activar el menú desplegable de terminales
    btn_terminales = tk.Button(
        frame_controls,
        text="Por Terminales",
        width=20,
        height=2,
        bg="#D9EAF7",
        command=lambda: enable_dropdown("terminales")
    )
    btn_terminales.grid(row=0, column=1, padx=10, pady=5)

    #menú desplegable de terminales
    dropdown_terminales = ttk.Combobox(frame_controls, values=terminales, width=20, state="disabled")
    dropdown_terminales.set("Seleccione un terminal...")
    dropdown_terminales.grid(row=1, column=1, padx=10, pady=5)

    #botón para regresar
    btn_volver = tk.Button(
        frame_controls,
        text="Regresa",
        width=20,
        height=2,
        bg="#D9EAF7",
        command=lambda: cerrar_y_volver(ventana_visual)
    )
    btn_volver.grid(row=2, column=0, padx=10, pady=10)

    #botón aceptar (inicialmente deshabilitado)
    btn_aceptar = tk.Button(
        frame_controls,
        text="Aceptar",
        width=20,
        height=2,
        bg="#D9EAF7",
        state="disabled",
        command=lambda: abrir_ventana(dropdown_lugares.get(), dropdown_terminales.get())
    )
    btn_aceptar.grid(row=2, column=1, padx=10, pady=10)

    #variable para saber qué modo está activo
    modo_seleccion = {"tipo": None}

    #función para habilitar los menús desplegables
    def enable_dropdown(option):
        if option == "lugares":
            modo_seleccion["tipo"] = "lugares"
            dropdown_lugares.config(state="readonly")
            dropdown_terminales.config(state="disabled")
            dropdown_terminales.set("Seleccione un terminal...")  # limpia terminales
        elif option == "terminales":
            modo_seleccion["tipo"] = "terminales"
            dropdown_terminales.config(state="readonly")
            dropdown_lugares.config(state="disabled")
            dropdown_lugares.set("Seleccione un lugar...")  # limpia lugares
        btn_aceptar.config(state="disabled")

    #función para habilitar el botón aceptar solo si el campo activo tiene selección válida
    def check_selection(event=None):
        if modo_seleccion["tipo"] == "lugares" and dropdown_lugares.get() != "Seleccione un lugar...":
            btn_aceptar.config(state="normal")
        elif modo_seleccion["tipo"] == "terminales" and dropdown_terminales.get() != "Seleccione un terminal...":
            btn_aceptar.config(state="normal")
        else:
            btn_aceptar.config(state="disabled")

    #vincula los menús desplegables con la función check_selection
    dropdown_lugares.bind("<<ComboboxSelected>>", check_selection)
    dropdown_terminales.bind("<<ComboboxSelected>>", check_selection)

    #función para abrir una nueva ventana dependiendo de la selección
    def abrir_ventana(lugar, terminal):
        print(f"DEBUG: usuario eligió lugar='{lugar}' terminal='{terminal}' modo={modo_seleccion['tipo']}")
        if modo_seleccion["tipo"] == "lugares":
            resultados = filtrar_por_seleccion(lugar, None)
            seleccion = lugar
            tipo = "lugar"
        elif modo_seleccion["tipo"] == "terminales":
            resultados = filtrar_por_seleccion(None, terminal)
            seleccion = terminal
            tipo = "terminal"
        else:
            print("error: modo de selección no definido")
            tk.messagebox.showinfo("Sin resultados", "Seleccione un modo de búsqueda.")
            return

        if not resultados:
            print(f"error: {tipo} '{seleccion}' no tiene resultados")
            tk.messagebox.showinfo("Sin resultados", f"No se encontraron filas para la selección: {seleccion}")
            return

        ventana_resultados = tk.Toplevel(ventana_visual)
        ventana_resultados.title("Resultados")
        ventana_resultados.geometry("700x400")
        ventana_resultados.config(bg="white")

        #frame con scrollbar si hay muchos resultados
        frame_canvas = tk.Frame(ventana_resultados, bg="white")
        frame_canvas.pack(fill="both", expand=True)
        canvas = tk.Canvas(frame_canvas, bg="white")
        scrollbar = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        frame_labels = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=frame_labels, anchor="nw")

        def actualizar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        frame_labels.bind("<Configure>", actualizar_scroll)

        #muestra cada id y recorrido en un label separado
        for idx, row in enumerate(resultados):
            bus_id = str(row.get("id", row.get("codigo", "")))
            recorrido = str(row.get("recorrido", ""))
            #debug: si alguno está vacío, lo reporta
            if not bus_id or not recorrido:
                print(f"error: id vacío='{bus_id}' recorrido vacío='{recorrido}' para selección lugar='{lugar}' terminal='{terminal}'")
            label = tk.Label(
                frame_labels,
                text=f"ID: {bus_id}\nRecorrido: {recorrido}",
                font=("Arial", 11),
                bg="white",
                anchor="w",
                justify="left",
                relief="groove",
                borderwidth=1,
                padx=6, pady=4
            )
            label.pack(fill="x", pady=3, padx=3)

        btn_cerrar = tk.Button(ventana_resultados, text="Cerrar", command=ventana_resultados.destroy)
        btn_cerrar.pack(pady=8)

###################################################################################################33
##############################################################################################################
##########################################################################################





##############################################################
############################################################

# -------------------------------------------------------------
# agregar vehiculo - ventana emergente 4
# -------------------------------------------------------------

def ventana_emergente_4(padre):
    #crear ventana toplevel
    ventana = tk.Toplevel(padre)
    ventana.title("Ventana emergente")
    ventana.transient(padre)
    ventana.grab_set()
    ventana.geometry("900x900")

    #preparar opciones desde el dataframe
    try:
        serie_empresas = df_filtrado["empresa"].dropna().astype(str).str.replace(
            "OPERACIÓN AUTORIZADA A ", "", regex=False).str.strip()
        opciones_empresa = sorted(serie_empresas.unique().tolist())
    except Exception as e:
        print("debug: no se pudo obtener empresas desde df_filtrado:", e)
        opciones_empresa = ["Empresa A", "Empresa B"]

    try:
        if 'terminales' in globals() and terminales:
            opciones_terminal = sorted(list(terminales))
        else:
            opciones_terminal = sorted(df_filtrado["terminal"].dropna().astype(str).str.strip().unique().tolist())
    except Exception as e:
        print("debug: no se pudo obtener terminales:", e)
        opciones_terminal = ["Terminal 1", "Terminal 2"]

    def limpiar_lista_horas(lista):
        return sorted({str(x).strip() for x in lista if str(x).strip() and str(x).strip().lower() not in ("nan", "none")})

    try:
        horas_primer_despacho = limpiar_lista_horas(df_filtrado["hora_primer_despacho"].dropna().astype(str).tolist())
    except Exception:
        horas_primer_despacho = []
    try:
        horas_ultimo_despacho = limpiar_lista_horas(df_filtrado["hora_ultimo_despacho"].dropna().astype(str).tolist())
    except Exception:
        horas_ultimo_despacho = []

    if not horas_primer_despacho:
        horas_primer_despacho = [f"{h:02d}:00" for h in range(0, 24)]
    if not horas_ultimo_despacho:
        horas_ultimo_despacho = [f"{h:02d}:00" for h in range(0, 24)]

    #dividir clases en dos categorías fijas: buseta y microbus
    opciones_clase = ["buseta", "microbus"]

    #estilos
    estilo = ttk.Style(ventana)
    estilo.theme_use('clam')
    estilo.configure("TButton", padding=8)
    estilo.configure("TEntry", padding=4)
    estilo.configure("TLabel", padding=4)

    #frames principales
    marco_principal = ttk.Frame(ventana, padding=(20, 20, 20, 20))
    marco_principal.grid(row=0, column=0, sticky="nsew")
    ventana.columnconfigure(0, weight=1)
    ventana.rowconfigure(0, weight=1)

    marco_izq = ttk.Frame(marco_principal)
    marco_der = ttk.Frame(marco_principal)
    marco_izq.grid(row=2, column=0, padx=(10, 30), sticky="n")
    marco_der.grid(row=2, column=1, padx=(30, 10), sticky="n")

    etiqueta_encabezado = ttk.Label(marco_principal, text="Seleccione las siguientes opciones:", anchor="center")
    etiqueta_encabezado.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")

    btn_agregar_recorrido = ttk.Button(marco_principal, text="Agregar recorrido")
    btn_agregar_recorrido.grid(row=1, column=0, columnspan=1, sticky="w", pady=(0, 12))

    entrada_texto = ttk.Entry(marco_principal, width=90)
    entrada_texto.insert(0, "")
    entrada_texto.grid(row=1, column=0, columnspan=2, pady=(50, 20), sticky="ew")

    #columna izquierda
    btn_agregar_empresa = ttk.Button(marco_izq, text="Agregar empresa")
    btn_agregar_empresa.grid(row=0, column=0, pady=(0, 8), sticky="w")

    empresa_var = tk.StringVar()
    combo_empresa = ttk.Combobox(
        marco_izq, textvariable=empresa_var,
        values=opciones_empresa, state="readonly", width=35
    )
    combo_empresa.set("Seleccione una empresa...")
    combo_empresa.grid(row=1, column=0, pady=(0, 12), sticky="w")

    ttk.Label(marco_izq, text="Capacidad mínima").grid(row=2, column=0, sticky="w")
    capacidad_min_var = tk.StringVar()
    entrada_capacidad_min = ttk.Entry(marco_izq, textvariable=capacidad_min_var, width=30)
    entrada_capacidad_min.grid(row=3, column=0, pady=(0, 12), sticky="w")

    ttk.Label(marco_izq, text="Frecuencia hora pico").grid(row=4, column=0, sticky="w")
    frecuencia_pico_var = tk.StringVar()
    entrada_frecuencia_pico = ttk.Entry(marco_izq, textvariable=frecuencia_pico_var, width=30)
    entrada_frecuencia_pico.grid(row=5, column=0, pady=(0, 12), sticky="w")

    ttk.Label(marco_izq, text="Hora primer despacho").grid(row=6, column=0, sticky="w")
    hora_primer_var = tk.StringVar()
    combo_hora_primer = ttk.Combobox(
        marco_izq, textvariable=hora_primer_var,
        values=horas_primer_despacho, width=30, state="readonly"
    )
    combo_hora_primer.set("Seleccione hora...")
    combo_hora_primer.grid(row=7, column=0, pady=(0, 12), sticky="w")

    ttk.Label(marco_izq, text="Longitud (km)").grid(row=8, column=0, sticky="w")
    longitud_var = tk.StringVar()
    entrada_longitud = ttk.Entry(marco_izq, textvariable=longitud_var, width=30)
    entrada_longitud.grid(row=9, column=0, pady=(0, 20), sticky="w")

    def cancelar():
        ventana.destroy()

    btn_cancelar = ttk.Button(marco_izq, text="Cancelar", command=cancelar)
    btn_cancelar.grid(row=10, column=0, pady=(30, 0), sticky="w")

    #columna derecha
    btn_agregar_terminal = ttk.Button(marco_der, text="Agregar terminal")
    btn_agregar_terminal.grid(row=0, column=0, pady=(0, 8), sticky="e")

    terminal_var = tk.StringVar()
    combo_terminal = ttk.Combobox(
        marco_der, textvariable=terminal_var,
        values=opciones_terminal, state="readonly", width=35
    )
    combo_terminal.set("Seleccione un terminal...")
    combo_terminal.grid(row=1, column=0, pady=(0, 12), sticky="e")

    ttk.Label(marco_der, text="Capacidad máxima").grid(row=2, column=0, sticky="e")
    capacidad_max_var = tk.StringVar()
    entrada_capacidad_max = ttk.Entry(marco_der, textvariable=capacidad_max_var, width=30)
    entrada_capacidad_max.grid(row=3, column=0, pady=(0, 12), sticky="e")

    ttk.Label(marco_der, text="Frecuencia hora valle").grid(row=4, column=0, sticky="e")
    frecuencia_valle_var = tk.StringVar()
    entrada_frecuencia_valle = ttk.Entry(marco_der, textvariable=frecuencia_valle_var, width=30)
    entrada_frecuencia_valle.grid(row=5, column=0, pady=(0, 12), sticky="e")

    ttk.Label(marco_der, text="Hora último despacho").grid(row=6, column=0, sticky="e")
    hora_ultimo_var = tk.StringVar()
    combo_hora_ultimo = ttk.Combobox(
        marco_der, textvariable=hora_ultimo_var,
        values=horas_ultimo_despacho, width=30, state="readonly"
    )
    combo_hora_ultimo.set("Seleccione hora...")
    combo_hora_ultimo.grid(row=7, column=0, pady=(0, 12), sticky="e")

    ttk.Label(marco_der, text="Clase").grid(row=8, column=0, sticky="e")
    clase_var = tk.StringVar()
    combo_clase = ttk.Combobox(
        marco_der, textvariable=clase_var,
        values=opciones_clase, width=30, state="readonly"
    )
    combo_clase.set("Seleccione clase...")
    combo_clase.grid(row=9, column=0, pady=(0, 20), sticky="e")

    #guardar datos con autenticacion y persistencia
    def guardar():
        #recolectar datos del formulario
        datos = {
            "empresa": empresa_var.get().strip(),
            "terminal": terminal_var.get().strip(),
            "capacidad_minima": capacidad_min_var.get().strip(),
            "capacidad_maxima": capacidad_max_var.get().strip(),
            "frecuencia_de_despacho_hora_pico": frecuencia_pico_var.get().strip(),
            "frecuencia_despacho_hora_valle": frecuencia_valle_var.get().strip(),
            "hora_primer_despacho": hora_primer_var.get().strip(),
            "hora_ultimo_despacho": hora_ultimo_var.get().strip(),
            "long_km": longitud_var.get().strip(),
            "clase": clase_var.get().strip(),  #será 'buseta' o 'microbus'
            "ruta": entrada_texto.get().strip(),
        }

        #solicitar credenciales antes de guardar
        autorizado = solicitar_credenciales(ventana)
        if not autorizado:
            try:
                tk.messagebox.showinfo("Cancelado", "no autorizado. registro no guardado.")
            except:
                pass
            return

        #agregar fila a df global
        try:
            #declarar globals que vamos a modificar
            global df, df_filtrado, terminales, lugares

            #calcular nuevo codigo para el indice 'codigo' (índice del DataFrame)
            try:
                idx_numerico = pd.to_numeric(df.index.astype(str), errors="coerce")
                max_idx = int(idx_numerico.max()) if not np.isnan(idx_numerico.max()) else None
                if max_idx is None:
                    nuevo_codigo = df.reset_index().shape[0] + 1
                else:
                    nuevo_codigo = max_idx + 1
            except Exception:
                nuevo_codigo = df.reset_index().shape[0] + 1

            #calcular nuevo id (columna 'id')
            try:
                if "id" in df.columns:
                    max_id = int(pd.to_numeric(df["id"], errors="coerce").max())
                    nuevo_id = max_id + 1
                else:
                    nuevo_id = 1
            except Exception:
                nuevo_id = 1

            #construir fila nueva con todas las columnas existentes en df
            fila = {}
            for col in df.columns:
                if col in datos:
                    val = datos[col]
                    if col in ("capacidad_minima", "capacidad_maxima", "long_km",
                               "frecuencia_de_despacho_hora_pico", "frecuencia_despacho_hora_valle"):
                        try:
                            val_num = float(str(val).replace(",", "."))
                            fila[col] = val_num
                        except:
                            fila[col] = val
                    else:
                        fila[col] = datos[col]
                else:
                    fila[col] = np.nan

            #asegurar que existan tanto 'ruta' como 'recorrido' si corresponden
            if "ruta" in df.columns:
                fila["ruta"] = datos.get("ruta", fila.get("ruta", ""))
            if "recorrido" in df.columns:
                fila["recorrido"] = datos.get("ruta", fila.get("recorrido", ""))

            #asegurar columna 'id' en la fila y en el df
            fila["id"] = nuevo_id
            if "id" not in df.columns:
                df["id"] = np.nan

            #asegurar nombre del índice
            df.index.name = "codigo"
            #añadir la fila con índice nuevo_codigo
            df.loc[nuevo_codigo] = fila

            #actualizar df_filtrado: si no existe la fila la añadimos; si existe la reemplazamos
            try:
                if nuevo_codigo in df_filtrado.index:
                    df_filtrado.loc[nuevo_codigo] = fila
                else:
                    #si df_filtrado no contiene algunas columnas, lo intentamos añadir de forma segura
                    df_filtrado = df_filtrado.reindex(df.index)  #sincroniza índices y columnas mínimas
                    df_filtrado.loc[nuevo_codigo] = fila
                #actualizar empresa_limpia si aplica
                if "empresa_limpia" in df_filtrado.columns and "empresa" in df_filtrado.columns:
                    df_filtrado["empresa_limpia"] = df_filtrado["empresa"].astype(str).str.replace(
                        "OPERACIÓN AUTORIZADA A ", "", regex=False).str.strip()
            except Exception as e:
                print("debug: no se pudo agregar a df_filtrado directamente:", e)
                #en caso crítico, rehacer df_filtrado desde df (preservando fillna básico)
                try:
                    df_filtrado = df.fillna({"empresa":"BUSETAS AUTONOMA"
                                             ,"capacidad_minima" : df["capacidad_minima"].mean(),
                                             'capacidad_maxima':df["capacidad_maxima"].mean(),
                                            'frecuencia_de_despacho_hora_pico': "00",
                                            'hora_primer_despacho': "05:00:00 a.m.",
                                            'hora_ultimo_despacho': "08:30:00 p.m",})
                    df_filtrado["empresa_limpia"] = df_filtrado["empresa"].str.replace("OPERACIÓN AUTORIZADA A ", "", regex=False)
                except Exception as e2:
                    print("debug: error recreando df_filtrado:", e2)

            #guardar el df actualizado al CSV original
            try:
                df.index.name = "codigo"
                df.to_csv("8._RUTAS_TRANSPORTE_URBANO_20251011.csv")
            except Exception as e:
                print("debug: error guardando CSV:", e)
                try:
                    tk.messagebox.showwarning("Advertencia", "registro guardado en memoria pero no se pudo escribir el CSV.")
                except:
                    pass

            #actualizar listas globales terminales y lugares para que otras ventanas vean los cambios
            try:
                terminales = sorted(set(df["terminal"].dropna().astype(str).str.strip()))
            except:
                try:
                    terminales = sorted(set(df_filtrado["terminal"].dropna().astype(str).str.strip()))
                except:
                    terminales = terminales

            try:
                if "ruta" in df.columns:
                    rutas = df["ruta"].dropna().unique().tolist()
                elif "recorrido" in df.columns:
                    rutas = df["recorrido"].dropna().unique().tolist()
                else:
                    rutas = []

                lugares_separados = set()
                for r in rutas:
                    lugares_separados.update([lugar.strip() for lugar in str(r).split("-") if lugar and lugar.strip()])
                lugares = sorted(lugares_separados)
            except:
                pass

            try:
                tk.messagebox.showinfo("Éxito", "registro guardado correctamente")
            except:
                pass

        except Exception as e:
            print("debug: error al guardar registro:", e)
            try:
                tk.messagebox.showerror("Error", f"ocurrió un error al guardar: {e}")
            except:
                pass

        ventana.destroy()

    btn_guardar = ttk.Button(marco_der, text="Guardar", command=guardar)
    btn_guardar.grid(row=10, column=0, pady=(30, 0), sticky="e")

    marco_principal.columnconfigure(0, weight=1)
    marco_principal.columnconfigure(1, weight=1)
    marco_izq.columnconfigure(0, weight=1)
    marco_der.columnconfigure(0, weight=1)


#############################################################################
##################################################################
###################################################



# -------------------------------------------------------------------
# ----- VENTANA DE SELECCION DE ESTADISTICAS ------------------------
# -------------------------------------------------------------------
def estats():
    est_dec = tk.Toplevel(ventana)
    est_dec.columnconfigure(0, weight=1)
    est_dec.columnconfigure(1, weight=1)
    est_dec.title("Estadísticas de vehículos")
    est_dec.geometry("450x300")

    #obtener empresas únicas desde df_filtrado (empresa_limpia)
    try:
        empresas = sorted(df_filtrado["empresa_limpia"].dropna().astype(str).str.strip().unique().tolist())
    except Exception:
        empresas = []

    if not empresas:
        #fallback si por alguna razón no hay empresas extraídas
        empresas = ["(sin datos)"]

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
btn_agregar = tk.Button(text="Agregar vehiculo", width=20, height=2, command=lambda: ventana_emergente_4(ventana))
btn_visual = tk.Button(text="Visualización de rutas", width=20, height=2, command=visualizacion_rutas)

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


#usar df ya cargado y normalizado arriba
DF = df.copy()

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
#transpone la tabla para que     renombre las columnas del resultado 
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
