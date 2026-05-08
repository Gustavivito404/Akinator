import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk

ARCHIVO_CONOCIMIENTO = 'base_conocimiento_lol.json'
CARPETA_IMAGENES = 'imagenes'

# --- CLASE NODO (Misma lógica, sin cambios) ---
class Nodo:
    def __init__(self, texto, es_hoja=False, si=None, no=None):
        self.texto = texto
        self.es_hoja = es_hoja
        self.si = si
        self.no = no

    def a_diccionario(self):
        if self.es_hoja:
            return {"texto": self.texto, "es_hoja": True}
        return {"texto": self.texto, "es_hoja": False, 
                "si": self.si.a_diccionario() if self.si else None, 
                "no": self.no.a_diccionario() if self.no else None}

    @staticmethod
    def desde_diccionario(datos):
        if datos["es_hoja"]:
            return Nodo(datos["texto"], es_hoja=True)
        nodo = Nodo(datos["texto"], es_hoja=False)
        nodo.si = Nodo.desde_diccionario(datos["si"])
        nodo.no = Nodo.desde_diccionario(datos["no"])
        return nodo

# --- LÓGICA DE ARCHIVOS ---
def guardar_arbol(raiz):
    with open(ARCHIVO_CONOCIMIENTO, 'w', encoding='utf-8') as f:
        json.dump(raiz.a_diccionario(), f, indent=4, ensure_ascii=False)

def cargar_arbol():
    if os.path.exists(ARCHIVO_CONOCIMIENTO):
        with open(ARCHIVO_CONOCIMIENTO, 'r', encoding='utf-8') as f:
            return Nodo.desde_diccionario(json.load(f))
    raiz = Nodo("¿El campeón ataca a distancia (Ranged)?")
    raiz.si = Nodo("Ashe", es_hoja=True)
    raiz.no = Nodo("Garen", es_hoja=True)
    return raiz

# --- INTERFAZ GRÁFICA ---
class AdivinaQuienApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adivina Quién: League of Legends")
        self.root.geometry("600x700")
        self.root.configure(bg="#010A13") # Color estilo cliente de LoL

        self.arbol = cargar_arbol()
        self.nodo_actual = self.arbol

        # Variables de la UI
        self.lbl_imagen = tk.Label(root, bg="#010A13")
        self.lbl_imagen.pack(pady=20)

        self.lbl_texto = tk.Label(root, text="", font=("Arial", 16, "bold"), fg="#C8AA6E", bg="#010A13", wraplength=500)
        self.lbl_texto.pack(pady=20)

        frame_botones = tk.Frame(root, bg="#010A13")
        frame_botones.pack(pady=20)

        self.btn_si = tk.Button(frame_botones, text="SÍ", font=("Arial", 14), bg="#0AC8B9", fg="white", width=10, command=lambda: self.procesar_respuesta("si"))
        self.btn_si.grid(row=0, column=0, padx=20)

        self.btn_no = tk.Button(frame_botones, text="NO", font=("Arial", 14), bg="#CD4337", fg="white", width=10, command=lambda: self.procesar_respuesta("no"))
        self.btn_no.grid(row=0, column=1, padx=20)
        
        self.btn_reiniciar = tk.Button(root, text="Jugar de nuevo", font=("Arial", 12), command=self.reiniciar_juego)
        self.btn_reiniciar.pack(pady=10)
        self.btn_reiniciar.pack_forget() # Oculto al inicio

        self.actualizar_pantalla()

    def cargar_imagen(self, nombre_campeon=None):
        """Carga el splash art si existe, si no, pone una imagen por defecto"""
        ruta_img = f"{CARPETA_IMAGENES}/default.jpg" # Imagen genérica de interrogación
        if nombre_campeon:
            ruta_posible = f"{CARPETA_IMAGENES}/{nombre_campeon}.jpg"
            if os.path.exists(ruta_posible):
                ruta_img = ruta_posible
        
        try:
            img = Image.open(ruta_img)
            img = img.resize((400, 235), Image.Resampling.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(img) # Necesario guardarlo en self para que no se borre
            self.lbl_imagen.config(image=self.img_tk)
        except:
            self.lbl_imagen.config(text="[Imagen no encontrada]", fg="white")

    def actualizar_pantalla(self):
        if self.nodo_actual.es_hoja:
            self.lbl_texto.config(text=f"¿Tu campeón es {self.nodo_actual.texto}?")
            self.cargar_imagen(self.nodo_actual.texto)
        else:
            self.lbl_texto.config(text=self.nodo_actual.texto)
            self.cargar_imagen() # Carga la imagen genérica de pregunta

    def procesar_respuesta(self, respuesta):
        if self.nodo_actual.es_hoja:
            if respuesta == "si":
                messagebox.showinfo("¡Gané!", "¡El sistema experto ha acertado! GG.")
                self.fin_juego()
            else:
                self.aprender()
        else:
            if respuesta == "si":
                self.nodo_actual = self.nodo_actual.si
            else:
                self.nodo_actual = self.nodo_actual.no
            self.actualizar_pantalla()

    def aprender(self):
        viejo_campeon = self.nodo_actual.texto
        
        # Cuadros de diálogo nativos de tkinter para pedir datos
        nuevo_campeon = simpledialog.askstring("Aprender", "¡Me rindo! ¿En qué campeón estabas pensando?")
        if not nuevo_campeon:
            self.fin_juego()
            return
            
        nuevo_campeon = nuevo_campeon.strip().title()
        
        nueva_pregunta = simpledialog.askstring("Aprender", f"Escribe una pregunta de Sí/No que sea 'Sí' para {nuevo_campeon} y 'No' para {viejo_campeon}:")
        if not nueva_pregunta:
            self.fin_juego()
            return
            
        nueva_pregunta = nueva_pregunta.strip()

        # Actualizar el árbol
        self.nodo_actual.texto = nueva_pregunta
        self.nodo_actual.es_hoja = False
        self.nodo_actual.si = Nodo(nuevo_campeon, es_hoja=True)
        self.nodo_actual.no = Nodo(viejo_campeon, es_hoja=True)
        
        guardar_arbol(self.arbol)
        messagebox.showinfo("Aprendizaje", "¡He actualizado mi base de conocimientos!")
        self.fin_juego()

    def fin_juego(self):
        self.btn_si.config(state="disabled")
        self.btn_no.config(state="disabled")
        self.btn_reiniciar.pack()

    def reiniciar_juego(self):
        self.nodo_actual = self.arbol
        self.btn_si.config(state="normal")
        self.btn_no.config(state="normal")
        self.btn_reiniciar.pack_forget()
        self.actualizar_pantalla()

if __name__ == "__main__":
    # Crear carpeta de imágenes si no existe
    if not os.path.exists(CARPETA_IMAGENES):
        os.makedirs(CARPETA_IMAGENES)
        
    root = tk.Tk()
    app = AdivinaQuienApp(root)
    root.mainloop()