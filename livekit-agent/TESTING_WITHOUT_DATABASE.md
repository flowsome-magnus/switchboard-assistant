# Testing the Agent Without Database

If your Supabase project is paused, you can still test the core agent functionality!

## What Works Without Database

✅ **Voice Pipeline**
- Agent greeting
- Speech-to-text (listening)
- Text-to-speech (responding)
- Natural conversation flow

✅ **Basic Features**
- Answering calls
- Having conversations
- Basic responses

✅ **Improvements We Made**
- asyncio.Event (no polling)
- Resource cleanup
- Error handling
- All code quality improvements

## What's Limited Without Database

❌ **Employee Search** - No database to search
❌ **Warm Transfers** - Requires employee phone numbers from database
❌ **Message Taking** - No database to store messages
❌ **Company Info** - No custom greeting from database

## Quick Setup for Testing

### 1. Update your `.env` file:

```bash
# Keep these (required)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
OPENAI_API_KEY=your-openai-key

# Comment out or remove these
# SUPABASE_URL=
# SUPABASE_KEY=
# LIVEKIT_SIP_TRUNK_ID=
```

### 2. Run the agent in console mode:

```bash
uv run python livekit_switchboard_agent.py console
```

You should see:
```
Database client initialization failed: [some error]  ← This is OK!
📋 Agent initialized with instructions...
🎤 Voice pipeline configured with OpenAI Realtime Model
```

### 3. Test the conversation:

The agent will:
1. ✅ Greet you with the default message
2. ✅ Listen to your speech
3. ✅ Respond naturally
4. ✅ Handle interruptions
5. ⚠️ Say "I can't find that employee" (no database)

## What You Can Test

### Test 1: Basic Conversation
```
You: "Hello"
Agent: "Thank you for calling. How may I direct your call?"
You: "I have a question about services"
Agent: [responds naturally]
```

### Test 2: Verify No Polling
- Watch the logs - you should NOT see repeated sleep cycles
- The agent should respond quickly
- No CPU spikes

### Test 3: Error Handling
```
You: "Connect me to John"
Agent: "I'm having trouble accessing the directory right now..."
```
- Check logs for specific error messages (not generic "Exception")
- Verify graceful degradation

### Test 4: Resource Cleanup
- Make multiple test conversations
- Monitor memory usage (should be stable)
- No API connection leaks

## Expected Log Output

```
Database client initialization failed: Missing SUPABASE_URL
Database client not available, using default company info
💬 Generated greeting: 'Thank you for calling. How may I direct your call?'
```

This is **normal and expected** when database is not available!

## When You're Ready for Full Testing

Once you restore your Supabase project:

1. Update `.env` with Supabase credentials
2. Run database migrations
3. Add test employees to the database
4. Configure SIP trunk for warm transfers
5. Test full workflow with `uv run python livekit_switchboard_agent.py dev`

## Testing the Improvements

Even without the database, you can verify our improvements:

```bash
# Run the test suite
uv run python test_improvements.py
```

All tests should pass because they test code quality, not database features!

## Next Steps

**For now (testing only):**
```bash
uv run python livekit_switchboard_agent.py console
```

**When database is ready:**
1. Restore Supabase project
2. Update `.env` with credentials
3. Run full deployment workflow

The core improvements (asyncio.Event, resource cleanup, error handling) are **already working** and testable!
