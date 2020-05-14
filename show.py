import json
import time
import pymongo
import pandas as pd
import plotly.express as px


with open('config.json', encoding='utf-8') as config_file:
    config = json.load(config_file)

myDB_Client = pymongo.MongoClient(
    'mongodb://%s:%s@%s/' % (config['database_user'],
                             config['database_password'],
                             config['database_address'])
)

myDatabase = myDB_Client['homeMac_usage']
usageDB = myDatabase.usage
data = usageDB.find()
# data = list(data)  # 在转换成列表时，可以根据情况只过滤出需要的数据。(for遍历过滤)
df = []
for row in data:
    for i in row['programs']:
        row_data = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row['timestamp'])),
                    i['program'],
                    i['cpu']]
        df.append(row_data)

# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
df = pd.DataFrame(df, columns=['time', 'command', 'cpu'])  # 读取整张表 (DataFrame)
print(df)
fig = px.scatter(df, x="time", y="cpu", color='command', size='cpu')
fig.show()
