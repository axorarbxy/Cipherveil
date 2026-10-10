-- Optional: run this once against your MySQL server before pointing DATABASE_URL at it.
-- SQLAlchemy (Base.metadata.create_all) will create the actual tables on first app startup.

CREATE DATABASE IF NOT EXISTS ransomware_ews CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'ews_user'@'%' IDENTIFIED BY 'ews_password';
GRANT ALL PRIVILEGES ON ransomware_ews.* TO 'ews_user'@'%';
FLUSH PRIVILEGES;
