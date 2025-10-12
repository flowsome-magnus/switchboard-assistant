"""
LiveKit Voice Agent - Quick Start
==================================
The simplest possible LiveKit voice agent to get you started.
Requires only OpenAI and Deepgram API keys.
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import openai, deepgram, silero
from datetime import datetime
import os

from agent_instructions import instructions as agent_instructions

# Load environment variables
load_dotenv(".env")

class Assistant(Agent):
    """Basic switchboard operator talking and transferring calls as well as taking messages."""

    def __init__(self):
        super().__init__(
            instructions=agent_instructions
        )

        # Mock employees database - flat structure with explicit department
        self.employees = {
            "e001": {
                "name": "Magnus Edin",
                "department": "Management",
                "phone": "+46702778411",
                "office": "Östersund",
                "email": "magnus@flowsome.se",
                "roles": ["CEO", "Owner"]
            },
            "e002": {
                "name": "Kurt Olsson",
                "department": "Management",
                "phone": "+46702778412",
                "office": "Östersund",
                "email": "kurt@flowsome.se",
                "roles": ["CTO", "Teknikchef"]
            },
            "e003": {
                "name": "Warren Buffett",
                "department": "Management",
                "phone": "+46702778413",
                "office": "Östersund",
                "email": "warren@flowsome.se",
                "roles": ["CFO"]
            },
            "e004": {
                "name": "Anna Nilsson",
                "department": "Sales",
                "phone": "+46702778414",
                "office": "Östersund",
                "email": "anna@flowsome.se",
                "roles": ["Sales Manager", "Försäljningschef"]
            },
            "e005": {
                "name": "Peter Svensson",
                "department": "Sales",
                "phone": "+46702778415",
                "office": "Stockholm",
                "email": "peter@flowsome.se",
                "roles": ["Sales Representative", "Försäljningsassistent"]
            },
            "e006": {
                "name": "Jörgen Johansson",
                "department": "Support",
                "phone": "+46702778416",
                "office": "Östersund",
                "email": "jorgen@flowsome.se",
                "roles": ["Support Engineer", "Supporttekniker"]
            },
            "e007": {
                "name": "Johan Nilsson",
                "department": "Support",
                "phone": "+46702778417",
                "office": "Stockholm",
                "email": "johan@flowsome.se",
                "roles": ["Support Engineer", "Supporttekniker"]
            }
        }

        # Track transfers
        self.transfers = []

    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """Get the current date and time."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"The current date and time is {current_datetime}"

    @function_tool
    async def search_person(self, context: RunContext, department: str) -> str:
        """Search for available people in a department.

        Args:
            department: The department name to search for people (e.g., 'Ledningen', 'Försäljning', 'Support')
        """
        # Map department names to the correct keys
        department_mapping = {
            'management': 'Management',
            'ledningen': 'Management', 
            'sales': 'Sales',
            'försäljning': 'Sales',
            'support': 'Support'
        }
        
        department_key = department_mapping.get(department.lower())
        if not department_key:
            return f"Sorry, I don't have any people in the {department} department at the moment. Available departments are: Management, Sales, and Support."

        # Filter employees by department
        department_employees = [
            (emp_id, emp_data) for emp_id, emp_data in self.employees.items() 
            if emp_data['department'] == department_key
        ]
        
        if not department_employees:
            return f"Sorry, I don't have any people in the {department} department at the moment. Available departments are: Management, Sales, and Support."

        result = f"Found {len(department_employees)} people in the {department} department:\n\n"

        for emp_id, employee in department_employees:
            result += f"• {employee['name']}\n"
            result += f"  Phone: {employee['phone']}\n"
            result += f"  Office: {employee['office']}\n"
            result += f"  Email: {employee['email']}\n"
            result += f"  Roles: {', '.join(employee['roles'])}\n"
            result += f"  ID: {emp_id}\n\n"

        return result

    @function_tool
    async def make_transfer(self, context: RunContext, person_id: str, department: str) -> str:
        """Make a transfer to a person in a department.

        Args:
            person_id: The ID of the person to transfer to (e.g., 'e001')
            department: The department to transfer to (e.g., 'Management', 'Sales', 'Support')
        """
        # Find the person directly by ID
        if person_id not in self.employees:
            return f"Sorry, I couldn't find a person with ID {person_id}. Please search for available people first."

        found_person = self.employees[person_id]

        # Create transfer
        transfer = {
            "confirmation_number": f"TR{len(self.transfers) + 1001}",
            "person_name": found_person['name'],
            "department": found_person['department'],
        }

        self.transfers.append(transfer)

        result = f"✓ Transfer confirmed!\n\n"
        result += f"Confirmation Number: {transfer['confirmation_number']}\n"
        result += f"Person: {transfer['person_name']}\n"
        result += f"Department: {transfer['department']}\n\n"
        result += f"You'll receive a confirmation email shortly. Have a great day!"

        return result

async def entrypoint(ctx: agents.JobContext):
    """Entry point for the agent."""

    # Configure the voice pipeline with the essentials
    session = AgentSession(
        #stt=deepgram.STT(model="nova-2"),
        llm=openai.realtime.RealtimeModel(voice="alloy", temperature=0.8),
        #llm=openai.LLM(model=os.getenv("LLM_CHOICE", "gpt-4.1-mini")),
        #tts=openai.TTS(voice="echo"),
        #vad=silero.VAD.load(),
    )

    # Start the session
    await session.start(
        room=ctx.room,
        agent=Assistant()
    )

    # Generate initial greeting
    await session.generate_reply(
        instructions="Hälsa användaren vänligt och fråga hur du kan hjälpa."
    )

if __name__ == "__main__":
    # Run the agent
    agents.cli.run_app(agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="basic-agent"
    ))