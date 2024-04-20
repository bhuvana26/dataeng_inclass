import json
import logging
import pandas as pd
import requests
import base64
from google.cloud import pubsub_v1
import time 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_id = "dataeng-project-420102"
topic_id = "my-topic"
topic_path = f"projects/{project_id}/topics/{topic_id}"
publisher = pubsub_v1.PublisherClient()
processed_vehicle_ids = set()

def get_vehicle_ids(filename, column_name):
    df = pd.read_csv(filename)
    return df[column_name].tolist()

def get_response(vehicle_id):
    url = f"https://busdata.cs.pdx.edu/api/getBreadCrumbs?vehicle_id={vehicle_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.status_code, response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data for vehicle ID {vehicle_id}: {e}")
        return None, None

def publish_to_pubsub(vehicle_id, content):
    try:
        message_data = json.dumps(content).encode("utf-8")
        encoded_message_data = base64.b64encode(message_data)
        future = publisher.publish(topic_path, data=encoded_message_data, vehicle_id=str(vehicle_id))
        future.result()  # Block until the message is published
        logger.info(f"Published message for vehicle ID: {vehicle_id}")
        time.sleep(0.25)  # Add 250 milliseconds sleep
    except Exception as e:
        logger.error(f"Error publishing message for vehicle ID {vehicle_id}: {e}")

def main():
    filename = 'vehicle_ids - Sheet1.csv'
    column_name = 'Quest'
    vehicle_ids = get_vehicle_ids(filename, column_name)
    
    # Take only the two vehicle IDs
    vehicle_ids = vehicle_ids[:2]

    if not vehicle_ids:
        logger.warning("No vehicle IDs found in CSV file.")
        return

    for vehicle_id in vehicle_ids:
        if vehicle_id in processed_vehicle_ids:
            logger.info(f"Data for vehicle ID {vehicle_id} has already been sent. Skipping.")
            continue

        status_code, content = get_response(vehicle_id)
        if status_code == 200 and content:
            logger.info(f"Vehicle ID: {vehicle_id}, Response Status: {status_code}")
            logger.info(f"Raw data for vehicle ID {vehicle_id}: {content}")
            publish_to_pubsub(vehicle_id, content)  # Publish entire content for the vehicle ID
            processed_vehicle_ids.add(vehicle_id)  # Mark vehicle ID as processed
        else:
            logger.warning(f"Failed to fetch data for vehicle ID {vehicle_id}. Status Code: {status_code}")

if __name__ == "__main__":
    main()
