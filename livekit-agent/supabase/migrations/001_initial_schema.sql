-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create departments table
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    available_hours JSONB DEFAULT '{}',
    routing_priority INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create employees table
CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
    office VARCHAR(255),
    roles TEXT[] DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'available' CHECK (status IN ('available', 'busy', 'offline', 'unavailable')),
    availability_hours JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create company_info table
CREATE TABLE company_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL DEFAULT 'Your Company',
    greeting_message TEXT DEFAULT 'Thank you for calling. How may I direct your call?',
    business_hours JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create call_logs table
CREATE TABLE call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    caller_phone VARCHAR(20) NOT NULL,
    caller_name VARCHAR(255),
    employee_id UUID REFERENCES employees(id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    duration INTERVAL,
    status VARCHAR(50) DEFAULT 'completed' CHECK (status IN ('completed', 'missed', 'transferred', 'failed')),
    recording_url TEXT,
    room_id VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_caller VARCHAR(20) NOT NULL,
    to_employee_id UUID REFERENCES employees(id) ON DELETE SET NULL,
    message_text TEXT NOT NULL,
    delivered_via TEXT[] DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'delivered', 'failed', 'read')),
    delivery_details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_employees_department_id ON employees(department_id);
CREATE INDEX idx_employees_status ON employees(status);
CREATE INDEX idx_employees_phone ON employees(phone);
CREATE INDEX idx_employees_email ON employees(email);

CREATE INDEX idx_call_logs_employee_id ON call_logs(employee_id);
CREATE INDEX idx_call_logs_timestamp ON call_logs(timestamp);
CREATE INDEX idx_call_logs_caller_phone ON call_logs(caller_phone);
CREATE INDEX idx_call_logs_status ON call_logs(status);

CREATE INDEX idx_messages_employee_id ON messages(to_employee_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_from_caller ON messages(from_caller);
CREATE INDEX idx_messages_status ON messages(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_info_updated_at BEFORE UPDATE ON company_info
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_call_logs_updated_at BEFORE UPDATE ON call_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default company info
INSERT INTO company_info (company_name, greeting_message, business_hours, settings) VALUES (
    'Your Company',
    'Thank you for calling. How may I direct your call?',
    '{
        "monday": {"start": "09:00", "end": "17:00", "enabled": true},
        "tuesday": {"start": "09:00", "end": "17:00", "enabled": true},
        "wednesday": {"start": "09:00", "end": "17:00", "enabled": true},
        "thursday": {"start": "09:00", "end": "17:00", "enabled": true},
        "friday": {"start": "09:00", "end": "17:00", "enabled": true},
        "saturday": {"start": "10:00", "end": "14:00", "enabled": false},
        "sunday": {"start": "10:00", "end": "14:00", "enabled": false}
    }',
    '{
        "language": "en",
        "timezone": "America/New_York",
        "max_call_duration": 3600,
        "enable_recording": true,
        "warm_transfer_enabled": true,
        "message_delivery_enabled": true,
        "default_department": "Support"
    }'
);

-- Insert sample departments
INSERT INTO departments (name, description, available_hours, routing_priority) VALUES 
(
    'Management',
    'Executive and management team',
    '{
        "monday": {"start": "09:00", "end": "17:00", "enabled": true},
        "tuesday": {"start": "09:00", "end": "17:00", "enabled": true},
        "wednesday": {"start": "09:00", "end": "17:00", "enabled": true},
        "thursday": {"start": "09:00", "end": "17:00", "enabled": true},
        "friday": {"start": "09:00", "end": "17:00", "enabled": true}
    }',
    1
),
(
    'Sales',
    'Sales and business development',
    '{
        "monday": {"start": "08:00", "end": "18:00", "enabled": true},
        "tuesday": {"start": "08:00", "end": "18:00", "enabled": true},
        "wednesday": {"start": "08:00", "end": "18:00", "enabled": true},
        "thursday": {"start": "08:00", "end": "18:00", "enabled": true},
        "friday": {"start": "08:00", "end": "18:00", "enabled": true}
    }',
    2
),
(
    'Support',
    'Customer support and technical assistance',
    '{
        "monday": {"start": "08:00", "end": "20:00", "enabled": true},
        "tuesday": {"start": "08:00", "end": "20:00", "enabled": true},
        "wednesday": {"start": "08:00", "end": "20:00", "enabled": true},
        "thursday": {"start": "08:00", "end": "20:00", "enabled": true},
        "friday": {"start": "08:00", "end": "20:00", "enabled": true},
        "saturday": {"start": "10:00", "end": "16:00", "enabled": true},
        "sunday": {"start": "10:00", "end": "16:00", "enabled": true}
    }',
    3
);

-- Insert sample employees
INSERT INTO employees (name, phone, email, department_id, office, roles, status, availability_hours) VALUES 
(
    'John Smith',
    '+1234567890',
    'john@company.com',
    (SELECT id FROM departments WHERE name = 'Management'),
    'Main Office',
    ARRAY['manager', 'executive'],
    'available',
    '{
        "monday": {"start": "09:00", "end": "17:00", "enabled": true},
        "tuesday": {"start": "09:00", "end": "17:00", "enabled": true},
        "wednesday": {"start": "09:00", "end": "17:00", "enabled": true},
        "thursday": {"start": "09:00", "end": "17:00", "enabled": true},
        "friday": {"start": "09:00", "end": "17:00", "enabled": true}
    }'
),
(
    'Jane Doe',
    '+1234567891',
    'jane@company.com',
    (SELECT id FROM departments WHERE name = 'Sales'),
    'Main Office',
    ARRAY['sales_rep', 'senior_sales'],
    'available',
    '{
        "monday": {"start": "08:00", "end": "18:00", "enabled": true},
        "tuesday": {"start": "08:00", "end": "18:00", "enabled": true},
        "wednesday": {"start": "08:00", "end": "18:00", "enabled": true},
        "thursday": {"start": "08:00", "end": "18:00", "enabled": true},
        "friday": {"start": "08:00", "end": "18:00", "enabled": true}
    }'
),
(
    'Mike Johnson',
    '+1234567892',
    'mike@company.com',
    (SELECT id FROM departments WHERE name = 'Support'),
    'Branch Office',
    ARRAY['support_rep', 'technical_support'],
    'available',
    '{
        "monday": {"start": "08:00", "end": "20:00", "enabled": true},
        "tuesday": {"start": "08:00", "end": "20:00", "enabled": true},
        "wednesday": {"start": "08:00", "end": "20:00", "enabled": true},
        "thursday": {"start": "08:00", "end": "20:00", "enabled": true},
        "friday": {"start": "08:00", "end": "20:00", "enabled": true},
        "saturday": {"start": "10:00", "end": "16:00", "enabled": true}
    }'
),
(
    'Sarah Wilson',
    '+1234567893',
    'sarah@company.com',
    (SELECT id FROM departments WHERE name = 'Support'),
    'Main Office',
    ARRAY['support_rep', 'team_lead'],
    'available',
    '{
        "monday": {"start": "08:00", "end": "20:00", "enabled": true},
        "tuesday": {"start": "08:00", "end": "20:00", "enabled": true},
        "wednesday": {"start": "08:00", "end": "20:00", "enabled": true},
        "thursday": {"start": "08:00", "end": "20:00", "enabled": true},
        "friday": {"start": "08:00", "end": "20:00", "enabled": true},
        "sunday": {"start": "10:00", "end": "16:00", "enabled": true}
    }'
);


