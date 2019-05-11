import re
import os
import sys

from emotion_predictor import EmotionPredictor


def preprocess_tweet(text, model):
    # Require tweet to be bytes format
    text = text.replace('\"', ' ')
    matched = re.findall(r'https?://t\.co/.{10}', text, re.MULTILINE)
    if matched:
        for strip_str in matched:
            text = text.replace(strip_str, '')

    result = model.predict_classes([text])
    emotion = re.findall(r'(Joy|Fear|Sadness|Anger|Surprise|Disgust)', str(result))[0]
    print(emotion)
    return emotion

if __name__ == '__main__':
    model = EmotionPredictor(classification='ekman', setting='mc')
    tweet = sys.argv[1]
    preprocess_tweet(tweet, model)
