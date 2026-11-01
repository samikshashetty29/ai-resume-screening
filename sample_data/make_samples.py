"""Generate the sample resume PDFs and invalid test files without extra dependencies.

Run from the project folder:  python sample_data/make_samples.py
All people and companies below are fictional.
"""
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).parent

# Each resume is a list of pages; each page is a list of lines.
RESUMES = {
    "data_analyst_priya.pdf": [[
        "Priya Sharma - Data Analyst",
        "Email: priya@example.com",
        "",
        "SUMMARY",
        "Data analyst with 2 years of experience in Python, SQL and data visualization.",
        "",
        "SKILLS",
        "Python, Pandas, NumPy, SQL, MySQL, Excel, Power BI, Matplotlib, Git, Statistics",
        "Machine learning with scikit-learn. Strong communication and teamwork.",
        "",
        "EXPERIENCE",
        "Junior Data Analyst, ABC Retail (2023 - present)",
        "- Built sales dashboards in Power BI and automated reports with Python.",
        "- Wrote SQL queries to clean and analyze customer data.",
        "",
        "EDUCATION",
        "B.Sc. Computer Science, 2023",
    ]],
    "web_developer_arjun.pdf": [[
        "Arjun Mehta - Frontend Web Developer",
        "Portfolio: https://arjun.example.dev",
        "",
        "SUMMARY",
        "Frontend developer with 3 years building responsive web apps in React.",
        "",
        "SKILLS",
        "JavaScript, TypeScript, React, HTML, CSS, Node.js, Express, REST API",
        "MongoDB, Git, GitHub, Jira, Agile, Scrum",
        "",
        "EXPERIENCE",
        "Web Developer, PixelCraft Studio (2022 - present)",
        "- Built a React and TypeScript dashboard used by 5,000 customers.",
        "- Created REST API endpoints with Node.js and Express backed by MongoDB.",
        "- Improved page load time by 40% through code splitting and caching.",
        "",
        "EDUCATION",
        "B.Tech. Information Technology, 2022",
    ]],
    "ml_engineer_meera.pdf": [[
        "Meera Iyer - Machine Learning Engineer",
        "Email: meera@example.com",
        "",
        "SUMMARY",
        "ML engineer focused on deep learning, NLP and computer vision in production.",
        "",
        "SKILLS",
        "Python, PyTorch, TensorFlow, Keras, scikit-learn, Pandas, NumPy",
        "Natural Language Processing, Computer Vision, Deep Learning, Statistics",
        "Docker, Kubernetes, AWS, Linux, Git, CI/CD",
        "",
        "EXPERIENCE",
        "Machine Learning Engineer, VisionAI Labs (2021 - present)",
        "- Trained PyTorch image classifiers and deployed them with Docker on AWS.",
        "- Built an NLP pipeline for support-ticket classification.",
        "",
        "EDUCATION",
        "M.Tech. Artificial Intelligence, 2021",
    ]],
    # Two pages, to check that text from every page is extracted.
    "java_backend_rahul.pdf": [
        [
            "Rahul Verma - Backend Java Developer",
            "Email: rahul@example.com",
            "",
            "SUMMARY",
            "Backend developer with 5 years of experience building Java microservices.",
            "",
            "SKILLS",
            "Java, Spring Boot, REST API, PostgreSQL, MySQL, Kafka",
            "Docker, Kubernetes, Jenkins, CI/CD, Git, Linux",
            "",
            "EXPERIENCE",
            "Senior Software Engineer, FinServe Tech (2021 - present)",
            "- Designed Spring Boot microservices processing 2 million payments a day.",
            "- Set up Jenkins CI/CD pipelines and Kubernetes deployments.",
        ],
        [
            "Software Engineer, CloudNine Systems (2019 - 2021)",
            "- Built REST API services in Java backed by PostgreSQL.",
            "- Worked in an Agile Scrum team and mentored two interns (leadership).",
            "",
            "EDUCATION",
            "B.E. Computer Engineering, 2019",
        ],
    ],
    "fresher_sneha.pdf": [[
        "Sneha Reddy - Computer Science Graduate",
        "Email: sneha@example.com",
        "",
        "OBJECTIVE",
        "Fresh graduate looking for an entry-level software developer role.",
        "",
        "SKILLS",
        "C, C++, Python, HTML, CSS, SQL",
        "Problem solving, teamwork, communication",
        "",
        "PROJECTS",
        "- Library management system in C++ with file storage.",
        "- Personal portfolio website using HTML and CSS.",
        "",
        "EDUCATION",
        "B.Sc. Computer Science, 2026",
    ]],
    "marketing_karan.pdf": [[
        "Karan Malhotra - Marketing Executive",
        "Email: karan@example.com",
        "",
        "SUMMARY",
        "Marketing executive experienced in brand campaigns and social media growth.",
        "",
        "SKILLS",
        "Brand strategy, social media marketing, copywriting, event planning",
        "Public speaking, leadership, communication",
        "",
        "EXPERIENCE",
        "Marketing Executive, BrightLeaf Foods (2022 - present)",
        "- Ran Instagram campaigns that grew followers by 60% in one year.",
        "- Organized product launch events in three cities.",
        "",
        "EDUCATION",
        "BBA Marketing, 2022",
    ]],
    "hr_coordinator_neha.pdf": [[
        "Neha Kapoor - HR Coordinator",
        "Email: neha@example.com",
        "",
        "SUMMARY",
        "HR coordinator with 3 years of experience in recruitment and employee onboarding.",
        "",
        "SKILLS",
        "Recruitment, onboarding, payroll, employee engagement, Excel",
        "Communication, attention to detail, time management",
        "",
        "EXPERIENCE",
        "HR Coordinator, Maple Logistics (2022 - present)",
        "- Handled recruitment for 40 roles a year, from screening to offer letters.",
        "- Ran onboarding for 120 new employees and kept payroll records up to date.",
        "- Organized quarterly employee engagement surveys.",
        "",
        "EDUCATION",
        "MBA Human Resources, 2022",
    ]],
    "finance_analyst_vikram.pdf": [[
        "Vikram Iyer - Financial Analyst",
        "Email: vikram@example.com",
        "",
        "SUMMARY",
        "Financial analyst with 4 years of experience in budgeting and financial analysis.",
        "",
        "SKILLS",
        "Excel, financial modeling, financial analysis, budgeting, accounting, Power BI",
        "Attention to detail, communication",
        "",
        "EXPERIENCE",
        "Financial Analyst, Lakeside Retail (2021 - present)",
        "- Built financial modeling templates in Excel for 15 stores.",
        "- Led annual budgeting and reduced forecast errors by 18%.",
        "- Prepared monthly Power BI reports on costs and margins for senior managers.",
        "",
        "EDUCATION",
        "B.Com Accounting and Finance, 2021",
    ]],
    "ui_ux_designer_ananya.pdf": [[
        "Ananya Bose - UI/UX Designer",
        "Portfolio: https://ananya.example.dev",
        "",
        "PROFILE",
        "Product designer with 3 years of experience in mobile app design.",
        "",
        "KEY SKILLS",
        "Figma, UX design, UI design, Adobe Photoshop, Adobe Illustrator",
        "Teamwork, communication, user research, prototypes",
        "",
        "PROFESSIONAL EXPERIENCE",
        "Product Designer, TripNest (2023 - present)",
        "- Ran user research with 30 travellers and redesigned the booking flow in Figma.",
        "- Built clickable prototypes that raised booking completion by 12%.",
        "- Worked on UI design with developers using a shared component library.",
        "",
        "EDUCATION",
        "B.Des Interaction Design, 2023",
    ]],
    "devops_engineer_farhan.pdf": [[
        "Farhan Ali - DevOps Engineer",
        "Email: farhan@example.com",
        "",
        "SUMMARY",
        "DevOps engineer with 5 years of experience in cloud infrastructure and automation.",
        "",
        "TECHNICAL SKILLS",
        "Docker, Kubernetes, AWS, Linux, Python, Jenkins, GitHub, Terraform, CI/CD",
        "Problem solving, teamwork",
        "",
        "WORK EXPERIENCE",
        "DevOps Engineer, CloudHarbor (2020 - present)",
        "- Moved 25 services to Kubernetes on AWS and cut hosting costs by 30%.",
        "- Built CI/CD pipelines in Jenkins that reduced release time from days to hours.",
        "- Wrote Python scripts to automate Linux server patching.",
        "",
        "EDUCATION",
        "B.Tech Information Technology, 2020",
    ]],
    "android_developer_diya.pdf": [[
        "Diya Nair - Android Developer",
        "GitHub: https://github.example.dev/diya",
        "",
        "SUMMARY",
        "Android developer with 2 years of experience building consumer mobile apps.",
        "",
        "SKILLS",
        "Kotlin, Java, SQLite, REST APIs, Git, Firebase, Agile",
        "",
        "EXPERIENCE",
        "Android Developer, StepUp Apps (2024 - present)",
        "- Built workout tracking features in Kotlin for an app with 200,000 users.",
        "- Connected the app to REST APIs and stored offline data in SQLite.",
        "- Reduced crash rate by 40% through Git code reviews and testing.",
        "",
        "PROJECTS",
        "- Expense tracker Android app in Java, published on the Play Store.",
        "",
        "EDUCATION",
        "B.E. Computer Engineering, 2024",
    ]],
    "project_manager_rohan.pdf": [[
        "Rohan Desai - Project Manager",
        "Email: rohan@example.com",
        "",
        "SUMMARY",
        "Project manager with 6 years of experience delivering software for clients.",
        "",
        "SKILLS",
        "Project management, Agile, Scrum, stakeholder management, Jira, budgeting",
        "Leadership, communication",
        "",
        "EXPERIENCE",
        "Project Manager, Finlay Systems (2019 - present)",
        "- Led Agile delivery of 12 client projects worth over 2 million dollars.",
        "- Ran Scrum ceremonies and tracked work in Jira for teams of 10 developers.",
        "- Managed stakeholder management and monthly budgeting reports for clients.",
        "",
        "EDUCATION",
        "Bachelor of Engineering, 2019",
    ]],
}


def two_column_page(left, right, row_order=False):
    """Return a page of (x, y, text) lines laid out in two columns.

    By default the PDF stores the left column and then the right one. With row_order
    it stores lines row by row across the columns, which is harder to extract.
    """
    lines = [(40, 790 - 15 * i, text) for i, text in enumerate(left) if text]
    lines += [(225, 790 - 15 * i, text) for i, text in enumerate(right) if text]
    return sorted(lines, key=lambda line: (-line[1], line[0])) if row_order else lines


RESUMES["two_column_tanvi.pdf"] = [two_column_page(
    [
        "Tanvi Joshi",
        "tanvi@example.com",
        "",
        "SKILLS",
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
        "Tableau",
        "Power BI",
        "Statistics",
        "Git",
        "",
        "EDUCATION",
        "B.Sc. Statistics, 2022",
    ],
    [
        "SUMMARY",
        "Data analyst with 3 years of experience in Python and SQL.",
        "",
        "EXPERIENCE",
        "Data Analyst, Harbor Insurance (2022 - present)",
        "- Built Tableau dashboards used by 50 managers.",
        "- Automated monthly reports in Python, saving 10 hours.",
        "- Wrote SQL queries to find claims errors.",
        "- Presented findings to stakeholders with clear communication.",
        "",
        "PROJECTS",
        "- Customer churn analysis with Pandas and NumPy.",
        "- Sales forecast model using machine learning.",
    ],
)]

RESUMES["two_column_kabir.pdf"] = [two_column_page(
    [
        "Kabir Sethi",
        "kabir@example.com",
        "",
        "SKILLS",
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "HTML",
        "CSS",
        "Git",
        "",
        "EDUCATION",
        "B.Tech Computer Science",
        "2023",
    ],
    [
        "SUMMARY",
        "Frontend developer with 3 years of experience in React.",
        "",
        "EXPERIENCE",
        "Frontend Developer, PixelCart (2023 - present)",
        "- Built React and TypeScript pages for 80,000 shoppers.",
        "- Connected pages to REST APIs on a Node.js backend.",
        "- Improved page load time by 35% with CSS cleanup.",
        "- Reviewed code in Git with a team of 6 developers.",
        "",
        "PROJECTS",
        "- Recipe search site in JavaScript, HTML and CSS.",
    ],
    row_order=True,
)]


def _esc(s):
    return s.replace("\\", "\\\\").replace("(", r"\(").replace(")", r"\)")


def build_pdf(pages):
    """Return the bytes of a simple PDF. A page with no lines has no text layer."""
    n = len(pages)
    font_id = 3 + 2 * n
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(n))
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode(),
    ]
    for i, lines in enumerate(pages):
        if lines and isinstance(lines[0], tuple):  # two-column page of (x, y, text)
            ops = ["BT", "/F1 10 Tf"]
            ops += [f"1 0 0 1 {x} {y} Tm ({_esc(text)}) Tj" for x, y, text in lines]
        else:
            ops = ["BT", "/F1 11 Tf", "14 TL", "50 790 Td"]
            ops += [f"({_esc(line)}) Tj T*" for line in lines]
        ops.append("ET")
        stream = "\n".join(ops).encode("latin-1") if lines else b""
        objs.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Contents {4 + 2 * i} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>".encode()
        )
        objs.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)


def build_encrypted_pdf(pages, password="secret123"):
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter(clone_from=PdfReader(BytesIO(build_pdf(pages))))
    writer.encrypt(user_password=password, algorithm="RC4-128")
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


def main():
    resumes_dir = HERE / "resumes"
    invalid_dir = HERE / "invalid"
    resumes_dir.mkdir(exist_ok=True)
    invalid_dir.mkdir(exist_ok=True)

    for name, pages in RESUMES.items():
        (resumes_dir / name).write_bytes(build_pdf(pages))
        print(f"Wrote resumes/{name}")

    # Each job description as a PDF too, for the "Upload PDF" option.
    for job in sorted((HERE / "jobs").glob("*.txt")):
        job.with_suffix(".pdf").write_bytes(build_pdf([job.read_text().splitlines()]))
        print(f"Wrote jobs/{job.stem}.pdf")

    # T-05: a page with no text layer, like a scanned/image-only resume.
    (invalid_dir / "scanned_no_text.pdf").write_bytes(build_pdf([[]]))
    # T-09: a PDF whose bytes have been cut off / damaged.
    (invalid_dir / "corrupt.pdf").write_bytes(build_pdf(RESUMES["fresher_sneha.pdf"])[:200])
    # A text file renamed to .pdf.
    (invalid_dir / "not_really_a_pdf.pdf").write_bytes(b"Just a plain text file, not a PDF.\n")
    # A PDF that needs a password to open (password: secret123).
    (invalid_dir / "password_protected.pdf").write_bytes(
        build_encrypted_pdf(RESUMES["data_analyst_priya.pdf"])
    )
    print("Wrote invalid/ files")


if __name__ == "__main__":
    main()
