"""
LiveKit Switchboard Agent - Enhanced Version
===========================================
Enhanced switchboard agent with Supabase integration, warm transfers, and message delivery.
"""

from dotenv import load_dotenv
from livekit import agents, rtc

# Load environment variables
load_dotenv()
from livekit.agents import Agent, AgentSession, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import openai, deepgram, silero
from datetime import datetime
import os
import logging
import asyncio
from typing import Optional, List, Dict, Any

from agent_instructions import instructions as agent_instructions
from db.supabase_client import get_db_client, Employee, CompanyInfo
from messaging import sms_service, email_service
from warm_transfer import warm_transfer_manager
from sip_call_routing import sip_call_router

# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SwitchboardAssistant(Agent):
    """Enhanced switchboard operator with database integration and advanced features."""

    def __init__(self):
        super().__init__(
            instructions=agent_instructions
        )
        
        # Initialize database client (with error handling)
        try:
            self.db_client = get_db_client()
        except Exception as e:
            logger.warning(f"Database client initialization failed: {e}")
            self.db_client = None
        
        # Cache for company info and departments
        self._company_info: Optional[CompanyInfo] = None
        self._departments: List[Dict[str, Any]] = []
        
        # Track active calls and transfers
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.pending_transfers: Dict[str, Dict[str, Any]] = {}

    async def _get_company_info(self) -> Optional[CompanyInfo]:
        """Get company information with caching."""
        if self.db_client is None:
            logger.warning("Database client not available, using default company info")
            return None
            
        if self._company_info is None:
            try:
                self._company_info = await self.db_client.get_company_info()
            except Exception as e:
                logger.error(f"Error fetching company info: {e}")
                return None
        return self._company_info

    async def _get_departments(self) -> List[Dict[str, Any]]:
        """Get departments with caching."""
        if self.db_client is None:
            logger.warning("Database client not available, using default departments")
            return [{"id": "default", "name": "General", "description": "General inquiries"}]
            
        if not self._departments:
            try:
                departments = await self.db_client.get_departments()
                self._departments = [
                    {
                        "id": dept.id,
                        "name": dept.name,
                        "description": dept.description,
                        "routing_priority": dept.routing_priority
                    }
                    for dept in departments
                ]
            except Exception as e:
                logger.error(f"Error fetching departments: {e}")
                return [{"id": "default", "name": "General", "description": "General inquiries"}]
        return self._departments

    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """Get the current date and time."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"The current date and time is {current_datetime}"

    @function_tool
    async def get_company_greeting(self, context: RunContext) -> str:
        """Get the company greeting message."""
        try:
            company_info = await self._get_company_info()
            if company_info:
                return company_info.greeting_message
            return "Thank you for calling. How may I direct your call?"
        except Exception as e:
            logger.error(f"Error getting company greeting: {e}")
            return "Thank you for calling. How may I direct your call?"

    @function_tool
    async def search_employees(self, context: RunContext, query: str = "", department: str = "") -> str:
        """Search for employees by name, department, or role.

        Args:
            query: Search query for employee name or role
            department: Department name to filter by (e.g., 'Management', 'Sales', 'Support')
        """
        try:
            # Map Swedish department names to English
            department_mapping = {
                'ledningen': 'Management',
                'management': 'Management',
                'försäljning': 'Sales', 
                'sales': 'Sales',
                'support': 'Support',
                'kundservice': 'Support'
            }
            
            department_key = department_mapping.get(department.lower()) if department else None
            
            # Search employees
            employees = await self.db_client.search_employees(
                query=query if query else None,
                department=department_key,
                status="available"
            )
            
            if not employees:
                available_departments = await self._get_departments()
                dept_names = [dept["name"] for dept in available_departments]
                return f"Sorry, I couldn't find any available employees matching your search. Available departments are: {', '.join(dept_names)}."

            result = f"Found {len(employees)} available employee(s):\n\n"
            
            for employee in employees:
                result += f"• {employee.name}\n"
                result += f"  Department: {employee.department_name or 'N/A'}\n"
                result += f"  Phone: {employee.phone}\n"
                result += f"  Office: {employee.office or 'N/A'}\n"
                result += f"  Roles: {', '.join(employee.roles) if employee.roles else 'N/A'}\n"
                result += f"  ID: {employee.id}\n\n"

            return result
            
        except Exception as e:
            logger.error(f"Error searching employees: {e}")
            return "Sorry, I'm having trouble accessing the employee directory right now. Please try again later."

    @function_tool
    async def check_employee_availability(self, context: RunContext, employee_id: str) -> str:
        """Check if a specific employee is available.

        Args:
            employee_id: The ID of the employee to check
        """
        try:
            is_available = await self.db_client.is_employee_available(employee_id)
            
            if is_available:
                return f"Employee {employee_id} is currently available."
            else:
                return f"Employee {employee_id} is not available at the moment."
                
        except Exception as e:
            logger.error(f"Error checking employee availability: {e}")
            return "Sorry, I couldn't check the employee's availability right now."

    @function_tool
    async def get_departments(self, context: RunContext) -> str:
        """Get all available departments."""
        try:
            departments = await self._get_departments()
            
            if not departments:
                return "No departments are currently configured."
            
            result = "Available departments:\n\n"
            for dept in departments:
                result += f"• {dept['name']}\n"
                if dept['description']:
                    result += f"  {dept['description']}\n"
                result += f"  Priority: {dept['routing_priority']}\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting departments: {e}")
            return "Sorry, I couldn't retrieve the department list right now."

    @function_tool
    async def initiate_warm_transfer(self, context: RunContext, employee_id: str, caller_phone: str = "", caller_name: str = "", caller_reason: str = "") -> str:
        """Initiate a warm transfer to an employee with consultation room.

        Args:
            employee_id: The ID of the employee to transfer to
            caller_phone: The caller's phone number (if available)
            caller_name: The caller's name (if available)
            caller_reason: The reason for the call (if available)
        """
        try:
            # Check if employee exists and is available
            employees = await self.db_client.search_employees()
            target_employee = None
            
            for emp in employees:
                if emp.id == employee_id:
                    target_employee = emp
                    break
            
            if not target_employee:
                return f"Sorry, I couldn't find employee with ID {employee_id}."
            
            # Check availability
            is_available = await self.db_client.is_employee_available(employee_id)
            if not is_available:
                return f"Sorry, {target_employee.name} is not available at the moment. Would you like me to take a message instead?"
            
            # Prepare caller information
            caller_info = {
                "name": caller_name or "Unknown Caller",
                "phone": caller_phone or "Unknown Number",
                "reason": caller_reason or "No specific reason provided",
                "room_id": context.room.name if hasattr(context, 'room') else "caller_room"
            }
            
            # Send transfer notification to employee
            notification_results = []
            
            # Send SMS notification
            if target_employee.phone:
                sms_result = await sms_service.send_transfer_notification(
                    employee_phone=target_employee.phone,
                    caller_info=caller_info,
                    employee_name=target_employee.name
                )
                notification_results.append(f"SMS: {'✓' if sms_result['success'] else '✗'}")
            
            # Send email notification
            if target_employee.email:
                email_result = await email_service.send_transfer_notification(
                    employee_email=target_employee.email,
                    caller_info=caller_info,
                    employee_name=target_employee.name
                )
                notification_results.append(f"Email: {'✓' if email_result['success'] else '✗'}")
            
            # Execute warm transfer
            caller_room_id = context.room.name if hasattr(context, 'room') else "caller_room"
            transfer_result = await warm_transfer_manager.execute_warm_transfer(
                employee_phone=target_employee.phone,
                caller_info=caller_info,
                caller_room_id=caller_room_id,
                session=context.session if hasattr(context, 'session') else None
            )
            
            # Log the transfer attempt
            await self.db_client.log_call(
                caller_phone=caller_phone or "Unknown",
                employee_id=employee_id,
                status="transferred" if transfer_result["status"] == "completed" else "failed",
                notes=f"Warm transfer to {target_employee.name}: {transfer_result['status']}"
            )
            
            if transfer_result["status"] == "completed":
                result = f"✓ Warm transfer completed!\n\n"
                result += f"Transfer ID: {transfer_result['transfer_id']}\n"
                result += f"Employee: {target_employee.name}\n"
                result += f"Department: {target_employee.department_name}\n"
                result += f"Notifications: {', '.join(notification_results)}\n\n"
                result += f"You are now connected to {target_employee.name}. Have a great conversation!"
                
            elif transfer_result["status"] == "rejected":
                result = transfer_result.get("message", f"Sorry, {target_employee.name} is not available to take your call right now. Would you like me to take a message instead?")
                
            elif transfer_result["status"] == "message":
                result = f"I've notified {target_employee.name} about your call. They would prefer to take a message. Would you like me to take a message for them instead?"
                
            else:
                result = f"Sorry, I'm having trouble connecting you to {target_employee.name} right now. Would you like me to take a message instead?"
            
            return result
            
        except Exception as e:
            logger.error(f"Error initiating warm transfer: {e}")
            return "Sorry, I'm having trouble initiating the transfer right now. Please try again."

    @function_tool
    async def take_message(self, context: RunContext, employee_id: str, message_text: str, caller_phone: str = "") -> str:
        """Take a message for an employee and deliver it via SMS and email.

        Args:
            employee_id: The ID of the employee to take a message for
            message_text: The message content
            caller_phone: The caller's phone number (if available)
        """
        try:
            # Get employee info
            employees = await self.db_client.search_employees()
            target_employee = None
            
            for emp in employees:
                if emp.id == employee_id:
                    target_employee = emp
                    break
            
            if not target_employee:
                return f"Sorry, I couldn't find employee with ID {employee_id}."
            
            # Save message to database
            message_id = await self.db_client.save_message(
                from_caller=caller_phone or "Unknown",
                to_employee_id=employee_id,
                message_text=message_text,
                delivered_via=["voice"],  # Will be updated when delivered via SMS/email
                delivery_details={"taken_by": "switchboard_agent"}
            )
            
            # Deliver message via SMS and email
            delivery_results = []
            
            # Send SMS notification
            if target_employee.phone:
                sms_result = await sms_service.send_message_notification(
                    employee_phone=target_employee.phone,
                    caller_phone=caller_phone or "Unknown",
                    message_text=message_text,
                    employee_name=target_employee.name
                )
                delivery_results.append(f"SMS: {'✓' if sms_result['success'] else '✗'}")
                
                if sms_result['success']:
                    await self.db_client.update_message_status(
                        message_id, 
                        "delivered",
                        {"sms": sms_result}
                    )
            
            # Send email notification
            if target_employee.email:
                email_result = await email_service.send_message_notification(
                    employee_email=target_employee.email,
                    caller_phone=caller_phone or "Unknown",
                    message_text=message_text,
                    employee_name=target_employee.name
                )
                delivery_results.append(f"Email: {'✓' if email_result['success'] else '✗'}")
                
                if email_result['success']:
                    await self.db_client.update_message_status(
                        message_id, 
                        "delivered",
                        {"email": email_result}
                    )
            
            # Log the call
            await self.db_client.log_call(
                caller_phone=caller_phone or "Unknown",
                employee_id=employee_id,
                status="completed",
                notes=f"Message taken for {target_employee.name}: {message_text[:100]}..."
            )
            
            result = f"✓ Message recorded and delivered!\n\n"
            result += f"Message ID: {message_id}\n"
            result += f"For: {target_employee.name}\n"
            result += f"Department: {target_employee.department_name}\n"
            result += f"Message: {message_text}\n"
            result += f"Delivery: {', '.join(delivery_results)}\n\n"
            result += f"I've sent your message to {target_employee.name} via SMS and email. Is there anything else I can help you with?"
            
            return result
            
        except Exception as e:
            logger.error(f"Error taking message: {e}")
            return "Sorry, I'm having trouble recording your message right now. Please try again."

    @function_tool
    async def check_company_hours(self, context: RunContext) -> str:
        """Check if the company is currently open."""
        try:
            is_open = await self.db_client.is_company_open()
            
            if is_open:
                return "Yes, we are currently open and available to help you."
            else:
                return "We are currently closed, but I can still take a message for you or help you find the information you need."
                
        except Exception as e:
            logger.error(f"Error checking company hours: {e}")
            return "I'm having trouble checking our business hours right now, but I'm here to help you."

    @function_tool
    async def get_employee_by_phone(self, context: RunContext, phone_number: str) -> str:
        """Get employee information by phone number.

        Args:
            phone_number: The phone number to search for
        """
        try:
            employee = await self.db_client.get_employee_by_phone(phone_number)
            
            if not employee:
                return f"Sorry, I couldn't find any employee with phone number {phone_number}."
            
            result = f"Found employee:\n\n"
            result += f"• Name: {employee.name}\n"
            result += f"• Department: {employee.department_name or 'N/A'}\n"
            result += f"• Phone: {employee.phone}\n"
            result += f"• Email: {employee.email}\n"
            result += f"• Office: {employee.office or 'N/A'}\n"
            result += f"• Roles: {', '.join(employee.roles) if employee.roles else 'N/A'}\n"
            result += f"• Status: {employee.status}\n"
            result += f"• ID: {employee.id}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting employee by phone: {e}")
            return "Sorry, I'm having trouble looking up that phone number right now."

    async def on_call_start(self, context: RunContext, caller_phone: str = ""):
        """Called when a new call starts."""
        try:
            # Log the call start
            call_id = f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.active_calls[call_id] = {
                "caller_phone": caller_phone,
                "start_time": datetime.now(),
                "status": "active"
            }
            
            logger.info(f"Call started: {call_id} from {caller_phone}")
            
        except Exception as e:
            logger.error(f"Error in on_call_start: {e}")

    async def on_call_end(self, context: RunContext, call_id: str = ""):
        """Called when a call ends."""
        try:
            if call_id in self.active_calls:
                call_info = self.active_calls[call_id]
                duration = datetime.now() - call_info["start_time"]
                
                # Log the call end
                await self.db_client.log_call(
                    caller_phone=call_info["caller_phone"],
                    duration=str(duration),
                    status="completed",
                    notes=f"Call ended normally"
                )
                
                del self.active_calls[call_id]
                logger.info(f"Call ended: {call_id}, duration: {duration}")
                
        except Exception as e:
            logger.error(f"Error in on_call_end: {e}")

async def entrypoint(ctx: agents.JobContext):
    """Entry point for the enhanced switchboard agent with SIP call detection."""
    
    # Connect to the room - this is crucial for local agents
    await ctx.connect()

    # Configure the voice pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model=os.getenv("LLM_CHOICE", "gpt-4.1-mini")),
        tts=openai.TTS(voice="echo"),
        vad=silero.VAD.load(),
    )

    # Create the assistant
    assistant = SwitchboardAssistant()
    
    # Start the room cleanup task
    await sip_call_router.start_cleanup_task()
    
    # Detect SIP participants and extract caller information
    caller_info = {"phone": "Unknown", "name": "Unknown Caller", "caller_id": "unknown"}
    is_sip_call = False
    
    if hasattr(ctx.room, 'participants'):
        for participant in ctx.room.participants.values():
            if sip_call_router.is_sip_participant(participant):
                is_sip_call = True
                caller_info = sip_call_router.extract_caller_info(participant)
                logger.info(f"SIP call detected from: {caller_info}")
                break
    
    # Register the room for tracking
    room_name = ctx.room.name
    await sip_call_router.register_room(room_name, caller_info, session)
    
    # Set up participant event handlers
    async def on_participant_connected(participant: rtc.RemoteParticipant):
        await sip_call_router.handle_participant_joined(room_name, participant)
    
    async def on_participant_disconnected(participant: rtc.RemoteParticipant):
        await sip_call_router.handle_participant_left(room_name, participant)
    
    # Register event handlers
    ctx.room.on("participant_connected", on_participant_connected)
    ctx.room.on("participant_disconnected", on_participant_disconnected)

    # Start the session
    await session.start(
        room=ctx.room,
        agent=assistant
    )

    # Notify call start
    await assistant.on_call_start(ctx, caller_info.get("phone", ""))

    # Generate initial greeting based on call type
    try:
        company_info = await assistant._get_company_info()
        if is_sip_call:
            greeting = f"Hello {caller_info.get('name', 'there')}, {company_info.greeting_message if company_info else 'Thank you for calling. How may I direct your call?'}"
        else:
            greeting = company_info.greeting_message if company_info else "Thank you for calling. How may I direct your call?"
    except:
        greeting = "Thank you for calling. How may I direct your call?"
    
    await session.generate_reply(
        instructions=f"Greet the caller with: '{greeting}'"
    )
    
    # Clean up when session ends
    try:
        await sip_call_router.remove_room(room_name)
        await sip_call_router.stop_cleanup_task()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    # Run the agent with explicit dispatch for SIP calls
    agents.cli.run_app(agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="switchboard-agent"
    ))
