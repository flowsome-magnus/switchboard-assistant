#!/usr/bin/env python3
"""
Update the existing SIP dispatch rule to include agent dispatch
"""
import asyncio
import os
import json
from livekit import api

async def update_dispatch_rule():
    # Initialize LiveKit API client
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL", "wss://demo-41snsvwf.livekit.cloud"),
        api_key=os.getenv("LIVEKIT_API_KEY", "APIebvsBQ3xohnG"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "ik2ipeu4VhD3Pyohl1d21bdMft1UDXTtl5a6Nr9N1ow")
    )
    
    try:
        # First, delete the existing dispatch rule
        print("🗑️  Deleting existing dispatch rule...")
        try:
            await lkapi.sip.delete_sip_dispatch_rule(
                api.DeleteSIPDispatchRuleRequest(
                    sip_dispatch_rule_id="SDR_Gp4XBkW88D5g"
                )
            )
            print("✅ Deleted existing dispatch rule")
        except Exception as e:
            print(f"   Note: {e}")
        
        # Create new dispatch rule with agent configuration
        print("🚀 Creating new dispatch rule with agent dispatch...")
        
        dispatch_rule = await lkapi.sip.create_sip_dispatch_rule(
            api.CreateSIPDispatchRuleRequest(
                rule=api.SIPDispatchRule(
                    dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                        room_prefix="call-"
                    )
                ),
                name="Switchboard Agent Dispatch Rule",
                room_config=api.RoomConfiguration(
                    agents=[
                        api.RoomAgentDispatch(
                            agent_name="switchboard-agent",
                            metadata='{"source": "sip_dispatch_rule"}'
                        )
                    ]
                ),
                trunk_ids=[],  # Accept all trunks
                hide_phone_number=False
            )
        )
        
        print(f"✅ Created new dispatch rule: {dispatch_rule.sip_dispatch_rule_id}")
        print(f"   Rule type: Individual (Caller)")
        print(f"   Room prefix: call-")
        print(f"   Agent: switchboard-agent")
        print(f"   Agent will be automatically dispatched to SIP call rooms!")
        
        return dispatch_rule.sip_dispatch_rule_id
        
    except Exception as e:
        print(f"❌ Error updating dispatch rule: {e}")
        return None
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(update_dispatch_rule())