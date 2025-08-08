-- MS SQL Server Database Initialization Script
-- Creates database and user for EHS Electronic Journal

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ehs_electronic_journal')
BEGIN
    CREATE DATABASE ehs_electronic_journal;
END
GO

USE ehs_electronic_journal;
GO

-- Create login and user if they don't exist
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'ehs_user')
BEGIN
    CREATE LOGIN ehs_user WITH PASSWORD = 'EhsPassword123!';
END
GO

IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'ehs_user')
BEGIN
    CREATE USER ehs_user FOR LOGIN ehs_user;
    ALTER ROLE db_owner ADD MEMBER ehs_user;
END
GO