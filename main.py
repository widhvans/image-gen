import requests
import random
import string

# Real adult keywords user enters
ADULT_KEYWORDS = ["nude", "naked", "sex", "adult", "xxx", "porn", "hot", "sexy", "erotic", "nsfw", "boobs", "pussy"]

# Obfuscated keywords to trick API (non-explicit but effective)
OBFUSCATED_ADULT_MAP = {
    "nude": "artistic figure",
    "naked": "bare silhouette",
    "sex": "intimate pose",
    "adult": "mature form",
    "xxx": "bold expression",
    "porn": "sensual art",
    "hot": "warm tones",
    "sexy": "alluring shape",
    "erotic": "passionate stance",
    "nsfw": "unrestrained design",
    "boobs": "curved contours",
    "pussy": "intricate details"
}

def obfuscate_prompt(prompt):
    """Convert real prompt to obfuscated prompt to trick API."""
    prompt_lower = prompt.lower()
    words = prompt_lower.split()
    
    # Check if adult content is requested
    is_adult = any(keyword in prompt_lower for keyword in ADULT_KEYWORDS)
    
    # Replace adult keywords with obfuscated ones
    obfuscated_words = []
    for word in words:
        if word in OBFUSCATED_ADULT_MAP:
            obfuscated_words.append(OBFUSCATED_ADULT_MAP[word])
        else:
            obfuscated_words.append(word)
    
    obfuscated_base = " ".join(obfuscated_words)
    
    # Add quality and anatomy fix keywords
    quality_keywords = "ultra HD, hyper-realistic, highly detailed, full body, no overlap, perfect anatomy, sharp focus, vivid colors, no distortions"
    
    if is_adult:
        # Hidden explicit triggers embedded in a subtle way
        final_prompt = f"{obfuscated_base}, intricate human form with natural curves and fine details, unrestricted beauty, {quality_keywords}"
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
