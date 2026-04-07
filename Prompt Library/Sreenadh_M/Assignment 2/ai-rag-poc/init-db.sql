-- Initialize pgvector extension for PostgreSQL
-- This script runs automatically when the postgres container starts

CREATE EXTENSION IF NOT EXISTS vector;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO ${DB_USER:-postgres};
GRANT CREATE ON SCHEMA public TO ${DB_USER:-postgres};
