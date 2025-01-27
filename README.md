# Personalized Search with Deepseek

A web application that combines Deepseek LLM capabilities with internet search functionality, allowing users to interact with an AI assistant that can search and process information from the web.

## Author & Contact
**Mondweep Chakravorty**
- LinkedIn: [https://www.linkedin.com/in/mondweepchakravorty](https://www.linkedin.com/in/mondweepchakravorty)
- Feel free to connect for:
  - Questions about the application
  - Bug reports
  - Feature requests
  - Collaboration opportunities

## Features

- Direct AI interactions with Deepseek LLM
- General internet search capabilities
- Focused BBC News search
- Response refinement functionality
- Interactive chat interface

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- [Ollama](https://ollama.ai/) for running the Deepseek LLM
- A [Serper API key](https://serper.dev/) for web searches

## Installation

1. Clone the repository:
bash
git clone [your-repository-url]
cd personalised-search

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required Python packages:
```bash
pip install flask requests python-dotenv
```

4. Install the Deepseek model using Ollama:
```bash
ollama pull deepseek-r1:7b
```

## Configuration

1. Create a `.env` file in the project root:
```plaintext
SERPER_API_KEY=your_serper_api_key_here
```

2. Create a `config.py` file with whitelisted sources:
```python
WHITELISTED_SOURCES = [
    "https://www.bbc.co.uk/news"
]
```

3. Ensure your project structure looks like this:
```
personalised-search/
├── chat-web-app.py
├── config.py
├── .env
├── static/
│   └── style.css
└── templates/
    └── index.html
```

## Running the Application

1. Start the Ollama service:
```bash
ollama serve
```

2. In a new terminal, navigate to the project directory and start the Flask application:
```bash
python chat-web-app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

The web interface provides four main functions:

1. **Ask Deepseek Only**: Direct interaction with the Deepseek LLM
2. **Search the Internet**: General web search combined with AI analysis
3. **Search BBC News**: Focused search on BBC News articles
4. **Refine Response**: Click any response and use this button to request refinements

To use:
1. Type your question or search query in the input field
2. Click the appropriate button for your needs
3. To refine a response:
   - Click on the response you want to refine
   - Enter refinement instructions
   - Click the "Refine Response" button

## Troubleshooting

Common issues and solutions:

1. **Ollama Connection Error**:
   - Ensure Ollama is running (`ollama serve`)
   - Check if the Deepseek model is installed (`ollama list`)

2. **Search Not Working**:
   - Verify your Serper API key in the `.env` file
   - Check your internet connection

3. **Application Won't Start**:
   - Ensure all dependencies are installed
   - Check if port 5000 is available
   - Verify Python version compatibility

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT](LICENSE)

