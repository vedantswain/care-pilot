'''
A single file for string literals that are being used across files.
This ensures that we only need to make changes in one location to reflect it across multiple scripts.
Reduces risk of errors when changing code or introducing new types.
'''

TYPE_EMO_THOUGHT = "You might be thinking"
TYPE_EMO_SHOES = "Put Yourself in the Client's Shoes"
TYPE_EMO_REFRAME = "Be Mindful of Your Emotions"
TYPE_SENTIMENT = "Client's Sentiment"

SUPPORT_TYPE_STRINGS = {
    "TYPE_EMO_THOUGHT" : TYPE_EMO_THOUGHT,
    "TYPE_EMO_SHOES" : TYPE_EMO_SHOES,
    "TYPE_EMO_REFRAME" : TYPE_EMO_REFRAME,
    "TYPE_SENTIMENT" : TYPE_SENTIMENT
}