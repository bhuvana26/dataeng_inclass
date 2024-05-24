import os
import base64
import json
import zlib
from google.cloud import pubsub_v1
from google.cloud import storage
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Generate RSA keys (this should ideally be done once and stored securely)
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Load the RSA keys from a file or define them in the script
private_key, public_key = generate_rsa_keys()

# You can save and load the keys using the following functions (not used in this script)
def save_private_key(private_key, filename):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filename, 'wb') as pem_out:
        pem_out.write(pem)

def load_private_key(filename):
    with open(filename, 'rb') as pem_in:
        private_key = serialization.load_pem_private_key(
            pem_in.read(),
            password=None,
        )
    return private_key

def save_public_key(public_key, filename):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filename, 'wb') as pem_out:
        pem_out.write(pem)

def load_public_key(filename):
    with open(filename, 'rb') as pem_in:
        public_key = serialization.load_pem_public_key(
            pem_in.read()
        )
    return public_key

# Project and GCS configuration
project_id = "dataeng-project-420102"
subscription_id = "archivetest-sub"
bucket_name = "singlebus"  # Update this with your actual bucket name
output_file_name = "all_data.json.gz.enc"  # Name of the output file with .enc extension

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
storage_client = storage.Client()

# Global list to collect data
all_data = []

def upload_to_gcs(bucket_name, destination_blob_name, data):
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(data, content_type='application/octet-stream')
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
        
        # Compress the JSON data using zlib
        compressed_data = zlib.compress(json_data.encode('utf-8'))
        
        # Encrypt the compressed data using RSA
        encrypted_data = public_key.encrypt(
            compressed_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Upload the encrypted data to GCS
        upload_to_gcs(bucket_name, output_file_name, encrypted_data)

if __name__ == "__main__":
    main()
