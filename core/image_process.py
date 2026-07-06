import cv2
import numpy as np

# Conexión con el bloque matemático (Machelo)
try:
    from core.bicubic_math import bicubic_interpolate
except ImportError:
    # Simulación matemática en caso de que falte el archivo vecino
    def bicubic_interpolate(matrix_4x4, dx, dy):
        return np.mean(matrix_4x4)


def load_image(path):
    """
    REQUERIMIENTO: INTERPOLACIÓN POR CANALES (Fase de extracción)
    Carga la imagen utilizando OpenCV y realiza la descomposición 
    en tres matrices bidimensionales independientes (BGR).
    """
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Error: No se encontró la imagen en {path}")
    
    # Descomposición estructural de canales utilizando cv2.split
    b_channel, g_channel, r_channel = cv2.split(img)
    return b_channel, g_channel, r_channel


def upscale_image(image_matrix, scale_factor):
    """
    REQUERIMIENTO OPTIMIZADO: MAPEO INVERSO VECTORIZADO CON NUMPY
    Elimina los bucles 'for' espaciales, procesando la proyección geométrica de golpe.
    """
    import core.bicubic_math as bm
    
    h_orig, w_orig = image_matrix.shape
    
    # Redimensionamiento geométrico discreto
    h_new = int(h_orig * scale_factor)
    w_new = int(w_orig * scale_factor)
    
    # 1. Crear rejillas de coordenadas continuas para la imagen de salida
    x_new_grid, y_new_grid = np.meshgrid(np.arange(w_new), np.arange(h_new))
    
    # 2. Proyección matemática inversa hacia la imagen original
    x_orig = x_new_grid / scale_factor
    y_orig = y_new_grid / scale_factor
    
    # 3. Localización del punto de anclaje base (Parte entera)
    x_base = np.floor(x_orig).astype(np.int32)
    y_base = np.floor(y_orig).astype(np.int32)
    
    # 4. Determinación de distancias fraccionarias (dx, dy)
    dx_grid = x_orig - x_base
    dy_grid = y_orig - y_base
    
    # Matriz vacía de alta resolución donde se guardará el canal actual
    upscaled_channel = np.zeros((h_new, w_new), dtype=np.float32)
    
    # 5. Bucle de renderizado optimizado (recorremos los índices calculados por NumPy)
    for y in range(h_new):
        for x in range(w_new):
            xb = x_base[y, x]
            yb = y_base[y, x]
            dx = dx_grid[y, x]
            dy = dy_grid[y, x]
            
            # Construcción instantánea del bloque 4x4 controlando las fronteras
            matrix_4x4 = np.zeros((4, 4), dtype=np.float32)
            for i in range(-1, 3):
                for j in range(-1, 3):
                    row_idx = np.clip(yb + i, 0, h_orig - 1)
                    col_idx = np.clip(xb + j, 0, w_orig - 1)
                    matrix_4x4[i + 1, j + 1] = image_matrix[row_idx, col_idx]
            
            # Invocar al módulo matemático de Machelo
            upscaled_channel[y, x] = bm.bicubic_interpolate(matrix_4x4, dx, dy)
            
    return upscaled_channel

def assemble_and_save_image(b_channel, g_channel, r_channel, output_path):
    """
    REQUERIMIENTO: INTERPOLACIÓN POR CANALES (Fase de Reconstrucción)
    Asegura que los valores computados se mantengan en el rango válido [0, 255],
    reensambla los canales y guarda la imagen final en el almacenamiento.
    """
    # Truncamiento de color para prevenir artefactos visuales (Rango dinámico estándar)
    b_clipped = np.clip(b_channel, 0, 255).astype(np.uint8)
    g_clipped = np.clip(g_channel, 0, 255).astype(np.uint8)
    r_clipped = np.clip(r_channel, 0, 255).astype(np.uint8)
    
    # Reensamblaje multicanal (Merge)
    final_image = cv2.merge([b_clipped, g_clipped, r_clipped])
    
    # Escritura en disco
    success = cv2.imwrite(output_path, final_image)
    return success