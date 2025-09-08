-- Configure MySQL for UTF-8 support (required for Persian text)
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Create database with proper character set if it doesn't exist
CREATE DATABASE IF NOT EXISTS bot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Set default character set for the database
ALTER DATABASE bot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON bot_db.* TO 'bot_user'@'%';
FLUSH PRIVILEGES;
