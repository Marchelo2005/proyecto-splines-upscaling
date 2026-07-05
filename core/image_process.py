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
    REQUERIMIENTO: MAPEO INVERSO Y CONDICIONES DE FRONTERA
    Calcula la nueva resolución geométrica y barre cada coordenada espacial 
    mapeándola hacia atrás para extraer la vecindad de 4x4 píxeles.
    """
    h_orig, w_orig = image_matrix.shape
    
    # Redimensionamiento geométrico discreto
    h_new = int(h_orig * scale_factor)
    w_new = int(w_orig * scale_factor)
    
    # Inicialización de la matriz de alta resolución para el canal actual
    upscaled_channel = np.zeros((h_new, w_new), dtype=np.float32)
    
    # Bucle de Mapeo Inverso (Barre la imagen de salida)
    for y_new in range(h_new):
        for x_new in range(w_new):
            
            # Proyección matemática inversa a coordenadas continuas
            x_orig = x_new / scale_factor
            y_orig = y_new / scale_factor
            
            # Localización del punto de anclaje inferior (Parte entera)
            x_base = int(np.floor(x_orig))
            y_base = int(np.floor(y_orig))
            
            # Determinación de distancias fraccionarias (dx, dy) ∈ [0, 1)
            dx = x_orig - x_base
            dy = y_orig - y_base
            
            # Construcción de la matriz de vecindad de 16 píxeles (4x4)
            matrix_4x4 = np.zeros((4, 4), dtype=np.float32)
            
            for i in range(-1, 3):
                for j in range(-1, 3):
                    # REQUERIMIENTO: CONDICIONES DE FRONTERA (Truncamiento Dinámico)
                    # Evita desbordamientos de memoria limitando los índices al tamaño de la matriz original
                    row_idx = np.clip(y_base + i, 0, h_orig - 1)
                    col_idx = np.clip(x_base + j, 0, w_orig - 1)
                    
                    # Asignación a la submatriz local 4x4
                    matrix_4x4[i + 1, j + 1] = image_matrix[row_idx, col_idx]
            
            # Envío de la vecindad y coeficientes al motor matemático de Splines Bicúbicos
            upscaled_channel[y_new, x_new] = bicubic_interpolate(matrix_4x4, dx, dy)
            
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