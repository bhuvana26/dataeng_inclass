from google.cloud import pubsub_v1
project_id = "dataeng-project-420102"
topic_name = "my-topic"
subscription_name = "my-sub"
sub = pubsub_v1.SubscriberClient()
topic_path = sub.topic_path(project_id, topic_name)
subscription_path = sub.subscription_path(project_id, subscription_name)
subscription = sub.create_subscription(request={"name": subscription_path, "topic": topic_path})

print(f"Subscription '{subscription_path}' is created for the topic '{topic_path}'.")
