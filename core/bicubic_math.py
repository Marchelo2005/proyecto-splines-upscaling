import numpy as np
import math
import numpy as np
def cubic_weight(x, a=-0.5):
    """
    Evalúa la función de peso del spline cúbico para una distancia 'x'.
    El parámetro 'a' define la pendiente de la función en los cruces por cero.
    a = -0.5 es el estándar matemático óptimo para el rescalado de imágenes.
    
    Ecuaciones polinómicas (Método Numérico):
    Si |x| <= 1: (a+2)|x|^3 - (a+3)|x|^2 + 1
    Si 1 < |x| <= 2: a|x|^3 - 5a|x|^2 + 8a|x| - 4a
    Si |x| > 2: 0
    """
    abs_x = abs(x)
    
    if abs_x <= 1:
        return (a + 2) * (abs_x**3) - (a + 3) * (abs_x**2) + 1
    elif 1 < abs_x <= 2:
        return a * (abs_x**3) - 5 * a * (abs_x**2) + 8 * a * abs_x - 4 * a
    else:
        return 0.0

def bicubic_interpolate(matrix_4x4, dx, dy):
    """
    Calcula el valor interpolado usando una vecindad de 4x4 (16 píxeles).
    
    Parámetros:
    - matrix_4x4: Arreglo de NumPy de 4x4 con los valores originales de los píxeles.
    - dx: Distancia fraccional en el eje X (de 0.0 a 1.0).
    - dy: Distancia fraccional en el eje Y (de 0.0 a 1.0).
    
    Retorna:
    - El valor numérico del nuevo píxel interpolado (0-255).
    """
    # 1. Validar que la matriz sea exactamente de 4x4
    if matrix_4x4.shape != (4, 4):
        raise ValueError("La matriz de entrada debe ser de 4x4")

    # 2. Calcular los vectores de distancias.
    # En una matriz 4x4 (índices 0, 1, 2, 3), el punto interpolado cae 
    # entre los índices 1 y 2. Por tanto, las distancias a cada punto son:
    dist_x = [1 + dx, dx, 1 - dx, 2 - dx]
    dist_y = [1 + dy, dy, 1 - dy, 2 - dy]

    # 3. Evaluar los polinomios cúbicos para obtener los pesos en X y en Y
    weights_x = np.array([cubic_weight(x) for x in dist_x])
    weights_y = np.array([cubic_weight(y) for y in dist_y])

    # 4. Multiplicación Matricial (El corazón del método numérico)
    # Ecuación: p(x,y) = Wy * Matriz * Wx
    # Realizamos un producto punto entre las matrices para obtener el valor interpolado.
    
    # Primero interpolamos horizontalmente (multiplicamos filas por pesos en X)
    interp_x = np.dot(matrix_4x4, weights_x)
    
    # Luego interpolamos verticalmente (multiplicamos el resultado por pesos en Y)
    final_value = np.dot(weights_y, interp_x)

    # 5. Normalización y control de límites
    # Los splines cúbicos pueden generar valores "overshoot" (menores a 0 o mayores a 255).
    # Debemos limitarlos al rango válido de color de un píxel.
    final_value = np.clip(final_value, 0.0, 255.0)

    return final_value

if __name__ == "__main__":
    # --- ZONA DE PRUEBAS DE MACHELO ---
    # Este bloque te permite probar tu código matematico en tu propia rama
    # sin tener que esperar a que Frank cargue las imágenes con OpenCV.
    
    print("--- INICIANDO PRUEBA DEL MOTOR MATEMÁTICO ---")
    
    # Simulamos un bloque de 4x4 píxeles en escala de grises (valores de 0 a 255)
    # Imagina que hay una línea oscura cruzando una zona clara.
    mock_pixels = np.array([
        [200, 210, 50, 45],
        [195, 205, 55, 40],
        [190, 200, 60, 35],
        [185, 195, 65, 30]
    ], dtype=np.float32)
    
    print("Matriz original 4x4 (píxeles cercanos):")
    print(mock_pixels)
    
    # Simulamos que queremos crear un nuevo píxel justo en la mitad 
    # de los cuatro píxeles centrales (dx = 0.5, dy = 0.5)
    fractional_x = 0.5
    fractional_y = 0.5
    
    print(f"\nCalculando interpolación para dx={fractional_x}, dy={fractional_y}...")
    
    # Llamamos a tu función
    nuevo_pixel = bicubic_interpolate(mock_pixels, fractional_x, fractional_y)
    
    print(f"Valor del nuevo píxel interpolado: {nuevo_pixel:.2f}")
    print("\n¡Prueba exitosa! Si el valor es un promedio suave de los centrales, el spline funciona.")
def calculate_mse(original_image, processed_image):
    """
    Calcula el Error Cuadrático Medio (MSE) entre dos imágenes.
    Compara la diferencia de color píxel por píxel. 
    Un MSE más bajo significa que la interpolación por splines fue más exacta.
    """
    # Verificamos que las matrices tengan las mismas dimensiones
    if original_image.shape != processed_image.shape:
        raise ValueError("Las imágenes deben tener exactamente las mismas dimensiones para calcular el MSE.")
    
    # Se convierte a float para evitar desbordamientos (overflow) en la resta de 8-bits
    err = np.sum((original_image.astype("float") - processed_image.astype("float")) ** 2)
    err /= float(original_image.shape[0] * original_image.shape[1])
    
    return err

def calculate_psnr(original_image, processed_image, max_pixel_value=255.0):
    """
    Calcula la Relación Señal a Ruido de Máxima Amplitud (PSNR).
    Esta es la métrica de oro en los papers científicos. 
    Devuelve un valor en decibelios (dB). Un valor > 30 dB indica excelente calidad.
    """
    mse = calculate_mse(original_image, processed_image)
    
    # Si el MSE es 0, las imágenes son idénticas (ruido cero)
    if mse == 0:
        return float('inf')
    
    # Fórmula matemática del PSNR
    psnr = 10 * math.log10((max_pixel_value ** 2) / mse)
    return psnr