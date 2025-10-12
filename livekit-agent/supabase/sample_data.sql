-- Sample data for Switchboard Assistant
-- Run this after creating the schema

-- Insert sample departments
INSERT INTO departments (name, description, routing_priority) VALUES
('Management', 'Executive and management team', 1),
('Sales', 'Sales and business development', 2),
('Support', 'Customer support and technical assistance', 3),
('HR', 'Human resources and administration', 4),
('Finance', 'Accounting and financial services', 5);

-- Insert sample employees with real phone numbers for testing
INSERT INTO employees (first_name, last_name, email, phone_number, department_id, office, roles, status) VALUES
('John', 'Smith', 'john.smith@company.com', '+46701234567', (SELECT id FROM departments WHERE name = 'Management'), 'A101', ARRAY['CEO', 'Executive'], 'available'),
('Sarah', 'Johnson', 'sarah.johnson@company.com', '+46701234568', (SELECT id FROM departments WHERE name = 'Management'), 'A102', ARRAY['CTO', 'Technical Lead'], 'available'),
('Mike', 'Davis', 'mike.davis@company.com', '+46701234569', (SELECT id FROM departments WHERE name = 'Sales'), 'B201', ARRAY['Sales Manager'], 'available'),
('Lisa', 'Wilson', 'lisa.wilson@company.com', '+46701234570', (SELECT id FROM departments WHERE name = 'Sales'), 'B202', ARRAY['Sales Representative'], 'available'),
('Tom', 'Brown', 'tom.brown@company.com', '+46701234571', (SELECT id FROM departments WHERE name = 'Support'), 'C301', ARRAY['Support Lead'], 'available'),
('Emma', 'Garcia', 'emma.garcia@company.com', '+46701234572', (SELECT id FROM departments WHERE name = 'Support'), 'C302', ARRAY['Support Specialist'], 'available'),
('David', 'Miller', 'david.miller@company.com', '+46701234573', (SELECT id FROM departments WHERE name = 'HR'), 'D401', ARRAY['HR Manager'], 'available'),
('Anna', 'Taylor', 'anna.taylor@company.com', '+46701234574', (SELECT id FROM departments WHERE name = 'Finance'), 'E501', ARRAY['CFO', 'Finance Manager'], 'available');

-- Insert company info
INSERT INTO company_info (company_name, greeting_message, business_hours, settings) VALUES
('Acme Corporation', 'Hello! Thank you for calling Acme Corporation. How may I direct your call today?', 
 '{"monday": {"start": "09:00", "end": "17:00"}, "tuesday": {"start": "09:00", "end": "17:00"}, "wednesday": {"start": "09:00", "end": "17:00"}, "thursday": {"start": "09:00", "end": "17:00"}, "friday": {"start": "09:00", "end": "17:00"}}',
 '{"language": "en", "timezone": "UTC", "voice": "echo", "max_call_duration": 3600}');

-- Insert some sample call logs
INSERT INTO call_logs (caller_phone, caller_name, employee_id, room_name, status, outcome) VALUES
('+1987654321', 'Jane Doe', (SELECT id FROM employees WHERE email = 'john.smith@company.com'), 'call-20241012-001', 'completed', 'Transferred to CEO'),
('+1987654322', 'Bob Smith', (SELECT id FROM employees WHERE email = 'lisa.wilson@company.com'), 'call-20241012-002', 'completed', 'Sales inquiry handled'),
('+1987654323', 'Alice Johnson', (SELECT id FROM employees WHERE email = 'tom.brown@company.com'), 'call-20241012-003', 'completed', 'Technical support provided');

-- Insert some sample messages
INSERT INTO messages (from_caller, to_employee_id, message_text, delivered_via, status) VALUES
('+1987654324', (SELECT id FROM employees WHERE email = 'john.smith@company.com'), 'Please call me back about the quarterly report. Urgent!', ARRAY['sms', 'email'], 'delivered'),
('+1987654325', (SELECT id FROM employees WHERE email = 'mike.davis@company.com'), 'Interested in your premium package. Please contact me.', ARRAY['sms'], 'delivered'),
('+1987654326', (SELECT id FROM employees WHERE email = 'emma.garcia@company.com'), 'Having issues with my account. Need help ASAP.', ARRAY['email'], 'pending');

