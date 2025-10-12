#!/usr/bin/env python3
"""
Agent Dispatcher Service - Monitors for new SIP rooms and dispatches agents
"""
import asyncio
import os
import logging
from livekit import api

logger = logging.getLogger(__name__)

class AgentDispatcher:
    def __init__(self):
        self.lkapi = api.LiveKitAPI(
            url=os.getenv("LIVEKIT_URL", "wss://demo-41snsvwf.livekit.cloud"),
            api_key=os.getenv("LIVEKIT_API_KEY", "APIebvsBQ3xohnG"),
            api_secret=os.getenv("LIVEKIT_API_SECRET", "ik2ipeu4VhD3Pyohl1d21bdMft1UDXTtl5a6Nr9N1ow")
        )
        self.agent_name = "switchboard-agent"
        self.running = False
        
    async def start_monitoring(self):
        """Start monitoring for new rooms and dispatch agents"""
        self.running = True
        logger.info("🚀 Starting agent dispatcher monitoring...")
        
        while self.running:
            try:
                # Get list of active rooms
                rooms_response = await self.lkapi.room.list_rooms(api.ListRoomsRequest())
                
                for room in rooms_response.rooms:
                    # Check if this is a SIP call room (starts with "call-")
                    if room.name.startswith("call-"):
                        await self._check_and_dispatch_agent(room.name)
                
                # Wait before checking again
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in agent dispatcher: {e}")
                await asyncio.sleep(5)
    
    async def _check_and_dispatch_agent(self, room_name: str):
        """Check if agent is already dispatched to room, if not dispatch it"""
        try:
            # Check if agent is already in the room
            room_info = await self.lkapi.room.get_room(room_name)
            
            # Check if there are any agents in the room
            has_agent = False
            for participant in room_info.participants:
                if participant.identity.startswith("agent-"):
                    has_agent = True
                    break
            
            if not has_agent:
                logger.info(f"🤖 Dispatching agent to room: {room_name}")
                
                # Dispatch the agent to the room
                dispatch = await self.lkapi.agent_dispatch.create_dispatch(
                    api.CreateAgentDispatchRequest(
                        agent_name=self.agent_name,
                        room=room_name,
                        metadata='{"source": "sip_dispatcher"}'
                    )
                )
                logger.info(f"✅ Agent dispatched: {dispatch.dispatch_id}")
            else:
                logger.debug(f"Agent already in room: {room_name}")
                
        except Exception as e:
            logger.error(f"Error dispatching agent to {room_name}: {e}")
    
    async def stop(self):
        """Stop the dispatcher"""
        self.running = False
        await self.lkapi.aclose()
        logger.info("🛑 Agent dispatcher stopped")

async def main():
    """Main function to run the agent dispatcher"""
    logging.basicConfig(level=logging.INFO)
    
    dispatcher = AgentDispatcher()
    
    try:
        await dispatcher.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await dispatcher.stop()

if __name__ == "__main__":
    asyncio.run(main())
