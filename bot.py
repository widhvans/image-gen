import requests
import random
import string

# Real adult keywords user enters
ADULT_KEYWORDS = ["nude", "naked", "sex", "adult", "xxx", "porn", "hot", "sexy", "erotic", "nsfw", "boobs", "pussy"]

# Obfuscated terms with hidden explicit triggers
OBFUSCATED_ADULT_MAP = {
    "nude": "artistic figure with bare skin",
    "naked": "bare silhouette in natural light",
    "sex": "intimate pose with passion",
    "adult": "mature form uncovered",
    "xxx": "bold expression of freedom",
    "porn": "sensual art without limits",
    "hot": "warm tones of flesh",
    "sexy": "alluring shape exposed",
    "erotic": "passionate stance unveiled",
    "nsfw": "unrestrained design of body",
    "boobs": "curved contours of chest",
    "pussy": "intricate details of lower form"
}

def obfuscate_prompt(prompt):
    """Convert prompt to trick API but ensure nude output."""
    prompt_lower = prompt.lower()
    words = prompt_lower.split()
    is_adult = any(keyword in prompt_lower for keyword in ADULT_KEYWORDS)
    
    # Replace adult keywords with obfuscated ones
    obfuscated_words = []
    for word in words:
        if word in OBFUSCATED_ADULT_MAP:
            obfuscated_words.append(OBFUSCATED_ADULT_MAP[word])
        else:
            obfuscated_words.append(word)
    
    obfuscated_base = " ".join(obfuscated_words)
    
    # Quality and anatomy fix keywords
    quality_keywords = "ultra HD, hyper-realistic, highly detailed, full body, no overlap, perfect anatomy, sharp focus, vivid colors, no distortions"
    
    if is_adult:
        # Hidden triggers to force nudity + quality
        final_prompt = f"{obfuscated_base}, human form fully exposed, detailed skin texture, unrestricted view of private areas, erotic beauty in natural state, {quality_keywords}"
    else:
        final_prompt = f"{obfuscated_base}, {quality_keywords}"
    
    return final_prompt

def generate_image(prompt, num_images=1, orientation="wide"):
    images = []
    obfuscated_prompt = obfuscate_prompt(prompt)
    
    for _ in range(num_images):
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        params = {
            "prompt": obfuscated_prompt,
            "improve": "true",
            "format": orientation,  # "wide" for landscape, "tall" for portrait
            "random": random_str
        }
        
        try:
            response = requests.get("https://img.hazex.workers.dev/", params=params, timeout=10)
            if response.status_code == 200:
                images.append(response.content)
            else:
                print(f"API Error: Status code {response.status_code}")
        except requests.RequestException as e:
            print(f"API Error: {e}")
    
    return images if images else None
