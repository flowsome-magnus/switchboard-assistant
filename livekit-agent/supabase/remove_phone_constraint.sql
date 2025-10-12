-- Remove unique constraint from phone_number and set all to your number
-- Run this in your Supabase SQL editor

-- First, drop the unique constraint on phone_number
ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_phone_number_key;

-- Update all employees to use your phone number
UPDATE employees SET phone_number = '+46702778411';

-- Optional: Add a comment to document this change
COMMENT ON COLUMN employees.phone_number IS 'Phone number - unique constraint removed for testing purposes';
