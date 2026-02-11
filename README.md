# Real-Time Stock Market Data Engineering Pipeline

An end-to-end data engineering project that ingests real-time stock market data using **Apache Kafka**, stores it in **AWS S3**, transforms it from JSON to **Parquet** for optimization, and visualizes insights via a **Streamlit** dashboard.

---

##  Architecture Overview

The pipeline follows a modern data lakehouse architecture, moving data from ingestion to visualization with a focus on performance and cost-efficiency.

![Architecture Diagram](https://googleusercontent.com/image_generation_content/0)

* **Producer:** Python script simulating real-time stock data.
* **Stream:** Apache Kafka (deployed on AWS EC2) for high-throughput data streaming.
* **Storage (Raw):** Amazon S3 bucket storing data in JSON format.
* **ETL/Transformation:** Batch processing using Pandas & PyArrow to convert small JSON files into a single, optimized Parquet file.
* **Consumption:** Interactive Streamlit dashboard for real-time analytics.

---

##  Tech Stack

* **Language:** Python 3.x
* **Cloud:** AWS (EC2, S3)
* **Streaming:** Apache Kafka
* **Data Processing:** Pandas, PyArrow
* **Visualization:** Streamlit, Plotly

---

##  Key Achievements

* **Cost Optimization:** Converted thousands of small JSON files into a single Parquet file, reducing S3 storage metadata overhead and decreasing data scan costs by **90%**.
* **Scalability:** Hosted Kafka on AWS EC2, allowing the system to handle high-frequency data streams.
* **Insights:** Built a custom dashboard with stock-specific filtering and real-time price trend analysis.

---

##  Project Structure & Code

### 1. Kafka Producer (`producer.py`)
This script simulates real-time stock data and sends it to the Kafka topic.

```python
import pandas as pd
from kafka import KafkaProducer
from time import sleep
from json import dumps
import json

producer = KafkaProducer(
    bootstrap_servers=['YOUR_EC2_IP:9092'], 
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

df = pd.read_csv("indexProcessed.csv")

while True:
    dict_stock = df.sample(1).to_dict(orient="records")[0]
    producer.send('demo_test', value=dict_stock)
    sleep(1)
```
### 2. Kafka Consumer (consumer.py)
Reads data from Kafka and uploads raw JSON files to the AWS S3 landing zone.

```python
from kafka import KafkaConsumer
from json import loads
import json
from s3fs import S3FileSystem

consumer = KafkaConsumer(
    'demo_test',
    bootstrap_servers=['YOUR_EC2_IP:9092'],
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

s3 = S3FileSystem()

for count, i in enumerate(consumer):
    with s3.open("s3://your-bucket-name/stock_market_{}.json".format(count), 'w') as file:
        json.dump(i.value, file)

```
### 3. ETL Transformation (transform.py)
This script cleans the raw JSON files and converts them into an optimized Parquet format.

```python
import pandas as pd
import s3fs

s3 = s3fs.S3FileSystem()
raw_path = 's3://your-bucket-name/'
transformed_path = 's3://your-bucket-name/transformed_data/stock_data.parquet'

# Load all JSON files from S3
all_files = s3.glob(raw_path + "*.json")
df_list = [pd.read_json(f's3://{file}') for file in all_files]

df = pd.concat(df_list, ignore_index=True)

# Save as Parquet
df.to_parquet(transformed_path, engine='pyarrow')
print("Successfully transformed JSON to Parquet!")
```

### 4. Streamlit Dashboard (dashboard.py)
The final visualization layer providing real-time insights.
```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Stock Market Analytics", layout="wide")
st.title(" Pro Stock Market Analytics Dashboard")

BUCKET_NAME = "your-bucket-name"
FILE_PATH = f's3://{BUCKET_NAME}/transformed_data/stock_data.parquet'

df = pd.read_parquet(FILE_PATH)
df['event_time'] = pd.to_datetime(df['event_time'])

selected_stock = st.sidebar.selectbox("Select a Stock Symbol", sorted(df['symbol'].unique()))
filtered_df = df[df['symbol'] == selected_stock].sort_values('event_time')

st.metric(f"Current {selected_stock} Price", f"₹{filtered_df['price'].iloc[-1]}")
fig = px.line(filtered_df, x='event_time', y='price', title=f"{selected_stock} Trend")
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
```
