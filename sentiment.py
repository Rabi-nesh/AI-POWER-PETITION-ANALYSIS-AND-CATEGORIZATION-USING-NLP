from textblob import TextBlob

def analyze_sentiment(text):
    if not text:
        return "Neutral"
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.2:
        return "Positive"
    elif polarity < -0.2:
        return "Negative"
    else:
        return "Neutral"
