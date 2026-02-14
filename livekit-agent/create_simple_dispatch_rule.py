#!/usr/bin/env python3
"""
Create a simple SIP dispatch rule for switchboard-agent
"""
import asyncio
import os
from livekit import api

async def create_simple_dispatch_rule():
    # Initialize LiveKit API client
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([url, api_key, api_secret]):
        raise ValueError("Missing required environment variables: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET")

    lkapi = api.LiveKitAPI(
        url=url,
        api_key=api_key,
        api_secret=api_secret
    )
    
    try:
        # Create a simple dispatch rule without room_config
        print("🚀 Creating simple SIP dispatch rule...")
        
        dispatch_rule = await lkapi.sip.create_sip_dispatch_rule(
            api.CreateSIPDispatchRuleRequest(
                rule=api.SIPDispatchRule(
                    dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                        room_prefix="call-"
                    )
                ),
                trunk_ids=[],  # Accept all trunks
                hide_phone_number=False
            )
        )
        
        print(f"✅ Created dispatch rule: {dispatch_rule.sip_dispatch_rule_id}")
        print(f"   Rule type: Individual (Caller)")
        print(f"   Room prefix: call-")
        print(f"   Note: Agent will be dispatched manually via agent dispatcher")
        
        return dispatch_rule.sip_dispatch_rule_id
        
    except Exception as e:
        print(f"❌ Error creating dispatch rule: {e}")
        return None
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(create_simple_dispatch_rule())







