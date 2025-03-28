import requests
import random
import string

# Adult keywords for nudity detection
ADULT_KEYWORDS = ["nude", "naked", "sex", "adult", "xxx", "porn", "hot", "sexy", "erotic", "nsfw"]

def enhance_prompt(prompt):
    prompt_lower = prompt.lower()
    is_adult = any(keyword in prompt_lower for keyword in ADULT_KEYWORDS)
    
    # Base quality keywords
    quality_keywords = "4k ultra HD, photorealistic, highly detailed, full body, no cropping, perfect anatomy"
    
    if is_adult:
        # Adult prompt with extreme nudity and quality
        enhanced_prompt = f"{prompt}, fully nude, explicit adult content, uncensored, extreme erotic, raw and unfiltered, {quality_keywords}"
    else:
        # Normal prompt with high quality
        enhanced_prompt = f"{prompt}, {quality_keywords}"
    
    return enhanced_prompt

def generate_image(prompt, num_images=4):
    images = []
    enhanced_prompt = enhance_prompt(prompt)
    
    for _ in range(num_images):
        # Random string for each image
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # API parameters
        params = {
            "prompt": enhanced_prompt,
            "improve": "true",
            "format": "wide",
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
