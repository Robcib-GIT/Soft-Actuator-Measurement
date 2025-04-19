from Utilities.data_operations import save_data, load_data
from Utilities.blood_pressure import BloodPressure

bp = BloodPressure(1/0.025)
_, pressures = load_data()

sys, dia = bp.get_blood_pressure(pressures)
bp.plot_results()