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
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect("/dashboard")
        else:
            return "Invalid email or password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM assessments WHERE user_id = ?", (session["user_id"],))
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

    conn.close()

    last_career = last_result[0] if last_result else "Not Taken Yet"
    last_score = last_result[1] if last_result else 0

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        total_assessments=total_assessments,
        last_career=last_career,
        last_score=last_score,
        recent_results=recent_results
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
            interest, skill, work_style, goal, personality
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

        return render_template(
            "result.html",
            name=session["user_name"],
            result=result,
            top_careers=top_careers,
            reasons=reasons
        )

    return render_template("questionnaire.html")


@app.route("/download_report")
def download_report():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT career, score, interest, skill, work_style, goal, personality FROM assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (session["user_id"],)
    )

    data = cursor.fetchone()
    conn.close()

    if not data:
        return redirect("/dashboard")

    career, score, interest, skill, work_style, goal, personality = data

    report = f"""
AI CAREER GUIDANCE REPORT
=========================

Student Name: {session["user_name"]}

Recommended Career: {career}
Compatibility Score: {score}%

Student Inputs:
Interest: {interest}
Strong Skill: {skill}
Work Style: {work_style}
Career Goal: {goal}
Personality: {personality}

Result Summary:
Based on your interests, skills, work style, career goal, and personality,
the system recommends {career} as your best suitable career path.

This report is generated by AI Career Guidance System.

Developed by Niranjan
Mini Project 2026
"""

    return Response(
        report,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=career_report.txt"}
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)