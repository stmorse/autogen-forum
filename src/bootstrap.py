# src/bootstrap.py
import os
from autogen import GroupChat, GroupChatManager
from CHSAgent import CHSAgent

# Load environment variables
OLLAMA_URL = os.getenv("OLLAMA_URL")
PG_CONN = os.getenv("PG_CONN")

# LLM configuration for Ollama
llm_config = {
    "config_list": [{
        "model": "llama3.1:8b",  # Adjust to your Ollama model
        "base_url": OLLAMA_URL,
        "api_key": "ollama",  # Typically not needed for Ollama
        "api_type": "openai"
    }],
    "cache_seed": None  # Disable caching for dynamic interactions
}

# Create agents
agent1 = CHSAgent(
    name="Alice",
    persona="Friendly and curious forum user who loves asking questions.",
    llm_config=llm_config,
    db_conn_str=PG_CONN
)

agent2 = CHSAgent(
    name="Bob",
    persona="Knowledgeable and slightly sarcastic tech enthusiast.",
    llm_config=llm_config,
    db_conn_str=PG_CONN
)

# Set up GroupChat
group_chat = GroupChat(
    agents=[agent1, agent2],
    messages=[],
    max_round=10  # Limit rounds for testing
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)

# Interactive loop
def main():
    print("Starting interactive forum simulation. Type a message to begin or 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        # Initiate chat with user message
        response = agent1.initiate_chat(
            recipient=manager,
            message=user_input,
            max_turns=group_chat.max_round
        )
        
        # Add user message to GroupChat and let manager handle it
        # group_chat.messages.append({"role": "user", "content": user_input})
        # response = manager.run_chat(messages=group_chat.messages, sender=agent1)
        
        print(f"Forum Response: {response}")

if __name__ == "__main__":
    main()