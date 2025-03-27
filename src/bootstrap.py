import configparser
import sys
from typing import Any

from autogen import ConversableAgent, GroupChat, GroupChatManager

import psycopg2
from psycopg2 import pool
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from agent import CHSAgent

BASE_SYSTEM_MSG = (
    'You are roleplaying as someone with the backstory described as '
    '{backstory} and personality described as {personality}. '
    'Keep responses to under a paragraph.'
)

# Update these with your actual database credentials
# Load database credentials from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

DB_PARAMS = {
    'database': config.get('DB', 'DB_NAME'),
    'user': config.get('DB', 'DB_USER'),
    'password': config.get('DB', 'DB_PASS'),
    'host': config.get('DB', 'DB_HOST'),
    'port': config.getint('DB', 'DB_PORT')
}

connection_pool = None

def init_connection_pool(minconn=1, maxconn=10):
    """
    Initializes and returns a connection pool.
    """
    global connection_pool
    if connection_pool is None:
        connection_pool = pool.SimpleConnectionPool(minconn, maxconn, **DB_PARAMS)
    return connection_pool

def execute_query(query, params=None):
    """
    Executes a SQL query using a connection from the pool and returns the result.

    Args:
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters for the SQL query.

    Returns:
        list: Fetched result rows from the query.
    """
    conn = None
    cursor = None
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        return result
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            connection_pool.putconn(conn)

def give_agent_personality(
        agent: ConversableAgent, 
        messages: list[dict[str, Any]]
    ) -> None:

    uuid = agent.uuid
    name = agent.name

    try:
        query = "SELECT * FROM agents WHERE uuid = %s LIMIT 1;"
        query = sql.SQL(query)
        conn = connection_pool.getconn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, [uuid])

        # save all results as object-level dict
        result = cursor.fetchall()[0]

        if result:
            # print(f'{name} data:', result)
            agent.update_system_message(
                BASE_SYSTEM_MSG.format(
                    backstory=result['backstory'],
                    personality=result['personality'],
                )
            )
        else:
            print(f'No data found for {name}.')
    except Exception as ex:
        print(f'Error fetching data for {name}', ex)


def main():
    # Initialize the connection pool
    init_connection_pool()

    # llm config
    llm_config = {
        "config_list": [{
            "api_type": "ollama",
            "model": "llama3.2:latest",
            "client_host": "http://ollama-brewster:80",
            "stream": False,
        }],
    }

    uuids = {
        'amina': '123db983-adbf-4abd-b104-b3bae46e779a',
        'gaston': '0ff20db2-529b-4fd7-9ffc-c60475ece754',
        'aldo': 'a8c7c403-ad8f-4d14-a24e-fc5d174b0751'
    }

    topic = 'community safety'

    roles = {
        'amina': f'Leading a discussion on {topic}.',
        'gaston': f'Participating in a discussion on {topic}',
        'aldo': f'Participating in a discussion on {topic}',
    }

    agents = []

    for name, uuid in uuids.items():
        agent = CHSAgent(
            name=name,
            llm_config=llm_config,
            system_message=(
                'You are roleplaying someone with specific personality. '
            ),
            description=roles[name],
            uuid=uuid
        )

        # TODO: this is querying the DB each time
        agent.register_hook(
            hookable_method='update_agent_state',
            hook=give_agent_personality,
        )

        agents.append(agent)
    
    groupchat = GroupChat(
        agents=agents,
        speaker_selection_method="auto",
        messages=[],
        max_round=4,
    )

    manager = GroupChatManager(
        name="mod",
        groupchat=groupchat,
        llm_config=llm_config,
    )

    agents[0].initiate_chat(
        recipient=manager,
        message=''
    )
    

if __name__ == "__main__":
    main()
