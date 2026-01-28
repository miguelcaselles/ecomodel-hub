-- Create first admin user for EcoModel Hub
-- Password: admin123 (hashed with bcrypt)

INSERT INTO users (
    email,
    password_hash,
    full_name,
    role,
    is_active,
    created_at,
    updated_at
) VALUES (
    'admin@ecomodel.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqj98kN/x2',  -- password: admin123
    'Administrator',
    'admin',
    true,
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Verify user was created
SELECT email, full_name, role, is_active FROM users WHERE email = 'admin@ecomodel.com';
