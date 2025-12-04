import pandas as pd #importa la libreria pandas para manejo de datos en tablas
import matplotlib.pyplot as plt #importa matplotlib para graficar
import numpy as np #importa numpy para operaciones matematicas
import tkinter as tk #importa tkinter para crear interfaces graficas
from tkinter import ttk #importa ttk para widgets con estilos modernos en tkinter
from PIL import Image, ImageTk #importa PIL para manejar imagenes en tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #permite mostrar graficas matplotlib en tkinter
import re #importa re para expresiones regulares
import unicodedata #importa unicodedata para normalizar texto y quitar acentos
import os #importa os para manejo de rutas de archivos
import unicodedata #importa unicodedata de nuevo (ya estaba arriba, pero no afecta)
import platform #importa platform para detectar el sistema operativo
import threading #importa threading para ejecutar tareas en segundo plano

#sonidos y compatibilidad (winsound en windows, si no disponible no hace nada)
try:
    import winsound #intenta importar winsound para reproducir sonidos en windows
except Exception:
    winsound = None #si falla, asigna None para evitar errores

#helper para reproducir sonidos de interfaz (no falla si winsound no existe)
def reproducir_sonido(nombre): #funcion para reproducir sonidos segun el nombre
    #nombre: 'abrir','click','ok','error'
    try:
        if winsound and platform.system()=="Windows": #si winsound existe y es windows
            if nombre == "abrir":
                winsound.MessageBeep(winsound.MB_ICONASTERISK) #sonido de abrir
            elif nombre == "click":
                winsound.MessageBeep(winsound.MB_OK) #sonido de click
            elif nombre == "ok":
                winsound.MessageBeep(winsound.MB_OK) #sonido de ok
            elif nombre == "error":
                winsound.MessageBeep(winsound.MB_ICONHAND) #sonido de error
            else:
                winsound.MessageBeep() #sonido generico
        else:
            #fallback cross-platform: si existe una ventana global, usar bell
            try:
                ventana.bell() #intenta hacer beep con la ventana principal
            except Exception:
                pass #si falla, no hace nada
    except Exception:
        pass #si ocurre cualquier error, no hace nada

#mostrar un cargador modal simple con progressbar indeterminada
def mostrar_cargador(padre, texto="Cargando…"): #muestra ventana de carga con barra de progreso
    #crea un Toplevel pequeño y devuelve el objeto para cerrarlo luego
    cargador = tk.Toplevel(padre) #crea ventana hija
    cargador.transient(padre) #la hace modal
    cargador.grab_set() #bloquea interaccion con otras ventanas
    cargador.title("") #sin titulo
    cargador.geometry("260x80") #tamaño fijo
    try:
        padre.update_idletasks() #actualiza la ventana padre
        px = padre.winfo_rootx() #obtiene posicion x de la ventana padre
        py = padre.winfo_rooty() #obtiene posicion y de la ventana padre
        pw = padre.winfo_width() #obtiene ancho de la ventana padre
        ph = padre.winfo_height() #obtiene alto de la ventana padre
        cargador.geometry(f"+{px + max(10, pw//2 - 130)}+{py + max(10, ph//2 - 40)}") #centra el cargador sobre la ventana padre
    except Exception:
        pass #si falla, no centra
    cargador.resizable(False, False) #no permite cambiar tamaño
    frame = ttk.Frame(cargador, padding=(8,8)) #crea frame con padding
    frame.pack(fill="both", expand=True) #lo expande en la ventana
    lbl = ttk.Label(frame, text=texto) #label con texto de carga
    lbl.pack(pady=(2,6)) #espaciado vertical
    barra = ttk.Progressbar(frame, mode="indeterminate", length=220) #barra de progreso indeterminada
    barra.pack() #muestra la barra
    barra.start(10) #inicia animacion de la barra
    cargador.update_idletasks() #actualiza la ventana
    return cargador #devuelve el objeto para cerrarlo luego

#detener y destruir cargador
def detener_cargador(cargador): #detiene y destruye la ventana de cargador
    try:
        for child in cargador.winfo_children(): #recorre los hijos de la ventana
            if isinstance(child, ttk.Progressbar): #si es una barra de progreso
                try:
                    child.stop() #detiene la animacion
                except:
                    pass #si falla, no hace nada
        cargador.grab_release() #libera el bloqueo modal
        cargador.destroy() #cierra la ventana
    except Exception:
        pass #si ocurre error, no hace nada

#animacionfadeentrada
def aparecer_con_fade(ventana_toplevel, x=None, y=None, ancho=None, alto=None, pasos=10, intervalo=25): #animacion de desvanecimiento al mostrar ventana
    try:
        if ancho and alto and x is not None and y is not None:
            ventana_toplevel.geometry(f"{ancho}x{alto}+{x}+{y}") #posiciona la ventana
        ventana_toplevel.attributes('-alpha', 0.0) #inicia con transparencia
        def paso(i):
            try:
                ventana_toplevel.attributes('-alpha', i/pasos) #aumenta opacidad gradualmente
                if i < pasos:
                    ventana_toplevel.after(intervalo, lambda: paso(i+1)) #programa siguiente paso
            except:
                pass #si falla, no hace nada
        paso(0) #inicia animacion
    except Exception:
        pass #si ocurre error, no hace nada

# Resolver la ruta del CSV relativa al archivo del script (evita FileNotFoundError
# cuando el script se ejecuta desde otro directorio de trabajo)
csv_filename = "8._RUTAS_TRANSPORTE_URBANO_20251011.csv" #nombre del archivo csv
base_dir = os.path.dirname(__file__) #directorio donde está el script
csv_path = os.path.join(base_dir, csv_filename) #ruta completa al csv
df = pd.read_csv(csv_path, index_col="codigo") #lee el csv y usa 'codigo' como índice
print("Leyendo CSV en:", csv_path) #imprime la ruta del csv
print(df.columns) #imprime las columnas del dataframe

#normalizar y convertir a numérico las columnas que deben ser números
cols_numericas = [
    "capacidad_minima",
    "capacidad_maxima",
    "frecuencia_de_despacho_hora_pico",
    "frecuencia_despacho_hora_valle",
    "long_km"
] #lista de columnas que deben ser numéricas
for col in cols_numericas:
    if col in df.columns:
        #convertir a string, cambiar comas por puntos y extraer el primer número que encuentre
        df[col] = df[col].astype(str).str.replace(",", ".", regex=False) #reemplaza comas por puntos
        df[col] = df[col].str.extract(r'([-+]?\d*\.?\d+)')[0] #extrae el primer número decimal
        df[col] = pd.to_numeric(df[col], errors="coerce") #convierte a número, si falla pone NaN

#crear diccionario de fillna usando medias numéricas limpias cuando existan
llenar = {"empresa": "BUSETAS AUTONOMA",
          "hora_primer_despacho": "05:00:00 a.m.",
          "hora_ultimo_despacho": "08:30:00 p.m"} #valores por defecto para columnas vacías

if "capacidad_minima" in df.columns:
    llenar["capacidad_minima"] = df["capacidad_minima"].mean() #usa la media si existe
if "capacidad_maxima" in df.columns:
    llenar["capacidad_maxima"] = df["capacidad_maxima"].mean()
if "frecuencia_de_despacho_hora_pico" in df.columns:
    llenar["frecuencia_de_despacho_hora_pico"] = df["frecuencia_de_despacho_hora_pico"].mean()
#nota: frecuencia_valle no está en la clave exacta usada para fillna en tu archivo original;
#si existe en df se puede añadir igual que arriba:
if "frecuencia_despacho_hora_valle" in df.columns:
    llenar["frecuencia_despacho_hora_valle"] = df["frecuencia_despacho_hora_valle"].mean()

df_filtrado = df.fillna(llenar) #rellena los valores nulos con el diccionario

df_filtrado["empresa_limpia"] = df_filtrado["empresa"].str.replace("OPERACIÓN AUTORIZADA A ", "", regex=False) #crea columna empresa_limpia quitando texto fijo

df_filtrado = df_filtrado.dropna(subset=['ruta','terminal'], how='all') #elimina filas donde ruta y terminal están vacías

print(df_filtrado.describe()) #imprime estadisticas del dataframe filtrado

print(df_filtrado) #imprime el dataframe filtrado completo

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

    # área scrollable (vertical + horizontal)
    contenedor = tk.Frame(ven_all)
    contenedor.pack(fill="both", expand=True)

    # canvas para scroll (vertical + horizontal)
    canvas = tk.Canvas(contenedor, bg=ven_all.cget("bg"), highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    # scroll vertical
    scrollbar_y = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scrollbar_y.grid(row=0, column=1, sticky="ns")

    # scroll horizontal
    scrollbar_x = tk.Scrollbar(contenedor, orient="horizontal", command=canvas.xview)
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    # conectar scrollbars al canvas
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # permitir expansión del área
    contenedor.rowconfigure(0, weight=1)
    contenedor.columnconfigure(0, weight=1)

    # frame interno que se va a desplazar
    frame_scroll = tk.Frame(canvas, bg=ven_all.cget("bg"))
    window_id = canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

    # actualizar región scroll cuando cambie el contenido
    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_scroll.bind("<Configure>", actualizar_scroll)

    # Evitar crear la ventana interna duplicada y permitir que el contenido
    # pueda crecer horizontalmente. Ajustar expand=True para que el contenido
    # pueda exceder el ancho del canvas (y así aparezca la barra X).
    # grid: dos columnas arriba y una fila ancha abajo
    marco_graficos = ttk.Frame(frame_scroll, padding=6)
    marco_graficos.pack(padx=8, pady=8, fill="both", expand=True)

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

def filtrar_por_seleccion(lugar, terminal): #función para filtrar el dataframe según lugar o terminal seleccionados
    df_search = df_filtrado.reset_index().copy() #crea una copia del dataframe filtrado con el índice reiniciado

    if lugar and lugar != "Seleccione un lugar...": #si se seleccionó un lugar válido
        def ruta_contiene(r): #función interna para verificar si el lugar está en la ruta
            if not isinstance(r, str): #si la ruta no es string
                return False #no coincide
            partes = [p.strip().lower() for p in r.split("-")] #divide la ruta por '-' y normaliza a minúsculas
            return lugar.strip().lower() in partes #verifica si el lugar está en las partes

        filtrado = df_search[df_search["ruta"].astype(str).apply(ruta_contiene)].copy() #filtra el dataframe usando la función anterior
        lista_resultados = filtrado.to_dict(orient="records") #convierte el resultado a una lista de diccionarios
        return lista_resultados #devuelve la lista de resultados

    elif terminal and terminal != "Seleccione un terminal...": #si se seleccionó un terminal válido
        terminal_normalizado = terminal.strip().lower() #normaliza el terminal a minúsculas y sin espacios
        filtrado = df_search[
            df_search["terminal"].astype(str).str.strip().str.lower() == terminal_normalizado #filtra por terminal normalizado
        ].copy()
        print("DEBUG: terminales encontrados en el filtrado:") #imprime los terminales encontrados para depuración
        for t in filtrado["terminal"]:
            print(f"  '{t}'")
        lista_resultados = filtrado.to_dict(orient="records") #convierte el resultado a una lista de diccionarios
        return lista_resultados #devuelve la lista de resultados

    else: #si no se seleccionó nada válido
        return [] #devuelve lista vacía





        
"""ññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññ"""
"""ññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññ"""
"""ññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññññ"""
def debug_lugares_terminales_vacios(): #función para mostrar lugares y terminales que no tienen datos al filtrar
    print("\n--- DEBUG: Lugares vacíos tras filtrar ---") #imprime encabezado de depuración para lugares
    vacios_lugares = [] #lista para guardar lugares vacíos
    for lugar in lugares: #recorre todos los lugares
        res = filtrar_por_seleccion(lugar, None) #filtra usando el lugar y sin terminal
        if not res: #si no hay resultados
            print(f"lugar vacío: '{lugar}'") #imprime el lugar vacío
            vacios_lugares.append(lugar) #lo agrega a la lista de vacíos
    print(f"Total lugares vacíos: {len(vacios_lugares)}") #imprime el total de lugares vacíos

    print("\n--- DEBUG: Terminales vacíos tras filtrar ---") #imprime encabezado de depuración para terminales
    vacios_terminales = [] #lista para guardar terminales vacíos
    for terminal in terminales: #recorre todos los terminales
        res = filtrar_por_seleccion(None, terminal) #filtra usando el terminal y sin lugar
        if not res: #si no hay resultados
            print(f"terminal vacío: '{terminal}'") #imprime el terminal vacío
            vacios_terminales.append(terminal) #lo agrega a la lista de vacíos
    print(f"Total terminales vacíos: {len(vacios_terminales)}") #imprime el total de terminales vacíos
    print("--- FIN DEBUG ---\n") #imprime fin de depuración

debug_lugares_terminales_vacios() #ejecuta la función de depuración al iniciar el programa

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

def ventana_emergente_4(padre): #función para mostrar ventana emergente para agregar vehículo
    #crear ventana toplevel
    ventana = tk.Toplevel(padre) #crea ventana secundaria
    ventana.title("Ventana emergente") #asigna título a la ventana
    ventana.transient(padre) #la hace modal respecto al padre
    ventana.grab_set() #bloquea interacción con otras ventanas
    ventana.geometry("900x900") #define tamaño de la ventana

    #preparar opciones desde el dataframe
    try:
        serie_empresas = df_filtrado["empresa"].dropna().astype(str).str.replace(
            "OPERACIÓN AUTORIZADA A ", "", regex=False).str.strip() #obtiene empresas únicas, limpia texto y espacios
        opciones_empresa = sorted(serie_empresas.unique().tolist()) #ordena empresas únicas
    except Exception as e:
        print("debug: no se pudo obtener empresas desde df_filtrado:", e) #imprime error si falla
        opciones_empresa = ["Empresa A", "Empresa B"] #opciones por defecto

    try:
        if 'terminales' in globals() and terminales: #si existe la lista global terminales
            opciones_terminal = sorted(list(terminales)) #usa la lista global
        else:
            opciones_terminal = sorted(df_filtrado["terminal"].dropna().astype(str).str.strip().unique().tolist()) #extrae terminales únicas del dataframe
    except Exception as e:
        print("debug: no se pudo obtener terminales:", e) #imprime error si falla
        opciones_terminal = ["Terminal 1", "Terminal 2"] #opciones por defecto

    def limpiar_lista_horas(lista): #función para limpiar lista de horas y eliminar nulos
        return sorted({str(x).strip() for x in lista if str(x).strip() and str(x).strip().lower() not in ("nan", "none")})

    try:
        horas_primer_despacho = limpiar_lista_horas(df_filtrado["hora_primer_despacho"].dropna().astype(str).tolist()) #extrae y limpia horas de primer despacho
    except Exception:
        horas_primer_despacho = [] #si falla, lista vacía
    try:
        horas_ultimo_despacho = limpiar_lista_horas(df_filtrado["hora_ultimo_despacho"].dropna().astype(str).tolist()) #extrae y limpia horas de último despacho
    except Exception:
        horas_ultimo_despacho = [] #si falla, lista vacía

    if not horas_primer_despacho: #si no hay horas de primer despacho
        horas_primer_despacho = [f"{h:02d}:00" for h in range(0, 24)] #genera lista de horas por defecto
    if not horas_ultimo_despacho: #si no hay horas de último despacho
        horas_ultimo_despacho = [f"{h:02d}:00" for h in range(0, 24)] #genera lista de horas por defecto

    #dividir clases en dos categorías fijas: buseta y microbus
    opciones_clase = ["buseta", "microbus"] #opciones fijas para clase

    #estilos
    estilo = ttk.Style(ventana) #crea objeto de estilos para la ventana
    estilo.theme_use('clam') #usa tema 'clam'
    estilo.configure("TButton", padding=8) #configura padding para botones
    estilo.configure("TEntry", padding=4) #configura padding para entradas
    estilo.configure("TLabel", padding=4) #configura padding para etiquetas

    #frames principales
    marco_principal = ttk.Frame(ventana, padding=(20, 20, 20, 20)) #frame principal con padding
    marco_principal.grid(row=0, column=0, sticky="nsew") #coloca el frame en la ventana
    ventana.columnconfigure(0, weight=1) #permite expansión horizontal
    ventana.rowconfigure(0, weight=1) #permite expansión vertical

    marco_izq = ttk.Frame(marco_principal) #frame para columna izquierda
    marco_der = ttk.Frame(marco_principal) #frame para columna derecha
    marco_izq.grid(row=2, column=0, padx=(10, 30), sticky="n") #coloca frame izquierdo
    marco_der.grid(row=2, column=1, padx=(30, 10), sticky="n") #coloca frame derecho

    etiqueta_encabezado = ttk.Label(marco_principal, text="Seleccione las siguientes opciones:", anchor="center") #etiqueta de encabezado
    etiqueta_encabezado.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew") #coloca la etiqueta

    btn_agregar_recorrido = ttk.Button(marco_principal, text="Agregar recorrido") #botón para agregar recorrido
    btn_agregar_recorrido.grid(row=1, column=0, columnspan=1, sticky="w", pady=(0, 12)) #coloca el botón

    entrada_texto = ttk.Entry(marco_principal, width=90) #entrada de texto para recorrido/ruta
    entrada_texto.insert(0, "") #inicializa vacía
    entrada_texto.grid(row=1, column=0, columnspan=2, pady=(50, 20), sticky="ew") #coloca la entrada

    #columna izquierda
    btn_agregar_empresa = ttk.Button(marco_izq, text="Agregar empresa") #botón para agregar empresa
    btn_agregar_empresa.grid(row=0, column=0, pady=(0, 8), sticky="w") #coloca el botón

    empresa_var = tk.StringVar() #variable para empresa seleccionada
    combo_empresa = ttk.Combobox(
        marco_izq, textvariable=empresa_var,
        values=opciones_empresa, state="readonly", width=35
    ) #combobox para seleccionar empresa
    combo_empresa.set("Seleccione una empresa...") #texto inicial
    combo_empresa.grid(row=1, column=0, pady=(0, 12), sticky="w") #coloca el combobox

    ttk.Label(marco_izq, text="Capacidad mínima").grid(row=2, column=0, sticky="w") #etiqueta capacidad mínima
    capacidad_min_var = tk.StringVar() #variable para capacidad mínima
    entrada_capacidad_min = ttk.Entry(marco_izq, textvariable=capacidad_min_var, width=30) #entrada para capacidad mínima
    entrada_capacidad_min.grid(row=3, column=0, pady=(0, 12), sticky="w") #coloca la entrada

    ttk.Label(marco_izq, text="Frecuencia hora pico").grid(row=4, column=0, sticky="w") #etiqueta frecuencia pico
    frecuencia_pico_var = tk.StringVar() #variable para frecuencia pico
    entrada_frecuencia_pico = ttk.Entry(marco_izq, textvariable=frecuencia_pico_var, width=30) #entrada para frecuencia pico
    entrada_frecuencia_pico.grid(row=5, column=0, pady=(0, 12), sticky="w") #coloca la entrada

    ttk.Label(marco_izq, text="Hora primer despacho").grid(row=6, column=0, sticky="w") #etiqueta hora primer despacho
    hora_primer_var = tk.StringVar() #variable para hora primer despacho
    combo_hora_primer = ttk.Combobox(
        marco_izq, textvariable=hora_primer_var,
        values=horas_primer_despacho, width=30, state="readonly"
    ) #combobox para seleccionar hora primer despacho
    combo_hora_primer.set("Seleccione hora...") #texto inicial
    combo_hora_primer.grid(row=7, column=0, pady=(0, 12), sticky="w") #coloca el combobox

    ttk.Label(marco_izq, text="Longitud (km)").grid(row=8, column=0, sticky="w") #etiqueta longitud
    longitud_var = tk.StringVar() #variable para longitud
    entrada_longitud = ttk.Entry(marco_izq, textvariable=longitud_var, width=30) #entrada para longitud
    entrada_longitud.grid(row=9, column=0, pady=(0, 20), sticky="w") #coloca la entrada

    def cancelar(): #función para cerrar ventana
        ventana.destroy()

    btn_cancelar = ttk.Button(marco_izq, text="Cancelar", command=cancelar) #botón cancelar
    btn_cancelar.grid(row=10, column=0, pady=(30, 0), sticky="w") #coloca el botón

    #columna derecha
    btn_agregar_terminal = ttk.Button(marco_der, text="Agregar terminal") #botón para agregar terminal
    btn_agregar_terminal.grid(row=0, column=0, pady=(0, 8), sticky="e") #coloca el botón

    terminal_var = tk.StringVar() #variable para terminal seleccionada
    combo_terminal = ttk.Combobox(
        marco_der, textvariable=terminal_var,
        values=opciones_terminal, state="readonly", width=35
    ) #combobox para seleccionar terminal
    combo_terminal.set("Seleccione un terminal...") #texto inicial
    combo_terminal.grid(row=1, column=0, pady=(0, 12), sticky="e") #coloca el combobox

    ttk.Label(marco_der, text="Capacidad máxima").grid(row=2, column=0, sticky="e") #etiqueta capacidad máxima
    capacidad_max_var = tk.StringVar() #variable para capacidad máxima
    entrada_capacidad_max = ttk.Entry(marco_der, textvariable=capacidad_max_var, width=30) #entrada para capacidad máxima
    entrada_capacidad_max.grid(row=3, column=0, pady=(0, 12), sticky="e") #coloca la entrada

    ttk.Label(marco_der, text="Frecuencia hora valle").grid(row=4, column=0, sticky="e") #etiqueta frecuencia valle
    frecuencia_valle_var = tk.StringVar() #variable para frecuencia valle
    entrada_frecuencia_valle = ttk.Entry(marco_der, textvariable=frecuencia_valle_var, width=30) #entrada para frecuencia valle
    entrada_frecuencia_valle.grid(row=5, column=0, pady=(0, 12), sticky="e") #coloca la entrada

    ttk.Label(marco_der, text="Hora último despacho").grid(row=6, column=0, sticky="e") #etiqueta hora último despacho
    hora_ultimo_var = tk.StringVar() #variable para hora último despacho
    combo_hora_ultimo = ttk.Combobox(
        marco_der, textvariable=hora_ultimo_var,
        values=horas_ultimo_despacho, width=30, state="readonly"
    ) #combobox para seleccionar hora último despacho
    combo_hora_ultimo.set("Seleccione hora...") #texto inicial
    combo_hora_ultimo.grid(row=7, column=0, pady=(0, 12), sticky="e") #coloca el combobox

    ttk.Label(marco_der, text="Clase").grid(row=8, column=0, sticky="e") #etiqueta clase
    clase_var = tk.StringVar() #variable para clase seleccionada
    combo_clase = ttk.Combobox(
        marco_der, textvariable=clase_var,
        values=opciones_clase, width=30, state="readonly"
    ) #combobox para seleccionar clase
    combo_clase.set("Seleccione clase...") #texto inicial
    combo_clase.grid(row=9, column=0, pady=(0, 20), sticky="e") #coloca el combobox

    #guardar datos con autenticacion y persistencia
    def guardar(): #función para guardar los datos ingresados
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
            global df, df_filtrado, terminales, lugares #declarar variables globales que se van a modificar

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

    btn_guardar = ttk.Button(marco_der, text="Guardar", command=guardar) #botón para guardar datos
    btn_guardar.grid(row=10, column=0, pady=(30, 0), sticky="e") #coloca el botón

    marco_principal.columnconfigure(0, weight=1) #permite expansión horizontal
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
df.to_excel("Excel_RUTAS_TRANSPORTE_URBANO.xlsx", index=False) #guarda el dataframe en un archivo excel sin el índice
print("Guardado Excel_RUTAS_TRANSPORTE_URBANO.xlsx") #imprime mensaje de confirmación en consola

cant_total = len(df_filtrado) #calcula la cantidad total de vehículos registrados en el dataframe filtrado
prom_gen_max = df_filtrado["capacidad_maxima"].mean() #calcula el promedio de la capacidad máxima
prom_gen_min = df_filtrado["capacidad_minima"].mean() #calcula el promedio de la capacidad mínima
prom_frec_pico = df_filtrado["frecuencia_de_despacho_hora_pico"].mean() #calcula el promedio de la frecuencia de despacho en hora pico
prom_frec_valle = df_filtrado["frecuencia_despacho_hora_valle"].mean() #calcula el promedio de la frecuencia de despacho en hora valle

df_filtrado["long_km"] = pd.to_numeric(df_filtrado["long_km"], errors="coerce") #convierte la columna long_km a valores numéricos, ignorando errores
prom_km = df_filtrado["long_km"].mean() #calcula el promedio de kilómetros recorridos

mindf = {
    "Cantidad de veiculos registrados" : cant_total, #guarda la cantidad total de vehículos
    "Promedio Capacidad Maxima" : round(prom_gen_max,2), #guarda el promedio de capacidad máxima redondeado a 2 decimales
    "Promedio Capacidad Minima" : round(prom_gen_min,2), #guarda el promedio de capacidad mínima redondeado a 2 decimales
    "Promedio Frecuencia de despacho en hora pico" : round(prom_frec_pico,2), #guarda el promedio de frecuencia en hora pico redondeado a 2 decimales
    "Promedio Frecuencia de despacho en hora valle" : round(prom_frec_valle,2), #guarda el promedio de frecuencia en hora valle redondeado a 2 decimales
    "Promedio de Kilometros" : round(prom_km, 2) #guarda el promedio de kilómetros redondeado a 2 decimales
}
minidata = pd.DataFrame([mindf]) #crea un dataframe con los datos estadísticos mínimos