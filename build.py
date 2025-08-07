#!/usr/bin/env python3
"""
Script para construir el ejecutable de Asteroids
"""
import os
import sys
import subprocess
import platform


def install_pyinstaller():
    """Instala PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("PyInstaller ya está instalado")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_executable():
    """Construye el ejecutable usando PyInstaller"""
    system = platform.system()

    # Comando base de PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",  # Un solo archivo ejecutable
        "--windowed",  # Sin consola (para juegos)
        "--name", "Asteroids",
        "--icon", "icon.ico" if system == "Windows" else "icon.icns",
        "main.py"
    ]

    # Agregar archivos de datos si existen
    if os.path.exists("assets"):
        cmd.extend(["--add-data", "assets:assets"])

    print(f"Construyendo ejecutable para {system}...")
    print(f"Comando: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print("¡Ejecutable creado exitosamente!")

        # Mostrar ubicación del ejecutable
        if system == "Windows":
            exe_path = os.path.join("dist", "Asteroids.exe")
        else:
            exe_path = os.path.join("dist", "Asteroids")

        if os.path.exists(exe_path):
            print(f"Ejecutable ubicado en: {exe_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error al construir el ejecutable: {e}")
        sys.exit(1)


if __name__ == "__main__":
    install_pyinstaller()
    build_executable()
