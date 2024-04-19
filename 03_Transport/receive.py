import os
import json
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1

# Set the directory to save JSON files
data_directory = "data"

# Ensure the data directory exists
os.makedirs(data_directory, exist_ok=True)

# TODO(developer)
project_id = "dataeng-project-420102"
subscription_id = "my-sub"
# Number of seconds the subscriber should listen for messages
timeout = 5.0

subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    message_data = message.data.decode("utf-8")
    message_attributes = dict(message.attributes)
    message_id = message.message_id
    message_info = {
        "data": message_data,
        "attributes": message_attributes,
        "message_id": message_id
    }

    # Generate a unique filename for each message
    filename = os.path.join(data_directory, f"{message_id}.json")

    # Write message info to a JSON file
    with open(filename, "w") as file:
        json.dump(message_info, file)

    # Acknowledge the message
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        streaming_pull_future.result(timeout=timeout)
    except TimeoutError:
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.
