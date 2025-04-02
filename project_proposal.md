# 📌 Project Proposal: Job Application Tracker

## 📝 Description
The **Job Application Tracker** is a full-stack web application designed to help job seekers efficiently manage and organize their job search process. The application provides a centralized dashboard where users can track applications, schedule interviews, set reminders, and (in future versions) analyze job search trends.

Deployed App: [https://job-tracker-frontend-0fs5.onrender.com](https://job-tracker-frontend-0fs5.onrender.com)

---

## 🧰 Tech Stack

### 🖥 Front-end
- React (via Create React App)
- Bootstrap
- React Router DOM

### ⚙️ Back-end
- Node.js with Express
- PostgreSQL (`pg` module)
- JWT for authentication
- bcrypt for password hashing

### 🗄 Database
- PostgreSQL
- SQL migrations

### 🚀 Deployment
- Hosted on Render (frontend and backend)

### 🧪 Testing (Back-end)
- Jest + Supertest
- Front-end tests planned (React Testing Library)

---

## ✅ Currently Implemented

- User registration & login (JWT-based)
- Secure password hashing
- Job application CRUD (Create, Read, Update, Delete)
- Interview scheduling and notes
- Authentication middleware
- Responsive mobile/desktop design
- PostgreSQL schema migrations
- RESTful API
- Fully deployed frontend + backend

---

## 🔜 Future Enhancements

- 📊 Analytics dashboard for job search insights
- 🗓 Google Calendar API integration
- 📝 Resume matching via NLP
- 🔎 Job scraping from public APIs (if feasible)
- 🧪 Front-end testing with React Testing Library

---

## 🧠 Goal
The primary goal is to eliminate the chaos of spreadsheets and scattered notes. This project helps job seekers track every stage of their job hunt, from applying to landing interviews, all in one place.

---

## 👥 Users

- Recent graduates
- Career switchers
- Active job seekers applying to multiple roles

---

## 🗃️ Data

- User-generated job and interview records
- Manually entered job details
- Optional future: calendar data (via Google API), NLP resume insights

---

## 🧱 Database Schema

### Users Table
| Field       | Type         | Description              |
|-------------|--------------|--------------------------|
| id          | SERIAL       | Primary key              |
| name        | VARCHAR(100) | User's name              |
| email       | VARCHAR(255) | Unique user email        |
| password    | TEXT         | Hashed password          |
| created_at  | TIMESTAMP    | Account creation date    |

### Jobs Table
| Field            | Type         | Description                                 |
|------------------|--------------|---------------------------------------------|
| id               | SERIAL       | Primary key                                 |
| user_id          | INTEGER      | References users(id)                        |
| company          | VARCHAR(255) | Company name                                |
| position         | VARCHAR(255) | Job title                                   |
| status           | VARCHAR(50)  | 'applied', 'interviewing', 'offer', etc.    |
| application_date | DATE         | When the job was applied to                 |
| notes            | TEXT         | Optional notes                              |

### Interviews Table
| Field        | Type     | Description                                |
|--------------|----------|--------------------------------------------|
| id           | SERIAL   | Primary key                                |
| job_id       | INTEGER  | References jobs(id)                        |
| user_id      | INTEGER  | References users(id)                       |
| date         | DATE     | Date of interview                          |
| time         | TIME     | Time of interview                          |
| duration     | INTEGER  | Duration in minutes                        |
| location     | TEXT     | Location or link                          |
| userEmail    | TEXT     | Email used for the event (Google or manual)|
| description  | TEXT     | Description or notes                       |
| created_at   | TIMESTAMP| When the interview was scheduled           |

### Reminders Table (Stretch Feature)
| Field         | Type      | Description                        |
|---------------|-----------|------------------------------------|
| id            | SERIAL    | Primary key                        |
| user_id       | INTEGER   | References users(id)               |
| interview_id  | INTEGER   | References interviews(id)          |
| reminder_date | TIMESTAMP | When to remind user                |
| status        | BOOLEAN   | Sent or pending                    |

---

## 🧩 Potential Issues & Solutions

### 🔒 User Data Security
Handled with strong JWT-based auth and bcrypt password hashing.

### ⚠️ Google API Limitations
Integration is a stretch goal — fallback options (like email reminders) may be used.

### 📝 Manual Data Entry
To simplify MVP delivery, users enter job details manually. Future updates may support scraping job boards via open APIs.

---

## 🧭 User Flow

1. User registers or logs in.
2. Adds job applications with relevant details.
3. Updates status throughout the hiring process.
4. Schedules interviews manually with title, date/time, notes.
5. Views all interviews on the "View Scheduled Interviews" screen.
6. (Optional) Tracks notes per job or interview.

---

## 🧪 Stretch Goals

- 🧠 Resume-to-job matching via OpenAI or open-source NLP
- 📈 Analytics dashboard for job activity tracking
- 📥 Job board integration (via public APIs)

---

## 💼 Summary

This project is a strong demonstration of:
- Full-stack app development
- JWT authentication and middleware
- RESTful API with real database integration
- Real-world features like interview scheduling

It’s live, polished, and ready for real-world job search use.

---

## ✍️ Author

**Johnny [JohnnyQN]**  
📧 Email: johnny.q.ngo@gmail.com  
🔗 GitHub: [github.com/JohnnyQN](https://github.com/JohnnyQN)
