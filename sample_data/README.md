# Sample data

Fictional resumes, job descriptions and broken files for trying the app and for
`tests/test_samples.py`. To recreate the PDFs, run `python sample_data/make_samples.py`.

## Resumes (`resumes/`)

| File | Profile | Best matching job |
|---|---|---|
| `data_analyst_priya.pdf` | Data analyst: Python, SQL, Power BI | `data_analyst.txt` |
| `web_developer_arjun.pdf` | Frontend: React, TypeScript, Node.js | `frontend_developer.txt` |
| `ml_engineer_meera.pdf` | ML engineer: PyTorch, NLP, AWS | `ml_engineer.txt` |
| `java_backend_rahul.pdf` | Java / Spring Boot (2 pages) | `java_backend.txt` |
| `fresher_sneha.pdf` | Fresh graduate: C, C++, Python | none (low scores everywhere) |
| `marketing_karan.pdf` | Non-technical marketing profile | `marketing_executive.txt` |
| `hr_coordinator_neha.pdf` | HR: recruitment, onboarding, payroll | `hr_coordinator.txt` |
| `finance_analyst_vikram.pdf` | Finance: budgeting, financial modeling | `finance_analyst.txt` |
| `ui_ux_designer_ananya.pdf` | Designer: Figma, user research | `ui_ux_designer.txt` |
| `devops_engineer_farhan.pdf` | DevOps: Docker, Kubernetes, AWS | `devops_engineer.txt` |
| `android_developer_diya.pdf` | Android: Kotlin, Java, SQLite | `android_developer.txt` |
| `project_manager_rohan.pdf` | Project manager: Agile, Scrum, Jira | `project_manager.txt` |
| `two_column_tanvi.pdf` | Two columns, stored one column after the other | `data_analyst.txt` |
| `two_column_kabir.pdf` | Two columns, stored row by row (harder to extract) | `frontend_developer.txt` |

## Full-length resumes (`realistic_resumes/`)

One-page resumes laid out like real ones: name and contact line, coloured headings,
skill groups, jobs with dates on the right, bullet points with results, education and
certifications. There is one for each job description, and each scores highest on its
own job. They are made by `python sample_data/make_realistic_resumes.py`, which needs
fpdf2 and the Calibri font that comes with Windows.

| File | Profile | Best matching job |
|---|---|---|
| `ishita_rao_data_analyst.pdf` | Data analyst, 3 years: SQL, Power BI, Tableau | `data_analyst.txt` |
| `rohit_kulkarni_frontend_developer.pdf` | Frontend, 4 years: React, TypeScript, GraphQL | `frontend_developer.txt` |
| `ananya_menon_ml_engineer.pdf` | ML engineer, 4 years: PyTorch, NLP, MLOps | `ml_engineer.txt` |
| `vivek_shetty_java_backend.pdf` | Java backend, 6 years: Spring Boot, Kubernetes | `java_backend.txt` |
| `sanya_kapoor_marketing_executive.pdf` | Marketing, 3 years: social media, launch events | `marketing_executive.txt` |
| `kavya_reddy_hr_coordinator.pdf` | HR, 3 years: recruitment, onboarding, payroll | `hr_coordinator.txt` |
| `arnav_desai_financial_analyst.pdf` | Finance, 4 years: budgeting, financial modeling | `finance_analyst.txt` |
| `meher_joshi_ui_ux_designer.pdf` | Designer, 3 years: Figma, user research | `ui_ux_designer.txt` |
| `farah_khan_devops_engineer.pdf` | DevOps, 5 years: AWS EKS, Terraform, Jenkins | `devops_engineer.txt` |
| `nikhil_bhat_android_developer.pdf` | Android, 3 years: Kotlin, Compose, Room | `android_developer.txt` |
| `pooja_iyer_project_manager.pdf` | Project manager, 7 years: Scrum, PMP | `project_manager.txt` |

## Full-length job descriptions (`realistic_jobs/`)

Job adverts written like real postings, with the company, location, "About us", "About
the role", responsibilities, requirements, nice-to-haves, benefits and how to apply.
Each `.txt` has a formatted PDF copy with the same name. They pair with the resumes in
`realistic_resumes/`, and each resume scores highest on its own job. The PDFs are made
by `python sample_data/make_realistic_resumes.py` from the `.txt` files.

| File | Company (fictional) | Matching resume |
|---|---|---|
| `data_analyst` | Marigold Retail | `ishita_rao_data_analyst.pdf` |
| `frontend_developer` | Basket Lane Technologies | `rohit_kulkarni_frontend_developer.pdf` |
| `ml_engineer` | Saransh AI Labs | `ananya_menon_ml_engineer.pdf` |
| `java_backend` | Ledgerly Payments | `vivek_shetty_java_backend.pdf` |
| `marketing_executive` | Tadka Foods | `sanya_kapoor_marketing_executive.pdf` |
| `hr_coordinator` | Northstar Logistics | `kavya_reddy_hr_coordinator.pdf` |
| `finance_analyst` | Rangoli Home Stores | `arnav_desai_financial_analyst.pdf` |
| `ui_ux_designer` | Yatra Kit | `meher_joshi_ui_ux_designer.pdf` |
| `devops_engineer` | Skyforge Cloud | `farah_khan_devops_engineer.pdf` |
| `android_developer` | Pulse Fit | `nikhil_bhat_android_developer.pdf` |
| `project_manager` | Bluewave Software Services | `pooja_iyer_project_manager.pdf` |

## Job descriptions (`jobs/`)

| File | What it tests |
|---|---|
| `data_analyst.txt`, `frontend_developer.txt`, `ml_engineer.txt`, `java_backend.txt`, `marketing_executive.txt` | Normal analyses (T-04, T-06, T-07) |
| `hr_coordinator.txt` | HR skills (recruitment, payroll, onboarding) |
| `finance_analyst.txt`, `ui_ux_designer.txt`, `devops_engineer.txt`, `android_developer.txt`, `project_manager.txt` | Realistic layout with headings, bullets, years of experience and degree requirements, for the suggestions |
| `delivery_driver.txt` | No known skills, so the app shows a warning |
| `too_short.txt` | Too short, so the app asks for more detail (T-03) |

Every job also has a PDF copy with the same name (for example `ml_engineer.pdf`), for
the app's "Upload PDF" option.

## Invalid files (`invalid/`)

| File | Expected error |
|---|---|
| `scanned_no_text.pdf` | No selectable text (T-05) |
| `corrupt.pdf` | Cannot be read; may be corrupt (T-09) |
| `not_really_a_pdf.pdf` | A text file renamed to `.pdf` (T-09) |
| `password_protected.pdf` | Password-protected (password `secret123`) |

## Scores of each resume against each job

TF-IDF text similarity % / number of matched skills. The highest score for each resume is in bold.

| Resume | android | data | delivery | devops | finance | frontend | hr | java | marketing | ml | project | ui |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| diya | **28.6 / 6** | 4.3 / 2 | 0.0 / 0 | 2.2 / 2 | 2.3 / 0 | 5.6 / 3 | 0.0 / 0 | 7.8 / 4 | 1.9 / 0 | 1.6 / 0 | 2.2 / 1 | 3.0 / 0 |
| priya | 4.8 / 1 | **21.5 / 10** | 0.4 / 0 | 2.6 / 1 | 9.7 / 4 | 3.9 / 2 | 0.5 / 0 | 3.8 / 2 | 3.8 / 2 | 7.3 / 6 | 1.8 / 1 | 3.1 / 2 |
| farhan | 2.5 / 0 | 6.8 / 4 | 0.4 / 0 | **26.6 / 9** | 2.7 / 0 | 3.9 / 2 | 0.0 / 0 | 10.0 / 5 | 1.9 / 0 | 11.2 / 6 | 1.5 / 0 | 2.4 / 1 |
| vikram | 2.0 / 0 | 6.7 / 2 | 0.0 / 0 | 1.4 / 0 | **35.2 / 8** | 2.0 / 1 | 0.0 / 1 | 1.9 / 0 | 2.8 / 2 | 0.8 / 0 | 2.8 / 2 | 1.9 / 1 |
| sneha | 1.9 / 0 | 4.6 / 4 | 0.0 / 0 | 1.9 / 2 | 2.2 / 2 | **7.5 / 4** | 0.0 / 0 | 1.1 / 0 | 1.0 / 1 | 2.7 / 1 | 2.9 / 1 | 5.0 / 4 |
| neha | 2.2 / 0 | 3.1 / 1 | 0.5 / 0 | 1.9 / 0 | 3.5 / 3 | 1.7 / 1 | **18.2 / 5** | 2.2 / 0 | 2.8 / 2 | 0.8 / 0 | 2.7 / 1 | 2.1 / 1 |
| rahul | 8.6 / 4 | 4.0 / 3 | 0.0 / 0 | 9.8 / 7 | 2.4 / 0 | 8.6 / 5 | 0.0 / 0 | **28.7 / 13** | 2.1 / 1 | 7.4 / 4 | 4.1 / 3 | 1.8 / 0 |
| karan | 0.8 / 0 | 2.4 / 1 | 0.0 / 0 | 0.4 / 0 | 1.5 / 1 | 1.4 / 1 | 0.5 / 0 | 1.8 / 1 | **29.9 / 5** | 0.4 / 0 | 1.6 / 2 | 1.9 / 1 |
| meera | 1.1 / 1 | 12.0 / 8 | 0.0 / 0 | 7.4 / 6 | 1.3 / 0 | 2.5 / 2 | 0.5 / 0 | 5.2 / 5 | 1.1 / 0 | **29.8 / 16** | 0.4 / 0 | 0.7 / 0 |
| rohan | 4.0 / 1 | 4.5 / 2 | 0.5 / 0 | 4.2 / 2 | 5.2 / 2 | 3.9 / 3 | 0.0 / 0 | 4.3 / 2 | 3.1 / 2 | 1.2 / 0 | **29.9 / 8** | 2.8 / 1 |
| kabir | 7.2 / 2 | 4.7 / 1 | 0.9 / 0 | 2.0 / 0 | 2.5 / 0 | **14.2 / 7** | 0.0 / 0 | 5.5 / 2 | 2.0 / 0 | 1.7 / 0 | 2.4 / 0 | 4.8 / 2 |
| tanvi | 3.7 / 1 | **21.8 / 11** | 0.0 / 0 | 2.7 / 1 | 10.0 / 4 | 2.6 / 2 | 0.5 / 0 | 2.6 / 1 | 2.7 / 1 | 7.6 / 5 | 2.3 / 1 | 2.5 / 1 |
| ananya | 2.8 / 0 | 3.0 / 1 | 0.0 / 0 | 1.8 / 0 | 2.6 / 1 | 2.9 / 1 | 0.0 / 0 | 4.7 / 0 | 3.0 / 1 | 3.3 / 0 | 2.2 / 1 | **34.9 / 7** |
| arjun | 8.5 / 3 | 2.6 / 2 | 1.4 / 0 | 2.3 / 3 | 1.4 / 0 | **16.3 / 9** | 0.0 / 0 | 6.2 / 3 | 1.1 / 0 | 0.4 / 0 | 2.3 / 3 | 2.1 / 2 |
