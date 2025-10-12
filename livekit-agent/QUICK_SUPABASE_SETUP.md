# Quick Supabase Setup Guide

## Step 1: Get Your Supabase Credentials

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project (or create a new one)
3. Go to **Settings** → **API**
4. Copy these values:
   - **Project URL** (starts with `https://`)
   - **anon public** key
   - **service_role** key

## Step 2: Update Your .env File

Edit your `.env` file and replace these lines:

```bash
# Replace these with your actual values:
SUPABASE_URL=https://your-actual-project-ref.supabase.co
SUPABASE_ANON_KEY=your-actual-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-actual-service-role-key-here
```

## Step 3: Create Database Tables

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **New query**
3. Copy the entire contents of `supabase/schema.sql` and paste it
4. Click **Run** to execute
5. Create another new query
6. Copy the entire contents of `supabase/sample_data.sql` and paste it
7. Click **Run** to execute

## Step 4: Verify Setup

1. Go to **Table Editor** in Supabase
2. You should see these tables with data:
   - `departments` (5 rows)
   - `employees` (8 rows) 
   - `company_info` (1 row)
   - `call_logs` (3 sample rows)
   - `messages` (3 sample rows)

## Step 5: Test the Agent

```bash
source .venv/bin/activate
source .env
python livekit_switchboard_agent.py dev
```

## Step 6: Test Database Connection

```bash
python setup_supabase.py
```

This should show "✅ Connection successful!" if everything is working.

## Troubleshooting

- **"Connection failed"**: Check your credentials in `.env`
- **"Tables don't exist"**: Make sure you ran both SQL files
- **"Permission denied"**: Use the service_role key, not the anon key

