import numpy as np
import quandl
import configparser

config = configparser.ConfigParser()
config.read('conf/config.ini')
key = config['QUANDL']['api_key']
key2 = config['QUANDL']['api_key2']
print(type(key), key)
print(type(key2), key2)

quandl.ApiConfig.api_key = key
data = quandl.get('BCHARTS/BITFLYERUSD',
                  start_date='2020-03-07', end_date='2020-03-07')

print(data)
