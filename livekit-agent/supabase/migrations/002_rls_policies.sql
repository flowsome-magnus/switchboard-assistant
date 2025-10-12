-- Enable Row Level Security on all tables
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create a service role for the agent and backend
-- This role will have full access to all tables for system operations
CREATE ROLE switchboard_service;

-- Grant necessary permissions to the service role
GRANT USAGE ON SCHEMA public TO switchboard_service;
GRANT ALL ON ALL TABLES IN SCHEMA public TO switchboard_service;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO switchboard_service;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO switchboard_service;

-- RLS Policies for departments table
-- Allow read access to all authenticated users
CREATE POLICY "Allow read access to departments" ON departments
    FOR SELECT USING (true);

-- Allow full access to service role
CREATE POLICY "Allow full access to service role" ON departments
    FOR ALL USING (current_user = 'switchboard_service');

-- RLS Policies for employees table
-- Allow read access to all authenticated users
CREATE POLICY "Allow read access to employees" ON employees
    FOR SELECT USING (true);

-- Allow full access to service role
CREATE POLICY "Allow full access to service role" ON employees
    FOR ALL USING (current_user = 'switchboard_service');

-- RLS Policies for company_info table
-- Allow read access to all authenticated users
CREATE POLICY "Allow read access to company_info" ON company_info
    FOR SELECT USING (true);

-- Allow full access to service role
CREATE POLICY "Allow full access to service role" ON company_info
    FOR ALL USING (current_user = 'switchboard_service');

-- RLS Policies for call_logs table
-- Allow read access to all authenticated users
CREATE POLICY "Allow read access to call_logs" ON call_logs
    FOR SELECT USING (true);

-- Allow insert access to all authenticated users (for logging calls)
CREATE POLICY "Allow insert access to call_logs" ON call_logs
    FOR INSERT WITH CHECK (true);

-- Allow update access to service role only
CREATE POLICY "Allow update access to service role" ON call_logs
    FOR UPDATE USING (current_user = 'switchboard_service');

-- Allow full access to service role
CREATE POLICY "Allow full access to service role" ON call_logs
    FOR ALL USING (current_user = 'switchboard_service');

-- RLS Policies for messages table
-- Allow read access to all authenticated users
CREATE POLICY "Allow read access to messages" ON messages
    FOR SELECT USING (true);

-- Allow insert access to all authenticated users (for creating messages)
CREATE POLICY "Allow insert access to messages" ON messages
    FOR INSERT WITH CHECK (true);

-- Allow update access to service role only
CREATE POLICY "Allow update access to service role" ON messages
    FOR UPDATE USING (current_user = 'switchboard_service');

-- Allow full access to service role
CREATE POLICY "Allow full access to service role" ON messages
    FOR ALL USING (current_user = 'switchboard_service');

-- Create a function to check if current user is service role
CREATE OR REPLACE FUNCTION is_service_role()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_user = 'switchboard_service';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to get current user's role
CREATE OR REPLACE FUNCTION get_current_user_role()
RETURNS TEXT AS $$
BEGIN
    RETURN current_user;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION is_service_role() TO switchboard_service;
GRANT EXECUTE ON FUNCTION get_current_user_role() TO switchboard_service;


