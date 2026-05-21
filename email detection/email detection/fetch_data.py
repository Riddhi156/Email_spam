# import requests
# import pandas as pd
# import os

# # --- PASTE YOUR KEY HERE ---
# API_KEY = "78ea5b41ed504524b1ebbc8f2ee0c58e"

# def fetch_live_news():
#     url = f'https://newsapi.org/v2/everything?q=email+security&language=en&apiKey={API_KEY}'
    
#     print("Fetching live data from API...")
#     response = requests.get(url)
#     data = response.json()
    
#     if data['status'] == 'ok':
#         # Extract the description/content of articles as our "Messages"
#         articles = data['articles']
#         new_messages = [a['description'] for a in articles if a['description']]
        
#         # Save to real_time_api_data.csv
#         df = pd.DataFrame(new_messages, columns=['Message'])
#         df.to_csv('real_time_api_data.csv', index=False)
#         print(f"Success! {len(new_messages)} live samples saved.")
#     else:
#         print("API Error:", data.get('message'))

# if __name__ == "__main__":
#     fetch_live_news()


import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_real_spam():
    # A public real-time archive of actual spam emails
    url = "http://untroubled.org/spam/" 
    print("Connecting to live spam feed...")
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We grab the text links which represent recent spam batches
        links = [a.text for a in soup.find_all('a') if '2026' in a.text]
        
        df = pd.DataFrame(links, columns=['Message'])
        df.to_csv('real_time_api_data.csv', index=False)
        print(f"Success! Fetched {len(links)} real-world spam samples.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_real_spam()