import csv
from tkinter import Tk, filedialog
from typing import Tuple, List
import pandas as pd
import os

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def save_data(data, x_label, y_label):
    # Crear ventana de diálogo para guardar el archivo CSV
    root = Tk()
    root.withdraw()  # Ocultar ventana principal
    file_path = filedialog.asksaveasfilename(
        initialdir= data_dir,
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")])

    if file_path:
        # Guardar los datos en un archivo CSV
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([x_label, y_label])
            for x, y in zip(data[0], data[1]):
                writer.writerow([x, y])  # Escribe la pareja de valores en una fila
        print(f"Archivo guardado como {file_path}")
    else:
        print("No se guardó el archivo.")


def load_data() -> Tuple[List, List]:
    root = Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        initialdir=data_dir,
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv")]
    )

    df = pd.read_csv(filepath)
    return df.iloc[:, 0].values, df.iloc[:, 1].values
