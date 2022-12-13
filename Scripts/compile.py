# get all the files from /home/paritosh/My-Projects/amazon-price-tracker/Data/files
import os 
import glob
import json
import pandas as pd
import numpy as np
import sys
import datetime
# get data file names


def compile_data(stamp_date):
    path = r'/home/paritosh/My-Projects/amazon-price-tracker/Data/files/{}/'.format(stamp_date) # use your path
    all_files = glob.glob(path + "/*.json")
    list = []
    for filename in all_files:
        with open(filename) as f:
            data = json.load(f)
            list.append(data)

    with open('Data/files/{}/'.format(stamp_date) + 'Data.json', mode='w') as f:
        json.dump(list, f)

