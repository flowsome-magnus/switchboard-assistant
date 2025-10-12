-- Switchboard Assistant Database Schema
-- Run this in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create departments table
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    available_hours JSONB DEFAULT '{"monday": {"start": "09:00", "end": "17:00"}, "tuesday": {"start": "09:00", "end": "17:00"}, "wednesday": {"start": "09:00", "end": "17:00"}, "thursday": {"start": "09:00", "end": "17:00"}, "friday": {"start": "09:00", "end": "17:00"}}',
    routing_priority INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create employees table
CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT UNIQUE NOT NULL,
    department_id UUID REFERENCES departments(id),
    office TEXT,
    roles TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'available' CHECK (status IN ('available', 'busy', 'unavailable', 'offline')),
    availability_hours JSONB DEFAULT '{"monday": {"start": "09:00", "end": "17:00"}, "tuesday": {"start": "09:00", "end": "17:00"}, "wednesday": {"start": "09:00", "end": "17:00"}, "thursday": {"start": "09:00", "end": "17:00"}, "friday": {"start": "09:00", "end": "17:00"}}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create company_info table
CREATE TABLE company_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT NOT NULL,
    greeting_message TEXT DEFAULT 'Thank you for calling. How may I direct your call?',
    business_hours JSONB DEFAULT '{"monday": {"start": "09:00", "end": "17:00"}, "tuesday": {"start": "09:00", "end": "17:00"}, "wednesday": {"start": "09:00", "end": "17:00"}, "thursday": {"start": "09:00", "end": "17:00"}, "friday": {"start": "09:00", "end": "17:00"}}',
    settings JSONB DEFAULT '{"language": "en", "timezone": "UTC", "voice": "echo"}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create call_logs table
CREATE TABLE call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    caller_phone TEXT NOT NULL,
    caller_name TEXT,
    employee_id UUID REFERENCES employees(id),
    room_name TEXT,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'transferred', 'failed', 'message_taken')),
    outcome TEXT,
    transcript TEXT,
    recording_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_caller TEXT NOT NULL,
    to_employee_id UUID REFERENCES employees(id),
    message_text TEXT NOT NULL,
    delivered_via TEXT[] DEFAULT '{}',
    delivery_details JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'delivered', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_status ON employees(status);
CREATE INDEX idx_employees_phone ON employees(phone_number);
CREATE INDEX idx_call_logs_caller ON call_logs(caller_phone);
CREATE INDEX idx_call_logs_employee ON call_logs(employee_id);
CREATE INDEX idx_call_logs_start_time ON call_logs(start_time);
CREATE INDEX idx_messages_employee ON messages(to_employee_id);
CREATE INDEX idx_messages_status ON messages(status);

-- Enable Row Level Security
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow all for now - you can restrict later)
CREATE POLICY "Allow all operations on departments" ON departments FOR ALL USING (true);
CREATE POLICY "Allow all operations on employees" ON employees FOR ALL USING (true);
CREATE POLICY "Allow all operations on company_info" ON company_info FOR ALL USING (true);
CREATE POLICY "Allow all operations on call_logs" ON call_logs FOR ALL USING (true);
CREATE POLICY "Allow all operations on messages" ON messages FOR ALL USING (true);

-- Create helper functions
CREATE OR REPLACE FUNCTION search_employees(p_query TEXT DEFAULT '', p_department TEXT DEFAULT '')
RETURNS TABLE (
    id UUID,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone_number TEXT,
    department_id UUID,
    department_name TEXT,
    office TEXT,
    roles TEXT[],
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.first_name,
        e.last_name,
        e.email,
        e.phone_number,
        e.department_id,
        d.name as department_name,
        e.office,
        e.roles,
        e.status
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE 
        (p_query = '' OR 
         e.first_name ILIKE '%' || p_query || '%' OR 
         e.last_name ILIKE '%' || p_query || '%' OR 
         e.email ILIKE '%' || p_query || '%' OR
         e.phone_number ILIKE '%' || p_query || '%' OR
         d.name ILIKE '%' || p_query || '%')
    AND (p_department = '' OR d.name ILIKE '%' || p_department || '%')
    AND e.status = 'available'
    ORDER BY d.routing_priority ASC, e.first_name ASC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION is_employee_available(p_employee_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    employee_status TEXT;
BEGIN
    SELECT status INTO employee_status
    FROM employees
    WHERE id = p_employee_id;
    
    RETURN employee_status = 'available';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION is_company_open()
RETURNS BOOLEAN AS $$
DECLARE
    current_hour INTEGER;
    current_day TEXT;
    business_hours JSONB;
    day_hours JSONB;
BEGIN
    current_hour := EXTRACT(HOUR FROM NOW());
    current_day := LOWER(TO_CHAR(NOW(), 'day'));
    current_day := TRIM(current_day);
    
    SELECT settings->'business_hours' INTO business_hours
    FROM company_info
    LIMIT 1;
    
    IF business_hours IS NULL THEN
        RETURN true; -- Default to open if no hours set
    END IF;
    
    day_hours := business_hours->current_day;
    
    IF day_hours IS NULL THEN
        RETURN false; -- Closed if no hours for this day
    END IF;
    
    -- Simple check: assume 9-17 if no specific hours
    RETURN current_hour >= 9 AND current_hour < 17;
END;
$$ LANGUAGE plpgsql;

