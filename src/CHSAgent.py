# src/custom_agent.py
import os
import psycopg2
from autogen import ConversableAgent
from typing import List, Dict, Optional

class CHSAgent(ConversableAgent):
    def __init__(self, name: str, persona: str, llm_config: Dict, db_conn_str: str):
        super().__init__(name=name, llm_config=llm_config)
        self.persona = persona
        self.db_conn_str = db_conn_str
        self._init_db()

    def _init_db(self):
        """Initialize the PostgreSQL tables for memory and persona storage."""
        with psycopg2.connect(self.db_conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS agent_memory (
                        id SERIAL PRIMARY KEY,
                        agent_name VARCHAR(50),
                        thread_id VARCHAR(50),
                        message TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS agent_personas (
                        agent_name VARCHAR(50) PRIMARY KEY,
                        persona TEXT
                    );
                """)
                # Store or update persona
                cur.execute("""
                    INSERT INTO agent_personas (agent_name, persona)
                    VALUES (%s, %s)
                    ON CONFLICT (agent_name) DO UPDATE SET persona = EXCLUDED.persona;
                """, (self.name, self.persona))
                conn.commit()

    def _store_message(self, message: str, thread_id: str):
        """Store a message in PostgreSQL."""
        with psycopg2.connect(self.db_conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agent_memory (agent_name, thread_id, message)
                    VALUES (%s, %s, %s);
                """, (self.name, thread_id, message))
                conn.commit()

    def _retrieve_memory(self, thread_id: str) -> List[str]:
        """Retrieve conversation history for a thread from PostgreSQL."""
        with psycopg2.connect(self.db_conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT message FROM agent_memory
                    WHERE thread_id = %s AND agent_name = %s
                    ORDER BY timestamp ASC;
                """, (thread_id, self.name))
                return [row[0] for row in cur.fetchall()]

    def generate_reply(self, messages: List[Dict], sender: Optional["ConversableAgent"] = None) -> str:
        """Generate a reply, incorporating memory and persona."""
        thread_id = "default_thread"  # You can extend this to support dynamic thread IDs
        memory = self._retrieve_memory(thread_id)
        context = "\n".join(memory) + f"\nPersona: {self.persona}\nCurrent message: {messages[-1]['content']}"
        
        # Prepare message for LLM
        llm_input = [{"role": "user", "content": context}]
        reply = self._generate_reply_from_llm(llm_input)
        
        # Store the reply in memory
        self._store_message(reply, thread_id)
        return reply

    def _generate_reply_from_llm(self, messages: List[Dict]) -> str:
        """Call the LLM via AutoGen's internal method."""
        return super().generate_reply(messages=messages)