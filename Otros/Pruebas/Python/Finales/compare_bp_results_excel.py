from Utilities.data_operations import load_data, save_data
import os
import numpy as np
from Utilities.blood_pressure import BloodPressure
from openpyxl import load_workbook

if __name__ == "__main__":

    carpeta = "data"
    all_data = {}

    for filename in os.listdir(carpeta):
        if filename.startswith("PRESION_") and filename.endswith(".csv"):
            filepath = os.path.join(carpeta, filename)
            data_dict, param_dict = load_data(filepath)
            # print(param_dict)

            fs = 1 / np.mean(np.diff(data_dict["Time"]))
            bp = BloodPressure(fs)

            # Obtener información
            subject = param_dict['Subject']
            version = param_dict['Version']

            results = {
                "real_sys": param_dict.get("SYS", None),
                "real_dia": param_dict.get("DIA", None),
                "real_ppm": param_dict.get("PPM", None)
            }

            # Calcular presiones con mi algoritmo
            try:
                sys, dia = bp.get_blood_pressure(data_dict["Pressure"])
                results["sam_sys"] = sys
                results["sam_dia"] = dia
            except Exception:
                results["sam_sys"] = None
                results["sam_dia"] = None

            # Almacenar informacion
            all_data.setdefault(subject, {})[version] = results

    # Ordenar la información por versions
    results_excel_dir = "data/RESULTADOS.xlsx"
    workbook = load_workbook(results_excel_dir)
    sheet = workbook["BloodPressure_v1"]
    all_data_ordered = {}
    n = 0
    for subject, versions in all_data.items():
        ordered_versions = dict(sorted(versions.items(), key=lambda item: item[0]))
        for version, results in ordered_versions.items():
            row = 3+n
            sheet.cell(row=row, column=1).value = n
            sheet.cell(row=row, column=2).value = subject
            sheet.cell(row=row, column=3).value = version
            sheet.cell(row=row, column=4).value = results['sam_sys'] if results['sam_sys'] is not None else '=NA()'
            sheet.cell(row=row, column=5).value = results['sam_dia'] if results['sam_dia'] is not None else '=NA()'
            sheet.cell(row=row, column=7).value = results['real_sys'] if results['real_sys'] is not None else '=NA()'
            sheet.cell(row=row, column=8).value = results['real_dia'] if results['real_dia'] is not None else '=NA()'
            sheet.cell(row=row, column=9).value = results['real_ppm'] if results['real_ppm'] is not None else '=NA()'

            n += 1

        all_data_ordered[subject] = ordered_versions

    # Guardar los cambios
    workbook.save(results_excel_dir)
