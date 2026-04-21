from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
import sqlite3

# ============================================================
# DB SETUP
# ============================================================

def setup_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        authenticated INTEGER
    )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    users = [
        ("ML001", "Raj", 1),
        ("ML002", "Ram", 0),
        ("ML003", "Sham", 1)
    ]

    cursor.executemany("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", users)

    conn.commit()
    conn.close()


# ============================================================
# TOOLS (STRUCTURED)
# ============================================================

# @tool("add_user", description="Use this tool to add a user to the database. Provide name and id as input.")
# def add_user(name: str, user_id: str) -> str:
#     """Add a user to the database"""
#     # print(f"Adding user with name={name} and id={user_id}")
#     conn = sqlite3.connect("users.db")
#     cursor = conn.cursor()

#     try:
#         cursor.execute(
#             "INSERT INTO users (id, name, authenticated) VALUES (?, ?, ?)",
#             (user_id, name, 1)
#         )
#         conn.commit()
#         conn.close()
#         return f"User {name} added with ID {user_id}"
#     except Exception as e:
#         conn.close()
#         return f"Error: {str(e)}"

import random

@tool("add_user", description="Add user with auto-random ID if exists")
def add_user(name: str, user_id: str) -> str:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        existing = cursor.fetchone()

        new_id = user_id

        if existing:
            while True:
                new_id = f"ML{random.randint(1000, 9999)}"
                cursor.execute("SELECT id FROM users WHERE id = ?", (new_id,))
                if not cursor.fetchone():
                    break

        cursor.execute(
            "INSERT INTO users (id, name, authenticated) VALUES (?, ?, ?)",
            (new_id, name, 1)
        )

        conn.commit()
        conn.close()

        return f"User {name} added with ID {new_id}"

    except Exception as e:
        conn.close()
        return f"Error: {str(e)}"
        
@tool
def list_users() -> str:
    """List all users"""
    # print("[Tool] Listing all users...")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, authenticated FROM users")
    rows = cursor.fetchall()
    conn.close()

    response = "\n".join([str(r) for r in rows]) or "No users found"
    # print("[Tool] List of users:\n", response)
    return response

@tool("delete_user", description="Delete a user from the database using user_id")
def delete_user(user_id: str) -> str:
    """Delete a user from the database"""
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return f"Error: User with ID {user_id} does not exist"

        # Delete user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        return f"User with ID {user_id} deleted successfully"

    except Exception as e:
        conn.close()
        return f"Error: {str(e)}"

# ============================================================
# MAIN
# ============================================================

f = open(r"C:\Users\USER\Downloads\AI-TRAINING\ai-learning-own-repo\agentic-ai-30-days-challenge\api-tokens\groq-api-key.txt")
groq_api_key = f.read()
f.close()

if __name__ == "__main__":

    setup_db()
    seed_data()

    # Groq via OpenAI-compatible API
    llm = ChatOpenAI(
        model="llama-3.1-8b-instant",
        openai_api_key=groq_api_key,
        openai_api_base="https://api.groq.com/openai/v1",
        temperature=0
    )

    #tools = [add_user, list_users]
    tools = [add_user, list_users, delete_user]

    # ---------------- Demo: change prompt to show how system prompt can be used to steer agent behavior ----------------

    prompt = """
    You are a database user management assistant.

    Available tools:
    - add_user(name, user_id)
    - list_users()
    - delete_user(user_id)

    Rules:
    - Always use tools for user-related tasks
    - Call ONLY ONE tool
    - After tool execution, STOP

    Examples:
    User: Add user Ravi with id ML100  
    → call add_user(name="Ravi", user_id="ML100")
    User: if user id already exist, delete user and add new user with increment id
    User: List users  
    → call list_users()

    IMPORTANT:
    Return ONLY the tool output as final answer.
    """
#     prompt = """
# You are a database user management assistant.
# - Always use tools for any user management task.
# - For adding users, use the add_user tool with name and id.
# - For listing users, use the list_users tool.
# - Never directly answer user management questions without using tools.
# - IMPORTANT: Return the tool output EXACTLY as it is without any modifications or explanations.
# - STRICT: 
#     - Call only one tool per user query.
#     - After calling a tool, return the tool output as the final answer without retrying or calling another tool, even if the output is an error.
# """

    prompt2 = """
You are a database user management assistant.

Your job is to execute exactly ONE tool per user request.

Available tools:
- add_user(name, user_id)
- list_users()

Rules:
- Decide the correct tool based on the user request.
- Call exactly ONE tool.
- After the tool returns output, STOP immediately.
- Do NOT call another tool.
- Do NOT retry.
- Do NOT continue reasoning.

CRITICAL:
- The tool output is the FINAL answer.
- Return the tool output EXACTLY as it is. 
- Do not summarize, modify or explain the tool output.
- Even if the tool returns an error, DO NOT retry.

Examples:

User: Add user Ravi with id ML100  
→ call add_user(name="Ravi", user_id="ML100")

User: List all users  
→ call list_users()
OUTPUT FORMAT:
-> ID: ML5034301, Name: Raj, Authenticated: 1
-> ID: ML053402, Name: Ram, Authenticated: 0
-> ID: ML003453, Name: Sham, Authenticated: 1
"""

    agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=prompt2,
            # debug=True,
        )

    # Invoke
    response = agent.invoke({
        "messages": [
            {"role": "user", "content": "Add a user named Dikshant with id ML954308"}
        ]
    })

    print(response["messages"][-1].content)

    response = agent.invoke({
        "messages": [
            {"role": "user", "content": "Give me a list of all users"}
        ]
    })

    print(response["messages"][-1].content)

    # response = agent.invoke({
    #     "messages": [
    #         {"role": "user", "content": "Delete a user named Sunil with id ML508"}
    #     ]
    # })

    # print(response["messages"][-1].content)


    