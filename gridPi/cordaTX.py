import http.client
import yaml
import json

def startTransaction(txValue):
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    txStr = str(txValue)
    
    txEndPoint = "/v2gtransaction?iouValue="+txStr+"&otherParty="+config['VehicleParty']+"&sanctionedParty="+config["SanctionsBody"]
    print (txEndPoint)
    conn = http.client.HTTPConnection("3.87.175.168", 10070)

    payload = ''
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    conn.request("POST", txEndPoint, payload, headers)
    res = conn.getresponse()
    data = res.read()
    dataDec= data.decode("utf-8")
    print(res.status)
    print(dataDec)
    if res.status==201:
        return dataDec, True
    else:
        return dataDec, False
    


