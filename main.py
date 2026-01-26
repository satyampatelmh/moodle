from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
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
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Routes
@app.route("/")
def home():
    if "username" in session and "user_type" in session:
        if session["user_type"] == "teacher":
            return redirect(url_for('teacherDashboard'))
        elif session["user_type"] == "student":
            return redirect(url_for('studentDashboard'))
    return render_template("index.html")


# Login
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
        return redirect(url_for("dashboard"))
    else:
        return render_template("index.html")
    


        
    
# Register
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index.html", error="User already registered")
    else:
        new_user = User(username=username, user_type="student")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session["username"] = username
        return redirect(url_for("dashboard"))
        
# Dashboard
@app.route("/studentDashboard")
def studentDashboard():
    if "username" in session:
        return render_template("studentDashboard.html", username=session["username"])
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
    

#Make Quiz
@app.route("/makeQuiz")
def makeQuiz():
    if "username" in session:
        return render_template("makeQuiz.html",username=session["username"])
    
#Grade Quiz
@app.route("/gradeQuiz")
def gradeQuiz():
    if "username" in session:
        return render_template("gradeQuiz.html",username=session["username"])
        



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)