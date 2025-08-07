"""
Entidades del juego Asteroids: Ship, Bullet, Asteroid, UFO
"""

import pygame
import math
import random
from constants import *


class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # ángulo en grados
        self.vel_x = 0
        self.vel_y = 0
        self.size = SHIP_SIZE

    def rotate_left(self):
        self.angle -= 5

    def rotate_right(self):
        self.angle += 5

    def accelerate(self):
        angle_rad = math.radians(self.angle)
        self.vel_x += math.cos(angle_rad) * SHIP_THRUST
        self.vel_y += math.sin(angle_rad) * SHIP_THRUST

        # Limitar velocidad máxima
        speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
        if speed > SHIP_MAX_SPEED:
            self.vel_x = (self.vel_x / speed) * SHIP_MAX_SPEED
            self.vel_y = (self.vel_y / speed) * SHIP_MAX_SPEED

    def update(self):
        # Aplicar fricción
        self.vel_x *= SHIP_FRICTION
        self.vel_y *= SHIP_FRICTION

        # Actualizar posición
        self.x += self.vel_x
        self.y += self.vel_y

        # Wraparound en los bordes
        self.x = self.x % WINDOW_WIDTH
        self.y = self.y % WINDOW_HEIGHT

    def get_tip(self):
        angle_rad = math.radians(self.angle)
        tip_x = self.x + math.cos(angle_rad) * self.size
        tip_y = self.y + math.sin(angle_rad) * self.size
        return tip_x, tip_y

    def reset_position(self):
        """Resetear nave al centro"""
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.vel_x = 0
        self.vel_y = 0

    def draw(self, screen):
        angle_rad = math.radians(self.angle)

        # Punto frontal
        tip_x = self.x + math.cos(angle_rad) * self.size
        tip_y = self.y + math.sin(angle_rad) * self.size

        # Puntos traseros
        back_angle1 = angle_rad + 2.8
        back_angle2 = angle_rad - 2.8

        back1_x = self.x + math.cos(back_angle1) * (self.size * 0.7)
        back1_y = self.y + math.sin(back_angle1) * (self.size * 0.7)

        back2_x = self.x + math.cos(back_angle2) * (self.size * 0.7)
        back2_y = self.y + math.sin(back_angle2) * (self.size * 0.7)

        points = [(tip_x, tip_y), (back1_x, back1_y), (back2_x, back2_y)]
        pygame.draw.polygon(screen, WHITE, points, 1)


class Bullet:
    def __init__(self, x, y, angle, is_ufo_bullet=False):
        self.x = x
        self.y = y
        angle_rad = math.radians(angle)
        self.vel_x = math.cos(angle_rad) * BULLET_SPEED
        self.vel_y = math.sin(angle_rad) * BULLET_SPEED
        self.lifetime = BULLET_LIFETIME
        self.is_ufo_bullet = is_ufo_bullet

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1

        # Wraparound en los bordes
        self.x = self.x % WINDOW_WIDTH
        self.y = self.y % WINDOW_HEIGHT

        return self.lifetime > 0

    def draw(self, screen):
        color = RED if self.is_ufo_bullet else WHITE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)


class Asteroid:
    def __init__(self, x, y, size_index):
        self.x = x
        self.y = y
        self.size_index = size_index
        self.size = ASTEROID_SIZES[size_index]
        self.vel_x = random.uniform(
            -ASTEROID_SPEEDS[size_index], ASTEROID_SPEEDS[size_index])
        self.vel_y = random.uniform(
            -ASTEROID_SPEEDS[size_index], ASTEROID_SPEEDS[size_index])
        self.rotation = 0
        self.rotation_speed = random.uniform(-1, 1)

        # Crear forma poligonal irregular
        self.points = []
        num_points = random.randint(6, 10)
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            radius = self.size * random.uniform(0.8, 1.2)
            point_x = radius * math.cos(angle)
            point_y = radius * math.sin(angle)
            self.points.append((point_x, point_y))

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rotation += self.rotation_speed

        # Wraparound en los bordes
        self.x = self.x % WINDOW_WIDTH
        self.y = self.y % WINDOW_HEIGHT

    def draw(self, screen):
        rotated_points = []
        rotation_rad = math.radians(self.rotation)

        for point_x, point_y in self.points:
            # Rotar el punto
            rotated_x = point_x * \
                math.cos(rotation_rad) - point_y * math.sin(rotation_rad)
            rotated_y = point_x * \
                math.sin(rotation_rad) + point_y * math.cos(rotation_rad)

            # Trasladar a la posición del asteroide
            final_x = rotated_x + self.x
            final_y = rotated_y + self.y

            rotated_points.append((final_x, final_y))

        pygame.draw.polygon(screen, WHITE, rotated_points, 1)

    def get_collision_radius(self):
        return self.size * 0.8

    def split(self):
        """Dividir asteroide en asteroides más pequeños"""
        if self.size_index < 2:
            asteroids = []
            for _ in range(2):
                new_asteroid = Asteroid(self.x, self.y, self.size_index + 1)
                angle = random.uniform(0, 360)
                speed = ASTEROID_SPEEDS[self.size_index + 1]
                new_asteroid.vel_x = math.cos(math.radians(angle)) * speed
                new_asteroid.vel_y = math.sin(math.radians(angle)) * speed
                asteroids.append(new_asteroid)
            return asteroids
        return []


class UFO:
    def __init__(self):
        # Aparecer desde un lado aleatorio
        side = random.choice(['left', 'right'])
        if side == 'left':
            self.x = -20
            self.direction = 1
        else:
            self.x = WINDOW_WIDTH + 20
            self.direction = -1

        self.y = random.randint(50, WINDOW_HEIGHT - 50)
        self.vel_x = UFO_SPEED * self.direction
        self.vel_y = random.uniform(-0.5, 0.5)
        self.width = 20
        self.height = 8
        self.shoot_timer = 0

    def update(self, ship):
        self.x += self.vel_x
        self.y += self.vel_y

        # Cambiar dirección vertical ocasionalmente
        if random.random() < 0.01:
            self.vel_y = random.uniform(-1, 1)

        # Mantener dentro de los límites verticales
        if self.y < 20:
            self.vel_y = abs(self.vel_y)
        elif self.y > WINDOW_HEIGHT - 20:
            self.vel_y = -abs(self.vel_y)

        # Disparar ocasionalmente hacia el jugador
        self.shoot_timer += 1
        if self.shoot_timer > 30 and random.random() < UFO_SHOOT_CHANCE:
            self.shoot_timer = 0
            # Calcular ángulo hacia el jugador (con imprecisión)
            dx = ship.x - self.x
            dy = ship.y - self.y
            angle = math.degrees(math.atan2(dy, dx))
            # Agregar imprecisión al disparo
            angle += random.uniform(-20, 20)
            return Bullet(self.x, self.y, angle, is_ufo_bullet=True)
        return None

    def is_off_screen(self):
        return self.x < -50 or self.x > WINDOW_WIDTH + 50

    def get_collision_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                           self.width, self.height)

    def draw(self, screen):
        # Dibujar UFO como dos óvalos conectados
        pygame.draw.ellipse(screen, WHITE,
                            (self.x - self.width//2, self.y - self.height//4,
                             self.width, self.height//2), 1)
        pygame.draw.ellipse(screen, WHITE,
                            (self.x - self.width//3, self.y - self.height//2,
                             self.width//1.5, self.height//2), 1)
