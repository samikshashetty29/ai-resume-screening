"""Generate full-length, realistically formatted sample resumes and job description PDFs.

Run from the project folder:  python sample_data/make_realistic_resumes.py
The job descriptions are written in realistic_jobs/*.txt; this makes a PDF of each.
It needs fpdf2 and the Calibri font that comes with Windows, which is embedded in
each PDF so the files look the same everywhere. All people, companies, colleges,
phone numbers and addresses below are fictional.
"""
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

HERE = Path(__file__).parent
OUT = HERE / "realistic_resumes"
JOBS = HERE / "realistic_jobs"
FONTS = Path("C:/Windows/Fonts")

ACCENT = (31, 78, 121)
GREY = (90, 90, 90)

# Each section is (heading, kind, content). Kinds:
#   text     a paragraph
#   labels   (label, value) lines, e.g. ("Languages", "Python, SQL")
#   entries  dicts with role, org, dates, optional place, and bullets
#   bullets  plain bullet points
RESUMES = {
    "ishita_rao_data_analyst.pdf": {
        "name": "Ishita Rao",
        "title": "Data Analyst",
        "contact": "Pune, India  |  ishita.rao@example.com  |  +91 90000 10001  |  ishitarao.example.com",
        "sections": [
            ("PROFESSIONAL SUMMARY", "text",
             "Data analyst with 3 years of experience turning sales and customer data into "
             "decisions. Builds dashboards in Power BI and Tableau, writes production SQL, "
             "and automates reporting in Python with Pandas and NumPy. Comfortable presenting "
             "findings to non-technical managers and working in Agile teams."),
            ("TECHNICAL SKILLS", "labels", [
                ("Languages", "Python, SQL"),
                ("Data and analysis", "Pandas, NumPy, statistics, A/B testing, Excel"),
                ("Visualization", "Power BI, Tableau, Matplotlib"),
                ("Tools", "MySQL, PostgreSQL, Git, Jira"),
            ]),
            ("PROFESSIONAL EXPERIENCE", "entries", [
                {"role": "Data Analyst", "org": "Kestrel Retail Pvt. Ltd.", "place": "Pune",
                 "dates": "Jun 2023 - Present", "bullets": [
                     "Built 14 Power BI dashboards for regional sales heads, replacing a weekly "
                     "Excel pack and saving about 6 hours of manual work each week.",
                     "Wrote SQL on a 40 million row PostgreSQL warehouse to track store "
                     "performance, returns and stock-outs.",
                     "Automated the monthly churn report in Python and Pandas, cutting its "
                     "turnaround from 3 days to 4 hours.",
                     "Ran A/B tests on 3 loyalty offers with the marketing team; the winning "
                     "offer lifted repeat purchases by 8%.",
                 ]},
                {"role": "Junior Data Analyst", "org": "Brightline Insights", "place": "Mumbai",
                 "dates": "Jul 2022 - May 2023", "bullets": [
                     "Cleaned and merged survey data from 12,000 respondents using Pandas.",
                     "Created Tableau reports for 5 client accounts and presented results in "
                     "fortnightly review calls.",
                     "Documented 20+ standard SQL queries so new analysts could reuse them.",
                 ]},
            ]),
            ("PROJECTS", "entries", [
                {"role": "Customer Segmentation", "org": "Personal project", "dates": "2024",
                 "bullets": [
                     "Grouped 50,000 online shoppers into 5 segments with k-means clustering "
                     "and explained each segment in a short Tableau story.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "B.Sc. Statistics", "org": "Deccan College of Science, Pune",
                 "dates": "2019 - 2022", "bullets": ["CGPA 8.4 / 10"]},
            ]),
            ("CERTIFICATIONS", "bullets", [
                "Microsoft Certified: Power BI Data Analyst Associate (2023)",
                "Google Data Analytics Certificate (2022)",
            ]),
        ],
    },
    "rohit_kulkarni_frontend_developer.pdf": {
        "name": "Rohit Kulkarni",
        "title": "Frontend Developer",
        "contact": "Bengaluru, India  |  rohit.k@example.com  |  +91 90000 10002  |  rohitk.example.dev",
        "sections": [
            ("SUMMARY", "text",
             "Frontend developer with 4 years of experience building fast, accessible web "
             "applications in React and TypeScript. Works closely with designers and backend "
             "teams on REST API and GraphQL integrations, and cares about performance, "
             "testing and clean, reusable components."),
            ("SKILLS", "labels", [
                ("Frontend", "React, TypeScript, JavaScript, HTML, CSS, Redux, Tailwind"),
                ("Backend and APIs", "Node.js, Express, REST API, GraphQL"),
                ("Testing and tools", "Jest, React Testing Library, Git, GitHub, Docker"),
                ("Ways of working", "Agile, Scrum, code reviews"),
            ]),
            ("WORK EXPERIENCE", "entries", [
                {"role": "Frontend Developer", "org": "Cartwheel Commerce", "place": "Bengaluru",
                 "dates": "Mar 2022 - Present", "bullets": [
                     "Rebuilt the checkout in React and TypeScript for 300,000 monthly "
                     "shoppers, raising completed orders by 11%.",
                     "Moved product pages to a GraphQL API, reducing data loaded per page "
                     "by 45%.",
                     "Cut the main bundle size from 1.8 MB to 700 KB with code splitting and "
                     "lazy loading.",
                     "Raised unit test coverage from 35% to 80% with Jest and React Testing "
                     "Library.",
                     "Mentored 2 junior developers through weekly pairing and code reviews.",
                 ]},
                {"role": "Web Developer", "org": "Lumen Digital Agency", "place": "Pune",
                 "dates": "Jul 2020 - Feb 2022", "bullets": [
                     "Delivered 15 responsive client websites in HTML, CSS and JavaScript.",
                     "Built a Node.js and Express REST API for a restaurant booking site "
                     "handling 2,000 bookings a month.",
                     "Fixed accessibility issues to meet WCAG 2.1 AA on 6 public sites.",
                 ]},
            ]),
            ("PROJECTS", "entries", [
                {"role": "Open-source date picker", "org": "React component library",
                 "dates": "2023", "bullets": [
                     "Keyboard-accessible date picker downloaded about 1,200 times a week.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "B.E. Computer Engineering", "org": "Sahyadri Institute of Technology",
                 "dates": "2016 - 2020", "bullets": []},
            ]),
        ],
    },
    "ananya_menon_ml_engineer.pdf": {
        "name": "Ananya Menon",
        "title": "Machine Learning Engineer",
        "contact": "Hyderabad, India  |  ananya.menon@example.com  |  +91 90000 10003",
        "sections": [
            ("PROFESSIONAL SUMMARY", "text",
             "Machine learning engineer with 4 years of experience designing, training and "
             "deploying deep learning models for natural language processing and computer "
             "vision. Strong in Python, PyTorch and scikit-learn, and in taking models to "
             "production with Docker, Kubernetes and CI/CD on AWS."),
            ("TECHNICAL SKILLS", "labels", [
                ("Machine learning", "PyTorch, TensorFlow, scikit-learn, Hugging Face Transformers"),
                ("Data", "Python, NumPy, Pandas, SQL, Spark, statistics"),
                ("MLOps", "Docker, Kubernetes, AWS SageMaker, MLflow, CI/CD, GitHub Actions"),
                ("Systems", "Linux, Git, FastAPI"),
            ]),
            ("PROFESSIONAL EXPERIENCE", "entries", [
                {"role": "Machine Learning Engineer", "org": "Quillbyte AI", "place": "Hyderabad",
                 "dates": "Jan 2023 - Present", "bullets": [
                     "Fine-tuned a transformer model in PyTorch to route support tickets, "
                     "reaching 92% accuracy and saving the support team 25 hours a week.",
                     "Served models behind FastAPI on Kubernetes, keeping response time under "
                     "120 ms at 50 requests per second.",
                     "Set up CI/CD with GitHub Actions to test, package with Docker and "
                     "deploy models to AWS, cutting release time from 2 days to 2 hours.",
                     "Tracked 300+ experiments in MLflow so results could be reproduced.",
                 ]},
                {"role": "Data Scientist", "org": "Opticore Vision Labs", "place": "Chennai",
                 "dates": "Jun 2021 - Dec 2022", "bullets": [
                     "Trained computer vision models to spot packaging defects, reducing "
                     "missed defects by 30% on 3 production lines.",
                     "Built feature pipelines in Pandas and NumPy, and baselines in "
                     "scikit-learn, for every new client dataset.",
                     "Explained model results to plant managers using simple statistics "
                     "and charts.",
                 ]},
            ]),
            ("PROJECTS", "entries", [
                {"role": "Hindi-English news classifier", "org": "Personal project",
                 "dates": "2024", "bullets": [
                     "Multilingual NLP model with 88% F1 on 20,000 labelled headlines.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "M.Tech. Artificial Intelligence", "org": "Coastal Institute of Technology",
                 "dates": "2019 - 2021", "bullets": [
                     "Thesis: low-light image enhancement with convolutional networks"]},
                {"role": "B.Tech. Computer Science", "org": "Malabar Engineering College",
                 "dates": "2015 - 2019", "bullets": []},
            ]),
            ("PUBLICATIONS", "bullets", [
                "A. Menon, \"Lightweight defect detection for packaging lines\", "
                "Regional Conference on Applied Vision, 2022",
            ]),
        ],
    },
    "vivek_shetty_java_backend.pdf": {
        "name": "Vivek Shetty",
        "title": "Backend Java Developer",
        "contact": "Mangaluru, India  |  vivek.shetty@example.com  |  +91 90000 10004",
        "sections": [
            ("SUMMARY", "text",
             "Backend developer with 6 years of experience building Java and Spring Boot "
             "microservices for payments and banking. Designs REST APIs, tunes PostgreSQL and "
             "MySQL databases, and runs services on Docker and Kubernetes with Jenkins CI/CD. "
             "Enjoys mentoring junior developers."),
            ("TECHNICAL SKILLS", "labels", [
                ("Languages", "Java 17, SQL, Bash"),
                ("Frameworks", "Spring Boot, Spring Security, Hibernate, JUnit, Mockito"),
                ("Data", "PostgreSQL, MySQL, Redis, Kafka"),
                ("DevOps", "Docker, Kubernetes, Jenkins, CI/CD, Linux, Git"),
            ]),
            ("PROFESSIONAL EXPERIENCE", "entries", [
                {"role": "Senior Software Engineer", "org": "Paylane Technologies",
                 "place": "Bengaluru", "dates": "Apr 2021 - Present", "bullets": [
                     "Led a team of 4 building the refunds service in Java and Spring Boot, "
                     "processing 1.5 million refunds a month.",
                     "Designed REST APIs used by 30 partner banks, with versioning and "
                     "OpenAPI documentation.",
                     "Cut the slowest PostgreSQL query from 4 seconds to 150 ms with "
                     "indexing and query rewrites.",
                     "Moved 9 services to Docker and Kubernetes with Jenkins pipelines, "
                     "reducing deployment time by 70%.",
                     "Mentored 3 junior developers, two of whom were promoted within a year.",
                 ]},
                {"role": "Software Engineer", "org": "Coastline Bank IT Services",
                 "place": "Mangaluru", "dates": "Jul 2018 - Mar 2021", "bullets": [
                     "Built account statement services in Java with MySQL for 2 million "
                     "customers.",
                     "Added JUnit and Mockito tests that caught 40+ bugs before release.",
                     "Worked in an Agile team with two-week sprints and daily stand-ups.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "B.E. Information Science", "org": "Karavali Institute of Engineering",
                 "dates": "2014 - 2018", "bullets": []},
            ]),
            ("CERTIFICATIONS", "bullets", [
                "Oracle Certified Professional: Java SE 17 Developer (2023)",
                "Certified Kubernetes Application Developer (CKAD) (2022)",
            ]),
        ],
    },
    "sanya_kapoor_marketing_executive.pdf": {
        "name": "Sanya Kapoor",
        "title": "Marketing Executive",
        "contact": "New Delhi, India  |  sanya.kapoor@example.com  |  +91 90000 10005",
        "sections": [
            ("PROFILE", "text",
             "Marketing executive with 3 years of experience running brand campaigns for food "
             "and lifestyle products. Grows social media communities, writes copy that sells, "
             "and organizes product launch events from idea to launch day. Confident speaker "
             "who coordinates designers, agencies and sales teams."),
            ("KEY SKILLS", "labels", [
                ("Marketing", "Social media marketing, brand strategy, content marketing, "
                              "copywriting, email marketing"),
                ("Channels", "Instagram, YouTube, LinkedIn, influencer partnerships"),
                ("Tools", "Meta Business Suite, Google Analytics, Canva, Excel"),
                ("Strengths", "Public speaking, leadership, event planning"),
            ]),
            ("EXPERIENCE", "entries", [
                {"role": "Marketing Executive", "org": "Haldi & Co. Foods", "place": "New Delhi",
                 "dates": "Aug 2022 - Present", "bullets": [
                     "Grew the brand's Instagram from 18,000 to 95,000 followers in 18 "
                     "months with a weekly recipe series.",
                     "Planned and ran 6 product launch events, each attracting 200+ guests "
                     "and local press.",
                     "Wrote packaging and campaign copy for 12 new products.",
                     "Tracked campaign results in Excel and Google Analytics and shared a "
                     "monthly report with the sales head.",
                 ]},
                {"role": "Marketing Intern", "org": "Bloom Lifestyle Pvt. Ltd.", "place": "Gurugram",
                 "dates": "Jan 2022 - Jul 2022", "bullets": [
                     "Coordinated 25 influencer partnerships for a skincare launch.",
                     "Drafted email newsletters with a 32% average open rate.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "BBA, Marketing", "org": "Yamuna School of Management", "dates": "2018 - 2021",
                 "bullets": []},
            ]),
            ("ACHIEVEMENTS", "bullets", [
                "Best Campaign award, Haldi & Co. annual awards (2023)",
                "Speaker at a regional food entrepreneurs meetup (2024)",
            ]),
        ],
    },
    "kavya_reddy_hr_coordinator.pdf": {
        "name": "Kavya Reddy",
        "title": "HR Coordinator",
        "contact": "Hyderabad, India  |  kavya.reddy@example.com  |  +91 90000 10006",
        "sections": [
            ("PROFESSIONAL SUMMARY", "text",
             "HR coordinator with 3 years of experience in recruitment, onboarding and "
             "employee engagement for a 600-person company. Organized and detail-oriented, "
             "keeps employee records accurate and answers payroll queries quickly and kindly."),
            ("CORE SKILLS", "labels", [
                ("HR", "Recruitment, interview scheduling, onboarding, payroll support, "
                       "employee engagement, HR records"),
                ("Systems", "Zoho People, Keka, Excel, Google Workspace"),
                ("Strengths", "Communication, attention to detail, time management"),
            ]),
            ("WORK EXPERIENCE", "entries", [
                {"role": "HR Coordinator", "org": "Greenfield Logistics", "place": "Hyderabad",
                 "dates": "May 2022 - Present", "bullets": [
                     "Scheduled 900+ interviews a year across 8 departments and kept every "
                     "hiring manager updated.",
                     "Redesigned onboarding so new joiners had laptops and access on day one, "
                     "raising first-month satisfaction from 3.6 to 4.5 out of 5.",
                     "Organized 20 training sessions and 4 engagement events each year.",
                     "Resolved about 60 payroll queries a month, working with the finance team.",
                     "Kept 600 employee records up to date for audits.",
                 ]},
                {"role": "HR Assistant", "org": "Sunrise Hospitals", "place": "Hyderabad",
                 "dates": "Jun 2021 - Apr 2022", "bullets": [
                     "Screened 150 nursing applications a month and arranged walk-in drives.",
                     "Prepared offer letters and joining documents.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "MBA, Human Resources", "org": "Godavari Business School",
                 "dates": "2019 - 2021", "bullets": []},
                {"role": "B.Com.", "org": "Charminar Degree College", "dates": "2016 - 2019",
                 "bullets": []},
            ]),
        ],
    },
    "arnav_desai_financial_analyst.pdf": {
        "name": "Arnav Desai",
        "title": "Financial Analyst",
        "contact": "Ahmedabad, India  |  arnav.desai@example.com  |  +91 90000 10007",
        "sections": [
            ("SUMMARY", "text",
             "Financial analyst with 4 years of experience in budgeting, forecasting and "
             "financial modeling for retail and manufacturing businesses. Builds clear Excel "
             "models and Power BI reports that help senior managers understand costs and "
             "margins."),
            ("SKILLS", "labels", [
                ("Finance", "Financial analysis, financial modeling, budgeting, forecasting, "
                            "variance analysis, accounting"),
                ("Tools", "Excel (advanced), Power BI, SQL, Tally, SAP"),
                ("Strengths", "Attention to detail, communication"),
            ]),
            ("EXPERIENCE", "entries", [
                {"role": "Financial Analyst", "org": "Sabarmati Retail Group", "place": "Ahmedabad",
                 "dates": "Jan 2022 - Present", "bullets": [
                     "Own the annual budget for 45 stores worth INR 320 crore, and the "
                     "monthly forecast that goes to the CFO.",
                     "Built a store profitability model in Excel that found INR 2.1 crore "
                     "of yearly savings in rent and staffing.",
                     "Created Power BI reports on margins and costs used by 12 senior managers.",
                     "Cut month-end reporting from 6 days to 3 by pulling data with SQL.",
                 ]},
                {"role": "Junior Analyst", "org": "Narmada Steel Works", "place": "Vadodara",
                 "dates": "Jul 2020 - Dec 2021", "bullets": [
                     "Prepared monthly variance analysis for 3 plants.",
                     "Supported the statutory audit by reconciling 200+ ledger accounts.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "B.Com. (Accounting and Finance)", "org": "Gujarat College of Commerce",
                 "dates": "2017 - 2020", "bullets": []},
            ]),
            ("CERTIFICATIONS", "bullets", [
                "CFA Level I (passed, 2022)",
                "Financial Modeling and Valuation course (2021)",
            ]),
        ],
    },
    "meher_joshi_ui_ux_designer.pdf": {
        "name": "Meher Joshi",
        "title": "UI/UX Designer",
        "contact": "Mumbai, India  |  meher.joshi@example.com  |  meherjoshi.example.com",
        "sections": [
            ("ABOUT ME", "text",
             "Product designer with 3 years of experience designing mobile and web apps. I "
             "run user research, turn findings into wireframes and prototypes in Figma, and "
             "work side by side with developers until the design ships."),
            ("SKILLS", "labels", [
                ("Design", "UX design, UI design, wireframes, prototypes, design systems"),
                ("Research", "User research, usability testing, interviews, journey maps"),
                ("Tools", "Figma, Adobe Illustrator, Adobe Photoshop, Miro"),
                ("Also", "HTML, CSS, teamwork, communication"),
            ]),
            ("EXPERIENCE", "entries", [
                {"role": "UI/UX Designer", "org": "Wanderly Travel App", "place": "Mumbai",
                 "dates": "Feb 2023 - Present", "bullets": [
                     "Redesigned hotel booking after 18 user interviews; bookings completed "
                     "on mobile rose by 22%.",
                     "Built a Figma design system with 120 components used by 3 product teams.",
                     "Ran monthly usability tests and shared clear findings with developers "
                     "and product managers.",
                 ]},
                {"role": "Junior Product Designer", "org": "Pixelnest Studio", "place": "Pune",
                 "dates": "Jun 2021 - Jan 2023", "bullets": [
                     "Designed screens for 7 client apps from wireframes to final UI.",
                     "Created marketing visuals in Adobe Illustrator and Photoshop.",
                 ]},
            ]),
            ("PROJECTS", "entries", [
                {"role": "Accessible bus timetable", "org": "Case study", "dates": "2024",
                 "bullets": [
                     "Prototype tested with 10 older users; task time fell from 90 to 35 seconds.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "B.Des. Interaction Design", "org": "Western Institute of Design",
                 "dates": "2017 - 2021", "bullets": []},
            ]),
        ],
    },
    "farah_khan_devops_engineer.pdf": {
        "name": "Farah Khan",
        "title": "DevOps Engineer",
        "contact": "Noida, India  |  farah.khan@example.com  |  +91 90000 10009",
        "sections": [
            ("PROFESSIONAL SUMMARY", "text",
             "DevOps engineer with 5 years of experience keeping cloud platforms fast and "
             "reliable. Runs Docker and Kubernetes in production on AWS, builds CI/CD "
             "pipelines in Jenkins and GitHub Actions, and automates infrastructure with "
             "Terraform and Python."),
            ("TECHNICAL SKILLS", "labels", [
                ("Cloud", "AWS (EKS, EC2, S3, RDS), Azure basics"),
                ("Containers", "Docker, Kubernetes, Helm"),
                ("CI/CD", "Jenkins, GitHub Actions, Argo CD"),
                ("Infrastructure", "Terraform, Ansible, Linux administration"),
                ("Scripting and monitoring", "Python, Bash, Prometheus, Grafana"),
            ]),
            ("PROFESSIONAL EXPERIENCE", "entries", [
                {"role": "DevOps Engineer", "org": "Cloudmint Software", "place": "Noida",
                 "dates": "Mar 2021 - Present", "bullets": [
                     "Run 14 Kubernetes clusters on AWS EKS serving 2 million daily users at "
                     "99.95% uptime.",
                     "Rebuilt CI/CD in Jenkins and GitHub Actions so 40 developers can "
                     "deploy in 12 minutes instead of 2 hours.",
                     "Wrote Terraform for all AWS infrastructure, removing manual changes.",
                     "Reduced the monthly AWS bill by 28% by right-sizing nodes and using "
                     "spot instances.",
                     "Led incident reviews and wrote 25 runbooks for the on-call team.",
                 ]},
                {"role": "Linux System Administrator", "org": "Indus Data Centres",
                 "place": "Gurugram", "dates": "Jul 2019 - Feb 2021", "bullets": [
                     "Managed 300 Linux servers and automated patching with Ansible and Python.",
                     "Moved 20 internal apps into Docker containers.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "B.Tech. Computer Science", "org": "Ganga Institute of Technology",
                 "dates": "2015 - 2019", "bullets": []},
            ]),
            ("CERTIFICATIONS", "bullets", [
                "AWS Certified Solutions Architect - Associate (2022)",
                "Certified Kubernetes Administrator (CKA) (2023)",
            ]),
        ],
    },
    "nikhil_bhat_android_developer.pdf": {
        "name": "Nikhil Bhat",
        "title": "Android Developer",
        "contact": "Bengaluru, India  |  nikhil.bhat@example.com  |  +91 90000 10010",
        "sections": [
            ("SUMMARY", "text",
             "Android developer with 3 years of experience building consumer apps in Kotlin "
             "and Java. Integrates REST APIs, stores data offline with Room and SQLite, and "
             "works on app speed and stability. Used to Git, code reviews and Agile teams."),
            ("SKILLS", "labels", [
                ("Languages", "Kotlin, Java"),
                ("Android", "Jetpack Compose, Room, SQLite, Retrofit, Coroutines, WorkManager"),
                ("Services", "REST API, Firebase (Crashlytics, Cloud Messaging)"),
                ("Tools", "Android Studio, Git, GitHub, Jira, Agile"),
            ]),
            ("EXPERIENCE", "entries", [
                {"role": "Android Developer", "org": "Stride Fitness", "place": "Bengaluru",
                 "dates": "Apr 2022 - Present", "bullets": [
                     "Built workout tracking screens in Kotlin and Jetpack Compose for an app "
                     "with 800,000 users.",
                     "Added offline mode with Room and SQLite, so workouts sync when the "
                     "phone reconnects.",
                     "Cut app start time from 2.4 to 1.1 seconds and crashes by 60%, tracked "
                     "with Firebase Crashlytics.",
                     "Reviewed about 10 pull requests a week in Git.",
                 ]},
                {"role": "Junior Android Developer", "org": "Kadamba Apps", "place": "Mysuru",
                 "dates": "Jul 2021 - Mar 2022", "bullets": [
                     "Maintained 3 Java apps and connected them to REST APIs with Retrofit.",
                     "Fixed 120 bugs reported from the Play Store.",
                 ]},
            ]),
            ("PROJECTS", "entries", [
                {"role": "Expense Split", "org": "Play Store app", "dates": "2023",
                 "bullets": ["Kotlin app for sharing trip costs, 10,000+ downloads, rated 4.6."]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "B.E. Computer Science", "org": "Chamundi Institute of Technology",
                 "dates": "2017 - 2021", "bullets": []},
            ]),
        ],
    },
    "pooja_iyer_project_manager.pdf": {
        "name": "Pooja Iyer",
        "title": "Project Manager",
        "contact": "Chennai, India  |  pooja.iyer@example.com  |  +91 90000 10011",
        "sections": [
            ("PROFESSIONAL SUMMARY", "text",
             "Project manager with 7 years of experience in project management for client "
             "software projects. Leads Agile and Scrum delivery, manages budgets and risks, "
             "and keeps clients and developers aligned from kickoff to launch."),
            ("CORE COMPETENCIES", "labels", [
                ("Delivery", "Agile, Scrum, Kanban, release planning, risk management"),
                ("Management", "Stakeholder management, budgeting, reporting, vendor management"),
                ("Tools", "Jira, Confluence, MS Project, Excel"),
                ("Strengths", "Communication, leadership, problem solving"),
            ]),
            ("PROFESSIONAL EXPERIENCE", "entries", [
                {"role": "Project Manager", "org": "Tidewater Software Solutions", "place": "Chennai",
                 "dates": "Jun 2020 - Present", "bullets": [
                     "Led 9 client projects worth INR 18 crore in total, delivering 8 on time "
                     "and within budget.",
                     "Ran Scrum for 3 teams of up to 12 people, using Jira for sprints and "
                     "reporting.",
                     "Kept a risk log reviewed weekly with clients, which helped avoid 2 major "
                     "launch delays.",
                     "Sent clear weekly status reports to client directors.",
                 ]},
                {"role": "Associate Project Manager", "org": "Kaveri Infotech", "place": "Chennai",
                 "dates": "Jul 2017 - May 2020", "bullets": [
                     "Coordinated delivery of a hospital billing system for 14 hospitals.",
                     "Tracked project budgets and raised invoices with the finance team.",
                 ]},
            ]),
            ("EDUCATION", "entries", [
                {"role": "B.E. Electronics and Communication", "org": "Marina Engineering College",
                 "dates": "2013 - 2017", "bullets": []},
            ]),
            ("CERTIFICATIONS", "bullets", [
                "Project Management Professional (PMP) (2022)",
                "Certified ScrumMaster (CSM) (2020)",
            ]),
        ],
    },
}


class ResumePDF(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        # A fixed date, so regenerating only changes files whose content changed.
        self.set_creation_date(datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.add_font("Calibri", "", FONTS / "calibri.ttf")
        self.add_font("Calibri", "B", FONTS / "calibrib.ttf")
        self.add_font("Calibri", "I", FONTS / "calibrii.ttf")
        self.set_margins(18, 15, 18)
        self.set_auto_page_break(True, margin=15)

    @property
    def width(self):
        return self.w - self.l_margin - self.r_margin

    def text_line(self, text, size=10.5, style="", color=(0, 0, 0), height=5.2):
        self.set_font("Calibri", style, size)
        self.set_text_color(*color)
        self.multi_cell(self.width, height, text, align=Align.L,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def heading(self, text):
        self.ln(2.5)
        self.set_font("Calibri", "B", 12)
        self.set_text_color(*ACCENT)
        self.cell(self.width, 6.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*ACCENT)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(1.5)

    def bullet(self, text):
        self.set_font("Calibri", "", 10.5)
        self.set_text_color(0, 0, 0)
        self.set_x(self.l_margin + 2)
        self.cell(4, 5.2, "•")
        self.multi_cell(self.width - 6, 5.2, text, align=Align.L,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def entry(self, item):
        # Role and organisation on the left, dates on the right of the same line.
        self.set_font("Calibri", "B", 11)
        self.set_text_color(0, 0, 0)
        y = self.get_y()
        self.cell(self.width - 40, 5.6, f"{item['role']}, {item['org']}")
        self.set_font("Calibri", "", 10.5)
        self.set_text_color(*GREY)
        self.set_xy(self.w - self.r_margin - 40, y)
        self.cell(40, 5.6, item["dates"], align=Align.R, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if item.get("place"):
            self.text_line(item["place"], size=10, style="I", color=GREY, height=4.8)
        for point in item["bullets"]:
            self.bullet(point)
        self.ln(1.2)


def build(resume):
    pdf = ResumePDF()
    pdf.add_page()
    pdf.text_line(resume["name"], size=22, style="B", color=ACCENT, height=9)
    pdf.text_line(resume["title"], size=12.5, color=GREY, height=6)
    pdf.text_line(resume["contact"], size=10, color=GREY)
    for heading, kind, content in resume["sections"]:
        pdf.heading(heading)
        if kind == "text":
            pdf.text_line(content)
        elif kind == "labels":
            for label, value in content:
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Calibri", "B", 10.5)
                pdf.write(5.2, f"{label}: ")
                pdf.set_font("Calibri", "", 10.5)
                pdf.write(5.2, value)
                pdf.ln(5.2)
        elif kind == "entries":
            for item in content:
                pdf.entry(item)
        elif kind == "bullets":
            for point in content:
                pdf.bullet(point)
    return bytes(pdf.output())


def build_job(text):
    """Lay out a job description: title, details, headings ending in ":" and bullets."""
    pdf = ResumePDF()
    pdf.add_page()
    blocks = text.strip().split("\n\n")
    details = blocks[0].splitlines()
    pdf.text_line(details[0].split(":", 1)[1].strip(), size=20, style="B", color=ACCENT, height=9)
    for line in details[1:]:
        label, value = line.split(":", 1)
        pdf.set_text_color(*GREY)
        pdf.set_font("Calibri", "B", 10.5)
        pdf.write(5.2, f"{label}: ")
        pdf.set_font("Calibri", "", 10.5)
        pdf.write(5.2, value.strip())
        pdf.ln(5.2)
    for block in blocks[1:]:
        heading, *lines = block.splitlines()
        pdf.heading(heading.rstrip(":"))
        bullets = [line[2:] for line in lines if line.startswith("- ")]
        if bullets:
            for point in bullets:
                pdf.bullet(point)
        else:
            # The .txt wraps paragraphs by hand; let the PDF wrap them instead.
            pdf.text_line(" ".join(lines))
    return bytes(pdf.output())


def main():
    OUT.mkdir(exist_ok=True)
    for name, resume in RESUMES.items():
        (OUT / name).write_bytes(build(resume))
        print(f"Wrote realistic_resumes/{name}")
    for job in sorted(JOBS.glob("*.txt")):
        job.with_suffix(".pdf").write_bytes(build_job(job.read_text(encoding="utf-8")))
        print(f"Wrote realistic_jobs/{job.stem}.pdf")


if __name__ == "__main__":
    main()
