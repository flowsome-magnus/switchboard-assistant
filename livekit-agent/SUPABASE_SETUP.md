# Supabase Setup Instructions

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `switchboard-assistant`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your location
5. Click "Create new project"
6. Wait for the project to be created (2-3 minutes)

## 2. Get Your Project Credentials

1. Go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (starts with `https://`)
   - **anon public** key
   - **service_role** key (keep this secret!)

## 3. Set Up Database Schema

1. Go to **SQL Editor** in your Supabase dashboard
2. Copy the contents of `supabase/schema.sql` and paste it into the editor
3. Click **Run** to execute the schema creation
4. Copy the contents of `supabase/sample_data.sql` and paste it into the editor
5. Click **Run** to add sample data

## 4. Configure Environment Variables

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your Supabase credentials:
   ```bash
   # Supabase
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

## 5. Test the Setup

1. Start the agent:
   ```bash
   source .venv/bin/activate
   source .env
   python livekit_switchboard_agent.py dev
   ```

2. Look for these log messages:
   ```
   INFO:__main__:Database client initialized successfully
   INFO:__main__:✅ Session started, generating greeting...
   ```

## 6. Verify Database Content

1. Go to **Table Editor** in Supabase
2. Check that these tables exist and have data:
   - `departments` (5 rows)
   - `employees` (8 rows)
   - `company_info` (1 row)
   - `call_logs` (3 sample rows)
   - `messages` (3 sample rows)

## 7. Test Agent Functions

Call your Twilio number and try these commands:

- **"Search for employees"** - Should list all available employees
- **"Find John Smith"** - Should find the CEO
- **"What departments do you have?"** - Should list all departments
- **"Take a message for Sarah Johnson"** - Should record a message

## Troubleshooting

### Database Connection Issues
- Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check that your project is not paused
- Ensure the service role key is used for backend operations

### Schema Issues
- Make sure you ran both `schema.sql` and `sample_data.sql`
- Check the SQL Editor for any error messages
- Verify all tables were created successfully

### Agent Issues
- Check the logs for "Database client initialized successfully"
- If you see "Database client initialization failed", check your environment variables
- The agent will still work without the database, but with limited functionality

## Next Steps

Once the database is working:
1. Test all the search functions
2. Add your own employees and departments
3. Customize the company greeting message
4. Set up proper business hours
5. Configure message delivery (SMS/Email) in the next phase

