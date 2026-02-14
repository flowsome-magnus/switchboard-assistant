#!/usr/bin/env python3

import asyncio
import os
from livekit.api import LiveKitAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def delete_dispatch_rule():
    """Delete the existing SIP dispatch rule"""

    # Validate environment variables
    url = os.getenv('LIVEKIT_URL')
    api_key = os.getenv('LIVEKIT_API_KEY')
    api_secret = os.getenv('LIVEKIT_API_SECRET')

    if not all([url, api_key, api_secret]):
        raise ValueError("Missing required environment variables: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET")

    # Initialize LiveKit API client
    lkapi = LiveKitAPI(url, api_key, api_secret)

    try:
        # Delete the existing dispatch rule
        await lkapi.sip.delete_dispatch_rule('SDR_Gp4XBkW88D5g')
        print('✅ Successfully deleted existing dispatch rule')
        
    except Exception as e:
        print(f'❌ Error deleting dispatch rule: {e}')
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(delete_dispatch_rule())

