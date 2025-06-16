#!/bin/bash

# Salir si ocurre algún error
set -e

echo "Instalando dependencias de Python desde requirements.txt..."
pip3 install -r requirements.txt

echo "Instalando ros-noetic-rosbridge-server..."
sudo apt update
sudo apt install -y ros-noetic-rosbridge-server

echo "Instalando librerías Python adicionales..."
sudo pip3 install ADS1x15-ADC
sudo pip3 install adafruit-circuitpython-pca9685

echo "Instalación completada con éxito."
