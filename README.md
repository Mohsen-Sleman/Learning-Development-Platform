## 📖 Table of Contents
1. [About The Project](#-about-the-project)
2. [Key Features](#-key-features)
3. [Tech Stack](#-tech-stack)
4. [Project Structure](#-project-structure)
5. [Getting Started & Installation](#-getting-started--installation)
6. [Running with Docker](#-running-with-docker)
7. [Contributing](#-contributing)
8. [Contact](#-contact)

---

## 🧐 About The Project

This repository contains a robust and scalable Backend API developed for a Learning Development Platform. Built using Python, Django, and Django REST Framework (DRF), the platform provides secure endpoints to manage educational resources, student tracks, and complex backend workflows efficiently.

---

## ✨ Key Features

* **Secure Authentication:** Integrated JSON Web Token (JWT) authentication for secure user sessions.
* **Course & Track Management:** Full system to organize, structure, and track courses and learning pathways.
* **Role-Based Permissions:** Granular access control allowing specific permissions for admins, instructors, and students.
* **Production Ready Database:** Seamless integration with PostgreSQL for reliable and high-performance data storage.
* **Containerized Environment:** Fully dockerized configuration to maintain consistent environments across development and production.

---

## 🛠️ Tech Stack

* **Backend Framework:** [Django](https://djangoproject.com) & [Django REST Framework (DRF)](https://django-rest-framework.org)
* **Database:** [PostgreSQL](https://postgresql.org)
* **Containerization:** [Docker](https://docker.com) & Docker Compose

---

## 📂 Project Structure

The project is structured efficiently to maintain scalability and separate configuration from business logic:
* `backend/` - Contains the core Django settings, API apps, models, serializers, and views.
* `docs/` - Holds documentation files related to the API design and development workflow.
* `docker-compose.yaml` - Orchestration file to define and manage multiple docker containers.

---

## 🚀 Getting Started & Installation

To set up a local copy for development and testing without Docker, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/Mohsen-Sleman/Learning-Development-Platform
cd Learning-Development-Platform
```

### 2. Set Up a Virtual Environment
* **On Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **On macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Database Migrations & Running Local Server
```bash
python backend/manage.py makemigrations
python backend/manage.py migrate
python backend/manage.py runserver
```

---

## 🐳 Running with Docker

The absolute easiest way to get this project up and running with all its services (including PostgreSQL) is using Docker:

1. Make sure you have **Docker** and **Docker Compose** installed on your system.
2. Build and run the containers using a single command:
   ```bash
   docker-compose up --build
   ```
3. The API server will boot up automatically and become accessible locally.

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📬 Contact

* **GitHub Profile:** [@Mohsen-Sleman](https://github.com)
* **Project Link:** [https://github.com/Learning-Development-Platform](https://github.com/Learning-Development-Platform)
