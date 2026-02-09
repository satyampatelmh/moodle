from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv() # Loading variables from .env
app.secret_key = os.environ.get("SECRET_KEY")


# Configure SQL Alchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(7), nullable = False)
    username = db.Column(db.String(14), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    has_code_question = db.Column(db.Boolean, default=False)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)

    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(10), nullable=False)  # "mcq" or "code"
    marks = db.Column(db.Integer, nullable=False)

    quiz = db.relationship("Quiz", backref="questions")


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    option_text = db.Column(db.String(300), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

    question = db.relationship("Question", backref="options")


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    is_finalized = db.Column(db.Boolean, default=False)
    total_score = db.Column(db.Integer)

    quiz = db.relationship("Quiz", backref="submissions")
    student = db.relationship("User", backref="submissions")


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submission.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    selected_option_id = db.Column(db.Integer, db.ForeignKey("option.id"))
    code_answer = db.Column(db.Text)

    marks_obtained = db.Column(db.Integer)
    is_graded = db.Column(db.Boolean, default=False)

    submission = db.relationship("Submission", backref="answers")
    question = db.relationship("Question")
    selected_option = db.relationship("Option")


# Routes
@app.route("/")
def home():
    if "username" in session and "user_type" in session:
        if session["user_type"] == "teacher":
            return redirect(url_for('teacherDashboard'))
        elif session["user_type"] == "student":
            return redirect(url_for('studentDashboard'))
    return render_template("index.html")


# Show Login Page
@app.route("/login-page")
def showLogin():
    return render_template("login.html")


# Show Register Page
@app.route("/register-page")
def showRegister():
    return render_template("register.html")


#Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session["username"] = username

        if user.user_type == "teacher":
            session["user_type"] = "teacher"
            return redirect(url_for("teacherDashboard"))

        elif user.user_type == "student":
            session["user_type"] = "student"
            return redirect(url_for("studentDashboard"))

    return render_template("login.html", error="Invalid username or password")


# Register
@app.route("/register", methods=["POST"])
def register():
    full_name = request.form["full_name"]
    username = request.form["username"]
    password = request.form["password"]
    mobile = request.form["mobile"]
    email = request.form["email"]

    user = User.query.filter_by(username=username).first()

    if user:
        return render_template("register.html", error="User already registered")

    new_user = User(
        full_name=full_name,
        username=username,
        mobile=mobile,
        email=email,
        user_type="student"
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    session["username"] = username
    session["user_type"] = "student"

    return redirect(url_for("studentDashboard"))


        
# Student Dashboard
@app.route("/studentDashboard")
def studentDashboard():
    if "username" in session:
        student_id = User.query.filter_by(username=session["username"]).first().id
        
        attempted_quiz_ids = {sub.quiz_id for sub in Submission.query.filter_by(student_id=student_id).all()}
        
        quizzes = Quiz.query.all()
        return render_template("studentDashboard.html", username=session["username"], quizzes=quizzes, attempted_quiz_ids=attempted_quiz_ids)
    
    return redirect(url_for('home'))

# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_type", None)
    return redirect(url_for('home'))

#Teacher Dashboard
@app.route("/teacherDashboard")
def teacherDashboard():
    if "username" in session:
        return render_template("teacherDashboard.html",username=session["username"])
    return redirect(url_for('home'))
    
#Make Quiz Dashboard
@app.route("/makeQuiz")
def makeQuiz():
    if "username" in session:
        return render_template("makeQuiz.html",username=session["username"])
    

        

# Publish Quiz
@app.route("/publishQuiz", methods=["POST"])
def publishQuiz():
    title = request.form["title"]

    question_types = request.form.getlist("question_type[]")
    question_texts = request.form.getlist("question_text[]")
    marks_list = request.form.getlist("marks[]")

    quiz = Quiz(
        title=title,
        has_code_question=False,
    )

    db.session.add(quiz)
    db.session.flush()

    for i, qtype in enumerate(question_types):
        question = Question(
            quiz_id=quiz.id,
            question_text=question_texts[i],
            question_type=qtype,
            marks=int(marks_list[i])
        )

        db.session.add(question)
        db.session.flush()

        if qtype == "mcq":
            options = request.form.getlist(f"option_{i}[]")
            correct_index = int(request.form.get(f"correct_{i}"))

            for idx, opt_text in enumerate(options):
                option = Option(
                    question_id=question.id,
                    option_text=opt_text,
                    is_correct=(idx == correct_index)
                )
                db.session.add(option)

        if qtype == "code":
            quiz.has_code_question = True

    db.session.commit()

    return redirect(url_for("teacherDashboard"))



#Attempt Quiz
@app.route("/attemptQuiz/<int:quiz_id>")
def attemptQuiz(quiz_id):
    if "username" in session:
        quiz = Quiz.query.get(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        return render_template("attemptQuiz.html",username=session["username"], quiz=quiz, questions=questions) 

# Submit Quiz
@app.route("/quiz/<int:quiz_id>/submit", methods=["POST"])
def submitQuiz(quiz_id):
    if "username" in session:
        quiz = Quiz.query.get(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        student_id = User.query.filter_by(username=session["username"]).first().id
        submission = Submission(
            quiz_id=quiz.id,
            student_id=student_id,
            total_score=0
        )

        db.session.add(submission)
        db.session.flush()  # get submission.id

        total_score = 0
        has_code = False

        for question in questions:

            # MCQ question
            if question.question_type == "mcq":
                option_id = int(request.form.get(f"answer_{question.id}"))
                option = Option.query.get(option_id)

                marks = question.marks if option.is_correct else 0

                answer = Answer(
                    submission_id=submission.id,
                    question_id=question.id,
                    selected_option_id=option.id,
                    marks_obtained=marks,
                    is_graded=True
                )

                total_score += marks
                db.session.add(answer)

            # CODE question
            else:
                code = request.form.get(f"code_answer_{question.id}")

                answer = Answer(
                    submission_id=submission.id,
                    question_id=question.id,
                    code_answer=code,
                    marks_obtained=None,
                    is_graded=False
                )

                has_code = True
                db.session.add(answer)

        # if any code question exists, delay result
        submission.total_score = None if has_code else total_score

        db.session.commit()
        return redirect(url_for("studentDashboard"))
    return redirect(url_for('home'))

# View Result
@app.route("/quiz/<int:quiz_id>/result")
def viewResult(quiz_id):
    student_id = User.query.filter_by(username=session["username"]).first().id

    quiz = Quiz.query.get_or_404(quiz_id)
    max_marks = sum( q.marks for q in quiz.questions)
    # get student's submission for this quiz
    submission = Submission.query.filter_by(
        quiz_id=quiz.id,
        student_id=student_id
        
    ).first()

    answers = Answer.query.filter_by(
        submission_id=submission.id
    ).all()

    # check if all answers are graded
    all_graded = all(ans.is_graded for ans in answers)

    return render_template(
        "viewResult.html",
        quiz=quiz,
        submission=submission,
        answers=answers,
        all_graded=all_graded,
        max_marks=max_marks    
    )



# Grade the code
@app.route("/gradeSubmission/<int:submission_id>")
def gradeSubmission(submission_id):
    submission = Submission.query.get(submission_id)

    # get only CODE answers
    answers = Answer.query.filter_by(
        submission_id=submission.id
    ).all()

    return render_template( 
        "gradeSubmission.html",
        submission=submission,
        answers=answers
    )


# Update marks
@app.route("/submitGrades/<int:submission_id>/submit", methods=["POST"])
def submitGrades(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    answers = Answer.query.filter_by(
        submission_id=submission.id
    ).all()

    total_score = 0

    for answer in answers:
        # MCQs already graded
        if answer.question.question_type == "mcq":
            total_score += answer.marks_obtained
            continue

        # CODE question
        marks = int(request.form.get(f"marks_{answer.id}"))

        answer.marks_obtained = marks
        answer.is_graded = True

        total_score += marks

    submission.total_score = total_score

    db.session.commit()
    return redirect(url_for("teacherDashboard"))



# Quiz list to grade
@app.route("/teacher/grade")
def gradeQuiz():
    teacher_id = session.get("user_id")

    submissions = Submission.query.all()

    return render_template(
        "gradeQuiz.html",
        submissions=submissions
    )



#Search a Student
@app.route("/teacher/studentHistory", methods=["GET", "POST"])
def studentHistory():
    if request.method == "POST":
        student_id = request.form["student_id"]

        student = User.query.get(student_id)

        submissions = Submission.query.filter_by(
            student_id=student_id
        ).all()

        results = []

        for sub in submissions:
            total_possible = sum(q.marks for q in sub.quiz.questions)

            if sub.total_score is None:
                percentage = None
                status = "Pending"
            else:
                percentage = round((sub.total_score / total_possible) * 100, 2)
                status = "Pass" if percentage >= 35 else "Fail"

            results.append({
                "quiz_title": sub.quiz.title,
                "score": sub.total_score,
                "total": total_possible,
                "percentage": percentage,
                "status": status
            })

        return render_template(
            "studentHistory.html",
            student=student,
            results=results
        )

    return render_template("studentSearch.html")


# View all Students
@app.route("/teacher/viewStudents")
def viewStudents():
    students = User.query.filter_by(user_type="student").all()
    return render_template("studentList.html", students=students)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)