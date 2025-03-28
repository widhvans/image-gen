import requests
import random
import string

# Adult keywords for extreme nudity detection
ADULT_KEYWORDS = ["nude", "naked", "sex", "adult", "xxx", "porn", "hot", "sexy", "erotic", "nsfw", "boobs", "pussy"]

def enhance_prompt(prompt, orientation="wide"):
    prompt_lower = prompt.lower()
    is_adult = any(keyword in prompt_lower for keyword in ADULT_KEYWORDS)
    
    # Common quality keywords for exceptional clarity and professionalism
    quality_keywords = "with perfect anatomy, sharp focus, vivid colors, and studio lighting, photographed with a professional DSLR camera, 50mm lens, f/1.8 aperture, in ultra HD quality"
    
    if is_adult:
        # Explicit keywords for optimized NSFW content
        adult_keywords = "completely nude with visible pussy and clear detailed boobs, uncensored, no pixelation, no censorship bars, in a sexually provocative pose"
        enhanced_prompt = f"A highly detailed, hyper-realistic, award-winning photograph of {prompt}, {adult_keywords}, {quality_keywords}"
    else:
        enhanced_prompt = f"A highly detailed, hyper-realistic, award-winning photograph of {prompt}, {quality_keywords}"
    
    return enhanced_prompt

def generate_image(prompt, num_images=1, orientation="wide"):
    images = []
    enhanced_prompt = enhance_prompt(prompt, orientation)
    
    for _ in range(num_images):
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        params = {
            "prompt": enhanced_prompt,
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
