-- Function to search employees by name, department, or role
CREATE OR REPLACE FUNCTION search_employees(
    search_query TEXT DEFAULT NULL,
    department_name TEXT DEFAULT NULL,
    employee_status TEXT DEFAULT 'available'
)
RETURNS TABLE (
    id UUID,
    name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    department_id UUID,
    department_name VARCHAR(255),
    office VARCHAR(255),
    roles TEXT[],
    status VARCHAR(50),
    availability_hours JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.name,
        e.phone,
        e.email,
        e.department_id,
        d.name as department_name,
        e.office,
        e.roles,
        e.status,
        e.availability_hours
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE 
        (search_query IS NULL OR 
         e.name ILIKE '%' || search_query || '%' OR 
         e.email ILIKE '%' || search_query || '%' OR
         e.phone ILIKE '%' || search_query || '%')
        AND (department_name IS NULL OR d.name ILIKE '%' || department_name || '%')
        AND (employee_status IS NULL OR e.status = employee_status)
    ORDER BY 
        CASE WHEN e.status = 'available' THEN 1 ELSE 2 END,
        d.routing_priority,
        e.name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if an employee is available at a specific time
CREATE OR REPLACE FUNCTION is_employee_available(
    employee_id_param UUID,
    check_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS BOOLEAN AS $$
DECLARE
    employee_record RECORD;
    day_name TEXT;
    day_hours JSONB;
    start_time TIME;
    end_time TIME;
    is_enabled BOOLEAN;
BEGIN
    -- Get employee record
    SELECT e.*, d.name as department_name
    INTO employee_record
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE e.id = employee_id_param;
    
    -- If employee not found, return false
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- If employee status is not available, return false
    IF employee_record.status != 'available' THEN
        RETURN FALSE;
    END IF;
    
    -- Get day name (lowercase)
    day_name := LOWER(TO_CHAR(check_time, 'day'));
    
    -- Get availability hours for the day
    day_hours := employee_record.availability_hours->day_name;
    
    -- If no hours set for this day, return false
    IF day_hours IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Check if day is enabled
    is_enabled := COALESCE((day_hours->>'enabled')::BOOLEAN, FALSE);
    IF NOT is_enabled THEN
        RETURN FALSE;
    END IF;
    
    -- Get start and end times
    start_time := (day_hours->>'start')::TIME;
    end_time := (day_hours->>'end')::TIME;
    
    -- Check if current time is within availability window
    RETURN (check_time::TIME >= start_time AND check_time::TIME <= end_time);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get available employees for a department
CREATE OR REPLACE FUNCTION get_available_employees(
    department_name_param TEXT DEFAULT NULL,
    check_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS TABLE (
    id UUID,
    name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    department_id UUID,
    department_name VARCHAR(255),
    office VARCHAR(255),
    roles TEXT[],
    availability_hours JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.name,
        e.phone,
        e.email,
        e.department_id,
        d.name as department_name,
        e.office,
        e.roles,
        e.availability_hours
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE 
        e.status = 'available'
        AND (department_name_param IS NULL OR d.name ILIKE '%' || department_name_param || '%')
        AND is_employee_available(e.id, check_time)
    ORDER BY 
        d.routing_priority,
        e.name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log a call
CREATE OR REPLACE FUNCTION log_call(
    caller_phone_param VARCHAR(20),
    caller_name_param VARCHAR(255) DEFAULT NULL,
    employee_id_param UUID DEFAULT NULL,
    call_duration INTERVAL DEFAULT NULL,
    call_status VARCHAR(50) DEFAULT 'completed',
    recording_url_param TEXT DEFAULT NULL,
    room_id_param VARCHAR(255) DEFAULT NULL,
    notes_param TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    call_id UUID;
BEGIN
    INSERT INTO call_logs (
        caller_phone,
        caller_name,
        employee_id,
        duration,
        status,
        recording_url,
        room_id,
        notes
    ) VALUES (
        caller_phone_param,
        caller_name_param,
        employee_id_param,
        call_duration,
        call_status,
        recording_url_param,
        room_id_param,
        notes_param
    ) RETURNING id INTO call_id;
    
    RETURN call_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to save a message
CREATE OR REPLACE FUNCTION save_message(
    from_caller_param VARCHAR(20),
    to_employee_id_param UUID,
    message_text_param TEXT,
    delivered_via_param TEXT[] DEFAULT ARRAY[]::TEXT[],
    delivery_details_param JSONB DEFAULT '{}'::JSONB
)
RETURNS UUID AS $$
DECLARE
    message_id UUID;
BEGIN
    INSERT INTO messages (
        from_caller,
        to_employee_id,
        message_text,
        delivered_via,
        delivery_details
    ) VALUES (
        from_caller_param,
        to_employee_id_param,
        message_text_param,
        delivered_via_param,
        delivery_details_param
    ) RETURNING id INTO message_id;
    
    RETURN message_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update message delivery status
CREATE OR REPLACE FUNCTION update_message_status(
    message_id_param UUID,
    new_status VARCHAR(50),
    delivery_details_param JSONB DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE messages 
    SET 
        status = new_status,
        delivery_details = COALESCE(delivery_details_param, delivery_details),
        updated_at = NOW()
    WHERE id = message_id_param;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get company business hours
CREATE OR REPLACE FUNCTION get_company_business_hours()
RETURNS JSONB AS $$
DECLARE
    business_hours JSONB;
BEGIN
    SELECT business_hours INTO business_hours
    FROM company_info
    ORDER BY created_at DESC
    LIMIT 1;
    
    RETURN COALESCE(business_hours, '{}'::JSONB);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if company is open
CREATE OR REPLACE FUNCTION is_company_open(
    check_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS BOOLEAN AS $$
DECLARE
    business_hours JSONB;
    day_name TEXT;
    day_hours JSONB;
    start_time TIME;
    end_time TIME;
    is_enabled BOOLEAN;
BEGIN
    -- Get business hours
    business_hours := get_company_business_hours();
    
    -- Get day name (lowercase)
    day_name := LOWER(TO_CHAR(check_time, 'day'));
    
    -- Get hours for the day
    day_hours := business_hours->day_name;
    
    -- If no hours set for this day, return false
    IF day_hours IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Check if day is enabled
    is_enabled := COALESCE((day_hours->>'enabled')::BOOLEAN, FALSE);
    IF NOT is_enabled THEN
        RETURN FALSE;
    END IF;
    
    -- Get start and end times
    start_time := (day_hours->>'start')::TIME;
    end_time := (day_hours->>'end')::TIME;
    
    -- Check if current time is within business hours
    RETURN (check_time::TIME >= start_time AND check_time::TIME <= end_time);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get employee by phone number
CREATE OR REPLACE FUNCTION get_employee_by_phone(phone_param VARCHAR(20))
RETURNS TABLE (
    id UUID,
    name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    department_id UUID,
    department_name VARCHAR(255),
    office VARCHAR(255),
    roles TEXT[],
    status VARCHAR(50),
    availability_hours JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.name,
        e.phone,
        e.email,
        e.department_id,
        d.name as department_name,
        e.office,
        e.roles,
        e.status,
        e.availability_hours
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE e.phone = phone_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions on all functions to service role
GRANT EXECUTE ON FUNCTION search_employees(TEXT, TEXT, TEXT) TO switchboard_service;
GRANT EXECUTE ON FUNCTION is_employee_available(UUID, TIMESTAMP WITH TIME ZONE) TO switchboard_service;
GRANT EXECUTE ON FUNCTION get_available_employees(TEXT, TIMESTAMP WITH TIME ZONE) TO switchboard_service;
GRANT EXECUTE ON FUNCTION log_call(VARCHAR, VARCHAR, UUID, INTERVAL, VARCHAR, TEXT, VARCHAR, TEXT) TO switchboard_service;
GRANT EXECUTE ON FUNCTION save_message(VARCHAR, UUID, TEXT, TEXT[], JSONB) TO switchboard_service;
GRANT EXECUTE ON FUNCTION update_message_status(UUID, VARCHAR, JSONB) TO switchboard_service;
GRANT EXECUTE ON FUNCTION get_company_business_hours() TO switchboard_service;
GRANT EXECUTE ON FUNCTION is_company_open(TIMESTAMP WITH TIME ZONE) TO switchboard_service;
GRANT EXECUTE ON FUNCTION get_employee_by_phone(VARCHAR) TO switchboard_service;


