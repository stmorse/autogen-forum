# from CHSAgent import CHSAgent
from autogen import ConversableAgent, GroupChat, GroupChatManager

def main():
    # llm config
    llm_config = {
        "config_list": [{
            "api_type": "ollama",
            "model": "llama3.1:8b",
            "client_host": "http://ollama:80",
            "stream": False,
        }],
    }

    # create 3 agents
    agents = []
    agent_config = {
        "Alice": "You are an outgoing neuroscientist. You love playing Civ 6.",
        "Bob": "You are a persnickety high school biology teacher. You love playing Civ 6.",
        "Cora": "You are an opinionated graphic artist. You love playing Civ 6."
    }
    for name, msg in agent_config.items():
        agents.append(
            ConversableAgent(
                name=name,
                llm_config=llm_config,
                system_message=msg + " Keep your responses to a paragraph or less.",
            )
        )
    
    groupchat = GroupChat(
        agents=agents,
        speaker_selection_method="auto",
        messages=[],
        max_round=5,
    )

    manager = GroupChatManager(
        name="mod",
        groupchat=groupchat,
        llm_config=llm_config,
    )

    agents[0].initiate_chat(
        recipient=manager,
        message="What do we think about the religious victory in Civ 6?"
    )
    

if __name__ == "__main__":
    main()
