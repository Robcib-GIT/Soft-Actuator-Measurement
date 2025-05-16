import csv
from tkinter import Tk, filedialog
from typing import Tuple, Dict, List, Any
import pandas as pd
import os
import re

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def save_data(data_dict: Dict[str, List[float]], results_dict: Dict[str, int] = {}):
    """
    Guarda los datos de dos diccionarios en un archivo CSV.

    :param data_dict: Diccionario con los encabezados como clave y una lista de datos como valor
    :param results_dict: Diccionario con parámetros que se comentaran al principio del csv
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
            # Dejar solo 3 decimales por limpieza
            rounded_rows = [
                [round(val, 3) if isinstance(val, float) else val for val in row]
                for row in rows
            ]
            writer.writerows(rounded_rows)

        print(f"Archivo guardado como {file_path}")
    else:
        print("No se guardó el archivo.")


def load_data(filepath = None) -> Tuple[Dict[str, List[float]], Dict[str, Any]]:
    """
    Carga información de un CSV y también los datos comentados al principio de este.

    :param filepath: Ruta del archivo CSV. Si es None, se abre un diálogo para seleccionar el archivo.
    :returns: Una tupla con dos elementos:
        - data_dict (dict): Diccionario que contiene la información general del CSV.
        - param_dict (dict): Diccionario que contiene la información comentada del CSV.
    """
    if filepath is None:
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
