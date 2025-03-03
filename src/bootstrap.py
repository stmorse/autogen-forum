from CHSAgent import CHSAgent
from autogen.agent_chat import GroupChat  # adjust import based on your AutoGen API

def main():
    # Customize these endpoints and DB credentials as needed.
    llm_endpoint = "http://ollama:80"  # example endpoint; adjust port as required
    db_config = {
        "host": "postgres-stm-service",
        "port": 5432,
        "user": "forum_user",
        "password": "forum_password",
        "dbname": "forum_db"
    }

    # Create two agents.
    agent1 = CHSAgent(name="Agent1", llm_endpoint=llm_endpoint, db_config=db_config)
    agent2 = CHSAgent(name="Agent2", llm_endpoint=llm_endpoint, db_config=db_config)
    
    # Instantiate a group chat session with both agents.
    chat = GroupChat(agents=[agent1, agent2])
    
    print("Starting group chat (type 'exit' to quit).")
    while True:
        message = input("You: ")
        if message.lower() == "exit":
            break
        # Dispatch message to agents; adjust behavior per your API.
        response = chat.send(message)
        print("Chat:", response)

if __name__ == "__main__":
    main()
