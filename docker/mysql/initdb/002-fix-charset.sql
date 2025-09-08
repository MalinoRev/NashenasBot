-- Fix character set for existing tables
-- This script will be run after the database is created

-- Fix report_categories table
ALTER TABLE report_categories CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Fix any other tables that might have been created with wrong charset
-- (This is a safety measure in case other tables were created before charset fix)
ALTER TABLE reports CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE chat_requests CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE media CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Ensure all string columns use utf8mb4
ALTER TABLE report_categories MODIFY COLUMN subject VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE reports MODIFY COLUMN reason VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
