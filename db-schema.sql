-- Cleanup for fresh start (if needed)
DROP TABLE IF EXISTS event_dependencies;
DROP TABLE IF EXISTS event_participants;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS persons;
DROP TABLE IF EXISTS categories;

-- 1. Categories Table (Flexible types)
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color_code VARCHAR(7) DEFAULT '#3498db',
    description VARCHAR(255)
);

-- 2. Persons Table (Contacts & Relationships)
CREATE TABLE persons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Events Table (Core Timeline Data)
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    is_milestone BOOLEAN DEFAULT FALSE,
    start_date DATE NULL,
    end_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT chk_dates CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

-- 4. Participants Table (n:m Relation)
CREATE TABLE event_participants (
    event_id INT,
    person_id INT,
    participant_role VARCHAR(100),
    PRIMARY KEY (event_id, person_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
);

-- 5. Dependencies Table (Logic & Flow)
CREATE TABLE event_dependencies (
    event_id INT,
    predecessor_id INT,
    dependency_type VARCHAR(50) DEFAULT 'requires_completion',
    PRIMARY KEY (event_id, predecessor_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (predecessor_id) REFERENCES events(id) ON DELETE CASCADE,
    CONSTRAINT chk_no_self_dependency CHECK (event_id <> predecessor_id)
);

CREATE OR REPLACE VIEW view_birthday_events AS
SELECT 
    CONCAT('1000', id) AS id, -- Dummy ID to avoid conflicts with real events
    'Birthday' AS category_name,
    CONCAT('Birthday: ', full_name) AS title,
    CONCAT('Yearly recurring birthday of ', full_name) AS description,
    FALSE AS is_public,
    TRUE AS is_milestone,
    birth_date AS start_date,
    birth_date AS end_date
FROM persons 
WHERE birth_date IS NOT NULL;

CREATE OR REPLACE VIEW view_complete_timeline AS
SELECT 
    e.id, 
    e.title, 
    COALESCE(e.start_date, e.end_date) AS start_date, 
    e.end_date, 
    CAST(e.is_milestone AS UNSIGNED) AS is_milestone, 
    CAST(e.is_public AS UNSIGNED) AS is_public,
    e.category_id,
    COALESCE(c.name, 'Keine Kategorie') AS category_name, 
    COALESCE(c.color_code, '#cccccc') AS color_code
FROM events e
LEFT JOIN categories c ON e.category_id = c.id

UNION ALL

SELECT 
    p.id + 10000 AS id, 
    CONCAT('🎂 ', p.full_name) AS title, 
    STR_TO_DATE(CONCAT(YEAR(CURDATE()), DATE_FORMAT(p.birth_date, '-%m-%d')), '%Y-%m-%d') AS start_date,
    NULL AS end_date, 
    1 AS is_milestone, 
    1 AS is_public,
    c.id AS category_id,
    c.name AS category_name, 
    c.color_code
FROM persons p
JOIN categories c ON c.name = 'Birthday'
WHERE p.birth_date IS NOT NULL;