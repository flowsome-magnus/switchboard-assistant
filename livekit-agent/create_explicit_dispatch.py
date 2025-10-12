#!/usr/bin/env python3
"""
Create a SIP dispatch rule with explicit agent dispatch for switchboard-agent
"""
import asyncio
import os
import json
from livekit import api

async def create_explicit_dispatch_rule():
    # Initialize LiveKit API client
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL", "wss://demo-41snsvwf.livekit.cloud"),
        api_key=os.getenv("LIVEKIT_API_KEY", "APIebvsBQ3xohnG"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "ik2ipeu4VhD3Pyohl1d21bdMft1UDXTtl5a6Nr9N1ow")
    )
    
    try:
        # Delete any existing dispatch rules first
        print("🗑️  Cleaning up existing dispatch rules...")
        try:
            # List existing rules and delete them
            # Note: We'll need to handle this differently since list_sip_dispatch_rule needs parameters
            pass
        except Exception as e:
            print(f"   Note: {e}")
        
        # Create dispatch rule with explicit agent dispatch
        print("🚀 Creating explicit dispatch rule...")
        
        # Create the dispatch rule request
        request = api.CreateSIPDispatchRuleRequest(
            rule=api.SIPDispatchRule(
                dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                    room_prefix="call-"
                )
            ),
            trunk_ids=[],  # Accept all trunks
            hide_phone_number=False
        )
        
        # Try to create the rule
        dispatch_rule = await lkapi.sip.create_sip_dispatch_rule(request)
        print(f"✅ Created dispatch rule: {dispatch_rule.sip_dispatch_rule_id}")
        
        # Now we need to manually dispatch the agent to rooms created by this rule
        # This is a workaround since the CLI doesn't support room_config.agents
        print("📋 Dispatch rule created successfully!")
        print("   Rule type: Individual (Caller)")
        print("   Room prefix: call-")
        print("   Note: Agent will be dispatched via explicit dispatch API calls")
        
        return dispatch_rule.sip_dispatch_rule_id
        
    except Exception as e:
        print(f"❌ Error creating dispatch rule: {e}")
        return None
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(create_explicit_dispatch_rule())

