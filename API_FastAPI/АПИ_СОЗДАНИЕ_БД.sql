-- -- Создание таблицы logs
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    event TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

--   -- Создание таблицы tasks
CREATE TABLE tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    info TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

SELECT * FROM tasks ORDER BY updated_at DESC LIMIT 100;  

SELECT * FROM logs ORDER BY created_at DESC LIMIT 100;

TRUNCATE TABLE tasks, logs

ALTER TABLE tasks
ADD COLUMN error_code TEXT,
ADD COLUMN predictions TEXT;

ALTER TABLE tasks DROP COLUMN predictions;
