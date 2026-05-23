CREATE TABLE donors (
    id SERIAL PRIMARY KEY,
    donor_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    blood_type VARCHAR(5) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Table for Hospitals
CREATE TABLE hospitals (
    id SERIAL PRIMARY KEY,
    hospital_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Table for Blood Requests
CREATE TABLE blood_requests (
    id SERIAL PRIMARY KEY,
    request_code TEXT UNIQUE NOT NULL,
    hospital_name TEXT NOT NULL,
    blood_type TEXT NOT NULL,
    units_needed INTEGER NOT NULL,
    units_collected INTEGER DEFAULT 0,
    urgency TEXT DEFAULT 'Normal',
    description TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Table for acceptances (one record per donor acceptance)
CREATE TABLE acceptances (
    id BIGSERIAL PRIMARY KEY,
    acceptance_code TEXT UNIQUE NOT NULL,
    request_id INTEGER NOT NULL,
    donor_name TEXT,
    donor_phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT NOW()
);