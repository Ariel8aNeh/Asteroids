#!/usr/bin/env python3
"""
Asteroids Game - Versión Mobile con Kivy
"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Line, Color
from kivy.event import EventDispatcher
import math
import random


class Ship(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(0, 0)
        self.angle = 0
        self.thrust = False
        self.size = (20, 20)
        self.center = (Window.width / 2, Window.height / 2)

    def update(self, dt):
        # Aplicar thrust si está activo
        if self.thrust:
            thrust_vector = Vector(0, 200).rotate(self.angle)
            self.velocity += thrust_vector * dt

        # Aplicar fricción
        self.velocity *= 0.99

        # Actualizar posición
        self.center = Vector(self.center) + self.velocity * dt

        # Wrap around screen
        x, y = self.center
        if x < 0:
            x = Window.width
        elif x > Window.width:
            x = 0
        if y < 0:
            y = Window.height
        elif y > Window.height:
            y = 0
        self.center = (x, y)

    def rotate_left(self):
        self.angle += 5

    def rotate_right(self):
        self.angle -= 5

    def start_thrust(self):
        self.thrust = True

    def stop_thrust(self):
        self.thrust = False


class Asteroid(Widget):
    def __init__(self, size=3, **kwargs):
        super().__init__(**kwargs)
        self.size_level = size
        self.velocity = Vector(
            random.uniform(-100, 100),
            random.uniform(-100, 100)
        )
        self.rotation_speed = random.uniform(-180, 180)
        self.angle = 0

        # Tamaños basados en el nivel
        sizes = {1: 15, 2: 30, 3: 60}
        self.size = (sizes[size], sizes[size])

    def update(self, dt):
        # Actualizar posición
        self.center = Vector(self.center) + self.velocity * dt
        self.angle += self.rotation_speed * dt

        # Wrap around screen
        x, y = self.center
        if x < -30:
            x = Window.width + 30
        elif x > Window.width + 30:
            x = -30
        if y < -30:
            y = Window.height + 30
        elif y > Window.height + 30:
            y = -30
        self.center = (x, y)


class Bullet(Widget):
    def __init__(self, start_pos, angle, **kwargs):
        super().__init__(**kwargs)
        self.center = start_pos
        self.velocity = Vector(0, 400).rotate(angle)
        self.lifetime = 2.0
        self.size = (4, 4)

    def update(self, dt):
        self.center = Vector(self.center) + self.velocity * dt
        self.lifetime -= dt
        return self.lifetime > 0


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ship = Ship()
        self.asteroids = []
        self.bullets = []
        self.score = 0

        # Crear asteroides iniciales
        self.create_initial_asteroids()

        # Programar actualización del juego
        Clock.schedule_interval(self.update, 1.0/60.0)

        # Bind touch events para controles móviles
        self.bind(on_touch_down=self.on_touch_down)
        self.bind(on_touch_up=self.on_touch_up)
        self.bind(on_touch_move=self.on_touch_move)

    def create_initial_asteroids(self):
        for _ in range(5):
            asteroid = Asteroid(size=3)
            # Posicionar lejos de la nave
            while True:
                asteroid.center = (
                    random.uniform(0, Window.width),
                    random.uniform(0, Window.height)
                )
                if Vector(asteroid.center).distance(self.ship.center) > 100:
                    break
            self.asteroids.append(asteroid)

    def on_touch_down(self, touch):
        # Área de controles (parte inferior de la pantalla)
        if touch.y < Window.height * 0.3:
            # Control de rotación (izquierda/derecha)
            if touch.x < Window.width * 0.3:
                self.ship.rotate_left()
            elif touch.x > Window.width * 0.7:
                self.ship.rotate_right()
            elif Window.width * 0.4 < touch.x < Window.width * 0.6:
                # Botón de thrust (centro)
                self.ship.start_thrust()
        else:
            # Disparar tocando la pantalla superior
            self.shoot()
        return True

    def on_touch_up(self, touch):
        self.ship.stop_thrust()
        return True

    def on_touch_move(self, touch):
        # Opcional: control continuo por deslizamiento
        return True

    def shoot(self):
        bullet = Bullet(self.ship.center, self.ship.angle)
        self.bullets.append(bullet)

    def update(self, dt):
        # Actualizar nave
        self.ship.update(dt)

        # Actualizar balas
        self.bullets = [bullet for bullet in self.bullets if bullet.update(dt)]

        # Actualizar asteroides
        for asteroid in self.asteroids:
            asteroid.update(dt)

        # Detectar colisiones
        self.check_collisions()

        # Redibujar
        self.canvas.clear()
        self.draw_game()

    def check_collisions(self):
        # Colisiones bala-asteroide
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if Vector(bullet.center).distance(asteroid.center) < asteroid.size[0]/2:
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += 100

                    # Crear asteroides más pequeños
                    if asteroid.size_level > 1:
                        for _ in range(2):
                            new_asteroid = Asteroid(
                                size=asteroid.size_level - 1)
                            new_asteroid.center = asteroid.center
                            self.asteroids.append(new_asteroid)
                    break

        # Colisión nave-asteroide
        for asteroid in self.asteroids:
            if Vector(self.ship.center).distance(asteroid.center) < asteroid.size[0]/2 + 10:
                self.restart_game()
                break

    def restart_game(self):
        self.ship.center = (Window.width / 2, Window.height / 2)
        self.ship.velocity = Vector(0, 0)
        self.bullets.clear()
        self.asteroids.clear()
        self.create_initial_asteroids()
        self.score = 0

    def draw_game(self):
        with self.canvas:
            # Limpiar canvas
            Color(1, 1, 1, 1)  # Blanco

            # Dibujar nave
            PushMatrix()
            Rotate(angle=self.ship.angle, origin=self.ship.center)
            Line(points=[
                self.ship.center_x, self.ship.center_y + 10,
                self.ship.center_x - 8, self.ship.center_y - 8,
                self.ship.center_x + 8, self.ship.center_y - 8,
                self.ship.center_x, self.ship.center_y + 10
            ], width=2)
            PopMatrix()

            # Dibujar asteroides
            for asteroid in self.asteroids:
                PushMatrix()
                Rotate(angle=asteroid.angle, origin=asteroid.center)
                # Dibujar asteroide como octágono
                points = []
                radius = asteroid.size[0] / 2
                for i in range(8):
                    angle = i * 45
                    x = asteroid.center_x + radius * \
                        math.cos(math.radians(angle))
                    y = asteroid.center_y + radius * \
                        math.sin(math.radians(angle))
                    points.extend([x, y])
                points.extend([points[0], points[1]])  # Cerrar la forma
                Line(points=points, width=2)
                PopMatrix()

            # Dibujar balas
            for bullet in self.bullets:
                Line(circle=(bullet.center_x, bullet.center_y, 2), width=2)


class AsteroidsApp(App):
    def build(self):
        # Configurar ventana para móvil
        Window.orientation = 'portrait'  # o 'landscape'

        game = GameWidget()
        return game


if __name__ == '__main__':
    AsteroidsApp().run()
