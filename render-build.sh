#!/usr/bin/env bash
# Salir inmediatamente si algún comando falla
set -o errexit

# 1. Actualizar el gestor de paquetes de Render
apt-get update

# 2. Instalar librerías de sistema necesarias para PDFs (WeasyPrint)
apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libffi-dev shared-mime-info

# 3. Actualizar pip e instalar tus librerías de Python
python3 -m pip install --upgrade pip
pip install -r requirements.txt
