import requests
import Adafruit_DHT
import sys
import json
import time

sensor = Adafruit_DHT.DHT11
pin = 25

headers = {
  'Content-type': 'application/json',
  'Content-length' : ""
}


def req(payload):
  payload_text = json.dumps(payload)
  headers["Content-length"] = str(len(payload_text))
  try:
    r = requests.post('http://192.168.0.29:3000/', headers = headers, json=payload_text)
    print('req sent', payload_text)
  except Exception as e:
    print(e)  

def temps(run_time, time_between_readings):
  t_end = time.time() + run_time
  t_read = time_between_readings
  while(True):
    try:
      humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
      if humidity is not None and temperature is not None:
        json_data = {"temp": int(temperature), "humidity" : int(humidity)}
        req(json_data)
        time.sleep(t_read)
    except Exception as e:
      print(e) 
      break

if __name__ == "__main__":
  run_time = int(sys.argv[1])
  time_between_readings = int(sys.argv[2])
  temps(run_time, time_between_readings)