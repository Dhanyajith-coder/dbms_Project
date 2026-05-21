-- Migration: add acceptances, OTP verification, donor address, and entity codes

-- Donor cleanup: drop latitude/longitude if they exist and add address/code fields
ALTER TABLE donors
  DROP COLUMN IF EXISTS latitude,
  DROP COLUMN IF EXISTS longitude;

ALTER TABLE donors
  ADD COLUMN IF NOT EXISTS address TEXT;

ALTER TABLE donors
  ADD COLUMN IF NOT EXISTS donor_code TEXT UNIQUE;

-- Hospital cleanup: add hospital_code if missing
ALTER TABLE hospitals
  ADD COLUMN IF NOT EXISTS hospital_code TEXT UNIQUE;

-- Ensure blood_requests has expected columns
ALTER TABLE blood_requests
  ADD COLUMN IF NOT EXISTS request_code TEXT UNIQUE;

ALTER TABLE blood_requests
  ADD COLUMN IF NOT EXISTS hospital_name TEXT;

ALTER TABLE blood_requests
  ADD COLUMN IF NOT EXISTS blood_type TEXT;

ALTER TABLE blood_requests
  ADD COLUMN IF NOT EXISTS units_needed INTEGER DEFAULT 1;

ALTER TABLE blood_requests
  ADD COLUMN IF NOT EXISTS units_collected INTEGER DEFAULT 0;

ALTER TABLE blood_requests
  ADD COLUMN IF NOT EXISTS urgency TEXT DEFAULT 'Normal';

ALTER TABLE blood_requests
  ADD COLUMN IF NOT EXISTS description TEXT;

ALTER TABLE blood_requests
  ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'open';

-- Create acceptances table if missing
CREATE TABLE IF NOT EXISTS acceptances (
  id BIGSERIAL PRIMARY KEY,
  acceptance_code TEXT UNIQUE NOT NULL,
  request_id BIGINT NOT NULL,
  donor_name TEXT,
  donor_phone VARCHAR(15),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create OTP verification table
CREATE TABLE IF NOT EXISTS otp_verifications (
  id BIGSERIAL PRIMARY KEY,
  otp_code TEXT NOT NULL,
  phone VARCHAR(15) NOT NULL,
  purpose TEXT NOT NULL,
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes to speed up lookups
CREATE INDEX IF NOT EXISTS idx_acceptances_request ON acceptances(request_id);
CREATE INDEX IF NOT EXISTS idx_acceptances_phone ON acceptances(donor_phone);
CREATE INDEX IF NOT EXISTS idx_requests_status ON blood_requests(status);
CREATE INDEX IF NOT EXISTS idx_otp_phone ON otp_verifications(phone);
