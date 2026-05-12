import asyncio
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient

async def run_memory_chat():
    """Run a conversational MCP client for MongoDB operations."""
    load_dotenv()

    # Configure LLM (Groq)
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(model="llama-3.3-70b-versatile")

    # MCP config
    config_file = "server/mongodb.json"

    print("🔗 Connecting to MongoDB FastMCP Server...")

    # Initialize MCP Client
    client = MCPClient.from_config_file(config_file)

    # Create MCP Agent with conversation memory
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,
    )

    print("\n===== MongoDB MCP Chat =====")
    print("Type commands like:")
    print("- Insert a student named Hemesh with age 21")
    print("- List all students")
    print("- Update Hemesh age to 22")
    print("- Delete Hemesh")
    print("- Find Hemesh")
    print("Type 'clear' to clear chat memory or 'exit' to quit.")
    print("=============================\n")

    try:
        while True:
            user_input = input("\nYou: ")

            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting chat...")
                break

            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("🧹 Conversation memory cleared.")
                continue

            print("\nAssistant: ", end="", flush=True)

            try:
                # Send to LLM + MCP server
                response = await agent.run(user_input)
                print(response)
            except Exception as e:
                print(f"\n❌ Error: {e}")

    finally:
        if client and client.sessions:
            await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(run_memory_chat())
