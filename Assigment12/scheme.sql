drop table if exists student;
drop table if exists quiz;
drop table if exists student_quiz;
Create Table Student(
  id INTEGER PRIMARY KEY,
  first_name TEXT,
  last_name TEXT
);

Create TABLE Quiz(
  id INTEGER PRIMARY KEY,
  subject TEXT,
  question_num INTEGER,
  date DATETIME
);

CREATE TABLE student_quiz(
  student_id INTEGER,
  quiz_id INTEGER,
  score INTEGER,
  Foreign KEY(student_id) REFERENCES Student(id),
  FOREIGN KEY(quiz_id) REFERENCES Quiz(id)
);