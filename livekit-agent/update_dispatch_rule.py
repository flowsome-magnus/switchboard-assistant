#!/usr/bin/env python3
"""
Update the SIP dispatch rule to include explicit agent dispatch
"""
import asyncio
import os
from livekit import api

async def update_dispatch_rule():
    # Initialize LiveKit API client
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL", "wss://demo-41snsvwf.livekit.cloud"),
        api_key=os.getenv("LIVEKIT_API_KEY", "APIebvsBQ3xohnG"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "ik2ipeu4VhD3Pyohl1d21bdMft1UDXTtl5a6Nr9N1ow")
    )
    
    try:
        # First, get the current dispatch rule
        dispatch_rules = await lkapi.sip.list_sip_dispatch_rule()
        current_rule = None
        
        for rule in dispatch_rules:
            if rule.sip_dispatch_rule_id == "SDR_ukD7wiTV2yrk":
                current_rule = rule
                break
        
        if not current_rule:
            print("❌ Dispatch rule not found")
            return
            
        print(f"✅ Found dispatch rule: {current_rule.sip_dispatch_rule_id}")
        print(f"   Current rule type: {type(current_rule.rule).__name__}")
        
        # Try to update the rule with agent configuration
        # Note: This might not work if the API doesn't support updating room_config
        try:
            updated_rule = await lkapi.sip.update_sip_dispatch_rule(
                api.UpdateSIPDispatchRuleRequest(
                    sip_dispatch_rule_id="SDR_ukD7wiTV2yrk",
                    rule=api.SIPDispatchRule(
                        dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                            room_prefix="call-"
                        )
                    )
                )
            )
            print(f"✅ Updated dispatch rule: {updated_rule.sip_dispatch_rule_id}")
        except Exception as e:
            print(f"❌ Error updating dispatch rule: {e}")
            print("   This might be expected if the API doesn't support room_config updates")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(update_dispatch_rule())

