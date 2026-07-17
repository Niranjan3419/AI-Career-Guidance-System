from flask import Flask, render_template, request, redirect, session, Response, url_for
import sqlite3
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

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
@app.route("/download_report")
def download_report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result_data = session.get("career_result")
    top_careers = session.get("top_careers", [])
    reasons = session.get("reasons", [])

    if not result_data:
        return redirect("/questionnaire")

    student_name = session.get("user_name", "Student")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT education, college, department, year, cgpa, state
        FROM profiles
        WHERE user_id = ?
        """,
        (session["user_id"],)
    )
    profile = cursor.fetchone()
    conn.close()

    education = profile[0] if profile and profile[0] else "Not provided"
    college = profile[1] if profile and profile[1] else "V.S.B. Engineering College, Karur"
    department = profile[2] if profile and profile[2] else "Computer and Communication Engineering"
    academic_year = profile[3] if profile and profile[3] else "Not provided"
    cgpa = profile[4] if profile and profile[4] else "Not provided"
    state = profile[5] if profile and profile[5] else "Not provided"

    def safe_text(value):
        if value is None:
            return ""
        return escape(str(value)).replace("₹", "Rs. ")

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="AI Career Guidance Report",
        author="AI Career Guidance System"
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#3E3A8F"),
        spaceAfter=5 * mm
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=7 * mm
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#3E3A8F"),
        spaceBefore=5 * mm,
        spaceAfter=3 * mm
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#222222"),
        spaceAfter=2 * mm
    )

    center_style = ParagraphStyle(
        "CenterBody",
        parent=body_style,
        alignment=TA_CENTER
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=body_style,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#666666")
    )

    story = []

    story.append(Paragraph("AI CAREER GUIDANCE SYSTEM", title_style))
    story.append(Paragraph(
        "Professional Career Assessment Report<br/>"
        "Mini Project 2026 | Department of Computer and Communication Engineering",
        subtitle_style
    ))

    generated_on = datetime.now().strftime("%d %B %Y, %I:%M %p")

    student_table = Table(
        [
            [
                Paragraph("<b>Student Name</b>", body_style),
                Paragraph(safe_text(student_name), body_style),
                Paragraph("<b>Generated On</b>", body_style),
                Paragraph(safe_text(generated_on), body_style),
            ],
            [
                Paragraph("<b>Education</b>", body_style),
                Paragraph(safe_text(education), body_style),
                Paragraph("<b>Academic Year</b>", body_style),
                Paragraph(safe_text(academic_year), body_style),
            ],
            [
                Paragraph("<b>College</b>", body_style),
                Paragraph(safe_text(college), body_style),
                Paragraph("<b>CGPA</b>", body_style),
                Paragraph(safe_text(cgpa), body_style),
            ],
            [
                Paragraph("<b>Department</b>", body_style),
                Paragraph(safe_text(department), body_style),
                Paragraph("<b>State</b>", body_style),
                Paragraph(safe_text(state), body_style),
            ],
        ],
        colWidths=[31 * mm, 62 * mm, 30 * mm, 51 * mm],
    )

    student_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F5FF")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#AAA8D8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5D4EB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(student_table)
    story.append(Spacer(1, 7 * mm))

    best_match = Table(
        [
            [
                Paragraph("<b>BEST CAREER MATCH</b>", center_style),
                Paragraph("<b>COMPATIBILITY SCORE</b>", center_style),
            ],
            [
                Paragraph(
                    f"<font size='17'><b>{safe_text(result_data.get('career', 'Not available'))}</b></font>",
                    center_style
                ),
                Paragraph(
                    f"<font size='20'><b>{safe_text(result_data.get('score', 0))}%</b></font>",
                    center_style
                ),
            ],
        ],
        colWidths=[115 * mm, 59 * mm]
    )

    best_match.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3E3A8F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#EEEFFD")),
        ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#E7F8EF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3E3A8F")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#AAA8D8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(best_match)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        safe_text(result_data.get(
            "description",
            "This recommendation is based on the submitted interests, skills, work style and personality."
        )),
        body_style
    ))

    story.append(Paragraph("Career Overview", section_style))

    overview_table = Table(
        [
            [
                Paragraph("<b>Salary Range</b>", body_style),
                Paragraph(safe_text(result_data.get("salary", "Not available")), body_style),
            ],
            [
                Paragraph("<b>Job Demand</b>", body_style),
                Paragraph(safe_text(result_data.get("demand", "Not available")), body_style),
            ],
            [
                Paragraph("<b>Recommended Course</b>", body_style),
                Paragraph(safe_text(result_data.get("course", "Not available")), body_style),
            ],
        ],
        colWidths=[48 * mm, 126 * mm]
    )

    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEEFFD")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#AAA8D8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5D4EB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(overview_table)

    story.append(Paragraph("Top Career Matches", section_style))

    career_rows = [[
        Paragraph("<b>Rank</b>", center_style),
        Paragraph("<b>Career</b>", center_style),
        Paragraph("<b>Score</b>", center_style),
        Paragraph("<b>Demand</b>", center_style),
        Paragraph("<b>Salary</b>", center_style),
    ]]

    for index, career in enumerate(top_careers[:3], start=1):
        career_rows.append([
            Paragraph(str(index), center_style),
            Paragraph(safe_text(career.get("career", "")), body_style),
            Paragraph(f"{safe_text(career.get('score', 0))}%", center_style),
            Paragraph(safe_text(career.get("demand", "")), center_style),
            Paragraph(safe_text(career.get("salary", "")), body_style),
        ])

    career_table = Table(
        career_rows,
        colWidths=[14 * mm, 53 * mm, 21 * mm, 27 * mm, 59 * mm],
        repeatRows=1
    )

    career_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3E3A8F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#AAA8D8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5D4EB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F7F7FC")
        ]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(career_table)

    story.append(Paragraph("Why This Career Was Recommended", section_style))

    if reasons:
        for reason in reasons:
            story.append(Paragraph(f"&#10003; {safe_text(reason)}", body_style))
    else:
        story.append(Paragraph(
            "The selected career matches the student's submitted interests, skills, work style and personality.",
            body_style
        ))

    story.append(Paragraph("Recommended Skills", section_style))
    skills = result_data.get("skills", [])
    story.append(Paragraph(
        " &nbsp;&nbsp; | &nbsp;&nbsp; ".join(
            f"<b>{safe_text(skill)}</b>" for skill in skills
        ) if skills else "No skills available.",
        body_style
    ))

    story.append(Paragraph("Recommended Certifications", section_style))
    certifications = result_data.get("certifications", [])
    if certifications:
        for certification in certifications:
            story.append(Paragraph(f"&#8226; {safe_text(certification)}", body_style))
    else:
        story.append(Paragraph("No certifications available.", body_style))

    story.append(PageBreak())
    story.append(Paragraph("Personalized Career Roadmap", title_style))
    story.append(Paragraph(
        f"A practical step-by-step roadmap for becoming a "
        f"{safe_text(result_data.get('career', 'successful professional'))}.",
        subtitle_style
    ))

    roadmap = result_data.get("roadmap", [])
    if roadmap:
        roadmap_rows = []
        for index, step in enumerate(roadmap, start=1):
            roadmap_rows.append([
                Paragraph(
                    f"<font color='#FFFFFF'><b>{index}</b></font>",
                    center_style
                ),
                Paragraph(safe_text(step), body_style)
            ])

        roadmap_table = Table(
            roadmap_rows,
            colWidths=[18 * mm, 156 * mm]
        )

        roadmap_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#3E3A8F")),
            ("ROWBACKGROUNDS", (1, 0), (1, -1), [
                colors.HexColor("#F5F5FF"),
                colors.white
            ]),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#AAA8D8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5D4EB")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))

        story.append(roadmap_table)
    else:
        story.append(Paragraph("No roadmap information is available.", body_style))

    story.append(Spacer(1, 12 * mm))
    story.append(KeepTogether([
        Paragraph(
            "<b>Career Guidance Note</b>",
            section_style
        ),
        Paragraph(
            "This report is intended as educational career guidance. "
            "Students are encouraged to explore courses, internships, mentors and industry opportunities "
            "before making a final career decision.",
            body_style
        )
    ]))

    def add_page_footer(canvas, doc):
        canvas.saveState()
        page_width, _ = A4

        canvas.setStrokeColor(colors.HexColor("#AAA8D8"))
        canvas.line(18 * mm, 14 * mm, page_width - 18 * mm, 14 * mm)

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(
            18 * mm,
            9 * mm,
            "Generated by AI Career Guidance System | V.S.B. Engineering College, Karur"
        )
        canvas.drawRightString(
            page_width - 18 * mm,
            9 * mm,
            f"Page {doc.page}"
        )
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buffer.seek(0)

    filename_name = "".join(
        character if character.isalnum() else "_"
        for character in student_name.strip()
    ).strip("_") or "Student"

    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename_name}_Career_Guidance_Report.pdf"'
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
