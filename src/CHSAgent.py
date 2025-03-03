import psycopg2
import requests
from autogen.agent import BaseAgent  # adjust import based on your AutoGen package structure

class CHSAgent(BaseAgent):
    def __init__(self, name, llm_endpoint, db_config):
        super().__init__(name=name, llm_endpoint=llm_endpoint)
        self.db_config = db_config
        self.conn = psycopg2.connect(**db_config)
        self.create_table()
    
    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    agent_name TEXT,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()

    def store_message(self, message):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_history (agent_name, message) VALUES (%s, %s)",
                (self.name, message)
            )
            self.conn.commit()

    def process_message(self, message):
        # Save the incoming message.
        self.store_message(message)
        # Call the LLM service.
        response = self.call_llm(message)
        # Save the LLM response.
        self.store_message(response)
        return response

    def call_llm(self, prompt):
        # Post prompt to Ollama service; modify payload as needed.
        try:
            r = requests.post(self.llm_endpoint, json={"prompt": prompt, "model": "llama3.1:8b"})
            if r.status_code == 200:
                data = r.json()
                return data.get("response", "No response from LLM")
            else:
                return f"LLM error: {r.status_code}"
        except Exception as e:
            return f"Exception: {e}"
