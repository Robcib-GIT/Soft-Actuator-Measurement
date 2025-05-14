from Utilities.data_operations import load_data, save_data

if __name__ == "__main__":

    data, subject_data = load_data()
    print(subject_data)

    # Claves que queremos conservar
    claves_a_conservar = ['SYS', 'DIA', 'PPM']

    # Crear un nuevo diccionario solo con las claves seleccionadas
    diccionario_filtrado = {k: subject_data[k] for k in claves_a_conservar if k in subject_data}
    save_data(data_dict=data, results_dict=diccionario_filtrado)
