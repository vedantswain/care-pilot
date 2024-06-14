from transformers import pipeline

sentiment_analysis = pipeline("sentiment-analysis")

def get_sentiment_category(score, label):
    """Categorize sentiment based on score and label."""
    if label == "POSITIVE":
        if score > 0.85:
            return "Very Positive"
        elif score > 0.70:
            return "Positive"
        elif score > 0.55:
            return "Slightly Positive"
        elif score >= 0.45:
            return "Neutral"
    else:  
        if score > 0.85:
            return "Very Negative"
        elif score > 0.70:
            return "Negative"
        elif score > 0.55:
            return "Slightly Negative"
        elif score >= 0.45:
            return "Neutral"
    return "Neutral"

def analyze_sentiment(client_latest_response):
    """Analyze sentiment using transformers and return the sentiment category."""
    result = sentiment_analysis(client_latest_response)
    sentiment_score = result[0]['score']
    sentiment_label = result[0]['label']
    sentiment_category = get_sentiment_category(sentiment_score, sentiment_label)
    return sentiment_category

# client_latest_response = "Well, you better make it quick! And it better be the best room you have, or there will be even more complaints coming your way."
# print(analyze_sentiment(client_latest_response))

# client_latest_response = "Oh, you \"hear\" me? That's just great. Listening is one thing, but I want action, not just words! What are you going to do about it?."
# print(analyze_sentiment(client_latest_response))



# import nltk
# from nltk.sentiment import SentimentIntensityAnalyzer
# from random import shuffle
# from textblob import TextBlob
# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download('vader_lexicon')
# nltk.download('punkt') 

# sia = SentimentIntensityAnalyzer()

# # categorize sentiment into 7 levels，  it can range from -1 to 1.
# def get_sentiment_category(score):
#     """Categorize sentiment score into a 7-point scale."""
#     if score >= 0.75:
#         return "Very Positive"
#     elif score >= 0.5:
#         return "Positive"
#     elif score >= 0.25:
#         return "Slightly Positive"
#     elif score > -0.25:
#         return "Neutral"
#     elif score > -0.5:
#         return "Slightly Negative"
#     elif score > -0.75:
#         return " Negative"
#     else:
#         return "Very Negative"
    
# # analyze the last response from client
# def analyze_sentiment(client_latest_response):
#     """Analyze sentiment of a given text and return the sentiment category."""
#     score = sia.polarity_scores(client_latest_response)["compound"]
#     return get_sentiment_category(score)

# if __name__ == "__main__":
#     client_latest_response = "Sorry? That's all you've got? A simple \"sorry\" won't fix the mess of a stay I had. What are you going to do about it?"
#     print(f"Text: {client_latest_response}\nSentiment: {analyze_sentiment(client_latest_response)}")


# from textblob import TextBlob
# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# # -1 ≤ polarity ≤ 1
# def get_sentiment_category(score):
#     """Categorize sentiment based on polarity score into seven levels."""
#     if score > 0.5:
#         return "Very Positive"
#     elif score > 0.2:
#         return "Positive"
#     elif score > 0:
#         return "Slightly Positive"
#     elif score == 0:
#         return "Neutral"
#     elif score > -0.2:
#         return "Slightly Negative"
#     elif score > -0.5:
#         return "Negative"
#     else:
#         return "Very Negative"


# def analyze_sentiment(client_latest_response):
#     """Analyze sentiment using TextBlob and return sentiment category."""
#     blob = TextBlob(client_latest_response)
#     sentiment = blob.sentiment
#     sentiment_category = get_sentiment_category(sentiment.score)
#     return sentiment_category

# if __name__ == "__main__":
#     client_latest_response = "Sorry? That's all you've got? A simple \"sorry\" won't fix the mess of a stay I had. What are you going to do about it?"
#     sentiment_data = analyze_sentiment(client_latest_response)
#     print(f"Text: {client_latest_response}\nSentiment Data: {sentiment_data}")



