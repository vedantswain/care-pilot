import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from random import shuffle

# a lexicon and rule-based sentiment
nltk.download('vader_lexicon') 
# initialize it
sia = SentimentIntensityAnalyzer()

# categorize sentiment into 7 levels，  it can range from -1 to 1.
def get_sentiment_category(score):
    """Categorize sentiment score into a 7-point scale."""
    if score >= 0.75:
        return "Very Positive"
    elif score >= 0.5:
        return "Positive"
    elif score >= 0.25:
        return "Slightly Positive"
    elif score > -0.25:
        return "Neutral"
    elif score > -0.5:
        return "Slightly Negative"
    elif score > -0.75:
        return " Negative"
    else:
        return "Very Negative"
    
# analyze the last response from client
def analyze_sentiment(client_latest_response):
    """Analyze sentiment of a given text and return the sentiment category."""
    score = sia.polarity_scores(client_latest_response)["compound"]
    return get_sentiment_category(score)

# if __name__ == "__main__":
#     client_latest_response = "I am so upset and I hate your service!"
#     print(f"Text: {client_latest_response}\nSentiment: {analyze_sentiment(client_latest_response)}")


