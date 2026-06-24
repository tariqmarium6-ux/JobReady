import os
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.genai.errors import ServerError
from agents_config import analysis_agent, curator_agent

load_dotenv()

async def execute_adk_pipeline(user_input: str, retries: int = 3):
    print("\n====== [Antigravity 2.0: Orchestration Runtime Engaged] ======\n")
    print(f"Targeting Architecture: Ingestion ➔ Analysis ➔ Curator")
    
    runner = InMemoryRunner(agent=curator_agent, app_name="skillbridge_ai")
    session = await runner.session_service.create_session(app_name="skillbridge_ai", user_id="MARIUM_TARIQ")
    
    msg = types.Content(
        role="user", 
        parts=[types.Part(text=f"The user has basic Python and SQL skills. They want to be an 'AI Operations Specialist'. Build the curriculum based on the spec.")]
    )
    
    for attempt in range(retries):
        try:
            print(f"[{attempt + 1}/3] Routing payload through Agent Execution Handshake...")
            async for event in runner.run_async(user_id="MARIUM_TARIQ", session_id=session.id, new_message=msg) or []:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            # Emerald Green styling block for UI emulation
                            print("\n[✓] A2UI Canvas Sync Complete:")
                            print("-" * 50)
                            print(part.text)
                            print("-" * 50)
                            
            print("\n====== [Pipeline Sequence Concluded] ======")
            return
            
        except ServerError as e:
            if "503" in str(e) and attempt < retries - 1:
                wait = (attempt + 1) * 3
                print(f"[!] MCP Transport Delay: Google ADK Server Spiking. Retrying in {wait}s...")
                await asyncio.sleep(wait)
            else:
                raise e

if __name__ == "__main__":
    # Kicking off the async Antigravity 2.0 Loop
    asyncio.run(execute_adk_pipeline("Initialize Execution"))