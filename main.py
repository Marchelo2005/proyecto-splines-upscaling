# -*- coding: utf-8 -*-
import threading
import os
import customtkinter as ctk
from ui.app_window import AppWindow
from core.image_process import load_image, upscale_image, assemble_and_save_image

def ejecutar_proceso_upscaling(app_instancia, ruta_origen, scale_factor):
    try:
        # 1. Cargar y separar canales (Lógica de Frank)
        b, g, r = load_image(ruta_origen)
        
        # 2. Procesar matrices con Splines Bicúbicos (Frank + Machelo)
        b_up = upscale_image(b, scale_factor)
        g_up = upscale_image(g, scale_factor)
        r_up = upscale_image(r, scale_factor)
        
        # 3. Reconstrucción y guardado en disco con nombre único para evitar bloqueos
        directorio = os.path.dirname(ruta_origen)
        nombre_base = os.path.splitext(os.path.basename(ruta_origen))[0]
        ruta_salida = os.path.join(directorio, f"{nombre_base}_upscaled_{scale_factor}x.png")
        
        assemble_and_save_image(b_up, g_up, r_up, ruta_salida)
        
        # 4. Notificar a la UI para que dibuje el resultado
        app_instancia.actualizar_vista_resultado(ruta_salida)
        
    except Exception as e:
        app_instancia.lbl_preview_right.configure(
            text=f"[!] ERROR EN PROCESO:\n\n{str(e)}", 
            text_color="#FF3366"
        )

def lanzar_hilo_segundo_plano():
    if not app.ruta_imagen:
        app.lbl_preview_right.configure(
            text="[!] CRITICAL_ERROR:\n\nDEBES CARGAR UNA IMAGEN\nANTES DE PROCESAR.", 
            text_color="#FF3366"
        )
        return

    # Capturar copias de las variables para que el hilo trabaje de forma segura e independiente
    ruta_fija = app.ruta_imagen
    factor_texto = app.combo_escala.get()
    scale_factor = float(factor_texto.replace("x", ""))

    # CAMBIO SEGURO: Modificamos el texto sin tocar la propiedad 'image' bruscamente
    app.lbl_preview_right.configure(
        text=f"EJECUTANDO RENDER RASTER ({factor_texto})...\n\nCalculando matrices 4x4\ncon splines bicúbicos.", 
        text_color="#00FFCC"
    )
    
    # Lanzar el proceso en paralelo libre de cuelgues
    hilo = threading.Thread(target=ejecutar_proceso_upscaling, args=(app, ruta_fija, scale_factor))
    hilo.start()

if __name__ == "__main__":
    app = AppWindow()
    app.btn_upscale.configure(command=lanzar_hilo_segundo_plano)
    app.mainloop()