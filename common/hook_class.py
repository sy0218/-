#!/usr/bin/python3
from confluent_kafka import Producer
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro

import redis

import psycopg2
from psycopg2.extras import execute_values

class KafkaHook:
    """
       Kafka 연결/해제 및 메서드 제공
    """
    # 생성자는 브로커 정보만 관리
    def __init__(self, brokers):
        self.brokers = brokers
        self.conn = None

    # 일반 kafka 프로듀서
    def connect(self, **configs):
        conf = {
            "bootstrap.servers": self.brokers,
            **configs
        }
        self.conn = Producer(conf)

    # Avro Kafka 프로듀서
    def avro_connect(self, schema_registry_url, schema_path, **configs):
        avro_schema = avro.load(schema_path)
        conf = {
            "bootstrap.servers": self.brokers,
            "schema.registry.url": schema_registry_url,
            **configs
        }

        self.conn = AvroProducer(
            conf,
            default_value_schema = avro_schema
        )

    # 프로듀서 버퍼에 남은 메시지 모두 전송
    def flush(self, timeout=10):
        if self.conn:
            self.conn.flush(timeout)

    def __getattr__(self, name):
        return getattr(self.conn, name)


class RedisHook:
    """
        Redis 연결/해제 및 메서드 제공
    """
    def __init__(self, host, port, db, password):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.conn = None

    def connect(self):
        self.conn = redis.Redis(
            host = self.host,
            port = self.port,
            db = self.db,
            password = self.password
        )

    def close(self):
        if self.conn:
            self.conn.close()

    def __getattr__(self, name):
        return getattr(self.conn, name)


class PostgresHook:
    """
        PostgreSQL 연결 및 CRUD 메서드 제공
    """
    def __init__(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            host = self.host,
            port = self.port,
            dbname = self.dbname,
            user = self.user,
            password = self.password
        )

    def close(self):
        if self.conn:
            self.conn.close()

    def __getattr__(self, name):
        return getattr(self.conn, name)
