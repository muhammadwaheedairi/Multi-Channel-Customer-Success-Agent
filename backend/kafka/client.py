from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from kafka.topics import TOPICS
import json
import structlog

logger = structlog.get_logger()
KAFKA_BOOTSTRAP = "localhost:9092"

class FTEProducer:
    def __init__(self):
        self._producer = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()
        logger.info("kafka_producer_started")

    async def stop(self):
        if self._producer:
            await self._producer.stop()

    async def publish(self, topic: str, event: dict):
        try:
            await self._producer.send_and_wait(topic, event)
            logger.info("kafka_published", topic=topic)
        except Exception as e:
            logger.error("kafka_publish_failed", error=str(e))

class FTEConsumer:
    def __init__(self, topics: list, group_id: str):
        self._consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
        )

    async def start(self):
        await self._consumer.start()
        logger.info("kafka_consumer_started")

    async def stop(self):
        await self._consumer.stop()

    async def consume(self, handler):
        async for msg in self._consumer:
            try:
                await handler(msg.topic, msg.value)
            except Exception as e:
                logger.error("kafka_consume_error", error=str(e))
