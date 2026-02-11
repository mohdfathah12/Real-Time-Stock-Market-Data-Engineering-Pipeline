import json
import time
import uuid
import pandas as pd
from kafka import KafkaProducer
from datetime import datetime

from config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_NAME, SLEEP_SECONDS
from logger import get_logger

logger = get_logger("KafkaProducer")

def run_producer():
    logger.info("Starting Kafka Producer")
    df = pd.read_csv("C:/Users/User/Desktop/PythonProject Kafka stock market/data/nse_all_stock_data_clean.csv")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        api_version=(0, 10, 2),
        acks='all'
    )
    for _, row in df.iterrows():
        event = {"event_id": str(uuid.uuid4()),
                 "event_time": datetime.utcnow().isoformat(),
                 "stock_date": row["Date"],
                 "symbol": row["symbol"],
                 "price": float(row["price"])}
        producer.send(TOPIC_NAME, value=event)
        logger.info(f"Sent event: {event}")
        time.sleep(SLEEP_SECONDS)
    producer.flush()
    logger.info(f"Producer finished streaming")
if __name__ == "__main__":
    run_producer()


