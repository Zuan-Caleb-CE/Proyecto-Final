import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import unicodedata
import platform
import threading
import threading



#sonidos y compatibilidad (winsound en windows, si no disponible no hace nada)
try:
    import winsound
except Exception:
    winsound = None

#helper para reproducir sonidos de interfaz (no falla si winsound no existe)
def reproducir_sonido(nombre):
    #nombre: 'abrir','click','ok','error'
    try:
        if winsound and platform.system()=="Windows":
            if nombre == "abrir":
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            elif nombre == "click":
                winsound.MessageBeep(winsound.MB_OK)
            elif nombre == "ok":
                winsound.MessageBeep(winsound.MB_OK)
            elif nombre == "error":
                winsound.MessageBeep(winsound.MB_ICONHAND)
            else:
                winsound.MessageBeep()
        else:
            #fallback cross-platform: si existe una ventana global, usar bell
            try:
                ventana.bell()
            except Exception:
                pass
    except Exception:
        pass

#mostrar un cargador modal simple con progressbar indeterminada
def mostrar_cargador(padre, texto="Cargando…"):
    #crea un Toplevel pequeño y devuelve el objeto para cerrarlo luego
    cargador = tk.Toplevel(padre)
    cargador.transient(padre)
    cargador.grab_set()
    cargador.title("")
    cargador.geometry("260x80")
    try:
        padre.update_idletasks()
        px = padre.winfo_rootx()
        py = padre.winfo_rooty()
        pw = padre.winfo_width()
        ph = padre.winfo_height()
        cargador.geometry(f"+{px + max(10, pw//2 - 130)}+{py + max(10, ph//2 - 40)}")
    except Exception:
        pass
    cargador.resizable(False, False)
    frame = ttk.Frame(cargador, padding=(8,8))
    frame.pack(fill="both", expand=True)
    lbl = ttk.Label(frame, text=texto)
    lbl.pack(pady=(2,6))
    barra = ttk.Progressbar(frame, mode="indeterminate", length=220)
    barra.pack()
    barra.start(10)
    cargador.update_idletasks()
    return cargador

#detener y destruir cargador
def detener_cargador(cargador):
    try:
        for child in cargador.winfo_children():
            if isinstance(child, ttk.Progressbar):
                try:
                    child.stop()
                except:
                    pass
        cargador.grab_release()
        cargador.destroy()
    except Exception:
        pass


#animacionfadeentrada
def aparecer_con_fade(ventana_toplevel, x=None, y=None, ancho=None, alto=None, pasos=10, intervalo=25):
    try:
        if ancho and alto and x is not None and y is not None:
            ventana_toplevel.geometry(f"{ancho}x{alto}+{x}+{y}")
        ventana_toplevel.attributes('-alpha', 0.0)
        def paso(i):
            try:
                ventana_toplevel.attributes('-alpha', i/pasos)
                if i < pasos:
                    ventana_toplevel.after(intervalo, lambda: paso(i+1))
            except:
                pass
        paso(0)
    except Exception:
        pass



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



#animacion de entrada tipo rebote para la ventana principal
def bounce_in_from_left(root, pasos=36, duracion_ms=700, overshoot=50):
    #animacion: inicia fuera a la izquierda y llega al centro con overshoot y rebotes
    try:
        root.update_idletasks()
        geom = root.geometry().split('+')[0]
        ancho, alto = map(int, geom.split('x'))
        screen_w = root.winfo_screenwidth(); screen_h = root.winfo_screenheight()
        x_central = (screen_w - ancho) // 2
        y_central = max(30, (screen_h - alto) // 2)

        #posicion inicial fuera de pantalla (izquierda)
        x_inicio = -ancho - 20
        x_final = x_central

        #tiempo por paso
        dt = max(1, int(duracion_ms / max(1, pasos)))

        #generar curvas de movimiento con overshoot y amortiguacion
        xs = []
        for i in range(pasos):
            t = i / (pasos - 1)
            #ease out cubic para acercarse
            ease = 1 - (1 - t) ** 3
            #overshoot componente (seno decaido)
            overs = overshoot * np.sin(t * np.pi) * (1 - t)
            x = int(x_inicio + (x_final - x_inicio) * ease + overs)
            xs.append(x)

        #añadir algunos pasos finales para acomodar rebotes pequeños
        for extra in [int(x_final + overshoot*0.3), int(x_final - overshoot*0.15), x_final]:
            xs.append(extra)

        #aplicar posicion inicial y animar
        root.geometry(f"{ancho}x{alto}+{x_inicio}+{y_central}")
        def paso(i=0):
            if i < len(xs):
                root.geometry(f"{ancho}x{alto}+{xs[i]}+{y_central}")
                root.after(dt, lambda: paso(i+1))
            else:
                root.geometry(f"{ancho}x{alto}+{x_final}+{y_central}")
        root.after(30, lambda: paso(0))
    except Exception as e:
        print("debug: bounce_in_from_left failed:", e)



####################################################################3
#################################################################
##ver estadisticas de todas las empresas
#########################################################################3
#########################################################3


#mostrar estadisticas agregadas de todas las empresas (con cargador y layout 2+1)
def allempresas():
    try:
        df_todas = df.copy()
    except Exception as e:
        print("debug: no se pudo copiar df:", e)
        try:
            tk.messagebox.showerror("Error", "No fue posible acceder a los datos.")
        except:
            pass
        return

    if df_todas.empty:
        try:
            tk.messagebox.showinfo("Información", "No hay registros en el dataset.")
        except:
            pass
        return

    ven_all = tk.Toplevel(ventana)
    ven_all.title("Estadísticas — Todas las empresas")
    #reducir altura para evitar taskbar; usuario puede maximizar si quiere
    ven_all.geometry("980x680")
    ven_all.minsize(800, 600)
    ven_all.transient(ventana)
    ven_all.grab_set()

    aplicar_tema_a_toplevel(ven_all)

    #header fijo superior
    marco_header = ttk.Frame(ven_all, padding=(8,6))
    marco_header.pack(side="top", fill="x")
    etiqueta_titulo = ttk.Label(marco_header, text="Estadísticas agregadas — Todas las empresas", font=("Arial", 14, "bold"))
    etiqueta_titulo.pack(side="left", padx=(6,0))
    btn_volver_header = ttk.Button(marco_header, text="Volver al menú principal", width=20,
                                  command=lambda: cerrar_y_volver(ven_all))
    btn_volver_header.pack(side="right", padx=(0,8))

    #area scrollable
    contenedor = tk.Frame(ven_all)
    contenedor.pack(fill="both", expand=True)
    canvas = tk.Canvas(contenedor, bg=ven_all.cget("bg"), highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    frame_scroll = tk.Frame(canvas, bg=ven_all.cget("bg"))
    canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_scroll.bind("<Configure>", actualizar_scroll)

    #grid: dos columnas arriba y una fila ancha abajo
    marco_graficos = ttk.Frame(frame_scroll, padding=6)
    marco_graficos.pack(padx=8, pady=8, fill="both", expand=False)

    marco_graficos.columnconfigure(0, weight=1)
    marco_graficos.columnconfigure(1, weight=1)

    #frames contenedores vacíos
    frame_left = ttk.Frame(marco_graficos, padding=6)
    frame_left.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
    frame_right = ttk.Frame(marco_graficos, padding=6)
    frame_right.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
    frame_bottom = ttk.Frame(marco_graficos, padding=6)
    frame_bottom.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

    #mostrar cargador modal mientras se generan figuras en background
    carg = mostrar_cargador(ven_all, "Generando gráficos...")

    def generar_figuras_all():
        figs = {}
        try:
            #grafico Left: scatter entre dos mejores num cols globales
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
                    fig_b_local, ax_b_local = plt.subplots(figsize=(6,3), dpi=90)
                    ax_b_local.scatter(x, y, alpha=0.7, s=18)
                    if y_fit is not None:
                        ax_b_local.plot(x, y_fit, color='orange', linewidth=1.2)
                    ax_b_local.set_xlabel(xcol)
                    ax_b_local.set_ylabel(ycol)
                    ax_b_local.set_title(f"Dispersión: {ycol} vs {xcol}")
                    fig_b_local.tight_layout()
                    figs['left'] = fig_b_local

            #grafico Right: pico vs valle (media±std) global
            candidatos_pico = ["frecuencia_de_despacho_hora_pico", "frecuencia_de_despacho_pico", "frecuencia_pico"]
            candidatos_valle = ["frecuencia_despacho_hora_valle", "frecuencia_de_despacho_hora_valle", "frecuencia_valle"]
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
                    fig_c_local, ax_c_local = plt.subplots(figsize=(6,3), dpi=90)
                    ax_c_local.bar([0,1], medias_plot, width=0.6, yerr=desv_plot, capsize=5)
                    ax_c_local.set_xticks([0,1]); ax_c_local.set_xticklabels(['Pico','Valle'])
                    ax_c_local.set_title("Media ± desviación: Pico vs Valle")
                    fig_c_local.tight_layout()
                    figs['right'] = fig_c_local

            #grafico Bottom: barras por terminal (ancho grande)
            if "terminal" in df_todas.columns and not df_todas["terminal"].dropna().empty:
                conteo_term = df_todas["terminal"].value_counts()
                fig_d_local, ax_d_local = plt.subplots(figsize=(10,3.5), dpi=90)
                conteo_term.plot(kind="bar", ax=ax_d_local)
                ax_d_local.set_title("Frecuencia de terminales")
                ax_d_local.set_xlabel("Terminal")
                ax_d_local.set_ylabel("Cantidad")
                fig_d_local.tight_layout()
                figs['bottom'] = fig_d_local

        except Exception as e:
            print("debug: error generando figuras en hilo allempresas:", e)

        def pintar_y_cerrar():
            try:
                if 'left' in figs:
                    canvas_left = FigureCanvasTkAgg(figs['left'], master=frame_left)
                    canvas_left.draw()
                    canvas_left.get_tk_widget().pack(fill="both", expand=True)
                else:
                    ttk.Label(frame_left, text="no hay suficientes datos para scatter", background=ven_all.cget("bg")).pack(expand=True, fill="both")
                if 'right' in figs:
                    canvas_right = FigureCanvasTkAgg(figs['right'], master=frame_right)
                    canvas_right.draw()
                    canvas_right.get_tk_widget().pack(fill="both", expand=True)
                else:
                    ttk.Label(frame_right, text="sin datos Pico/Valle", background=ven_all.cget("bg")).pack(expand=True, fill="both")
                if 'bottom' in figs:
                    canvas_bottom = FigureCanvasTkAgg(figs['bottom'], master=frame_bottom)
                    canvas_bottom.draw()
                    canvas_bottom.get_tk_widget().pack(fill="both", expand=True)
                else:
                    ttk.Label(frame_bottom, text="sin datos de terminales", background=ven_all.cget("bg")).pack(expand=True, fill="both")
            finally:
                detener_cargador(carg)

        ven_all.after(50, pintar_y_cerrar)

    #iniciar hilo para generar figuras sin bloquear UI
    threading.Thread(target=generar_figuras_all, daemon=True).start()



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
    #cerrar toplevel previos
    try:
        for w in ventana.winfo_children():
            if isinstance(w, tk.Toplevel):
                try: w.destroy()
                except: pass
    except Exception as e:
        print("debug: cerrar toplevels:", e)

    #validar seleccion
    if not nombre or nombre.strip()=="" or "Seleccione" in nombre:
        try: messagebox.showinfo("Información", "Seleccione una empresa válida antes de ver.", parent=ventana)
        except: pass
        return

    nombre_buscar = nombre.strip().lower()
    try:
        df_emp = df_filtrado[df_filtrado["empresa_limpia"].astype(str).str.strip().str.lower() == nombre_buscar].copy()
    except Exception as e:
        print("debug: error filtrando empresa:", e)
        try: messagebox.showerror("Error", f"error interno al filtrar: {e}", parent=ventana)
        except: pass
        return

    if df_emp.empty:
        try:
            df_emp = df_filtrado[df_filtrado["empresa_limpia"].astype(str).str.strip().str.lower().str.contains(re.escape(nombre_buscar))].copy()
        except Exception as e:
            print("debug: error secundario filtrando:", e)
            df_emp = pd.DataFrame()

    if df_emp.empty:
        try: messagebox.showerror("Error", "No hay datos para esta empresa", parent=ventana)
        except: pass
        return

    #crear ventana y aplicar style B (fade + posicion centrada)
    ven_emp = tk.Toplevel(ventana)
    ven_emp.title(f"Estadísticas — {nombre}")
    #calcular tamaño centrado respecto a ventana principal
    screen_w = ven_emp.winfo_screenwidth(); screen_h = ven_emp.winfo_screenheight()
    ancho = min(1000, int(screen_w*0.8)); alto = min(820, int(screen_h*0.75))
    #posicionar centrado sobre pantalla
    x = max(20, (screen_w - ancho)//2); y = max(20, (screen_h - alto)//2)
    #aparecer con fade
    aparecer_con_fade(ven_emp, x=x, y=y, ancho=ancho, alto=alto)
    ven_emp.transient(ventana)
    ven_emp.grab_set()

    #header con titulo y boton volver
    header = ttk.Frame(ven_emp, padding=(6,6))
    header.pack(side="top", fill="x")
    ttk.Label(header, text=f"Empresa: {nombre}", font=("Arial", 14, "bold")).pack(side="left", padx=(6,0))
    ttk.Button(header, text="Volver al menú principal", command=lambda: cerrar_y_volver(ven_emp)).pack(side="right", padx=6)

    #contenedor scrollable
    cont = tk.Frame(ven_emp)
    cont.pack(fill="both", expand=True)
    canvas = tk.Canvas(cont, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(cont, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    frame_scroll = tk.Frame(canvas)
    canvas.create_window((0,0), window=frame_scroll, anchor="nw")
    def actualizar_scroll(event): canvas.configure(scrollregion=canvas.bbox("all"))
    frame_scroll.bind("<Configure>", actualizar_scroll)

    #asegurar conversion numerica de columnas importantes (si no existen no pasa nada)
    candidatos_num = ["capacidad_maxima","capacidad_minima",
                      "frecuencia_de_despacho_hora_pico","frecuencia_de_despacho_pico","frecuencia_pico",
                      "frecuencia_despacho_hora_valle","frecuencia_valle"]
    try:
        for c in candidatos_num:
            if c in df_emp.columns:
                df_emp[c] = pd.to_numeric(df_emp[c], errors="coerce")
    except:
        pass

    #marco grid 2x2 y frames vacíos para figuras
    marco_graficos = ttk.Frame(frame_scroll)
    marco_graficos.pack(padx=8, pady=8, fill="both", expand=True)
    marco_graficos.columnconfigure(0, weight=1); marco_graficos.columnconfigure(1, weight=1)
    marco_graficos.rowconfigure(0, weight=1); marco_graficos.rowconfigure(1, weight=1)

    frame_a = ttk.Frame(marco_graficos, padding=6); frame_a.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
    frame_b = ttk.Frame(marco_graficos, padding=6); frame_b.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
    frame_c = ttk.Frame(marco_graficos, padding=6); frame_c.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
    frame_d = ttk.Frame(marco_graficos, padding=6); frame_d.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)

    #sonido y cargador
    reproducir_sonido("abrir")
    carg = mostrar_cargador(ven_emp, "Generando gráficos…")

    #funcion que crea figuras en background y las pone listas en 'figs'
    def generar_figuras_en_hilo():
        figs = {}
        try:
            #A: barras por terminal
            if "terminal" in df_emp.columns and not df_emp["terminal"].dropna().empty:
                conteo_term = df_emp["terminal"].value_counts()
                fig_a_local, ax_a_local = plt.subplots(figsize=(3.5,3), dpi=80)
                conteo_term.plot(kind="bar", ax=ax_a_local)
                ax_a_local.set_title("Frecuencia de terminales")
                fig_a_local.tight_layout()
                figs['a'] = fig_a_local

            #B: scatter entre 2 columnas numéricas con más datos
            num_cols = df_emp.select_dtypes(include=[np.number]).columns.tolist()
            num_cols = [c for c in num_cols if c not in ("id",)]
            if len(num_cols) >= 2:
                conteos = {c: df_emp[c].count() for c in num_cols}
                cols_orden = sorted(conteos, key=lambda k: conteos[k], reverse=True)
                xcol, ycol = cols_orden[0], cols_orden[1]
                df_sc = df_emp[[xcol, ycol]].dropna()
                if len(df_sc) > 1:
                    x = df_sc[xcol].values; y = df_sc[ycol].values
                    try:
                        m, b = np.polyfit(x, y, 1); y_fit = m*x + b
                    except:
                        y_fit = None
                    fig_b_local, ax_b_local = plt.subplots(figsize=(3.5,3), dpi=80)
                    ax_b_local.scatter(x, y, alpha=0.7, s=18)
                    if y_fit is not None: ax_b_local.plot(x, y_fit, color='orange', linewidth=1.2)
                    ax_b_local.set_xlabel(xcol); ax_b_local.set_ylabel(ycol)
                    ax_b_local.set_title(f"Dispersión: {ycol} vs {xcol}")
                    fig_b_local.tight_layout()
                    figs['b'] = fig_b_local

            #C: pico vs valle media ± sd
            candidatos_pico = ["frecuencia_de_despacho_hora_pico","frecuencia_de_despacho_pico","frecuencia_pico"]
            candidatos_valle = ["frecuencia_despacho_hora_valle","frecuencia_valle","frecuencia_de_despacho_hora_valle"]
            pico_col = next((c for c in candidatos_pico if c in df_emp.columns), None)
            valle_col = next((c for c in candidatos_valle if c in df_emp.columns), None)
            if pico_col or valle_col:
                v_pico = df_emp[pico_col].dropna() if pico_col else pd.Series(dtype=float)
                v_valle = df_emp[valle_col].dropna() if valle_col else pd.Series(dtype=float)
                medias = [v_pico.mean() if not v_pico.empty else np.nan, v_valle.mean() if not v_valle.empty else np.nan]
                desv = [v_pico.std() if not v_pico.empty else np.nan, v_valle.std() if not v_valle.empty else np.nan]
                if not all(np.isnan(medias)):
                    medias_plot = [0 if np.isnan(m) else m for m in medias]; desv_plot = [0 if np.isnan(d) else d for d in desv]
                    fig_c_local, ax_c_local = plt.subplots(figsize=(3.5,3), dpi=80)
                    ax_c_local.bar([0,1], medias_plot, width=0.6, yerr=desv_plot, capsize=5)
                    ax_c_local.set_xticks([0,1]); ax_c_local.set_xticklabels(['Pico','Valle'])
                    ax_c_local.set_title("Media ± desviación: Pico vs Valle")
                    fig_c_local.tight_layout()
                    figs['c'] = fig_c_local

            #D: distribucion longitudes
            posibles_long = ["long_km","longitud","longitud_km"]
            long_col = next((c for c in posibles_long if c in df_emp.columns), None)
            if long_col:
                longitudes = pd.to_numeric(df_emp[long_col].dropna(), errors="coerce")
                if not longitudes.empty:
                    fig_d_local, ax_d_local = plt.subplots(figsize=(3.5,3), dpi=80)
                    ax_d_local.hist(longitudes, bins=8)
                    ax_d_local.set_title("Distribución longitudes (km)")
                    fig_d_local.tight_layout()
                    figs['d'] = fig_d_local
        except Exception as e:
            print("debug: error generando figuras en hilo:", e)

        #funcion que corre en hilo principal para renderizar las figuras en los frames
        def pintar_y_cerrar():
            try:
                if 'a' in figs:
                    canvas_a = FigureCanvasTkAgg(figs['a'], master=frame_a); canvas_a.draw(); canvas_a.get_tk_widget().pack(fill="both", expand=True)
                else:
                    ttk.Label(frame_a, text="sin datos terminales", background="#F5F5F5").pack(expand=True, fill="both")
                if 'b' in figs:
                    canvas_b = FigureCanvasTkAgg(figs['b'], master=frame_b); canvas_b.draw(); canvas_b.get_tk_widget().pack(fill="both", expand=True)
                else:
                    ttk.Label(frame_b, text="no hay suficientes datos para scatter", background="#F5F5F5").pack(expand=True, fill="both")
                if 'c' in figs:
                    canvas_c = FigureCanvasTkAgg(figs['c'], master=frame_c); canvas_c.draw(); canvas_c.get_tk_widget().pack(fill="both", expand=True)
                else:
                    ttk.Label(frame_c, text="sin datos Pico/Valle", background="#F5F5F5").pack(expand=True, fill="both")
                if 'd' in figs:
                    canvas_d = FigureCanvasTkAgg(figs['d'], master=frame_d); canvas_d.draw(); canvas_d.get_tk_widget().pack(fill="both", expand=True)
                else:
                    ttk.Label(frame_d, text="sin datos longitudes", background="#F5F5F5").pack(expand=True, fill="both")
            finally:
                detener_cargador(carg)

        #programar pintado en hilo principal
        ven_emp.after(50, pintar_y_cerrar)

    #lanzar hilo para generar figuras (no bloquea UI)
    threading.Thread(target=generar_figuras_en_hilo, daemon=True).start()



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
    #ocultar ventana principal
    ventana.withdraw()

    #crear toplevel y aplicar tema
    ventana_visual = tk.Toplevel(ventana)
    ventana_visual.title("Visualización de Rutas")
    ventana_visual.geometry("640x420")
    aplicar_tema_a_toplevel(ventana_visual)

    #detectar colores segun tema para widgets tk que usamos
    if tema_actual.get("valor","claro")=="oscuro":
        panel_bg = "#3a3a3a"
        fg_color = "white"
    else:
        panel_bg = "#f5f5f5"
        fg_color = "black"

    #frame titulo (ttk para temas)
    frame_visual = ttk.Frame(ventana_visual, padding=(12,12))
    frame_visual.pack(fill="x", pady=(8,6))
    label_visual = ttk.Label(frame_visual, text="Seleccione una de las dos opciones", anchor="center", font=("Arial", 14))
    label_visual.pack()

    #frame controles
    frame_controls = ttk.Frame(ventana_visual, padding=(10,10))
    frame_controls.pack(fill="both", expand=False, pady=6)

    #botones estilo ttk (heredan tema)
    btn_lugares = ttk.Button(frame_controls, text="Por Lugares", width=20,
                             command=lambda: enable_dropdown("lugares"))
    btn_lugares.grid(row=0, column=0, padx=10, pady=5)

    btn_terminales = ttk.Button(frame_controls, text="Por Terminales", width=20,
                                command=lambda: enable_dropdown("terminales"))
    btn_terminales.grid(row=0, column=1, padx=10, pady=5)

    #comboboxes (ttk, ya estilizadas por aplicar_tema_a_toplevel)
    dropdown_lugares = ttk.Combobox(frame_controls, values=lugares, width=28, state="disabled")
    dropdown_lugares.set("Seleccione un lugar...")
    dropdown_lugares.grid(row=1, column=0, padx=10, pady=6)

    dropdown_terminales = ttk.Combobox(frame_controls, values=terminales, width=28, state="disabled")
    dropdown_terminales.set("Seleccione un terminal...")
    dropdown_terminales.grid(row=1, column=1, padx=10, pady=6)

    #botones aceptar / volver
    btn_volver = ttk.Button(frame_controls, text="Regresa", width=20,
                            command=lambda: cerrar_y_volver(ventana_visual))
    btn_volver.grid(row=2, column=0, padx=10, pady=12)

    btn_aceptar = ttk.Button(frame_controls, text="Aceptar", width=20, state="disabled",
                             command=lambda: abrir_ventana(dropdown_lugares.get(), dropdown_terminales.get()))
    btn_aceptar.grid(row=2, column=1, padx=10, pady=12)

    modo_seleccion = {"tipo": None}

    #habilita dropdown correspondiente y resetea el otro
    def enable_dropdown(option):
        if option == "lugares":
            modo_seleccion["tipo"] = "lugares"
            dropdown_lugares.state(["!disabled","readonly"])
            dropdown_terminales.set("Seleccione un terminal...")
            dropdown_terminales.state(["disabled"])
        else:
            modo_seleccion["tipo"] = "terminales"
            dropdown_terminales.state(["!disabled","readonly"])
            dropdown_lugares.set("Seleccione un lugar...")
            dropdown_lugares.state(["disabled"])
        btn_aceptar.state(["disabled"])

    #habilita aceptar solo si hay seleccion valida
    def check_selection(event=None):
        if modo_seleccion["tipo"] == "lugares" and dropdown_lugares.get() not in ("", "Seleccione un lugar..."):
            btn_aceptar.state(["!disabled"])
        elif modo_seleccion["tipo"] == "terminales" and dropdown_terminales.get() not in ("", "Seleccione un terminal..."):
            btn_aceptar.state(["!disabled"])
        else:
            btn_aceptar.state(["disabled"])

    dropdown_lugares.bind("<<ComboboxSelected>>", check_selection)
    dropdown_terminales.bind("<<ComboboxSelected>>", check_selection)

    #abrir ventana de resultados (respeta tema y coloca contenido en scroll)
    def abrir_ventana(lugar, terminal):
        seleccion = lugar if modo_seleccion["tipo"]=="lugares" else terminal
        tipo = "lugar" if modo_seleccion["tipo"]=="lugares" else "terminal"
        if modo_seleccion["tipo"] not in ("lugares","terminales"):
            try: tk.messagebox.showinfo("Sin resultados", "Seleccione un modo de búsqueda.", parent=ventana_visual)
            except: pass
            return

        resultados = filtrar_por_seleccion(lugar if tipo=="lugar" else None, terminal if tipo=="terminal" else None)
        if not resultados:
            try: tk.messagebox.showinfo("Sin resultados", f"No se encontraron filas para: {seleccion}", parent=ventana_visual)
            except: pass
            return

        ventana_resultados = tk.Toplevel(ventana_visual)
        ventana_resultados.title("Resultados")
        #tamaño razonable para evitar solapamiento con taskbar
        ventana_resultados.geometry("740x420")
        aplicar_tema_a_toplevel(ventana_resultados)

        #contenedor scrollable
        frame_canvas = ttk.Frame(ventana_resultados)
        frame_canvas.pack(fill="both", expand=True, padx=6, pady=6)
        canvas = tk.Canvas(frame_canvas, highlightthickness=0, bg=ventana_resultados.cget("bg"))
        scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        frame_labels = ttk.Frame(canvas)
        canvas.create_window((0,0), window=frame_labels, anchor="nw")
        def actualizar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        frame_labels.bind("<Configure>", actualizar_scroll)

        #mostrar resultados
        for idx, fila in enumerate(resultados):
            bus_id = str(fila.get("id", fila.get("codigo", "")))
            recorrido = str(fila.get("recorrido", fila.get("ruta", "")))
            if not bus_id or not recorrido:
                print(f"debug: id vacío='{bus_id}' recorrido vacío='{recorrido}' para {tipo}='{seleccion}'")
            #usar ttk.Label no permite bg directo, asi que usamos tk.Label pero con colores del tema
            etiqueta = tk.Label(frame_labels,
                                text=f"ID: {bus_id}\nRecorrido: {recorrido}",
                                font=("Arial", 11),
                                bg=ventana_resultados.cget("bg"),
                                fg=fg_color,
                                anchor="w",
                                justify="left",
                                relief="groove",
                                borderwidth=1,
                                padx=6, pady=4)
            etiqueta.pack(fill="x", pady=4, padx=3)

        #boton cerrar
        btn_cerrar = ttk.Button(ventana_resultados, text="Cerrar", command=ventana_resultados.destroy)
        btn_cerrar.pack(pady=8)

    #al cerrar esta ventana, devolver principal
    def al_cerrar():
        try: ventana_visual.destroy()
        finally:
            try: ventana.deiconify()
            except: pass

    ventana_visual.protocol("WM_DELETE_WINDOW", al_cerrar)


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

#ventana de seleccion de estadisticas (reescrita para respetar tema y loading)
def estats():
    est_dec = tk.Toplevel(ventana)
    est_dec.columnconfigure(0, weight=1)
    est_dec.columnconfigure(1, weight=1)
    est_dec.title("Estadísticas de vehículos")
    #reducir altura para evitar solapamiento con barra tareas
    est_dec.geometry("460x340")

    #aplicar tema al toplevel
    aplicar_tema_a_toplevel(est_dec)

    #obtener empresas únicas desde df_filtrado (empresa_limpia)
    try:
        empresas = sorted(df_filtrado["empresa_limpia"].dropna().astype(str).str.strip().unique().tolist())
    except Exception:
        empresas = []

    if not empresas:
        empresas = ["(sin datos)"]

    list_emp = ttk.Combobox(est_dec, values=empresas, width=35, state="disabled")
    list_emp.set("Seleccione una empresa.")
    list_emp.grid(row=2, column=0, pady=10, columnspan=2)

    #usar ttk.Button para que herede estilos; si quieres sonido, envuelve en lambda con reproducir_sonido
    btn_ver = ttk.Button(est_dec, text="Ver Empresa", width=20,
                         command=lambda: invempresas(list_emp.get()))

    def toggle():
        if list_emp.instate(["disabled"]):
            list_emp.config(state="readonly")
            btn_all.config(state="disabled")
            btn_ver.config(state="normal")
        else:
            list_emp.config(state="disabled")
            btn_all.config(state="normal")
            btn_ver.config(state="disabled")

    btn_all = ttk.Button(est_dec, text="Todas las Empresas", width=20, command=allempresas)
    btn_all.grid(row=1, column=1, padx=6, pady=6)

    btn_inv = ttk.Button(est_dec, text="Empresa Individual", width=20, command=toggle)
    btn_inv.grid(row=1, column=0, padx=6, pady=6)

    btn_ver.grid(row=4, column=0, columnspan=2, pady=10)

    boton_cancelar = ttk.Button(est_dec, text="Cancelar", width=20, command=est_dec.destroy)
    boton_cancelar.grid(row=5, column=0, columnspan=2, pady=8, padx=10)



# -------------------------------------------------------------------
# -----  V E N T A N A   P R I N C I P A L ---------------------------
# -------------------------------------------------------------------
ventana = tk.Tk()
ventana.title("Menu Principal")
ventana.geometry("400x450")
ventana.update_idletasks()
bounce_in_from_left(ventana)
ventana.config(bg="white")

#cursor personalizado para botones (icono mano)
ventana.option_add("*Button.cursor", "hand2")

#tema actual (puede ser 'claro' o 'oscuro')
tema_actual = {"valor":"claro"}

#aplicar tema sencillo (colores mínimos)
def aplicar_tema(tema):
    #tema:'claro' o 'oscuro'
    if tema == "oscuro":
        fg = "white"
        bg = "#2b2b2b"
        panel = "#3a3a3a"
    else:
        fg = "black"
        bg = "white"
        panel = "#f5f5f5"
    try:
        ventana.config(bg=bg)
    except:
        pass
    try:
        style = ttk.Style()
        style.configure("TLabel", background=panel, foreground=fg)
        style.configure("TFrame", background=panel)
        style.configure("TButton", padding=6)
    except:
        pass

#aplicar tema a un toplevel y sus hijos (intenta configurar ttk y tk)
def aplicar_tema_a_toplevel(top):
    if tema_actual.get("valor", "claro") == "oscuro":
        fg = "white"
        bg = "#2b2b2b"
        panel = "#3a3a3a"
    else:
        fg = "black"
        bg = "white"
        panel = "#f5f5f5"
    try:
        top.config(bg=bg)
    except:
        pass
    #intentar aplicar estilos ttk globalmente (no rompe si falla)
    try:
        style = ttk.Style()
        style.configure("TLabel", background=panel, foreground=fg)
        style.configure("TFrame", background=panel)
        style.configure("TButton", padding=6)
        style.configure("TCombobox", fieldbackground=panel, foreground=fg)
    except:
        pass
    #recorrer hijos y aplicar background/foreground cuando sea posible
    try:
        for w in top.winfo_children():
            try:
                w.configure(bg=panel, fg=fg)
            except:
                try:
                    w.configure(background=panel, foreground=fg)
                except:
                    pass
            #si es frame, propagar a sus hijos
            try:
                for c in w.winfo_children():
                    try:
                        c.configure(bg=panel, fg=fg)
                    except:
                        try:
                            c.configure(background=panel, foreground=fg)
                        except:
                            pass
            except:
                pass
    except:
        pass


#toggle de tema
def toggle_tema():
    if tema_actual["valor"] == "claro":
        tema_actual["valor"] = "oscuro"
    else:
        tema_actual["valor"] = "claro"
    aplicar_tema(tema_actual["valor"])

#botón pequeño para cambiar tema (colocar en el header principal)
btn_tema_peq = ttk.Button(ventana, text="modo", width=5, command=lambda:[reproducir_sonido("click"), toggle_tema()])
btn_tema_peq.place(relx=0.95, rely=0.02, anchor="ne")




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
