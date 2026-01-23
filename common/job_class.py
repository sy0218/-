#!/usr/bin/python3
import os, configparser, random, hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Get_env:
    @staticmethod
    def _collector():
        return {
            "config_path": os.environ["COLLECTOR_CONFIG_PATH"],
            "stop_dir": os.environ["COLLECTOR_STOP_DIR"],
            "stop_file": os.environ["COLLECTOR_STOP_FILE"]
        }

    @staticmethod
    def _redis():
        return {
            "redis_host": os.environ["REDIS_HOST"],
            "redis_port": os.environ["REDIS_PORT"],
            "redis_db": os.environ["REDIS_DB"],
            "redis_password": os.environ["REDIS_PASSWORD"],
            "redis_jobhead_key": os.environ["REDIS_JOBHEAD_KEY"]
        }

    @staticmethod
    def _kafka():
        return {
            "kafka_host": os.environ["KAFKA_HOST"],
            "schema_registry": os.environ["SCHEMA_REGISTRY"],
            "job_topic": os.environ["JOB_TOPIC"]
        }

    @staticmethod
    def _postgres():
        return {
            "pg_host": os.environ["POSTGRESQL_HOST"],
            "pg_port": os.environ["POSTGRESQL_PORT"],
            "pg_db": os.environ["POSTGRESQL_DB"],
            "pg_user": os.environ["POSTGRESQL_USER"],
            "pg_password": os.environ["POSTGRESQL_PASSWORD"]
        }


class Get_properties:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.optionxform = str
        self.config.read(config_path)

    def __getitem__(self, section):
        return self.config[section]

class StopChecker:
    @staticmethod
    def _job_stop(stop_dir, stop_file):
        stop_path = os.path.join(stop_dir, stop_file)
        return os.path.exists(stop_path)

class DataPreProcessor:
    @staticmethod
    def _hash(data):
        """
            data를 SHA1 해시로 변경
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
