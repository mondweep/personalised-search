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
    
    prompt = f"""User asked: {user_input}

Here are the search results:
{search_results_text}

Important instructions:
1. Base your response ONLY on the information provided in these search results
2. If the search results don't contain enough information to answer fully, acknowledge the limitations
3. DO NOT make assumptions or add information not present in the search results
4. If you're unsure about something, say so explicitly
5. Use phrases like "According to the search results..." to show you're grounding your response in the provided information

Please provide a response based strictly on these search results."""
    
    deepseek_response = query_deepseek(prompt)
    
    return jsonify({
        'deepseek_response': deepseek_response,
        'search_results': search_results
    })

@app.route('/whitelist-search', methods=['POST'])
def whitelist_search():
    user_input = request.json.get('message')
    
    # Perform BBC News search
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
    
    prompt = f"""User asked: {user_input}

Here are the BBC News articles:
{search_results_text}

Important instructions:
1. Base your response ONLY on the information provided in these BBC News articles
2. If the articles don't contain enough information to answer fully, acknowledge the limitations
3. DO NOT make assumptions or add information not present in the BBC News articles
4. If you're unsure about something, say so explicitly
5. Use phrases like "According to BBC News..." to show you're grounding your response in the provided information

Please provide a response based strictly on these BBC News articles."""
    
    deepseek_response = query_deepseek(prompt)
    
    return jsonify({
        'deepseek_response': deepseek_response,
        'search_results': search_results
    })

@app.route('/refine', methods=['POST'])
def refine():
    data = request.json
    original_response = data.get('original_response', '')
    refinement_request = data.get('refinement_request', '')
    
    prompt = f"""Original response:
{original_response}

User's refinement request:
{refinement_request}

Important instructions:
1. Only refine the response using information that was present in the original response
2. DO NOT add new information or make assumptions
3. Focus on reorganizing, clarifying, or emphasizing existing information
4. If the refinement request asks for information not present in the original response, acknowledge that limitation
5. Maintain factual accuracy while making the requested refinements

Please refine the original response according to these guidelines."""
    
    refined_response = query_deepseek(prompt)
    
    return jsonify({
        'refined_response': refined_response
    })

if __name__ == '__main__':
    app.run(debug=True)
