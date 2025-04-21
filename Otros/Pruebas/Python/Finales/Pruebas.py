from Utilities.data_operations import save_data, load_data
from Utilities.blood_pressure import BloodPressure

"""
bp = BloodPressure(1/0.025)
_, pressures = load_data()

sys, dia = bp.get_blood_pressure(pressures)
bp.plot_results()
"""

# ppm = load_data()[0]
# print(ppm)

pulse = [[1, 5, 8, 9, 10, 11.1]]
save_data(pulse, ["Pulse"])

