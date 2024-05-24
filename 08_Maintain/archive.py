import os
import base64
import json
from google.cloud import pubsub_v1
from google.cloud import storage

project_id = "dataeng-project-420102"
subscription_id = "archivetest-sub"
bucket_name = "singlebus"  # Update this with your actual bucket name
output_file_name = "all_data.json"  # Name of the output file

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
storage_client = storage.Client()

# Global list to collect data
all_data = []

def upload_to_gcs(bucket_name, destination_blob_name, data):
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(data, content_type='application/json')
        print(f"Saved data to {bucket_name}/{destination_blob_name}")
    except Exception as e:
        print(f"Failed to upload to GCS: {e}")

def callback(message):
    global all_data
    try:
        data = base64.b64decode(message.data)
        data_json = json.loads(data)
        
        # Collect data from the message
        all_data.append(data_json)
        
        message.ack()
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    global all_data
    
    subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    print("Press Ctrl+C to exit")
    try:
        while True:
            continue
    except KeyboardInterrupt:
        subscriber.close()
        print("Subscriber stopped.")
        
        # After stopping the subscriber, upload the collected data to GCS
        json_data = json.dumps(all_data, indent=4)
        upload_to_gcs(bucket_name, output_file_name, json_data)

if __name__ == "__main__":
    main()
