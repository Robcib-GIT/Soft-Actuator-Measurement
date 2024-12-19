"""
Este codigo es la adaptación del código "DetecciónPulso" para ejecutarse en tiempo
real. El concepto es el siguiente:
1-Obtener tandas de datos cada 3secs
2-Unir la nueva tanda al restante de la anterior, siendo el restante los puntos a
    partir del último pico sistólico detectado
3-Obtener picos sistólicos y diastólicos del conjunto
4-Averiguar si se está detectando pulso
5-Si se detecta pulso obtener datos relacionados con el pulso
6-Mostrar/enviar resultados
7-Descartar tanda hasta ultimo pico sistolico (almacenar tambien tiempo del ultimo
    pico)
8-Repetir el proceso


De esta manera, al trabajar con un conjunto finito de datos, se pueden utilizar los
vectores de numpy para mayor agilidad. Hay que utilizar colas de datos para no
perderlos mientras se procesan las tandas.
"""


if __name__ == '__main__':

