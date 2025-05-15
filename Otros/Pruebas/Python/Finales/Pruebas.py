from Utilities.blood_pressure import BloodPressure
from Utilities.data_operations import load_data

if __name__ == "__main__":
    data, params_data = load_data()
    pressures = data['Pressure']
    # FIXME: Me he dado cuenta que no puse delay y se muestreo con 198sps aprox
    # TODO: Probar con 40 y sino ir subiendo
    """  
    time = np.array(data['Time'])
    fs = 1 / np.mean(np.diff(time))
    """
    fs = 198

    bp = BloodPressure(fs=fs)

    try:
        # Procesar información
        sys, dia = bp.get_blood_pressure(pressures=pressures)
        print(f"SAM_SYS:  {sys}  |  SAM_SIA:  {dia}")
        print(f"Real_SYS: {params_data['SYS']}  |  Real_SIA: {params_data['DIA']}")
    except Exception as e:
        print(f"Ocurrió un error al procesar los datos.\n {e}")
    finally:
        bp.plot_results()
