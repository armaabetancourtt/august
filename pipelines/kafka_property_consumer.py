"""Kafka ingestion demonstrator for property event JSONL landing."""
import argparse
import json


def consume(consumer, output, limit=100):
    count = 0
    with open(output, "a", encoding="utf8") as out:
        for record in consumer:
            try:
                obj = json.loads(record.value.decode("utf8"))
                if not all(
                    k in obj
                    for k in ("event_id", "property_id", "occurred_at", "amount", "event_type")
                ):
                    continue
                out.write(json.dumps(obj, sort_keys=True) + "\n")
                out.flush()
                consumer.commit()
                count += 1
                if count >= limit:
                    break
            except (UnicodeDecodeError, ValueError, TypeError):
                continue
    return count


def main():
    from kafka import KafkaConsumer

    parser = argparse.ArgumentParser()
    parser.add_argument("--brokers", default="localhost:9092")
    parser.add_argument("--topic", default="august.property.events")
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    consumer = KafkaConsumer(
        args.topic,
        bootstrap_servers=args.brokers.split(","),
        group_id="august-landing",
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    try:
        print(consume(consumer, args.output, args.limit))
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
