
import requests
import random
import string

def generate_image(prompt):
    # Random string generate karna random parameter ke liye
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # API ke liye parameters set karna
    params = {
        "prompt": prompt,
        "improve": "true",
        "format": "wide",
        "random": random_str
    }
    
    # API ko GET request bhejna
    try:
        response = requests.get("https://img.hazex.workers.dev/", params=params, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except requests.RequestException as e:
        print(f"API Error: {e}")
        return None
