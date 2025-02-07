import ADS1x15
import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random  # Para simular datos

ADS = ADS1x15.ADS1115(0, 0x48)

# Configuración inicial
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot([], [], lw=2)

ax.set_ylim(0, 2**16)
ax.set_xlim(0, 5)
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Valor del sensor")
ax.set_title("Gráfica PPG")

def update(frame):
    x_data.append(time.time() - start_time)  # Tiempo en segundos
    y_data.append(ADS.readADC(0)) 
    
    if len(x_data) > 100:
        x_data.pop(0)
        y_data.pop(0)

    ax.set_xlim(max(0, x_data[-1] - 10), x_data[-1] + 1)  # Ventana deslizante
    #ax.set_ylim(min(y_data) - 0.5, max(y_data) + 0.5)  # Ajuste dinámico de Y según los valores
    line.set_data(x_data, y_data)

    return line,

try:
        start_time = time.time()
        ani = animation.FuncAnimation(fig, update,  interval=100, blit=True)
        plt.show()
        

except KeyboardInterrupt:
        pass

