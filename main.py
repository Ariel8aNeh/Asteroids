#!/usr/bin/env python3
"""
Asteroids Game - Archivo Principal
Recreación del clásico juego Asteroids
"""

import pygame
import sys
from game import Game


def main():
    """Función principal del juego"""
    pygame.init()

    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error al ejecutar el juego: {e}")
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
