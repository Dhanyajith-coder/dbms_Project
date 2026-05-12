CREATE TABLE donors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    blood_type VARCHAR(5),
    latitude DECIMAL(10, 8), 
    longitude DECIMAL(11, 8),
    phone VARCHAR(15)
);

-- 2. Table for Hospitals
CREATE TABLE hospitals (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address TEXT
);

-- 3. Table for Blood Requests
CREATE TABLE blood_requests (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER REFERENCES hospitals(id),
    blood_type_needed VARCHAR(5),
    radius_km INTEGER DEFAULT 10,
    status TEXT DEFAULT 'active' 
);