"""
Sistema de puntuaciones altas para Asteroids
"""

import json
import os
from datetime import datetime


class HighScores:
    def __init__(self, filename="highscores.json", max_scores=10):
        self.filename = filename
        self.max_scores = max_scores
        self.scores = self.load_scores()

    def load_scores(self):
        """Cargar puntuaciones desde archivo"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []

    def save_scores(self):
        """Guardar puntuaciones en archivo"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except Exception as e:
            print(f"Error al guardar puntuaciones: {e}")

    def add_score(self, name, score):
        """Agregar nueva puntuación"""
        new_score = {
            "name": name[:10],  # Limitar nombre a 10 caracteres
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.scores.append(new_score)
        # Ordenar por puntuación (mayor a menor)
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        # Mantener solo las mejores puntuaciones
        self.scores = self.scores[:self.max_scores]
        self.save_scores()

    def is_high_score(self, score):
        """Verificar si la puntuación califica como alta"""
        if len(self.scores) < self.max_scores:
            return True
        return score > self.scores[-1]["score"]

    def get_rank(self, score):
        """Obtener el ranking de una puntuación"""
        rank = 1
        for high_score in self.scores:
            if score > high_score["score"]:
                break
            rank += 1
        return rank

    def get_scores(self):
        """Obtener lista de puntuaciones"""
        return self.scores.copy()

    def clear_scores(self):
        """Limpiar todas las puntuaciones"""
        self.scores = []
        self.save_scores()
