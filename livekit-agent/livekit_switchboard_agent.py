#!/usr/bin/env python3
"""
LiveKit Switchboard Agent - Fixed Version
=========================================
Simplified switchboard agent based on the working test agent.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.plugins import deepgram, openai, silero
from db.supabase_client import get_db_client, Employee, CompanyInfo

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify environment variables
logger.info(f"LIVEKIT_URL: {os.getenv('LIVEKIT_URL', 'NOT SET')}")
logger.info(f"LIVEKIT_API_KEY: {os.getenv('LIVEKIT_API_KEY', 'NOT SET')[:10]}..." if os.getenv('LIVEKIT_API_KEY') else "LIVEKIT_API_KEY: NOT SET")
logger.info(f"LIVEKIT_API_SECRET: {os.getenv('LIVEKIT_API_SECRET', 'NOT SET')[:10]}..." if os.getenv('LIVEKIT_API_SECRET') else "LIVEKIT_API_SECRET: NOT SET")

class SwitchboardAssistant(Agent):
    """Enhanced switchboard operator with database integration and search capabilities."""
    
    def __init__(self):
        super().__init__(
            instructions="""You are a professional switchboard assistant for a company. 
            Your role is to:
            1. Greet callers politely and professionally
            2. Help them find the right person or department
            3. Search for employees by name, department, or role
            4. Check employee availability
            5. Take messages when employees are unavailable
            6. Provide company information and business hours
            
            Always be helpful, courteous, and efficient. Use the search tools to find employees and departments."""
        )
        
        # Initialize database client
        try:
            self.db_client = get_db_client()
            logger.info("Database client initialized successfully")
        except Exception as e:
            logger.warning(f"Database client initialization failed: {e}")
            logger.warning("Agent will run without database integration")
            self.db_client = None
    
    @function_tool
    async def search_employees(self, query: str = "", department: str = "") -> str:
        """Search for employees by name, department, or role.
        
        Args:
            query: Search query for employee name, email, or role
            department: Department name to filter by (e.g., 'Management', 'Sales', 'Support')
        """
        try:
            if not self.db_client:
                return "Sorry, I'm having trouble accessing the employee directory right now. Please try again later."
            
            employees = await self.db_client.search_employees(query, department)
            
            if not employees:
                return f"Sorry, I couldn't find any available employees matching your search. Please try a different name or department."
            
            result = f"Found {len(employees)} available employee(s):\n\n"
            
            for employee in employees:
                result += f"• {employee.first_name} {employee.last_name}\n"
                result += f"  Department: {employee.department_name or 'N/A'}\n"
                result += f"  Phone: {employee.phone_number}\n"
                result += f"  Office: {employee.office or 'N/A'}\n"
                if employee.roles:
                    result += f"  Roles: {', '.join(employee.roles)}\n"
                result += f"  Status: {employee.status}\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching employees: {e}")
            return "Sorry, I'm having trouble accessing the employee directory right now. Please try again later."
    
    @function_tool
    async def check_employee_availability(self, employee_name: str) -> str:
        """Check if a specific employee is available.
        
        Args:
            employee_name: The name of the employee to check (first name, last name, or full name)
        """
        try:
            if not self.db_client:
                return "Sorry, I'm having trouble checking employee availability right now."
            
            # Search for the employee by name
            employees = await self.db_client.search_employees(employee_name)
            
            if not employees:
                return f"Sorry, I couldn't find an employee named '{employee_name}'. Please try searching for employees first."
            
            # Check availability for each matching employee
            result = ""
            for employee in employees:
                is_available = await self.db_client.is_employee_available(employee.id)
                status = "available" if is_available else "not available"
                result += f"{employee.first_name} {employee.last_name} is currently {status}.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking employee availability: {e}")
            return "Sorry, I couldn't check the employee's availability right now."
    
    @function_tool
    async def get_departments(self) -> str:
        """Get all available departments in the company."""
        try:
            if not self.db_client:
                return "Sorry, I'm having trouble accessing department information right now."
            
            departments = await self.db_client.get_departments()
            
            if not departments:
                return "No departments are currently configured."
            
            result = "Available departments:\n\n"
            for dept in departments:
                result += f"• {dept.name}\n"
                if dept.description:
                    result += f"  {dept.description}\n"
                result += f"  Priority: {dept.routing_priority}\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting departments: {e}")
            return "Sorry, I couldn't retrieve the department list right now."
    
    @function_tool
    async def get_company_info(self) -> str:
        """Get company information including greeting message and business hours."""
        try:
            if not self.db_client:
                return "Thank you for calling. How may I direct your call?"
            
            company_info = await self.db_client.get_company_info()
            
            if not company_info:
                return "Thank you for calling. How may I direct your call?"
            
            result = f"Welcome to {company_info.company_name}!\n"
            result += f"{company_info.greeting_message}\n\n"
            
            # Check if company is open
            is_open = await self.db_client.is_company_open()
            if is_open:
                result += "We are currently open and available to help you."
            else:
                result += "We are currently closed, but I can still take a message for you."
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            return "Thank you for calling. How may I direct your call?"
    
    @function_tool
    async def take_message(self, employee_name: str, message_text: str, caller_phone: str = "") -> str:
        """Take a message for an employee.
        
        Args:
            employee_name: The name of the employee to take a message for
            message_text: The message content
            caller_phone: The caller's phone number (if available)
        """
        try:
            if not self.db_client:
                return "Sorry, I'm having trouble recording your message right now. Please try again later."
            
            # Find the employee
            employees = await self.db_client.search_employees(employee_name)
            
            if not employees:
                return f"Sorry, I couldn't find an employee named '{employee_name}'. Please try searching for employees first."
            
            # Use the first matching employee
            employee = employees[0]
            
            # Save the message
            message_id = await self.db_client.save_message(
                from_caller=caller_phone or "Unknown",
                to_employee_id=employee.id,
                message_text=message_text
            )
            
            if message_id:
                result = f"✓ Message recorded successfully!\n\n"
                result += f"For: {employee.first_name} {employee.last_name}\n"
                result += f"Department: {employee.department_name or 'N/A'}\n"
                result += f"Message: {message_text}\n\n"
                result += f"I'll make sure {employee.first_name} receives your message. Is there anything else I can help you with?"
                
                # Log the call
                await self.db_client.log_call(
                    caller_phone=caller_phone or "Unknown",
                    outcome=f"Message taken for {employee.first_name} {employee.last_name}"
                )
                
                return result
            else:
                return "Sorry, I'm having trouble saving your message right now. Please try again."
                
        except Exception as e:
            logger.error(f"Error taking message: {e}")
            return "Sorry, I'm having trouble recording your message right now. Please try again."

async def entrypoint(ctx: JobContext):
    """Enhanced entrypoint with database integration and search capabilities."""
    logger.info(f"🚀 Switchboard agent started for room: {ctx.room.name}")
    
    try:
        # Connect to the room
        await ctx.connect()
        logger.info("✅ Connected to room")
        
        # Create the enhanced switchboard assistant
        assistant = SwitchboardAssistant()
        
        # Create session with basic plugins
        session = AgentSession(
            vad=silero.VAD.load(),
            stt=deepgram.STT(model="nova-2"),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=openai.TTS(voice="echo"),
        )
        
        logger.info("✅ Session created, starting...")
        
        # Start the session
        await session.start(
            room=ctx.room,
            agent=assistant
        )
        
        logger.info("✅ Session started, generating greeting...")
        
        # Get company greeting from database
        try:
            company_info = await assistant.get_company_info()
            greeting = company_info if company_info else "Hello! Thank you for calling. How may I direct your call today?"
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            greeting = "Hello! Thank you for calling. How may I direct your call today?"
        
        # Generate greeting
        await session.generate_reply(
            instructions=f"Greet the caller with: '{greeting}'"
        )
        
        logger.info("✅ Greeting sent successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in switchboard agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    logger.info("Starting switchboard agent...")
    
    # Check if required environment variables are set
    if not os.getenv('LIVEKIT_URL') or not os.getenv('LIVEKIT_API_KEY') or not os.getenv('LIVEKIT_API_SECRET'):
        logger.error("❌ Missing required environment variables!")
        logger.error("Please ensure LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET are set")
        exit(1)
    
    try:
        cli.run_app(WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="switchboard-agent"
        ))
    except Exception as e:
        logger.error(f"❌ Failed to start agent: {e}")
        import traceback
        traceback.print_exc()
