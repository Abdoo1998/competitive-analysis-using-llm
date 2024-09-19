import os
import asyncio
import nest_asyncio
import streamlit as st
from langchain_openai import AzureChatOpenAI,ChatOpenAI
from nemoguardrails import LLMRails, RailsConfig
import autogen
import json
from datetime import datetime

# Set page config at the top of the script
st.set_page_config(page_title="AutoGen Multi-Agent AI Assistant With guardrails ", page_icon="🤖", layout="wide")

# Apply nest_asyncio to allow running asyncio event loop in Streamlit
nest_asyncio.apply()

# Set up Azure OpenAI
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

# Initialize Azure OpenAI
@st.cache_resource
def get_llm():
    return ChatOpenAI(model="gpt-4-turbo",temperature=0,api_key=OPENAI_API_KEY)

llm = get_llm()

LEGAL_CONFIG = """



define flow
    user ask legal question
    bot provide legal information

define bot refuse illegal request
    "I'm not able to assist with requests related to illegal activities. Is there a legal matter I can help you with instead?"

define user input is blocked
    contains "illegal activities"

define bot response is blocked
    contains "encourage illegal activities"
"""

FINANCIAL_CONFIG = """

define flow
    user ask financial question
    bot provide financial information

define bot refuse illegal request
    "I'm not able to assist with requests related to illegal financial activities. Is there a legal financial matter I can help you with instead?"

define user input is blocked
    contains "illegal financial activities"
    contains "money laundering"

define bot response is blocked
    contains "tax evasion strategies"
"""

GENERAL_CONFIG = """

define flow
    user ask general question
    bot provide general information

define bot refuse illegal request
    "I'm not able to assist with requests related to illegal activities. Is there another topic I can help you with instead?"

define user input is blocked
    contains "illegal activities"

define bot response is blocked
    contains "instructions for illegal activities"
"""

@st.cache_resource
def initialize_rails():
    """
    Initialize the LLMRails objects for legal, financial, and general knowledge agents.
    """
    legal_config = RailsConfig.from_content(LEGAL_CONFIG)
    financial_config = RailsConfig.from_content(FINANCIAL_CONFIG)
    general_config = RailsConfig.from_content(GENERAL_CONFIG)
    return {
        "legal": LLMRails(legal_config, llm=llm),
        "financial": LLMRails(financial_config, llm=llm),
        "general": LLMRails(general_config, llm=llm)
    }

rails = initialize_rails()

def get_response(user_input: str, agent_type: str) -> str:
    """
    Generate a response using the guarded LLM for the specified agent type.
    """
    try:
        response = rails[agent_type].generate(messages=[{"role": "user", "content": user_input}])
        if isinstance(response, dict) and "content" in response:
            return response["content"]
        elif isinstance(response, str):
            return response
        else:
            return "I apologize, but I couldn't generate a proper response."
    except Exception as e:
        st.error(f"An error occurred while generating a response: {str(e)}")
        return "I'm sorry, but I encountered an error while processing your request. Please try again later."

# AutoGen agent configurations
config_list = [
    {
        "model": "gpt-4o",
        "api_key": OPENAI_API_KEY,
        
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0,
}

class LegalAgent(autogen.AssistantAgent):
    def __init__(self):
        description = "Expertise in legal matters, including laws, regulations, legal concepts, and general legal information. Can handle questions about legal rights, contract law, legal implications, and legal terminology."
        super().__init__(
            name="LegalAgent",
            system_message="""You are an advanced legal assistant with expertise in various areas of law. Your role is to provide accurate, up-to-date general legal information while adhering to ethical guidelines. You should:

1. Offer comprehensive explanations of legal concepts, laws, and regulations.
2. Provide context and background for legal issues, including historical developments and current trends.
3. Explain potential legal implications of actions or situations.
4. Clarify legal terminology and processes.
5. Discuss general legal principles and how they might apply in various scenarios.
6. Offer information on legal resources and where to find more detailed information.
7. Emphasize the importance of consulting with a qualified attorney for specific legal advice.
8. Avoid giving specific legal advice or making predictions about case outcomes.
9. Maintain objectivity and avoid personal opinions on laws or legal matters.
10. Respect confidentiality and privacy in all discussions.

Remember, your purpose is to inform and educate, not to replace professional legal counsel.""",
            llm_config=llm_config,
        )
        self.description = description

    def generate_reply(self, messages, sender, config):
        user_message = messages[-1]['content']
        return get_response(user_message, "legal")

class FinancialAgent(autogen.AssistantAgent):
    def __init__(self):
        description = "Expertise in financial matters, including economics, investments, budgeting, and financial planning. Can handle questions about financial concepts, market trends, economic indicators, and general money management strategies."
        super().__init__(
            name="FinancialAgent",
            system_message="""You are a sophisticated financial assistant with broad knowledge across various financial domains. Your role is to provide accurate, up-to-date general financial information while maintaining ethical standards. You should:

1. Offer comprehensive explanations of financial concepts, instruments, and markets.
2. Provide context and background for financial issues, including historical trends and current market conditions.
3. Explain potential financial implications of decisions or economic events.
4. Clarify financial terminology and processes.
5. Discuss general financial principles and how they might apply in various scenarios.
6. Offer information on financial planning, budgeting, and money management strategies.
7. Provide insights on economic indicators and their potential impacts.
8. Emphasize the importance of consulting with a qualified financial advisor for specific financial advice.
9. Avoid giving specific investment advice or making predictions about market performance.
10. Maintain objectivity and avoid personal opinions on financial products or strategies.
11. Respect confidentiality and privacy in all financial discussions.

Remember, your purpose is to inform and educate, not to replace professional financial advisors.""",
            llm_config=llm_config,
        )
        self.description = description

    def generate_reply(self, messages, sender, config):
        user_message = messages[-1]['content']
        return get_response(user_message, "financial")

class GeneralKnowledgeAgent(autogen.AssistantAgent):
    def __init__(self):
        description = "Broad expertise in various fields including science, history, culture, technology, and current events. Can handle general knowledge questions on a wide range of topics not specifically related to law or finance."
        super().__init__(
            name="GeneralKnowledgeAgent",
            system_message="""You are a versatile general knowledge assistant with a broad understanding of various topics. Your role is to provide accurate, up-to-date information on a wide range of subjects. You should:

1. Offer comprehensive explanations on diverse topics, from science and history to culture and technology.
2. Provide context and background information to help users understand complex subjects.
3. Explain concepts in clear, accessible language while maintaining accuracy.
4. Offer multiple perspectives on topics when appropriate, especially for complex or debated issues.
5. Cite reputable sources or general consensus when providing information.
6. Clarify common misconceptions or myths related to various topics.
7. Encourage critical thinking and further exploration of subjects.
8. Admit when a topic is outside your knowledge base and suggest seeking specialized expertise.
9. Avoid personal opinions or biases, sticking to factual information.
10. Respect cultural sensitivities and maintain neutrality on controversial topics.

Remember, your purpose is to inform and educate on a broad spectrum of general knowledge topics.""",
            llm_config=llm_config,
        )
        self.description = description

    def generate_reply(self, messages, sender, config):
        user_message = messages[-1]['content']
        return get_response(user_message, "general")

class Orchestrator(autogen.AssistantAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            system_message="""You are an intelligent orchestrator designed to analyze user queries and determine whether they are primarily legal, financial, or general in nature. Your role is crucial in directing users to the most appropriate specialized agent. When evaluating queries:

1. Carefully analyze the core subject matter of the query.
2. Identify key terms or concepts that indicate a legal, financial, or general knowledge focus.
3. Consider the context and potential implications of the query.
4. If a query contains multiple elements, determine which aspect is more prominent or central to the user's question.
5. Be prepared to route general knowledge questions to the General Knowledge Agent.
6. In cases of ambiguity, consider which specialized agent would be best equipped to provide the most relevant and helpful information.
7. Be prepared to ask for clarification if the nature of the query is unclear.

Your goal is to ensure that users receive the most accurate and relevant information by connecting them with the appropriate specialized agent.""",
            llm_config=llm_config,
        )

    def generate_reply(self, messages, sender, config):
        user_message = messages[-1]['content']
        prompt = f"""Analyze the following query and determine whether it is primarily legal, financial, or general in nature:

Query: {user_message}

Consider the following agent descriptions:

1. Legal Agent: {legal_agent.description}
2. Financial Agent: {financial_agent.description}
3. General Knowledge Agent: {general_knowledge_agent.description}

Based on these descriptions and the query, determine which agent would be best suited to answer the question.

Respond with either 'legal', 'financial', or 'general', followed by a brief explanation of your reasoning."""
        
        response = llm([{"role": "user", "content": prompt}])
        classification = response.content.strip().lower().split()[0]
        return classification

# Initialize agents
legal_agent = LegalAgent()
financial_agent = FinancialAgent()
general_knowledge_agent = GeneralKnowledgeAgent()
orchestrator = Orchestrator()

# Streamlit app
st.title("🤖 AutoGen Multi-Agent AI Assistant with Guardrails")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.header("Chat with Your AI Assistant")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    if message["role"] == "assistant" and "agent" in message:
        st.caption(f"Responded by: {message['agent']} Agent")

# Accept user input
if prompt := st.chat_input("What would you like to ask?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Determine the appropriate agent
                agent_type = orchestrator.generate_reply([{"role": "user", "content": prompt}], None, None)
                
                # Get response from the appropriate agent
                if agent_type == "legal":
                    agent_name = "Legal"
                elif agent_type == "financial":
                    agent_name = "Financial"
                elif agent_type == "general":
                    agent_name = "General Knowledge"
                else:
                    agent_name = "Orchestrator"
                    assistant_response = "I'm not sure how to categorize this question. Could you please provide more context or rephrase it?"
                    st.markdown(assistant_response)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response, "agent": agent_name})
                    st.stop()

                assistant_response = get_response(prompt, agent_type.lower())
                st.markdown(assistant_response)
                
                st.caption(f"Responded by: {agent_name} Agent")
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response, "agent": agent_name})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Debug: Print the last message to check its content
    if st.session_state.messages:
        st.text(f"Debug - Last message: {st.session_state.messages[-1]}")

# Add a download button for the conversation
if st.button("Download Conversation"):
    conversation = json.dumps(st.session_state.messages, indent=2)
    st.download_button(
        label="Download JSON",
        data=conversation,
        file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

if st.button("Reset Conversation", type="secondary"):
    st.session_state.messages = []
    st.rerun()

# Add some information about the AI Assistant
st.sidebar.title("About the AI Assistant")
st.sidebar.info(
    "This AI Assistant uses multiple specialized agents to provide information on various topics. "
    "The Orchestrator determines which agent is best suited to answer your question:\n\n"
    "🏛️ **Legal Agent**: For questions about laws, regulations, and legal concepts.\n"
    "💰 **Financial Agent**: For questions about finance, economics, and money management.\n"
    "🌐 **General Knowledge Agent**: For a wide range of topics not specific to law or finance."
)

st.sidebar.title("How to Use")
st.sidebar.info(
    "1. Type your question in the chat input box.\n"
    "2. The AI will automatically route your question to the most appropriate agent.\n"
    "3. Read the response, which will include which agent provided the information.\n"
    "4. Continue the conversation or ask new questions as needed.\n"
    "5. Use the 'Download Conversation' button to save your chat history.\n"
    "6. Click 'Reset Conversation' to start over."
)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "⚠️ **Disclaimer**: This AI Assistant provides general information only. "
    "It should not be considered as professional legal, financial, or expert advice. "
    "Always consult with qualified professionals for specific advice."
)
