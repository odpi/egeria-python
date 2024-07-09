#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Display the status of cataloged platforms and servers.
"""
import json
import sys
import time
import argparse
from confluent_kafka import Consumer, KafkaException


from rich.table import Table
from rich.live import Live
from rich.console import Console
from rich.markdown import Markdown

from pyegeria import RuntimeManager

disable_ssl_warnings = True
console = Console(width=200)


from confluent_kafka import Consumer, KafkaException

# Define the Kafka consumer configuration.
config = {
    'bootstrap.servers': 'localhost:9092',  # replace with your Kafka broker(s)
    'group.id': "w4",  # replace with your consumer group
    'auto.offset.reset': 'earliest'  # can be set to 'earliest' or 'latest'
}

# Initialize a Kafka consumer.
consumer = Consumer(config)

# Subscribe to a Kafka topic.
consumer.subscribe(['egeria.omag.server.active-metadata-store.omas.assetconsumer.outTopic'])  # replace with your Kafka topic

try:
    while True:
        msg = consumer.poll(1.0)  # timeout set to 1 second

        if msg is None:
            continue
        elif msg.error():
            raise KafkaException(msg.error())
        else:
            event = json.loads(msg.value())
            event_time = event["eventTime"]
            event_type = event["eventType"]
            guid = event["elementHeader"]["guid"]

            type_name = event["elementHeader"]["type"]["typeName"]
            origin = event["elementHeader"]["origin"]["sourceServer"]
            # classifications = event['elementHeader']["classifications"]
            # classification_md = ""
            # for c in classifications:
            #     cp = c.get("classificationProperties", None)
            #     if cp is not None:
            #         cl_name = c["classificationProperties"].get("name", None)
            #         cl = cl_name if not None else c["classificationName"]
            #         classification_md += f"* classifications: {cl}\n"

            element_properties = event["elementProperties"]
            element_properties_keys = element_properties.keys()
            props = " "
            for key in element_properties_keys:
                value = element_properties[key]
                props += f"* {key}: {value}\n"
            console.rule(style= "[bold red]")
            console.rule(f"\tMessage TimeStamp: {event_time}\t eventType: {event_type}\t typeName: {type_name}\t guid: {guid}")
            msg = (
                      # f"classifications: \n{classification_md}\n"
                      f"properties: \n{props}\n\n")
            msg = Markdown(msg)
            # msg = json.dumps(event, indent=4)
            console.print(msg)
finally:
    # Close down consumer to commit final offsets.
    consumer.close()
