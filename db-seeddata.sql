-- Standard Categories
INSERT INTO categories (name, color_code, description) VALUES 
('Education', '#3498db', 'Schools, Universities, Courses'),
('Career', '#2ecc71', 'Jobs and professional milestones'),
('Private', '#e74c3c', 'Personal life and family'),
('Hobbies', '#f1c40f', 'Leisure and travel'),
('Birthday', '#9b59b6', 'Automatically or manually tracked birthdays');

-- Five Persons
INSERT INTO persons (full_name, birth_date) VALUES 
('Petra Muster', '1985-05-15'),
('John Doe', '1990-01-20'),
('Alice Smith', '1992-11-03'),
('Marc Dubois', '1978-07-12'),
('Elena Rossi', '1988-03-25');

-- Example Events
-- 1. Education Course
INSERT INTO events (title, category_id, start_date, end_date, description) 
VALUES ('Business IT Studies', 1, '2007-07-01', '2011-07-15', 'Bachelor Degree Program');

-- 2. Graduation (Milestone depending on Course)
INSERT INTO events (title, category_id, is_milestone, end_date) 
VALUES ('Graduation Ceremony', 1, TRUE, '2011-07-15');

-- 3. Career Start
INSERT INTO events (title, category_id, start_date, description) 
VALUES ('Junior Developer at TechCorp', 2, '2011-08-01', 'First full-time job');

-- 4. Private Wedding
INSERT INTO events (title, category_id, start_date, is_public) 
VALUES ('Church Wedding', 3, '2012-12-12', FALSE);

-- Linking Dependencies
-- Graduation (ID 2) depends on Studies (ID 1)
INSERT INTO event_dependencies (event_id, predecessor_id) VALUES (2, 1);

-- Linking Participants
-- Wedding (ID 4) with Petra (ID 1)
INSERT INTO event_participants (event_id, person_id, participant_role) 
VALUES (4, 1, 'Spouse');

-- Career Start (ID 3) with John Doe (ID 2) as Mentor
INSERT INTO event_participants (event_id, person_id, participant_role) 
VALUES (3, 2, 'Mentor');
