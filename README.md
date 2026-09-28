# 3R Analyzer Intelligence Platform

AI-powered incident intelligence platform for **3R classification (Runner, Repeater, Rare)**, semantic clustering, recurrence analysis, ticket intelligence, advanced filtering, job operations, analytics, and reporting.

---

## Project Structure

```text
3R Analyzer Intelligence/
│
├── backend/                 # FastAPI backend
│
├── frontend/                # React + Vite frontend
│
├── docs/                    # Master Documentation (Start Here!)
│
├── .gitignore
└── README.md
```

> **IMPORTANT**: For all product, architecture, configuration, and setup information, please see the [Master Documentation Index](docs/DOCUMENTATION_INDEX.md).

---

# 1. Backend Setup

Navigate to the backend folder:

```powershell
cd backend
```

## Create virtual environment

```powershell
python -m venv venv
```

## Activate virtual environment

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## Install dependencies

```powershell
pip install -r requirements.txt
```

---

# 2. Configure Environment Variables

Create a `.env` file inside the `backend` folder.

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=3r_analyzer
DB_USER=
DB_PASSWORD=
```

Update the values according to your local PostgreSQL configuration:

```text
DB_HOST       PostgreSQL host
DB_PORT       PostgreSQL port
DB_NAME       PostgreSQL database name
DB_USER       PostgreSQL username
DB_PASSWORD   PostgreSQL password
```

For a typical local PostgreSQL installation:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=3r_analyzer
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

> **Important:** Do not commit the `.env` file to GitHub. It may contain database credentials and other environment-specific configuration.

# 3. Create PostgreSQL Database

Make sure PostgreSQL is running.

Using **pgAdmin** or **psql**, create the database:

```sql
CREATE DATABASE 3r_analyzer;
```

---

# 4. Run Database Migrations

From the `backend` directory:

```powershell
alembic upgrade head
```

This creates/updates the required database schema.

---

# 5. Start the Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 6. Frontend Setup

Open a **new terminal**.

Navigate to the frontend:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 7. Run the Complete Application

Two terminals are required during local development.

### Terminal 1 — Backend

```powershell
cd backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

Then open:

```text
http://localhost:5173
```

---

# 8. Main Platform Features

## Dashboard

* 3R Intelligence Summary
* Pattern Insights
* Trend and Distribution analytics
* Highest Impact Pattern
* Most Active Pattern
* Top Affected CI
* Top Assignment Group
* Executive-level insights

## Clusters

* Semantic incident clustering
* Cluster intelligence
* Cluster naming
* Recurrence analysis
* Problem candidate identification
* Cluster-level exports

## CI Analysis

Configuration-item level incident intelligence and analysis.

## Assigned Groups

Assignment-group level incident intelligence and analysis.

## Tickets

* Ticket-level 3R intelligence
* ServiceNow-style advanced filtering
* Nested AND / OR conditions
* Type-aware operators
* Multi-column sorting
* Server-side pagination
* Ticket intelligence drawer
* Cluster intelligence navigation

## Job History

* Dataset processing history
* Job status
* Processing progress
* Execution duration
* Ticket counts
* Cluster counts
* 3R classification metrics
* Job detail drawer
* Processing invariant validation

## Export & Reporting

* Ticket CSV export
* Cluster CSV export
* 3R summary CSV export
* Executive PDF report
* Filter-aware reporting

---

# 9. 3R Classification

The platform classifies incidents into three categories:

```text
RUNNER
REPEATER
RARE
```

The core data integrity invariant is:

```text
RUNNER + REPEATER + RARE = TOTAL INCIDENTS
```

This invariant must remain valid after every completed processing job.

---

# 10. AI / ML Processing Pipeline

The current processing pipeline consists of:

```text
Loading Data
      ↓
Applying Scope
      ↓
Data Preprocessing
      ↓
Generating Embeddings
      ↓
Storing Embeddings
      ↓
Semantic Clustering
      ↓
Cluster Analysis
      ↓
Naming Clusters
      ↓
Recurrence Analysis
      ↓
3R Classification
      ↓
Saving Results
```

The pipeline includes performance instrumentation for measuring individual stage execution time.

---

# 11. Local AI Processing

The current embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model runs locally after it has been downloaded and cached.

Incident data is processed by the local application pipeline. Using the Hugging Face-hosted model does **not** mean that incident data is automatically sent to Hugging Face for inference.

---

# 12. Running Tests

From the `backend` directory:

```powershell
pytest tests/ -v
```

To run a specific test:

```powershell
pytest tests/test_jobs_operations.py -v
```

---

# 13. Build Frontend for Production

From the `frontend` directory:

```powershell
npm run build
```

The production build is generated in:

```text
frontend/dist/
```

---

# 14. Security Notes

The following files/directories should never be committed:

```text
.env
venv/
.venv/
__pycache__/
*.pyc
node_modules/
uploads/
```

Never commit:

* Database passwords
* API keys
* Access tokens
* Enterprise LLM credentials
* ServiceNow credentials
* Production secrets

Use environment variables or a secure secrets-management solution for sensitive configuration.

---

# 15. Typical Development Workflow

```text
Start PostgreSQL
      ↓
Start FastAPI Backend
      ↓
Start React Frontend
      ↓
Upload / Load Incident Dataset
      ↓
Run 3R Analysis
      ↓
Monitor Job History
      ↓
Explore Dashboard
      ↓
Explore Clusters / CI / Assignment Groups
      ↓
Investigate Individual Tickets
      ↓
Apply Advanced Filters
      ↓
Export Reports / Analytics
```

---

# 16. Application URLs

| Component   | URL                          |
| ----------- | ---------------------------- |
| Frontend    | `http://localhost:5173`      |
| Backend     | `http://127.0.0.1:8000`      |
| Swagger API | `http://127.0.0.1:8000/docs` |

---

# 17. Development Roadmap

The platform has been developed incrementally:

```text
Phase 1
Core 3R Analyzer
        ↓
Phase 2
Ticket Intelligence & Analytics
        ↓
Phase 2.5
Job Operations
        ↓
Phase 2.6
Pipeline Performance Optimization
        ↓
Phase 3
Production Hardening
```

### Phase 3 — Production Hardening

The next phase focuses on:

* Security
* Authentication and authorization
* API protection
* Secrets management
* Observability
* Reliability
* Error handling
* Concurrency
* Scalability
* Background job execution
* Production database configuration
* Deployment architecture
* Performance under concurrent workloads

---

## License

Internal / private project. Add the appropriate license before public distribution.
