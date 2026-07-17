from flask import Flask, render_template, request, redirect, session, Response
import sqlite3

app = Flask(__name__)
app.secret_key = "career_secret_key"


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            mobile TEXT,
            dob TEXT,
            gender TEXT,
            education TEXT,
            college TEXT,
            department TEXT,
            year TEXT,
            cgpa TEXT,
            state TEXT,
            preferred_location TEXT,
            linkedin TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            career TEXT,
            score INTEGER,
            interest TEXT,
            skill TEXT,
            work_style TEXT,
            goal TEXT,
            personality TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


career_data = {
    "Software Developer": {
        "salary": "₹4 LPA - ₹18 LPA",
        "demand": "High",
        "course": "B.E / B.Tech CSE, IT, CCE or Software Development Courses",
        "skills": ["Python", "JavaScript", "SQL", "Git", "Flask"],
        "certifications": ["Python Programming", "Web Development", "SQL Database", "Git & GitHub"],
        "roadmap": ["Learn programming basics", "Build web projects", "Learn database", "Do internship", "Apply for developer roles"]
    },
    "AI/ML Engineer": {
        "salary": "₹6 LPA - ₹25 LPA",
        "demand": "Very High",
        "course": "Artificial Intelligence, Machine Learning, Data Science",
        "skills": ["Python", "Machine Learning", "Data Science", "TensorFlow", "Statistics"],
        "certifications": ["Machine Learning", "Data Science", "Python for AI", "Deep Learning Basics"],
        "roadmap": ["Learn Python", "Study ML basics", "Build AI models", "Create AI projects", "Apply for AI internships"]
    },
    "Data Analyst": {
        "salary": "₹3 LPA - ₹14 LPA",
        "demand": "High",
        "course": "Data Analytics, Statistics, Computer Science",
        "skills": ["Excel", "Python", "SQL", "Power BI", "Statistics"],
        "certifications": ["Data Analytics", "SQL", "Power BI", "Python Basics"],
        "roadmap": ["Learn Excel", "Learn SQL", "Study Python basics", "Create dashboards", "Apply for analyst roles"]
    },
    "UI/UX Designer": {
        "salary": "₹3 LPA - ₹12 LPA",
        "demand": "High",
        "course": "UI/UX Design, Product Design, Human Computer Interaction",
        "skills": ["Figma", "HTML", "CSS", "User Research", "Prototyping"],
        "certifications": ["Figma Design", "UI/UX Design", "User Research", "Web Design"],
        "roadmap": ["Learn design basics", "Practice Figma", "Create UI designs", "Build portfolio", "Apply for UI/UX roles"]
    },
    "Business Analyst": {
        "salary": "₹4 LPA - ₹16 LPA",
        "demand": "High",
        "course": "Business Analytics, MBA, Data Analytics",
        "skills": ["Communication", "Leadership", "Excel", "Business Strategy", "Problem Solving"],
        "certifications": ["Business Analytics", "Excel Advanced", "Project Management", "Digital Marketing"],
        "roadmap": ["Learn business basics", "Study market problems", "Learn Excel", "Create case studies", "Apply for analyst roles"]
    },
    "Embedded Systems Engineer": {
        "salary": "₹3.5 LPA - ₹15 LPA",
        "demand": "High",
        "course": "ECE, CCE, Embedded Systems, IoT",
        "skills": ["C Programming", "Arduino", "IoT", "Sensors", "Embedded C"],
        "certifications": ["Embedded C", "IoT Basics", "Arduino Projects", "Microcontroller Programming"],
        "roadmap": ["Learn electronics basics", "Practice Arduino", "Build IoT projects", "Learn embedded C", "Apply for core internships"]
    }
}


def smart_ai_recommendation(interest, skill, work_style, goal, personality):
    scores = {
        "Software Developer": 50,
        "AI/ML Engineer": 50,
        "Data Analyst": 50,
        "UI/UX Designer": 50,
        "Business Analyst": 50,
        "Embedded Systems Engineer": 50
    }

    reasons = []

    if interest == "Programming":
        scores["Software Developer"] += 25
        scores["AI/ML Engineer"] += 20
        scores["Data Analyst"] += 12
        reasons.append("Strong interest in programming")

    if interest == "Designing":
        scores["UI/UX Designer"] += 30
        reasons.append("Creative design interest")

    if interest == "Business":
        scores["Business Analyst"] += 30
        reasons.append("Business and management interest")

    if interest == "Electronics":
        scores["Embedded Systems Engineer"] += 32
        reasons.append("Electronics and hardware interest")

    if skill == "Python":
        scores["AI/ML Engineer"] += 22
        scores["Software Developer"] += 18
        scores["Data Analyst"] += 18
        reasons.append("Python skill is useful for AI, software, and data roles")

    if skill == "Java":
        scores["Software Developer"] += 22
        reasons.append("Java skill supports software development")

    if skill == "Creativity":
        scores["UI/UX Designer"] += 22
        reasons.append("Creativity matches design-based careers")

    if skill == "Leadership":
        scores["Business Analyst"] += 22
        reasons.append("Leadership supports business and management careers")

    if work_style == "Problem Solving":
        scores["Software Developer"] += 15
        scores["Data Analyst"] += 15
        reasons.append("Problem-solving ability is strong")

    if work_style == "Research":
        scores["AI/ML Engineer"] += 18
        scores["Data Analyst"] += 10
        reasons.append("Research interest supports AI and data careers")

    if work_style == "Creative Work":
        scores["UI/UX Designer"] += 18
        reasons.append("Creative work preference supports UI/UX")

    if work_style == "Team Management":
        scores["Business Analyst"] += 18
        reasons.append("Team management supports business roles")

    if personality == "Analytical":
        scores["Data Analyst"] += 15
        scores["AI/ML Engineer"] += 12
        reasons.append("Analytical personality supports data and AI roles")

    if personality == "Creative":
        scores["UI/UX Designer"] += 15
        reasons.append("Creative personality supports design careers")

    if personality == "Leader":
        scores["Business Analyst"] += 15
        reasons.append("Leadership personality supports business careers")

    sorted_careers = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    top_careers = []
    for career, score in sorted_careers[:3]:
        data = career_data[career]
        top_careers.append({
            "career": career,
            "score": min(score, 98),
            "salary": data["salary"],
            "demand": data["demand"],
            "course": data["course"],
            "skills": data["skills"],
            "certifications": data["certifications"],
            "roadmap": data["roadmap"]
        })

    best = top_careers[0]
    best["description"] = f"You are most suitable for {best['career']} based on your interest, skills, work style, and personality."

    return best, top_careers, reasons


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match"

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            return "Email already registered"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            cursor.execute(
                "INSERT INTO login_details (user_id, name, email) VALUES (?, ?, ?)",
                (user[0], user[1], user[2])
            )

            conn.commit()

            session["user_id"] = user[0]
            session["user_name"] = user[1]

            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user[0],))
            profile = cursor.fetchone()
            conn.close()

            if profile:
                return redirect("/dashboard")
            else:
                return redirect("/complete_profile")

        conn.close()
        return "Invalid email or password"

    return render_template("login.html")


@app.route("/complete_profile", methods=["GET", "POST"])
def complete_profile():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        mobile = request.form["mobile"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        education = request.form["education"]
        college = request.form["college"]
        department = request.form["department"]
        year = request.form["year"]
        cgpa = request.form["cgpa"]
        state = request.form["state"]
        preferred_location = request.form["preferred_location"]
        linkedin = request.form["linkedin"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO profiles
            (user_id, mobile, dob, gender, education, college, department, year, cgpa, state, preferred_location, linkedin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            mobile,
            dob,
            gender,
            education,
            college,
            department,
            year,
            cgpa,
            state,
            preferred_location,
            linkedin
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("complete_profile.html", name=session["user_name"])


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (session["user_id"],))
    profile = cursor.fetchone()
    conn.close()

    if request.method == "POST":
        mobile = request.form["mobile"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        education = request.form["education"]
        college = request.form["college"]
        department = request.form["department"]
        year = request.form["year"]
        cgpa = request.form["cgpa"]
        state = request.form["state"]
        preferred_location = request.form["preferred_location"]
        linkedin = request.form["linkedin"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO profiles
            (user_id, mobile, dob, gender, education, college, department, year, cgpa, state, preferred_location, linkedin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            mobile,
            dob,
            gender,
            education,
            college,
            department,
            year,
            cgpa,
            state,
            preferred_location,
            linkedin
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("complete_profile.html", name=session["user_name"], profile=profile)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM assessments WHERE user_id = ?",
        (session["user_id"],)
    )
    total_assessments = cursor.fetchone()[0]

    cursor.execute(
        "SELECT career, score FROM assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (session["user_id"],)
    )
    last_result = cursor.fetchone()

    cursor.execute(
        "SELECT career, score FROM assessments WHERE user_id = ? ORDER BY id DESC LIMIT 5",
        (session["user_id"],)
    )
    recent_results = cursor.fetchall()

    cursor.execute(
        "SELECT mobile, college, department, year, cgpa, state FROM profiles WHERE user_id = ?",
        (session["user_id"],)
    )
    profile = cursor.fetchone()

    conn.close()

    last_career = last_result[0] if last_result else "Not Taken Yet"
    last_score = last_result[1] if last_result else 0

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        total_assessments=total_assessments,
        last_career=last_career,
        last_score=last_score,
        recent_results=recent_results,
        profile=profile
    )


@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        interest = request.form["interest"]
        skill = request.form["skill"]
        work_style = request.form["work_style"]
        goal = request.form["goal"]
        personality = request.form["personality"]

        result, top_careers, reasons = smart_ai_recommendation(
            interest,
            skill,
            work_style,
            goal,
            personality
        )

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assessments
            (user_id, career, score, interest, skill, work_style, goal, personality)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            result["career"],
            result["score"],
            interest,
            skill,
            work_style,
            goal,
            personality
        ))

        conn.commit()
        conn.close()

        # Temporarily store the result until loading finishes
        session["career_result"] = result
        session["top_careers"] = top_careers
        session["reasons"] = reasons

        return redirect("/loading")

    return render_template("questionnaire.html")
@app.route("/loading")
def loading():
    if "user_id" not in session:
        return redirect("/login")

    if "career_result" not in session:
        return redirect("/questionnaire")

    return render_template("loading.html")


@app.route("/result")
def result():
    if "user_id" not in session:
        return redirect("/login")

    result_data = session.get("career_result")
    top_careers = session.get("top_careers")
    reasons = session.get("reasons")

    if not result_data:
        return redirect("/questionnaire")

    return render_template(
        "result.html",
        name=session["user_name"],
        result=result_data,
        top_careers=top_careers,
        reasons=reasons
    )
from flask import make_response, session, redirect, url_for


@app.route("/download_report")
def download_report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    career = session.get("recommended_career", "Career recommendation unavailable")
    score = session.get("compatibility_score", "Not available")

    report = f"""
AI CAREER GUIDANCE REPORT
=========================

Recommended Career: {career}
Compatibility Score: {score}

Generated by:
AI Career Guidance System
V.S.B. Engineering College, Karur
"""

    response = make_response(report)
    response.headers["Content-Type"] = "text/plain"
    response.headers["Content-Disposition"] = (
        "attachment; filename=career_guidance_report.txt"
    )

    return response
if __name__ == "__main__":
    init_db()
    app.run(debug=True)