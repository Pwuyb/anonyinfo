import argparse
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import tweepy
import facebook
import instaloader

# Load API keys from .env file
load_dotenv()

# Get keys from .env (these stay secret)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")  # Optional
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")  # Optional

# Set up Twitter API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth, wait_on_rate_limit=True)

# Set up Facebook API
facebook_api = facebook.GraphAPI(FACEBOOK_ACCESS_TOKEN)

# Set up Instagram (instaloader, no API key needed)
loader = instaloader.Instaloader()
if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
    loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

def search_web(target_name):
    """Search Google for the target - AnonyInfo"""
    try:
        url = f"https://www.google.com/search?q={target_name}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [link.get("href") for link in soup.find_all("a") if "http" in str(link.get("href"))]
        return links[:5] if links else ["No links found"]
    except Exception as e:
        return [f"Web search failed: {e}"]

def search_twitter(target_name):
    """Search Twitter for profile and tweets - AnonyInfo"""
    try:
        users = twitter_api.search_users(target_name, count=1)
        if users:
            user = users[0]
            return {
                "username": user.screen_name,
                "bio": user.description,
                "tweets": [tweet.text for tweet in twitter_api.user_timeline(screen_name=user.screen_name, count=3)]
            }
        return {"error": "No Twitter user found"}
    except Exception as e:
        return {"error": f"Twitter search failed: {e}"}

def search_facebook(target_name):
    """Search Facebook for public pages - AnonyInfo"""
    try:
        data = facebook_api.request(f"search?q={target_name}&type=page")
        if data.get("data"):
            page = data["data"][0]
            return {"name": page.get("name", "Unknown"), "about": page.get("about", "No about info")}
        return {"error": "No public Facebook page found"}
    except Exception as e:
        return {"error": f"Facebook search failed: {e}"}

def search_instagram(target_name):
    """Search Instagram for profile and posts - AnonyInfo"""
    try:
        profile = instaloader.Profile.from_username(loader.context, target_name)
        return {
            "username": profile.username,
            "bio": profile.biography,
            "posts": [post.caption for post in profile.get_posts()][:3]
        }
    except Exception as e:
        return {"error": f"Instagram search failed: {e}"}

def search_linkedin(target_name):
    """Basic LinkedIn search via web - AnonyInfo"""
    try:
        url = f"https://www.linkedin.com/search/results/people/?keywords={target_name}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        profiles = soup.find_all("span", {"class": "name"})
        if profiles:
            return {"profile": profiles[0].text.strip()}
        return {"error": "No LinkedIn profiles found (login may be required)"}
    except Exception as e:
        return {"error": f"LinkedIn search failed: {e}"}

def run_tool(target):
    """Main function for AnonyInfo"""
    print(f"🔎 AnonyInfo - Searching for: {target}")

    web_results = search_web(target)
    twitter_results = search_twitter(target)
    facebook_results = search_facebook(target)
    instagram_results = search_instagram(target)
    linkedin_results = search_linkedin(target)

    print("\n🌐 AnonyInfo - Web Results:")
    for link in web_results:
        print(f"- {link}")

    print("\n🐦 AnonyInfo - Twitter Data:")
    print(twitter_results)

    print("\n📘 AnonyInfo - Facebook Data:")
    print(facebook_results)

    print("\n📷 AnonyInfo - Instagram Data:")
    print(instagram_results)

    print("\n💼 AnonyInfo - LinkedIn Data:")
    print(linkedin_results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AnonyInfo - Open-Source Intelligence Tool")
    parser.add_argument("target", help="Enter the target's name or username")
    args = parser.parse_args()
    
    # Check if keys are there
    required_keys = [TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, FACEBOOK_ACCESS_TOKEN]
    if not all(required_keys):
        print("Bro, you’re missing API keys in .env! Set them up first.")
    else:
        print("Welcome to AnonyInfo - Let’s find some info, bro!")
        run_tool(args.target)