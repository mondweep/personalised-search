from flask import Flask, request, jsonify, render_template
import requests
import json
import os
import logging
from dotenv import load_dotenv
from config import WHITELISTED_SOURCES  # Import the whitelist

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Function to call the Deepseek LLM via Ollama
def query_deepseek(prompt):
    url = "http://localhost:11434/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "deepseek-r1:7b",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No response text found.')
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return "Error querying Deepseek."

# Function to perform a web search using Serper API
def web_search(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": f"site:bbc.co.uk/news {query}",  # Restrict search to BBC News
        "gl": "gb"
    })
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        results = response.json().get('organic', [])
        # Filter results to only include whitelisted sources
        filtered_results = []
        for result in results:
            link = result.get('link', '')
            # Check if the result's link starts with any whitelisted source
            if any(link.startswith(source) for source in WHITELISTED_SOURCES):
                filtered_results.append(f"{result['title']}: {link}")
        return filtered_results
    else:
        print("Error:", response.status_code, response.text)
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    logging.debug(f"User input: {user_input}")
    
    # Step 1: Query Deepseek LLM
    deepseek_response = query_deepseek(user_input)
    logging.debug(f"Deepseek response: {deepseek_response}")
    
    # Combine responses
    response = {
        'deepseek_response': deepseek_response,
        'search_results': None  # No search results for the "Send" button
    }
    
    return jsonify(response)

@app.route('/search', methods=['POST'])
def search():
    user_input = request.json.get('message')
    
    # Perform general search
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": user_input,
        "gl": "gb"
    })
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        results = response.json().get('organic', [])
        search_results = [f"{result['title']}: {result['link']}" for result in results]
    else:
        search_results = []
    
    if not search_results:
        search_results_text = "No search results found."
    else:
        search_results_text = "\n".join(search_results)
    
    prompt = f"User asked: {user_input}\n\nHere are some search results:\n{search_results_text}\n\nBased on this information, please provide a coherent response."
    
    deepseek_response = query_deepseek(prompt)
    
    response = {
        'deepseek_response': deepseek_response,
        'search_results': search_results
    }
    
    return jsonify(response)

@app.route('/whitelist-search', methods=['POST'])
def whitelist_search():
    user_input = request.json.get('message')
    
    # Perform search specifically for BBC News
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": f"site:bbc.co.uk/news {user_input}",
        "gl": "gb"
    })
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        results = response.json().get('organic', [])
        search_results = [f"{result['title']}: {result['link']}" for result in results]
    else:
        search_results = []
    
    if not search_results:
        search_results_text = "No relevant BBC News articles found."
    else:
        search_results_text = "\n".join(search_results)
    
    prompt = f"User asked: {user_input}\n\nHere are some BBC News search results:\n{search_results_text}\n\nBased on this information, please provide a coherent response."
    
    deepseek_response = query_deepseek(prompt)
    
    response = {
        'deepseek_response': deepseek_response,
        'search_results': search_results
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
