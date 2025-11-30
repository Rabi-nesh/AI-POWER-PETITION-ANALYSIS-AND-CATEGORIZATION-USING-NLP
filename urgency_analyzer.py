def detect_urgency(text):
    if not text:
        return 0
    keywords = ["urgent", "immediately", "important", "emergency", "critical"]
    count = sum(1 for word in keywords if word in text.lower())
    return count
