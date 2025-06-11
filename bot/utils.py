import os
from langdetect import detect

# Example in-memory subscription data
SUBSCRIPTIONS = {
    # user_id: 'free' | 'premium'
}

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return 'unknown'

def get_subscription_level(user_id: int) -> str:
    return SUBSCRIPTIONS.get(user_id, os.environ.get('DEFAULT_SUBSCRIPTION', 'free'))
