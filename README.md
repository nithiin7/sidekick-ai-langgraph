# Sidekick AI - Personal Co-Worker

A production-ready AI assistant built with LangGraph, OpenAI, and Gradio that can help you complete tasks using various tools including web browsing, file management, and code execution.

## Features

- 🤖 **Intelligent Task Processing**: Uses LangGraph for complex workflow management
- 🛠️ **Rich Toolset**: Web browsing, file management, Python code execution, Wikipedia search, and more
- 🔄 **Iterative Improvement**: Self-evaluates and improves responses until success criteria are met
- 🌐 **Modern Web Interface**: Clean Gradio-based UI for easy interaction
- 📱 **Push Notifications**: Optional push notifications for task completion
- 🧠 **Memory Management**: Maintains conversation context across sessions

## Architecture

The application follows a production-ready architecture with:

- **LangGraph Workflow**: State-based graph execution for complex task processing
- **Tool Integration**: Modular tool system for extensibility
- **Evaluation Loop**: Self-assessment and improvement mechanism
- **Resource Management**: Proper cleanup and memory management

## Prerequisites

- Python 3.8+
- OpenAI API key
- Optional: Pushover credentials for notifications

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd sidekick-ai-langgraph
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
PUSHOVER_TOKEN=your_pushover_token
PUSHOVER_USER=your_pushover_user_id
```

## Usage

### Running the Application

```bash
python src/main.py
```

The application will start a Gradio web interface accessible at `http://localhost:7860`.

### Basic Workflow

1. **Input your request** in the message field
2. **Define success criteria** for your task
3. **Click "Go!"** to start processing
4. The AI will work iteratively until your criteria are met
5. **Reset** to start a new conversation

### Example Tasks

- "Research the latest developments in AI and create a summary document"
- "Write a Python script to analyze CSV data and generate charts"
- "Find information about climate change and create a presentation outline"

## Project Structure

```
sidekick-ai-langgraph/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py            # Application entry point
│   ├── core/              # Core application logic
│   │   ├── __init__.py
│   │   ├── sidekick.py    # Main Sidekick class
│   │   └── state.py       # State management
│   ├── tools/             # Tool implementations
│   │   ├── __init__.py
│   │   ├── base.py        # Base tool classes
│   │   ├── browser.py     # Browser automation tools
│   │   ├── file.py        # File management tools
│   │   └── external.py    # External API tools
│   ├── ui/                # User interface
│   │   ├── __init__.py
│   │   └── gradio_app.py  # Gradio interface
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── config.py      # Configuration management
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_sidekick.py
│   └── test_tools.py
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── LICENSE               # License file
├── README.md             # This file
└── setup.py              # Package setup
```

## Development

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the code examples in the `examples/` folder

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [OpenAI](https://openai.com/)
- UI framework: [Gradio](https://gradio.app/)
- Browser automation: [Playwright](https://playwright.dev/)
