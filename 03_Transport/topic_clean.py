from google.cloud import pubsub_v1
project_id = "dataeng-project-420102"
topic_name = "my-topic"
subscriber = pubsub_v1.SubscriberClient()
topic_path = subscriber.topic_path(project_id, topic_name)
subscriptions = subscriber.list_subscriptions(project=f"projects/{project_id}")
for subscription in subscriptions:
    if topic_path in subscription.topic:
        subscription_path = subscription.name
        subscriber.delete_subscription(request={"subscription": subscription_path})
        print(f"All messages have been deleted in subscription '{subscription_path}'.")

print(f"All messages have been deleted in topic '{topic_path}'.")
