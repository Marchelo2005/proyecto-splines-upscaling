# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog
import os

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        ctk.set_appearance_mode("dark") 
        self.title("Laboratorio de Escalado Espacial")
        self.geometry("1000x600") 
        self.resizable(False, False) 
        
        # Color de fondo global de la ventana (Negro-Lila Profundo)
        self.configure(fg_color="#0A0712")

        # Variable para almacenar la ruta de la imagen seleccionada
        self.ruta_imagen = ""

        # --- ESTRUCTURA DE LA INTERFAZ ---
        
        # Título Principal con tipografía retro-consola cuadriculada
        self.title_label = ctk.CTkLabel(
            self, 
            text="▲ ESCALADO DE IMÁGENES ▲", 
            font=("Courier New", 22, "bold"),
            text_color="#00FFCC"
        )
        self.title_label.pack(pady=15)

        # Contenedor Principal (Divide la pantalla en dos columnas)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=25, pady=10)

        # -----------------------------------------------------------------
        # PANEL IZQUIERDO: Entrada (Imagen Original)
        # -----------------------------------------------------------------
        self.left_panel = ctk.CTkFrame(
            self.main_container, 
            width=460, 
            fg_color="#141024",        
            border_width=2, 
            border_color="#2E1F4D"     
        )
        self.left_panel.pack(side="left", fill="both", expand=True, padx=10)
        self.left_panel.pack_propagate(False)

        self.lbl_original_title = ctk.CTkLabel(
            self.left_panel, 
            text="[IMAGEN DE ENTRADA]", 
            font=("Courier New", 15, "bold"), 
            text_color="#9D4EDD"       
        )
        self.lbl_original_title.pack(pady=10)

        # Área de visualización de imagen original
        self.lbl_preview_left = ctk.CTkLabel(
            self.left_panel, 
            text="SISTEMA_IDLE // SIN IMAGEN\n\nPor favor, carga un archivo...", 
            font=("Courier New", 12, "bold"),
            fg_color="#07050E", 
            corner_radius=6,
            width=420,
            height=290,
            text_color="#625C73"
        )
        self.lbl_preview_left.pack(pady=10)

        # Botón Seleccionar Imagen
        self.btn_select = ctk.CTkButton(
            self.left_panel, 
            text="Cargar_Archivo.exe", 
            font=("Courier New", 13, "bold"),
            fg_color="#7B2CBF",        
            hover_color="#5A189A",     
            text_color="#FFFFFF",
            height=38,
            border_width=1,
            border_color="#9D4EDD"
        )
        self.btn_select.configure(command=self.seleccionar_imagen)
        self.btn_select.pack(pady=15)

        # -----------------------------------------------------------------
        # PANEL DERECHO: Configuración y Acción (Resultado)
        # -----------------------------------------------------------------
        self.right_panel = ctk.CTkFrame(
            self.main_container, 
            width=460, 
            fg_color="#141024",        
            border_width=2, 
            border_color="#2E1F4D"     
        )
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10)
        self.right_panel.pack_propagate(False)

        self.lbl_result_title = ctk.CTkLabel(
            self.right_panel, 
            text="[IMAGEN ESCALADA RESULTANTE]", 
            font=("Courier New", 15, "bold"), 
            text_color="#9D4EDD"
        )
        self.lbl_result_title.pack(pady=10)

        # Área de visualización de resultado
        self.lbl_preview_right = ctk.CTkLabel(
            self.right_panel, 
            text="ESPERANDO INICIALIZACIÓN...", 
            font=("Courier New", 12, "bold"),
            fg_color="#07050E", 
            corner_radius=6,
            width=420,
            height=290,
            text_color="#443F52"
        )
        self.lbl_preview_right.pack(pady=10)

        # Controles de Configuración de Escala
        self.controls_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.controls_frame.pack(pady=5)

        self.lbl_escala = ctk.CTkLabel(
            self.controls_frame, 
            text="FACTOR_ESCALA:", 
            font=("Courier New", 12, "bold"),
            text_color="#FFFFFF"
        )
        self.lbl_escala.pack(side="left", padx=5)

        self.combo_escala = ctk.CTkComboBox(
            self.controls_frame, 
            values=["x2", "x3", "x4"], 
            width=90, 
            font=("Courier New", 12, "bold"),
            fg_color="#141024",
            border_color="#2E1F4D",
            button_color="#2E1F4D"
        )
        self.combo_escala.pack(side="left", padx=5)
        self.combo_escala.set("x2")

        # Botón de acción principal: Aplicar Escalado 
        self.btn_upscale = ctk.CTkButton(
            self.right_panel, 
            text="APLICAR ESCALADO ESPACIAL", 
            font=("Courier New", 13, "bold"),
            fg_color="#00FFCC",        
            text_color="#0A0712",      
            hover_color="#00CC99",
            height=38,
            border_width=1,
            border_color="#00FFCC"
        )
        self.btn_upscale.pack(pady=10)

    # --- FUNCIONES DE CONTROL (MÉTODOS INTERNOS INDENTADOS) ---

    def seleccionar_imagen(self):
        archivo = filedialog.askopenfilename( 
            title="Seleccionar Captura de Pantalla",
            filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg *.bmp")]
        )
        if archivo:
            from PIL import Image
            self.ruta_imagen = archivo 
            nombre_archivo = os.path.basename(archivo) 
            
            try:
                img_pil = Image.open(archivo)
                img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(400, 260))
                
                self.lbl_preview_left.configure(image=img_ctk, text="") 
                self.title_label.configure(text=f"▲ DETECTADO: {nombre_archivo} ▲")
            except Exception as e:
                self.lbl_preview_left.configure(text=f"Error al cargar imagen:\n{e}", text_color="#FF3366")

    def actualizar_vista_resultado(self, ruta_imagen_salida):
        from PIL import Image
        import customtkinter as ctk
    
    # 1. Cargar la nueva imagen escalada desde el disco
        img_pil = Image.open(ruta_imagen_salida)
    
    # 2. Definir el tamaño del contenedor (puedes ajustarlo según tu diseño)
    # Por ejemplo, manteniendo el tamaño estándar de tu preview de entrada
        img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(400, 300))
    
    # 3. Dibujar la imagen borrando el texto de carga anterior
        self.lbl_preview_right.configure(image=img_ctk, text="")
    
    # 4. Guardar una referencia viva en la instancia para que el recolector de basura no la borre
        self.imagen_resultado_ref = img_ctk

# Bloque de arranque principal alineado al ras izquierdo
if __name__ == "__main__":
    app = AppWindow()
    # Conexión por defecto si se ejecuta la interfaz de forma aislada
    app.btn_upscale.configure(command=app.seleccionar_imagen)
    app.mainloop()