# 📌 Job Application Tracker

🔗 **Live Demo**: [https://job-tracker-frontend-0fs5.onrender.com](https://job-tracker-frontend-0fs5.onrender.com)

---

## 📊 Database Schema


Below is the visual representation of the database schema used in this app:

![Job Tracker Schema](./job-tracker-schema.png)

---

A full-stack job application tracker to help users organize job applications, schedule interviews, and take notes — all in one place. Built with **Node.js**, **Express**, **PostgreSQL**, and **React**.

---

## 🚀 Features

- ✅ User Authentication (JWT-based)
- ✅ Create, Read, Update, Delete job applications
- ✅ Interview Scheduling with notes and time
- ✅ Token-based Auth Middleware
- ✅ PostgreSQL Integration
- ✅ Tested API Endpoints with Supertest & Jest

---

## 🔜 Planned Enhancements

- 📊 Analytics Dashboard (application status trends)
- 🗓️ Google Calendar API Integration
- 📝 Resume Matching via OpenAI API
- 🔗 Job Board Integrations
- 🗂️ Role-Based User Permissions

---

## 🧰 Tech Stack

### Backend
- Node.js + Express.js
- PostgreSQL (pg)
- JWT + bcryptjs
- Sequelize ORM *(planned)*

### Frontend
- React (via Create React App)
- React Router DOM
- Material UI *(planned)*
- Redux *(planned)*

---

## 🗂️ Project Structure

job-tracker/
├── job-tracker-client/     # React frontend
│   └── src/
├── server/                 # Express backend
│   ├── routes/
│   ├── middleware/
│   └── ...
├── migrations/             # SQL schema
├── tests/                  # Jest + Supertest
├── db.js                   # PG connection
├── server.js               # App entry point
├── README.md               # ← You are here
└── .env                    # Environment variables

---

## 📦 Installation

```bash
git clone https://github.com/JohnnyQN/job-tracker.git
cd job-tracker
npm install

⚙️ Environment Setup

Create a .env file at the root with:

PORT=5000
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost/job_tracker
JWT_SECRET=your_jwt_secret_key

▶️ Running the App

🔧 Backend

node server.js
# OR for auto-reloading:
npm install -g nodemon
nodemon server.js

💻 Frontend

cd job-tracker-client
npm install
npm start

Open http://localhost:3000

🧪 Testing

npm test

Tests cover:

    ✅ User registration and login

    ✅ Job CRUD operations

    ✅ Interview scheduling

📡 API Endpoints

🔐 Authentication

Method	    Endpoint	        Description
POST	    /api/auth/register	Register a new user
POST	    /api/auth/login	    Login user & get token


📂 Jobs

Method	    Endpoint	        Description
POST	    /api/jobs	        Add new job
GET	        /api/jobs	        Get user jobs
GET	        /api/jobs/:id	    Get job by ID
PUT	        /api/jobs/:id	    Update job
DELETE	    /api/jobs/:id	    Delete job


🗓️ Interviews

Method	Endpoint	            Description
POST	/api/calendar/schedule	Schedule an interview


📌 Future Enhancements

🔍 Resume Matching via NLP

📅 Timeline view of all job stages

📥 Bulk import of applications

📈 Weekly success rate breakdowns

👨‍💼 Author

Johnny [JohnnyQN]
📧 Email: johnny.q.ngo@gmail.com🔗 GitHub: github.com/JohnnyQN

📜 License
MIT License – feel free to fork or contribute!

🚀 Ready to track your job applications like a pro? Let’s go!
