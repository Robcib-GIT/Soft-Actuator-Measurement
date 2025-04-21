import csv
from tkinter import Tk, filedialog
from typing import Tuple, List
import pandas as pd
import os

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def save_data(data, column_labels: List[str]):
    """
    Guarda los datos en un archivo CSV con el número de columnas personalizado.

    Args:
        data: Lista de listas (o tupla de listas) con los datos que se van a guardar.
              Cada sublista debe contener los datos correspondientes a una columna.
        column_labels: Lista con los nombres de las columnas.
    """
    # Crear ventana de diálogo para guardar el archivo CSV
    root = Tk()
    root.withdraw()  # Ocultar ventana principal
    file_path = filedialog.asksaveasfilename(
        initialdir=data_dir,
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")])

    if file_path:
        # Guardar los datos en un archivo CSV
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_labels)  # Escribe los encabezados de las columnas
            rows = zip(*data)  # Transponer la lista de listas para que cada fila contenga los datos correspondientes
            writer.writerows(rows)  # Escribe las filas de datos
        print(f"Archivo guardado como {file_path}")
    else:
        print("No se guardó el archivo.")


def load_data() -> List[List[any]]:
    """
    Carga los datos de un archivo CSV en una lista de listas, donde cada sublista
    representa una columna de datos.

    Returns:
        Una lista de listas (o tupla de listas) donde cada sublista corresponde
        a una columna de datos del archivo CSV.
    """
    root = Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        initialdir=data_dir,
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv")]
    )

    df = pd.read_csv(filepath)
    return df.values.T.tolist()  # Transpone los datos y los convierte en una lista de listas

