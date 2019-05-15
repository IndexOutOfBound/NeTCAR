import re
import os
import sys

from emotion_predictor import EmotionPredictor
from emojificate.filter import emojificate


def emoji_mapper(tweet):
    tweet = tweet.replace('\"', ' ')
    returned_text = emojificate(tweet)

    emojis = re.findall(r'<img.*?>', str(returned_text))
    if emojis:
        for emoji in emojis:
            matched_emoji = re.match(r'.*title="(.*?)".*', emoji).group(1)
            returned_text = returned_text.replace(emoji, ' '+matched_emoji+' ')
    return returned_text

def preprocess_tweet(text, model):
    # Require tweet to be bytes format
    # text = text.replace('\"', ' ')
    matched = re.findall(r'https?://t\.co/.{10}', text, re.MULTILINE)
    if matched:
        for strip_str in matched:
            text = text.replace(strip_str, '')
    text = emoji_mapper(text)
    # result = model.predict_classes([text])
    # emotion = re.findall(r'(Joy|Fear|Sadness|Anger|Surprise|Disgust)', str(result))[0]
    # print(emotion)
    return text

if __name__ == '__main__':
    model = EmotionPredictor(classification='ekman', setting='mc')
    # tweet = sys.argv[1]
    print("-------Before Processing--------")

    tweet = "🚤 ⛵♬ (at Elefant Lounge Cafe) — https://t.co/Tp6satho40"
    print(tweet)
    after_text = preprocess_tweet(tweet, model)
    print("-------After Processing--------")
    print(after_text)