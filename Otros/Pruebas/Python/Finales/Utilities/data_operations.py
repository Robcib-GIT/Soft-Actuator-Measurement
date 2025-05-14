import csv
from tkinter import Tk, filedialog
from typing import Tuple, Dict, List, Any
import pandas as pd
import os
import re

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def save_data_borrar(data, column_labels: List[str]):
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


def load_data_borrar() -> List[List[any]]:
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


def save_data(data_dict: Dict[str, List[float]], results_dict: Dict[str, int]): # TODO: cambiar nombre a save_data y en los otros ficheros adaptar
    """
    Guarda los datos de dos diccionarios en un archivo CSV.

    Args:
        data_dict: Diccionario con claves como string y valores como lista de floats.
        results_dict: Diccionario con claves como string y valores como string.
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

            # Escribir el contenido del diccionario 2
            for key, value in results_dict.items():
                writer.writerow([f"# {key}: {value}"])

            # Escribir una línea vacía entre los diccionarios y los datos
            writer.writerow([])

            # Escribir el contenido del diccionario 1 (convertir los datos a filas)
            # Escribir las cabeceras de las columnas
            writer.writerow(list(data_dict.keys()))  # Escribe las claves del primer diccionario

            # Convertir las listas de valores en filas y escribirlas
            rows = zip(*data_dict.values())
            writer.writerows(rows)

        print(f"Archivo guardado como {file_path}")
    else:
        print("No se guardó el archivo.")


def load_data() -> Tuple[Dict[str, List[float]], Dict[str, Any]]:  # TODO: cambiar nombre a load_data y en los otros ficheros adaptar
    """
    Carga un archivo CSV con metainformación comentada (# Param: valor) y una tabla de datos.
    Devuelve dos diccionarios:
    - Uno con los datos (columnas como claves y listas de valores).
    - Otro con los parámetros (convertidos automáticamente a int o float si es posible).

    Returns:
        Tupla con un diccionario que contiene la información del csv y otro diccionario con la información comentada al principio de este
    """
    root = Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        initialdir=data_dir,
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv")]
    )

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    param_dict = {}
    data_start_index = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("#"):
            if ":" in line:
                key, value = line[1:].split(":", 1)
                key = key.strip()
                value = value.strip()

                # Intentar convertir a int o float
                try:
                    if '.' in value:
                        param_dict[key] = float(value)
                    else:
                        param_dict[key] = int(value)
                except ValueError:
                    param_dict[key] = value  # Mantener como str si no se puede convertir
        elif "," in line:
            data_start_index = i
            break

    # Cargar los datos a partir del encabezado
    df = pd.read_csv(filepath, skiprows=data_start_index)
    data_dict = df.to_dict(orient="list")

    # Añadir info extra a partir del nombre del archivo
    filename = os.path.basename(filepath)
    match = re.match(r"PRESION_(.+?)_v(\d+)\.csv", filename)
    if match:
        param_dict["Subject"] = match.group(1)
        param_dict["Version"] = int(match.group(2))
    else:
        print("El nombre del archivo no sigue el patrón esperado, datos sobre el sujeto no extraidos")
    return data_dict, param_dict
