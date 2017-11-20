import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
my_db = None
logged_in = False


@app.route('/')
def index():
    return redirect("/login")


@app.route('/login', methods=["GET"])
def login():
    if not logged_in:
        result = render_template("login.html")
        return result
    else:
        return redirect("/dashboard")


@app.route('/results/add', methods=["GET", "POST"])
def quiz_results():
    if not logged_in:
        result = render_template("login.html")
        return result
    if request.method == "GET":
        student_ids = [student.id for student in my_db.get_all_students()]
        quiz_ids = [quiz.id for quiz in my_db.get_all_quizzes()]
        return render_template("quiz_results.html", student_ids=student_ids, quiz_ids=quiz_ids)
    student_id = request.form["student_id"]
    quiz_id = request.form["quiz_id"]
    score = request.form["score"]
    my_db.add_score(student_id, quiz_id, score)
    return redirect("/dashboard")


@app.route('/student/<student_id>')
def student_quizzes(student_id):
    if not logged_in:
        result = render_template("login.html")
        return result
    scores = my_db.get_scores_for_student(student_id)
    if len(scores) == 0:
        return "No Result"
    return render_template("score.html", scores=scores)


@app.route('/student/add', methods=["GET", "POST"])
def student_add():
    if not logged_in:
        result = render_template("login.html")
        return result
    if request.method == "GET":
        result = render_template("student_add.html")
        return result
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    student = Student("", first_name, last_name)
    my_db.add_student(student)
    return redirect("/dashboard")


@app.route('/quiz/add', methods=["GET", "POST"])
def quiz_add():
    if not logged_in:
        result = render_template("login.html")
        return result
    if request.method == "GET":
        result = render_template("quiz_add.html")
        return result
    subject = request.form["subject"]
    question_num = request.form["question_num"]
    date = request.form["date"]
    quiz = Quiz("", subject, question_num, date)
    my_db.add_quiz(quiz)
    return redirect("/dashboard")


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    global logged_in
    if request.method == "GET":
        if not logged_in:
            result = render_template("login.html")
            return result
        students = my_db.get_all_students()
        quizzes = my_db.get_all_quizzes()
        result = render_template("dashboard.html", students=students, quizzes=quizzes)
        return result
    username = request.form["username"]
    password = request.form["password"]
    if username == "admin" and password == "password":
        logged_in = True
        return redirect("/dashboard")
    else:
        return redirect('/login')


def main():
    global my_db
    my_db = MyDatabase()
    app.run()


class MyDatabase:
    connection = None

    def __init__(self):
        self.init_db()

    def add_score(self, student_id, quiz_id, score):
        cursor = self.connection.cursor()
        cursor.execute("insert into student_quiz(student_id, quiz_id, score) values(?,?,?)",
                       [student_id, quiz_id, score])
        self.connection.commit()

    def get_scores_for_student(self, student_id):
        cursor = self.connection.cursor()
        result = cursor.execute("select * from quiz q INNER JOIN student_quiz s ON q.id = s.student_id "
                                "where s.student_id = ?", [student_id]).fetchall()
        scores = list()
        for res in result:
            quiz_id = res[5]
            score = res[6]
            scores.append(Score(quiz_id, score))
        return scores

    def add_student(self, student):
        cursor = self.connection.cursor()
        cursor.execute("insert into student(first_name, last_name) values (?, ?)",
                       [student.first_name, student.last_name])
        self.connection.commit()

    def add_quiz(self, quiz):
        cursor = self.connection.cursor()
        cursor.execute("insert into quiz(subject, question_num, date) values (?, ?, ?)",
                       [quiz.subject, quiz.question_num, quiz.date])
        self.connection.commit()

    def get_all_students(self):
        cursor = self.connection.cursor()
        results = cursor.execute("select * from student").fetchall()
        students = list()
        for res in results:
            cur_student = Student(res[0], res[1], res[2])
            students.append(cur_student)
        return students

    def get_all_quizzes(self):
        cursor = self.connection.cursor()
        results = cursor.execute("select * from quiz").fetchall()
        quizzes = list()
        for res in results:
            cur_quiz = Quiz(res[0], res[1], res[2], res[3])
            quizzes.append(cur_quiz)
        return quizzes

    def init_db(self):
        with sqlite3.connect("hw12.db") as connection:
            self.connection = connection
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS Student(id INTEGER PRIMARY KEY,first_name TEXT,last_name TEXT);")
            cursor.execute("CREATE TABLE IF NOT EXISTS Quiz(id INTEGER PRIMARY KEY,subject TEXT,question_num INTEGER,"
                           "date DATETIME);")
            cursor.execute("CREATE TABLE IF NOT EXISTS student_quiz(student_id INTEGER,quiz_id INTEGER,score INTEGER,"
                           "Foreign KEY(student_id) REFERENCES Student(id),FOREIGN KEY(quiz_id) REFERENCES Quiz(id))")
            # cursor.execute("INSERT INTO Student(first_name, last_name) values('John', 'Smith')")
            # cursor.execute("INSERT INTO QUIZ(subject, question_num, date) values('Python Basics', 5, '2015-2-5')")
            # cursor.execute("Insert INTO student_quiz(student_id, quiz_id, score) values (1,1,85)")


class Student:
    def __init__(self, student_id, first_name, last_name):
        self.id = student_id
        self.first_name = first_name
        self.last_name = last_name


class Quiz:
    def __init__(self, quiz_id, subject, question_num, date):
        self.id = quiz_id
        self.subject = subject
        self.question_num = question_num
        self.date = date


class Score:
    def __init__(self, quiz_id, score):
        self.id = quiz_id
        self.score = score


if __name__ == "__main__":
    main()
