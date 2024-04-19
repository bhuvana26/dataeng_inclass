from google.cloud import pubsub_v1
project_id = "dataeng-project-420102"
topic_name = "my-topic"
sub = pubsub_v1.SubscriberClient()
topic_path = sub.topic_path(project_id, topic_name)
subscriptions = sub.list_subscriptions(project=f"projects/{project_id}")
for subscription in subscriptions:
    if topic_path in subscription.topic:
        sub_path = subscription.name
        sub.delete_subscription(request={"subscription": sub_path})
        print(f"All messages have been deleted in subscription '{sub_path}'.")

print(f"All messages have been deleted in topic '{topic_path}'.")
