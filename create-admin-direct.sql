-- Create admin user directly in PostgreSQL
-- This bypasses the Python code and inserts directly into the database

INSERT INTO users (
    id,
    email,
    password_hash,
    full_name,
    role,
    is_active,
    organization_id,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'admin@ecomodel.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqj98kN/x2',  -- password: admin123
    'Administrator',
    'global_admin',
    true,
    NULL,
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Verify user was created
SELECT id, email, full_name, role, is_active, created_at FROM users WHERE email = 'admin@ecomodel.com';
