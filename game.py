"""
Clase principal del juego Asteroids
"""

import pygame
import sys
import math
import random
from constants import *
from entities import Ship, Bullet, Asteroid, UFO
from highscores import HighScores


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        # Sistema de puntuaciones
        self.high_scores = HighScores()

        # Crear estrellas de fondo
        self.stars = []
        for _ in range(NUM_STARS):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            brightness = random.choice([128, 160, 192, 255])
            self.stars.append((x, y, brightness))

        # Estados del juego
        self.game_state = "playing"  # "playing", "game_over", "enter_name", "show_scores"
        self.name_input = ""

        self.reset_game()

    def reset_game(self):
        """Resetear el juego a estado inicial"""
        self.ship = Ship(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.bullets = []
        self.ufos = []
        self.asteroids = []
        self.spawn_asteroids(INITIAL_ASTEROIDS)

        self.score = 0
        self.lives = INITIAL_LIVES
        self.invulnerable_time = 0
        self.game_state = "playing"
        self.name_input = ""

    def spawn_asteroids(self, count):
        """Generar asteroides alejados de la nave"""
        for _ in range(count):
            while True:
                x = random.randint(0, WINDOW_WIDTH)
                y = random.randint(0, WINDOW_HEIGHT)
                dist = math.sqrt((x - self.ship.x)**2 + (y - self.ship.y)**2)
                if dist > 100:
                    break

            asteroid = Asteroid(x, y, 0)  # Comenzar con asteroides grandes
            self.asteroids.append(asteroid)

    def handle_input(self):
        """Manejar entrada del teclado"""
        keys = pygame.key.get_pressed()

        if self.game_state == "playing":
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.ship.rotate_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.ship.rotate_right()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.ship.accelerate()

    def handle_events(self):
        """Manejar eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif self.game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        self.shoot()

                elif self.game_state == "game_over":
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_h:
                        self.game_state = "show_scores"

                elif self.game_state == "enter_name":
                    if event.key == pygame.K_RETURN:
                        if self.name_input.strip():
                            self.high_scores.add_score(
                                self.name_input.strip(), self.score)
                        self.game_state = "show_scores"
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input = self.name_input[:-1]
                    else:
                        if len(self.name_input) < 10 and event.unicode.isprintable():
                            self.name_input += event.unicode.upper()

                elif self.game_state == "show_scores":
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "game_over"

        return True

    def shoot(self):
        """Disparar bala del jugador"""
        player_bullets = [b for b in self.bullets if not b.is_ufo_bullet]
        if len(player_bullets) < MAX_BULLETS:
            tip_x, tip_y = self.ship.get_tip()
            bullet = Bullet(tip_x, tip_y, self.ship.angle)
            self.bullets.append(bullet)

    def check_collisions(self):
        """Verificar todas las colisiones del juego"""
        # Colisiones bala del jugador - asteroide
        for bullet in self.bullets[:]:
            if bullet.is_ufo_bullet:
                continue

            for asteroid in self.asteroids[:]:
                dist = math.sqrt((bullet.x - asteroid.x) **
                                 2 + (bullet.y - asteroid.y)**2)
                if dist < asteroid.get_collision_radius():
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)

                    # Dividir el asteroide
                    new_asteroids = asteroid.split()
                    self.asteroids.extend(new_asteroids)

                    # Aumentar puntaje
                    self.score += ASTEROID_POINTS[asteroid.size_index]
                    break

        # Colisiones bala del jugador - UFO
        for bullet in self.bullets[:]:
            if bullet.is_ufo_bullet:
                continue

            for ufo in self.ufos[:]:
                ufo_rect = ufo.get_collision_rect()
                bullet_rect = pygame.Rect(bullet.x-2, bullet.y-2, 4, 4)
                if ufo_rect.colliderect(bullet_rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if ufo in self.ufos:
                        self.ufos.remove(ufo)
                    self.score += UFO_POINTS
                    break

        if self.invulnerable_time <= 0:
            # Colisiones nave - asteroide
            for asteroid in self.asteroids:
                dist = math.sqrt((self.ship.x - asteroid.x) **
                                 2 + (self.ship.y - asteroid.y)**2)
                if dist < asteroid.get_collision_radius() + self.ship.size:
                    self.hit_ship()
                    break

            # Colisiones nave - UFO
            for ufo in self.ufos:
                ufo_rect = ufo.get_collision_rect()
                ship_rect = pygame.Rect(self.ship.x-self.ship.size, self.ship.y-self.ship.size,
                                        self.ship.size*2, self.ship.size*2)
                if ufo_rect.colliderect(ship_rect):
                    self.hit_ship()
                    break

            # Colisiones nave - bala UFO
            for bullet in self.bullets[:]:
                if not bullet.is_ufo_bullet:
                    continue

                dist = math.sqrt((bullet.x - self.ship.x) **
                                 2 + (bullet.y - self.ship.y)**2)
                if dist < self.ship.size + 3:
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.hit_ship()
                    break

    def hit_ship(self):
        """Manejar cuando la nave es golpeada"""
        self.lives -= 1
        self.invulnerable_time = INVULNERABILITY_TIME
        self.ship.reset_position()

        if self.lives <= 0:
            if self.high_scores.is_high_score(self.score):
                self.game_state = "enter_name"
            else:
                self.game_state = "game_over"

    def update(self):
        """Actualizar lógica del juego"""
        if self.game_state != "playing":
            return

        self.ship.update()

        # Actualizar balas
        self.bullets = [bullet for bullet in self.bullets if bullet.update()]

        # Actualizar asteroides
        for asteroid in self.asteroids:
            asteroid.update()

        # Actualizar UFOs
        for ufo in self.ufos[:]:
            new_bullet = ufo.update(self.ship)
            if new_bullet:
                self.bullets.append(new_bullet)

            if ufo.is_off_screen():
                self.ufos.remove(ufo)

        # Spawn de UFOs ocasionalmente
        if random.random() < UFO_SPAWN_CHANCE and len(self.ufos) == 0:
            self.ufos.append(UFO())

        # Reducir tiempo de invulnerabilidad
        if self.invulnerable_time > 0:
            self.invulnerable_time -= 1

        self.check_collisions()

        # Verificar si se ganó el nivel
        if not self.asteroids:
            next_level_asteroids = INITIAL_ASTEROIDS + \
                min(self.score // 2000, 4)
            self.spawn_asteroids(next_level_asteroids)

    def draw_game(self):
        """Dibujar elementos del juego"""
        # Dibujar estrellas de fondo
        for x, y, brightness in self.stars:
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (x, y), 1)

        # Dibujar nave (parpadeando si es invulnerable)
        if self.invulnerable_time <= 0 or self.invulnerable_time % 10 < 5:
            self.ship.draw(self.screen)

        # Dibujar balas
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Dibujar asteroides
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)

        # Dibujar UFOs
        for ufo in self.ufos:
            ufo.draw(self.screen)

        # UI del juego
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

        # Instrucciones
        instructions = self.tiny_font.render(
            "Arrow keys/WASD: move, SPACE: shoot", True, GRAY)
        self.screen.blit(instructions, (10, WINDOW_HEIGHT - 20))

    def draw_game_over(self):
        """Dibujar pantalla de game over"""
        game_over_text = self.font.render("GAME OVER!", True, RED)
        score_text = self.small_font.render(
            f"Final Score: {self.score}", True, WHITE)

        # Verificar si es puntuación alta
        if self.high_scores.is_high_score(self.score):
            rank = self.high_scores.get_rank(self.score)
            rank_text = self.small_font.render(
                f"New High Score! Rank #{rank}", True, YELLOW)
        else:
            rank_text = None

        restart_text = self.small_font.render(
            "R: Restart  |  H: High Scores  |  ESC: Quit", True, WHITE)

        # Centrar textos
        game_over_rect = game_over_text.get_rect(
            center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
        score_rect = score_text.get_rect(
            center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 10))
        restart_rect = restart_text.get_rect(
            center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)

        if rank_text:
            rank_rect = rank_text.get_rect(
                center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 15))
            self.screen.blit(rank_text, rank_rect)

    def draw_name_input(self):
        """Dibujar pantalla de entrada de nombre"""
        title_text = self.font.render("NEW HIGH SCORE!", True, YELLOW)
        prompt_text = self.small_font.render("Enter your name:", True, WHITE)
        name_text = self.font.render(self.name_input + "_", True, GREEN)
        instruction_text = self.tiny_font.render(
            "Press ENTER to save", True, GRAY)

        title_rect = title_text.get_rect(
            center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60))
        prompt_rect = prompt_text.get_rect(
            center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
        name_rect = name_text.get_rect(
            center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 10))
        instruction_rect = instruction_text.get_rect(
            center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(prompt_text, prompt_rect)
        self.screen.blit(name_text, name_rect)
        self.screen.blit(instruction_text, instruction_rect)

    def draw_high_scores(self):
        """Dibujar tabla de puntuaciones altas"""
        title_text = self.font.render("HIGH SCORES", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)

        scores = self.high_scores.get_scores()

        if not scores:
            no_scores_text = self.small_font.render(
                "No high scores yet!", True, WHITE)
            no_scores_rect = no_scores_text.get_rect(
                center=(WINDOW_WIDTH//2, 200))
            self.screen.blit(no_scores_text, no_scores_rect)
        else:
            y_start = 150
            for i, score_data in enumerate(scores[:10]):
                rank = f"{i+1:2d}."
                name = score_data["name"][:10]
                score = f"{score_data['score']:,}"
                date = score_data["date"][:10]  # Solo la fecha

                # Formatear la línea
                line = f"{rank} {name:<10} {score:>8} {date}"
                color = YELLOW if i == 0 else WHITE

                score_line = self.small_font.render(line, True, color)
                self.screen.blit(score_line, (WINDOW_WIDTH //
                                 2 - 150, y_start + i * 25))

        # Instrucciones
        back_text = self.small_font.render(
            "R: Restart  |  ESC: Back  |  ESC ESC: Quit", True, GRAY)
        back_rect = back_text.get_rect(
            center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def draw(self):
        """Dibujar todo según el estado actual"""
        self.screen.fill(BLACK)

        if self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "enter_name":
            self.draw_name_input()
        elif self.game_state == "show_scores":
            self.draw_high_scores()

        pygame.display.flip()

    def run(self):
        """Loop principal del juego"""
        running = True

        while running:
            running = self.handle_events()
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()
