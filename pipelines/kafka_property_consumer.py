"""Kafka -> JSONL durable landing zone. Opt-in local demonstrator, not production service."""
import argparse
import json
from pathlib import Path
def consume(consumer,output,limit=100):
    count=0
    with open(output,"a",encoding="utf8") as out:
        for record in consumer:
            try:
                obj=json.loads(record.value.decode("utf8"))
                if not all(k in obj for k in ("event_id","property_id","occurred_at","amount","event_type")):
                    continue
                out.write(json.dumps(obj,sort_keys=True)+"\n")
                out.flush()
                consumer.commit()
                count+=1
                if count>=limit:break
            except (UnicodeDecodeError,ValueError,TypeError):
                continue
    return count
def main():
    from kafka import KafkaConsumer
    p=argparse.ArgumentParser()
    p.add_argument("--brokers",default="localhost:9092")
    p.add_argument("--topic",default="august.property.events")
    p.add_argument("--output",required=True)
    p.add_argument("--limit",type=int,default=100)
    a=p.parse_args()
    consumer=KafkaConsumer(a.topic,bootstrap_servers=a.brokers.split(","),
       group_id="august-landing",enable_auto_commit=False,auto_offset_reset="earliest")
    try:print(consume(consumer,a.output,a.limit))
    finally:consumer.close()
if __name__=="__main__":main()
