#!/usr/bin/env python3
"""
Create a SIP dispatch rule with agent dispatch configuration
"""
import asyncio
import os
from livekit import api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_dispatch_rule_with_agent():
    """Create a new SIP dispatch rule with agent dispatch"""

    # Validate environment variables
    url = os.getenv('LIVEKIT_URL')
    api_key = os.getenv('LIVEKIT_API_KEY')
    api_secret = os.getenv('LIVEKIT_API_SECRET')

    if not all([url, api_key, api_secret]):
        raise ValueError("Missing required environment variables: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET")

    # Initialize LiveKit API client
    lkapi = api.LiveKitAPI(url=url, api_key=api_key, api_secret=api_secret)

    try:
        print("🚀 Creating SIP dispatch rule with agent configuration...")

        # Create dispatch rule with agent configuration
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

        print(f'✅ Successfully created dispatch rule: {dispatch_rule.sip_dispatch_rule_id}')
        print(f'   Room prefix: call-')
        print(f'   Agent: switchboard-agent')
        print(f'   Agent will be automatically dispatched to SIP call rooms!')

        return dispatch_rule.sip_dispatch_rule_id

    except Exception as e:
        print(f'❌ Error creating dispatch rule: {e}')
        return None
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(create_dispatch_rule_with_agent())

