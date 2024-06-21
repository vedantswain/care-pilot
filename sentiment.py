'''
Sentiment analysis using two different approaches.
Approach 1: NLTK (traditional)
Approch 2: Transformers (Hugging-Face)
Approch 3: TextBlob
'''
from transformers import pipeline
from textblob import TextBlob

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('vader_lexicon')
nltk.download('punkt')

sentiment_analysis = pipeline("sentiment-analysis")

def get_sentiment_category_transformer(score, label):
    """Categorize sentiment based on score and label."""
    if label == "POSITIVE":
        if 0.75 < score <= 1:
            return "Very Positive"
        elif 0.5 < score <= 0.75:
            return "Positive"
        elif 0.25 < score <= 0.5:
            return "Slightly Positive"
        elif 0 < score <= 0.25:
            return "Neutral"
    else:  
        if 0.75 < score <= 1:
            return "Very Negative"
        elif 0.5 < score <= 0.75:
            return "Negative"
        elif 0.25 < score <= 0.5:
            return "Slightly Negative"
        elif 0 < score <= 0.25:
            return "Neutral"
    return "Neutral"

def analyze_sentiment_transformer(client_latest_response):
    """Analyze sentiment using transformers and return the sentiment category."""
    result = sentiment_analysis(client_latest_response)
    sentiment_score = result[0]['score']
    sentiment_label = result[0]['label']
    sentiment_category = get_sentiment_category_transformer(sentiment_score, sentiment_label)
    return sentiment_category

# client_latest_response = "Well, you better make it quick! And it better be the best room you have, or there will be even more complaints coming your way."
# print(analyze_sentiment(client_latest_response))

# client_latest_response = "Oh, you \"hear\" me? That's just great. Listening is one thing, but I want action, not just words! What are you going to do about it?."
# print(analyze_sentiment(client_latest_response))





sia = SentimentIntensityAnalyzer()

# categorize sentiment into 7 levels，  it can range from -1 to 1.
def get_sentiment_category_nltk(score):
    """Categorize sentiment score into a 7-point scale with equal intervals."""
    if 1 >= score > 0.714:
        return "Very Positive"
    elif 0.714 >= score > 0.428:
        return "Positive"
    elif 0.428 >= score > 0.142:
        return "Slightly Positive"
    elif 0.142 >= score > -0.142:
        return "Neutral"
    elif -0.142 >= score > -0.428:
        return "Slightly Negative"
    elif -0.428 >= score > -0.714:
        return "Negative"
    else:
        return "Very Negative"
    
# analyze the last response from client
def analyze_sentiment_nltk(client_latest_response):
    """Analyze sentiment of a given text and return the sentiment category."""
    score = sia.polarity_scores(client_latest_response)["compound"]
    return get_sentiment_category_nltk(score)




def analyze_sentiment_textblob(client_latest_response):
    """Analyze sentiment using TextBlob and return sentiment category."""
    blob = TextBlob(client_latest_response)
    sentiment = blob.sentiment
    sentiment_category = get_sentiment_category_nltk(sentiment.polarity)
    return sentiment_category

# if __name__ == "__main__":
#     client_latest_response = "Sorry? That's all you've got? A simple \"sorry\" won't fix the mess of a stay I had. What are you going to do about it?"
#     sentiment_data = analyze_sentiment(client_latest_response)
#     print(f"Text: {client_latest_response}\nSentiment Data: {sentiment_data}")

''' 
I couldn't find specific theories about the range of scores, 
but transformers can mainly identify positive, neutral, and negative sentiments. 
To increase the diversity of my evaluation, I added the following code:
'''
def analyze_sentiment_decision(client_latest_response):
    """Analyze sentiment and decide based on conditions."""
    textblob_result = analyze_sentiment_textblob(client_latest_response)
    transformers_result = analyze_sentiment_transformer(client_latest_response)

    if "Negative" in textblob_result and "Negative" in transformers_result:
        return textblob_result
    elif "Neutral" in textblob_result:
        return textblob_result
    else:
        return transformers_result

# if __name__ == "__main__":
#     test_queries = [
#         "Sorry? That's all you've got? A simple \"sorry\" won't fix the mess of a stay I had. What are you going to do about it?",
#         "Oh, you \"hear\" me? That's just great. Listening is one thing, but I want action, not just words! What are you going to do about it?",
#         "Well, you better make it quick! And it better be the best room you have, or there will be even more complaints coming your way.",
#         "The room that I booked at your hotel was not what was advertised. It was dirty and had a musty smell. I am very disappointed and will not be staying here again.",
#         "I appreciate your apology. Could you please let me know what steps can be taken to address this issue?",
#         "Thank you for offering to switch me to a clean room. Can you ensure that the new room will be in a better condition than the first one?",
#         "That sounds great, thank you. Could you also let me know how long it will take to prepare the new room?",
#         "I understand it may take some time, but spending the entire day waiting for a new room is quite inconvenient. Is there any way to expedite this process, or perhaps offer some form of compensation for the inconvenience caused?",
#         "That would be appreciated. What form of compensation are you considering?"
#     ]

#     for query in test_queries:
#         print(query)
#         print("NLTK:", analyze_sentiment_nltk(query))
#         print("TextBlob:", analyze_sentiment_textblob(query))
#         print("Transformers:", analyze_sentiment_transformer(query))
#         print("FinalDecision:", analyze_sentiment_decision(query))
#         print()