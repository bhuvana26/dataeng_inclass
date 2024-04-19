from google.cloud import pubsub_v1
project_id = "dataeng-project-420102"
topic_name = "my-topic"
subscription_name = "my-sub_1"
subscriber = pubsub_v1.SubscriberClient()
topic_path = subscriber.topic_path(project_id, topic_name)
subscription_path = subscriber.subscription_path(project_id, subscription_name)
subscription = subscriber.create_subscription(request={"name": subscription_path, "topic": topic_path})

print(f"Subscription '{subscription_path}' has been created for topic '{topic_path}'.")