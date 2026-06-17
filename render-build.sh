#!/usr/bin/env bash
# Salir inmediatamente si un comando falla
set -o errexit

# 1. Actualizar la lista de paquetes del servidor
apt-get update

# 2. Instalar las librerías de sistema que WeasyPrint necesita para dibujar el PDF
apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libffi-dev shared-mime-info

# 3. Instalar las librerías de Python de tu requirements.txt
pip install -r requirements.txt