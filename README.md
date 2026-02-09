# Moodle-Lite

A lightweight Learning Management System (LMS) built with Python and Flask. This application provides a platform for teachers to create quizzes and for students to attempt them, with features for manual grading and progress tracking.

## 🚀 Features

### For Teachers 👩‍🏫
- **Dashboard**: Central hub for managing quizzes and students.
- **Create Quizzes**:
  - Support for **Multiple Choice Questions (MCQs)**.
  - Support for **Coding Questions**.
- **Grading**:
  - Automatic grading for MCQs.
  - Manual grading interface for Coding questions.
- **Student History**: View detailed performance history for any student.
- **Student List**: View all registered students.

### For Students 👨‍🎓
- **Dashboard**: View available quizzes and past attempts.
- **Attempt Quizzes**: Interactive interface to take quizzes.
- **View Results**: Detailed breakdown of results, including marks and correct answers (after grading).

### Security 🔒
- Secure Login and Registration system.
- Role-based access control (Student vs Teacher).
- Password hashing for security.

## 🛠️ Tech Stack

- **Backend**: [Flask](https://flask.palletsprojects.com/) (Python)
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) (ORM), SQLite (default)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Tailwind CSS
- **Authentication**: Werkzeug Security

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd moodle
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Ensure you have the necessary packages installed. You can install them using:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**
    Create a `.env` file in the root directory with the following content:
    ```env
    SECRET_KEY=your_secret_key_here
    DATABASE_URL=sqlite:///moodle.db
    ```

5.  **Run the Application**
    ```bash
    python main.py
    ```
    *Note: The application will automatically create the database tables on the first run.*

6.  **Access the App**
    Open your browser and navigate to `http://127.0.0.1:5000`.

## 📂 Project Structure

```
moodle/
├── main.py              # Application entry point and routes
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── static/              # CSS, JS, Images
│   └── css/
├── templates/           # HTML Templates
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── teacherDashboard.html
│   ├── studentDashboard.html
│   ├── makeQuiz.html     # Quiz creation
│   ├── attemptQuiz.html  # Quiz taking
│   └── ...
└── instance/            # Database file (created at runtime)
```

## 📝 Usage

1.  **Register**: Create a new account. By default, all new registrations are created as **Students**.
2.  **Teacher Access**: 
    - *Note*: The registration form defaults to the "student" role. To access teacher features, you may need to manually update a user's `user_type` to `teacher` in the database after registration, or insert a teacher user directly.
3.  **Create Quiz**: As a teacher, use the "Make Quiz" page to add questions (MCQ or Code) and publish them.
4.  **Attempt Quiz**: As a student, log in to your dashboard to see available quizzes.
5.  **View Results**: After submission, students can view their scores (subject to manual grading for code questions).