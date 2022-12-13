import pandas as pd
def model():
    file_path = '/home/paritosh/My-Projects/amazon-price-tracker/Data/files/2022-11-29-15-06-50/Data.json'
    df = pd.read_json(file_path)
    data = []
    for i in range(len(df)):
        for j in range(len(df[i])):
            data.append(df[i][j])
    
    df = pd.DataFrame(data)
    print(df.head())


model()