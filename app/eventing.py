from datetime import datetime

analytics_events = []
webhook_events = []

def record_event(event_type, data):
    event = {"event_type": event_type, "data": data, "timestamp": datetime.utcnow().isoformat()}
    analytics_events.append(event)
    return event

def trigger_event(event_type, payload):
    event = {"event_type": event_type, "payload": payload, "timestamp": datetime.utcnow().isoformat()}
    webhook_events.append(event)
    return event
