-- Migration: Remove latitude/longitude from donors, remove OTP table, remove waste tables

-- 1. Drop OTP verification table if it exists
DROP TABLE IF EXISTS otp_verifications CASCADE;

-- 2. Remove latitude and longitude columns from donors table if they exist
ALTER TABLE donors
DROP COLUMN IF EXISTS latitude CASCADE,
DROP COLUMN IF EXISTS longitude CASCADE;

-- 3. Ensure address column exists (if not already present)
ALTER TABLE donors
ADD COLUMN IF NOT EXISTS address TEXT NOT NULL DEFAULT 'Not Provided';

-- 4. Drop any waste-related tables if they exist
DROP TABLE IF EXISTS waste CASCADE;
DROP TABLE IF EXISTS waste_collection CASCADE;
DROP TABLE IF EXISTS waste_management CASCADE;
DROP TABLE IF EXISTS waste_records CASCADE;

-- Confirm donors table structure
-- SELECT column_name, data_type FROM information_schema.columns 
-- WHERE table_name = 'donors' AND table_schema = 'public';
