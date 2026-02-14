#!/usr/bin/env python3
"""
List existing SIP dispatch rules
"""
import asyncio
import os
from livekit import api

async def list_dispatch_rules():
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
        print("📋 Listing existing SIP dispatch rules...")
        
        # List dispatch rules
        response = await lkapi.sip.list_sip_dispatch_rule(
            api.ListSIPDispatchRuleRequest()
        )
        
        print(f"Found {len(response.items)} dispatch rules:")
        for rule in response.items:
            print(f"  - ID: {rule.sip_dispatch_rule_id}")
            print(f"    Rule: {rule.rule}")
            print(f"    Trunk IDs: {rule.trunk_ids}")
            print(f"    Hide Phone: {rule.hide_phone_number}")
            print()
        
        return response.items
        
    except Exception as e:
        print(f"❌ Error listing dispatch rules: {e}")
        return []
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(list_dispatch_rules())







