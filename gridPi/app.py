from flask import Flask
import requests
import json
import time
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
import busio
import RPi.GPIO as GPIO
import cordaTX

i2c_bus = busio.I2C(board.SCL, board.SDA)
ina219 = INA219(i2c_bus,0x40)

ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V

channel = 21 ##Relay control pin - GPIO 21

demoSleepTime=4

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

def relay_on(pin):
    GPIO.output(pin, GPIO.LOW) #Turn on


def relay_off(pin):
    GPIO.output(pin, GPIO.HIGH)  # Turn off

def relay():
    sensorDataBoolean, sensor_data = sensorData()
    if sensorDataBoolean:
        relay_on(channel)
        sensorDataBoolean, sensor_data = sensorData()
        time.sleep(demoSleepTime)
        relay_off(channel)
        return True,sensor_data
    else:
        return False,sensor_data

def sensorData():
    bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
    shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
    current = ina219.current  # current in mA
    power = ina219.power  # power in watts

    sensorDataJson ={
        "v+":bus_voltage + shunt_voltage,
        "v-":bus_voltage,
        "Shunt Current":current,
        "Message":"Success"
    }

    sensorDataneg ={
        "v+":bus_voltage + shunt_voltage,
        "v-":bus_voltage,
        "Shunt Current":current,
        "Message":"Battery not connected"
    }

    # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
    if ina219.overflow:
        print("Internal Math Overflow Detected!")
        print("")

    if (bus_voltage <0.9):
        return False, sensorDataneg
    elif(bus_voltage<4):
        return True, sensorDataJson
    else:
        return False, sensorDataJson


relay_off(channel)

app = Flask(__name__)

@app.route('/startCharging', methods=['GET'])
def startCharge():

    relayBoolean, data = relay()
    i=data["Shunt Current"]
    v=data["v-"]
    power = i*v*demoSleepTime/3600
    powerStr= "Energy transferred over 4s :" + str(power) + "Wh"
    token = int(power *(-10000))
    
    data['Energy Transferred'] = str(power*(-1)) + " Wh"
    data['Token Equivalent '] = token
        
    resp, respBoolean = cordaTX.startTransaction(token)
    if respBoolean:
        txID = resp.split("id=")
        txID = resp.split("id=")
        txIDStr =  txID[1]
        txIDStr1 = txIDStr.split(")")
        txIDStr = txIDStr1[0]
        data['TransactionID']= txIDStr
        print(txIDStr)
    print(data)
    if respBoolean:
        return json.dumps(data) 
    else:
        return "Transaction failed : " #+ json.dumps(data)


@app.route('/stopCharging', methods=['GET'])
def stopCharge():

    relay_off(21)
    return "{\"Message\":\"Charging Stopped\"}"

@app.route('/getSensorData', methods=['GET'])
def getSensorData():
    sensorDataBool, sensorDetails = sensorData()

    return json.dumps(sensorDetails)   

if __name__ == '__main__':
    app.run(debug=True, port=50050, host='0.0.0.0')



