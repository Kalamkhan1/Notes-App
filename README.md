# 🗒️ Notes App

A full-stack notes management application built using **FastAPI** for the backend, **MongoDB** as the database, and a **vanilla JavaScript frontend**. The app allows users to register, log in, and manage their personal notes easily through a lightweight and responsive interface.

---

## 🚀 Features

* User authentication (register, login, logout)
* Create, edit, and delete notes
* Persistent storage using MongoDB
* RESTful backend built with FastAPI
* Simple, responsive frontend using vanilla JS, HTML, and CSS

---

## 🧰 Tech Stack

**Frontend:**

* HTML, CSS, JavaScript (Vanilla JS)

**Backend:**

* FastAPI (Python)
* Uvicorn ASGI server

**Database:**

* MongoDB (local or cloud instance, e.g., MongoDB Atlas)

---

## ⚙️ Local Deployment (Without Docker or Kubernetes)

### **1. Clone the Repository**

```bash
git clone https://github.com/<your-username>/notes-app.git
cd notes-app
```

---

### **2. Setup the Backend**

#### a. Navigate to the backend directory

```bash
cd backend
```

#### b. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

#### c. Install dependencies

```bash
pip install -r requirements.txt
```

#### d. Set up environment variables

Create a `.env` file in the `backend/` directory:

```
MONGO_URI=mongodb://localhost:27017
SECRET_KEY=your_secret_key
```

#### e. Run the FastAPI backend

```bash
uvicorn main:app --reload --port 8000
```

Backend will run at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### **3. Setup the Frontend**

#### a. Navigate to the frontend directory

```bash
cd ../frontend
```

#### b. Open `index.html` directly in your browser

(You can also serve it with a simple HTTP server:)

```bash
python -m http.server 3000
```

Frontend will be available at:
👉 **[http://127.0.0.1:3000](http://127.0.0.1:3000)**

Make sure your frontend’s API calls point to `http://127.0.0.1:8000`.

---

### **4. Run MongoDB**

If you have MongoDB installed locally, start it with:

```bash
mongod
```

---

### **5. Test the App**

* Register a new user via the frontend
* Login to start managing notes
* Notes should be persisted in your MongoDB instance

---

## 🧩 Folder Structure

```
notes-app/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── database.py
│   ├── models.py
│   ├── tests/
│   └── routes/ (routers)
│
├── frontend/
│   ├── index.html
│   ├── scripts/
│   └── styles/
│
└── README.md
```

---

## 💡 Future Enhancements

* Add dark mode UI
* Add search & filter functionality
* Docker/Kubernetes deployment (already supported via YAML manifests)

---

## 🧑‍💻 Author

**Mohammed Abdul Kalam Khan**
📫 [GitHub](https://github.com/kalamkhan1)
