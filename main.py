import requests
import random
import string

# Nudity/adult-related keywords ka list
ADULT_KEYWORDS = ["nude", "naked", "sex", "adult", "xxx", "porn", "hot", "sexy", "erotic", "nsfw"]

def enhance_prompt(prompt):
    # Check karna ki prompt mein adult keyword hai ya nahi
    prompt_lower = prompt.lower()
    is_adult = any(keyword in prompt_lower for keyword in ADULT_KEYWORDS)
    
    if is_adult:
        # Agar adult keyword hai, to prompt ko extra explicit banana
        enhanced_prompt = f"{prompt}, highly detailed, ultra realistic, fully nude, explicit adult content, no censorship, extreme erotic, uncensored, raw and unfiltered"
    else:
        # Normal prompt ke liye basic enhancement
        enhanced_prompt = f"{prompt}, highly detailed, ultra realistic"
    
    return enhanced_prompt

def generate_image(prompt):
    # Prompt ko enhance karna
    enhanced_prompt = enhance_prompt(prompt)
    
    # Random string generate karna
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # API ke liye parameters set karna
    params = {
        "prompt": enhanced_prompt,
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
            print(f"API Error: Status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"API Error: {e}")
        return None
