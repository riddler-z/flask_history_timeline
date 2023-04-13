DROP TABLE IF EXISTS tabUser;
DROP TABLE IF EXISTS tabTeacher;
DROP TABLE IF EXISTS tabStudent;
DROP TABLE IF EXISTS tabEvent;
DROP TABLE IF EXISTS tabAnnouncement;
DROP TABLE IF EXISTS tabQuiz;
DROP TABLE IF EXISTS tabQuizQuestion;
DROP TABLE IF EXISTS tabQuizAnswer;
DROP TABLE IF EXISTS tabQuizAssignment;
DROP TABLE IF EXISTS tabQuizResult;


CREATE TABLE tabUser (
	user_id INTEGER PRIMARY KEY AUTOINCREMENT,
	username VARCHAR(140) NOT NULL,
	email VARCHAR(140) UNIQUE NOT NULL,
	password VARCHAR(140) NOT NULL,
	role VARCHAR(140) NOT NULL,
	creation DATETIME(6),
	modified DATETIME(6),
	last_login DATETIME(6)
);

CREATE TABLE tabTeacher (
	teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
	teacher_department VARCHAR(140),
	creation DATETIME(6),
	modified DATETIME(6),
	user_id INTEGER REFERENCES tabUser(user_id) ON DELETE CASCADE
);

CREATE TABLE tabStudent (
	student_id INTEGER PRIMARY KEY AUTOINCREMENT,
	student_class VARCHAR(140),
	creation DATETIME(6),
	modified DATETIME(6),
	user_id INTEGER REFERENCES tabUser(user_id) ON DELETE CASCADE
);

CREATE TABLE tabEvent (
	event_id INTEGER PRIMARY KEY AUTOINCREMENT,
	event_country VARCHAR(140) NOT NULL,
	event_year INTEGER,
	event_title VARCHAR(140),
	event_description TEXT,
	creation DATETIME(6),
	modified DATETIME(6),
	created_by_user INTEGER REFERENCES tabUser(user_id),
	modified_by_user INTEGER REFERENCES tabUser(user_id),
	UNIQUE(event_year, event_title, event_country)
);

CREATE TABLE tabAnnouncement (
	announcement_id INTEGER PRIMARY KEY AUTOINCREMENT,
	announcement_title VARCHAR(140),
	announcement_content TEXT,
	creation DATETIME(6),
	created_by_user INTEGER REFERENCES tabUser(user_id) ON DELETE CASCADE
);

CREATE TABLE tabQuiz (
	quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
	quiz_description TEXT,
	creation DATETIME(6),
	modified DATETIME(6),
	created_by_user INTEGER REFERENCES tabUser(user_id),
	modified_by_user INTEGER REFERENCES tabUser(user_id),
	event_id INTEGER REFERENCES tabEvent(event_id) ON DELETE CASCADE
);

CREATE TABLE tabQuizQuestion (
	question_id INTEGER PRIMARY KEY AUTOINCREMENT,
	question TEXT NOT NULL,
	creation DATETIME(6),
	modified DATETIME(6),
	created_by_user INTEGER REFERENCES tabUser(user_id),
	modified_by_user INTEGER REFERENCES tabUser(user_id),
	quiz_id INTEGER REFERENCES tabQuiz(quiz_id) ON DELETE CASCADE
);

CREATE TABLE tabQuizAnswer (
	answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
	answer TEXT NOT NULL,
	is_correct BOOLEAN,
	creation DATETIME(6),
	modified DATETIME(6),
	created_by_user INTEGER REFERENCES tabUser(user_id),
	modified_by_user INTEGER REFERENCES tabUser(user_id),
	question_id INTEGER REFERENCES tabQuizQuestion(question_id) ON DELETE CASCADE
);

CREATE TABLE tabQuizResult (
	result_id INTEGER PRIMARY KEY AUTOINCREMENT,
	score INTEGER,
	total INTEGER,
	creation DATETIME(6),
	quiz_id INTEGER REFERENCES tabQuiz(quiz_id) ON DELETE CASCADE,
	user_id INTEGER REFERENCES tabUser(user_id) ON DELETE CASCADE
);

CREATE TABLE tabQuizAssignment (
	assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
	is_completed BOOLEAN,
	creation DATETIME(6),
	assigned_by_user INTEGER REFERENCES tabUser(user_id) ON DELETE CASCADE,
	assigned_to_user INTEGER REFERENCES tabUser(user_id) ON DELETE CASCADE
);
