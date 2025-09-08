-- Manual fix for character set issues
-- Run this inside the MySQL container

USE bot_db;

-- Fix the report_categories table
ALTER TABLE report_categories CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE report_categories MODIFY COLUMN subject VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Fix other tables that might have the same issue
ALTER TABLE reports CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE reports MODIFY COLUMN reason VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Show the table structure to verify
SHOW CREATE TABLE report_categories;
