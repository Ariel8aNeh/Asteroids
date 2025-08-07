"""
Constantes del juego Asteroids
"""

# Dimensiones de la ventana
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Configuración de la nave
SHIP_SIZE = 8
SHIP_THRUST = 0.2
SHIP_FRICTION = 0.985
SHIP_MAX_SPEED = 5

# Configuración de las balas
BULLET_SPEED = 8
BULLET_LIFETIME = 80  # frames
MAX_BULLETS = 4

# Configuración de asteroides
ASTEROID_SPEEDS = [0.5, 1.0, 1.5]  # velocidades por tamaño
ASTEROID_SIZES = [30, 20, 10]  # tamaños (grande, mediano, pequeño)
ASTEROID_POINTS = [20, 50, 100]  # puntos por tamaño

# Configuración de UFOs
UFO_SPAWN_CHANCE = 0.001  # Probabilidad por frame
UFO_SPEED = 2
UFO_SHOOT_CHANCE = 0.02  # Probabilidad por frame de disparo
UFO_POINTS = 500

# Configuración visual
NUM_STARS = 100
INVULNERABILITY_TIME = 120  # frames (2 segundos a 60 FPS)

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
GRAY = (128, 128, 128)
GREEN = (100, 255, 100)

# Configuración del juego
INITIAL_LIVES = 3
INITIAL_ASTEROIDS = 6
