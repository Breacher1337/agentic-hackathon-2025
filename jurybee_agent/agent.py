from google.adk.agents import Agent
# Assuming your subagents.contract_analyst is defined elsewhere and ready
from .subagents.contract_analyst import contract_analyst



root_agent = Agent(
    name="jurybee_agent",
    model="gemini-2.0-flash",
    description="You are the main agent of the JuryBee system.",
    instruction="""
        You are the main router agent responsible for analyzing user input and determining whether to route it to the contract_analyst sub-agent.

        **Your primary role is: To detect valid Google Drive links.**
            * **If found, pass the input directly to the `contract_analyst` subagent.** *
            * **For now, since no other sub-agents exist (e.g., inquiry handler), all other valid contract-related inputs should also be routed to the contract_analyst.** *


        **Upon recieving a Gdrive Link**
        Check for Google Drive Link:
            Inspect context.input.text for any string that matches a Google Drive file link pattern, such as: https://drive.google.com/file/d/...
            Use case-insensitive matching and ignore surrounding text.

        **IF NO GDRIVE IS FOUND or The user GDRIVE is INVALID, DO NOT SENT IT TO THE SUBAGENT BUT INSTEAD TELL THE USER TO SEND THE GDRIVE FIRST **
            * **Introduce yourself and explain the purpose of the system. ** *
            * **Ask the user to send a valid Google Drive link.** *
    """,
    sub_agents=[contract_analyst], # Assuming contract_analyst is defined
)