import os
import base64
import json
from google.cloud import pubsub_v1

# Google Cloud project and subscription information
project_id = "dataeng-project-420102"
subscription_id = "my-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Create the "data" directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

def callback(message):
    try:
        vehicle_id = message.attributes['vehicle_id']
        data = base64.b64decode(message.data)
        data_json = json.loads(data)
        
        # Save JSON data to a file in the "data" directory
        file_path = os.path.join("data", f"{vehicle_id}.json")
        with open(file_path, "w") as json_file:
            json.dump(data_json, json_file, indent=4)
            print(f"Saved data for vehicle {vehicle_id} to {file_path}")
        
        message.ack()
    except Exception as e:
        print(f"Error processing message: {e}")

subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

# Keep the main thread alive
print("Press Ctrl+C to exit")
try:
    while True:
        continue
except KeyboardInterrupt:
    subscriber.close()