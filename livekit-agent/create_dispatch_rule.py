#!/usr/bin/env python3
"""
Create a SIP dispatch rule with explicit agent dispatch for switchboard-agent
"""
import asyncio
import os
from livekit import api

async def create_dispatch_rule():
    # Initialize LiveKit API client
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL", "wss://demo-41snsvwf.livekit.cloud"),
        api_key=os.getenv("LIVEKIT_API_KEY", "APIebvsBQ3xohnG"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "ik2ipeu4VhD3Pyohl1d21bdMft1UDXTtl5a6Nr9N1ow")
    )
    
    try:
        # Create dispatch rule with explicit agent dispatch
        dispatch_rule = await lkapi.sip.create_sip_dispatch_rule(
            api.CreateSIPDispatchRuleRequest(
                rule=api.SIPDispatchRule(
                    dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                        room_prefix="call-",
                        room_config=api.RoomConfiguration(
                            agents=[
                                api.RoomAgentDispatch(
                                    agent_name="switchboard-agent"
                                )
                            ]
                        )
                    )
                ),
                trunk_ids=[],  # Accept all trunks
                hide_phone_number=False
            )
        )
        
        print(f"✅ Created dispatch rule: {dispatch_rule.sip_dispatch_rule_id}")
        print(f"   Rule type: Individual (Caller)")
        print(f"   Room prefix: call-")
        print(f"   Agent: switchboard-agent")
        
    except Exception as e:
        print(f"❌ Error creating dispatch rule: {e}")
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(create_dispatch_rule())
