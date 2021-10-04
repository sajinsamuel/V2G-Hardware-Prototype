from flask import Flask
import json
import time
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
import busio

i2c_bus = busio.I2C(board.SCL, board.SDA)
ina219 = INA219(i2c_bus,0x40)

ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V

def sensorData():
    bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
    shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
    current = ina219.current  # current in mA
    power = ina219.power  # power in watts

    sensorDataJson ={
        "v+":bus_voltage + shunt_voltage,
        "v-":bus_voltage,
        "Shunt Current":current,
    }

    # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
    if ina219.overflow:
        print("Internal Math Overflow Detected!")
        print("")

    return sensorDataJson

app = Flask(__name__)

@app.route('/getSensorData', methods=['GET'])
def getSensorData():
    sensorDetails = sensorData()

    return json.dumps(sensorDetails)   

if __name__ == '__main__':
    app.run(debug=True, port=50092, host='0.0.0.0')



