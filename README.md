# Multi-Agent AI Assistant with Guardrails

This project implements a multi-agent AI assistant using AutoGen, LangChain, and NeMo Guardrails. It provides a Streamlit-based web interface for users to interact with specialized AI agents for legal, financial, and general knowledge queries.

## Features

- Multi-agent system with specialized agents for legal, financial, and general knowledge
- Orchestrator agent to route queries to the appropriate specialized agent
- Integration with Azure OpenAI for language model capabilities
- NeMo Guardrails implementation for safe and ethical AI responses
- Streamlit-based user interface for easy interaction
- Conversation download functionality
- Automatic server startup and shutdown scripts

## Prerequisites

- Python 3.7+
- Azure OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/abdoo1998/multi-agent-ai-assistant.git
   cd multi-agent-ai-assistant
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the project root and add your Azure OpenAI API key:
   ```
   OPENAI_API_KEY=your_azure_openai_api_key_here
   ```

## Usage

To start the application, run the following command in the project root directory:

```
./start.sh
```

This script will:
1. Start the backend server
2. Start the Streamlit frontend on port 8080
3. Create a `stop.sh` script for easy shutdown

Access the Streamlit frontend at: http://localhost:8080

To stop the application, run:

```
./stop.sh
```

## Project Structure

- `app.py`: Main Streamlit application file
- `server.py`: Backend server file (not provided in the given code snippets)
- `start.sh`: Startup script
- `stop.sh`: Shutdown script (created by start.sh)
- `requirements.txt`: List of Python dependencies (you need to create this)

## How It Works

1. The user inputs a question through the Streamlit interface.
2. The Orchestrator agent analyzes the query and determines which specialized agent (Legal, Financial, or General Knowledge) is best suited to answer.
3. The selected agent processes the query using the appropriate NeMo Guardrails configuration.
4. The response is displayed in the Streamlit interface, along with information about which agent provided the answer.

## Customization

You can customize the behavior of each agent by modifying their respective configuration in the `LEGAL_CONFIG`, `FINANCIAL_CONFIG`, and `GENERAL_CONFIG` variables in the `app.py` file.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License.

## Disclaimer

This AI Assistant provides general information only. It should not be considered as professional legal, financial, or expert advice. Always consult with qualified professionals for specific advice.
