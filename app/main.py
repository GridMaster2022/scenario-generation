import logging
import os
import sys
from signal import signal, SIGINT
import time
import boto3
import json
import os
from copy import deepcopy

from esdl_generator import generate_esdl
from credentials import get_secret
from rds_handler import SqlHandler
from helper import *
from config import *

if logging.getLogger().hasHandlers():
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO,
                        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")

s3_client = boto3.client('s3')
tmp_file = 'tmp/tmp.esdl'


def handler(signal_received, frame):
    logging.info('SIGINT or CTRL-C detected. Exiting gracefully')
    sys.exit(0)


def main(db_secret):
    total_timeout_time = 0
    sql_handler = SqlHandler(db_secret)
    while True:
        body, receipt_handle = get_message_from_queue(esdl_gen_queue_url)
        if not body:
            # There is no message in the queue, wait and try again
            logging.info('Queue is empty, waiting for 5 seconds')
            time.sleep(5)
            if total_timeout_time > container_timeout:
                # If no messages received for timeout limit, exit container/loop
                logging.info('Container timeout exceeded, shutting down')
                break
            total_timeout_time += 5
            continue
        total_timeout_time = 0
        logging.info('Starting new scenario generation for UUID: {}'.format(body['scenarioUuid']))
        # Load scenario json
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=body['scenarioJsonLocation']
        )
        scenario_params = json.load(response['Body'])
        # Generate ESDL's based on scenario_json
        generate_esdl(body['scenarioUuid'], scenario_params, body['bucketName'])
        # Update scenario DB
        with open('sql/update_scenario.sql', 'r') as f:
            sql_stmt = f.read()
        sql_handler.update_scenario_state(sql_stmt, [body])
        delete_message_from_queue(ESDL_QUEUE_URL, receipt_handle)
        push_message_to_next_queue(INIT_QUEUE_URL, body)
        logging.info('Finished scenario generation for UUID: {}'.format(body['scenarioUuid']))


if __name__ == '__main__':
    secret = get_secret(DATABASE_SECRET_NAME)
    signal(SIGINT, handler)
    main(secret)
