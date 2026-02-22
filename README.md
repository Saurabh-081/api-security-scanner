# API Security Scanner

A comprehensive web application for automated API security testing and vulnerability scanning. This tool helps identify common security vulnerabilities in REST APIs including SQL injection, authentication flaws, IDOR (Insecure Direct Object References), and rate limiting issues.

## 🚀 Features

- **Multiple Vulnerability Scanners**
  - SQL Injection (SQLi) Detection
  - Authentication & Authorization Testing
  - IDOR (Insecure Direct Object Reference) Testing
  - Rate Limit Testing
  
- **User Management**
  - Secure user registration and authentication
  - JWT-based authorization
  - Password hashing with bcrypt

- **Scan Management**
  - Create and configure security scans
  - View detailed scan results
  - Historical scan tracking
  - Vulnerability severity ratings

- **Modern Tech Stack**
  - FastAPI backend with Python
  - React + TypeScript frontend
  - PostgreSQL database
  - Docker containerization

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Just command runner (optional, but recommended)

## 🛠️ Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/api-security-scanner.git
cd api-security-scanner
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Start the application:
```bash
# Development mode
docker-compose -f compose.yml -f dev.compose.yml up

# Or using just
just dev-up
```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup

```bash
cd backend
pip install -r pyproject.toml
uvicorn backend.main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
api-security-scanner/
├── backend/              # FastAPI backend
│   ├── core/            # Core functionality (database, security)
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # API endpoints
│   ├── scanners/        # Vulnerability scanners
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── store/       # State management
├── conf/                # Configuration files
│   ├── docker/         # Dockerfiles
│   └── nginx/          # Nginx configuration
├── learn/              # Documentation
├── mock_target/        # Mock vulnerable API for testing
└── compose.yml         # Docker compose configuration
```

## 🔍 Usage

1. **Register/Login**: Create an account or log in to the application
2. **Create a Scan**: Enter the target API URL and select scan types
3. **Run Scan**: Execute the security scan
4. **View Results**: Review detailed vulnerability reports with severity ratings

## 🧪 Scanners

### SQL Injection Scanner
Tests for SQL injection vulnerabilities using various payloads and injection techniques.

### Authentication Scanner
Validates authentication mechanisms and tests for common authentication flaws.

### IDOR Scanner
Tests for insecure direct object references by attempting to access unauthorized resources.

### Rate Limit Scanner
Tests API rate limiting implementation and identifies potential DoS vulnerabilities.

## 🔒 Security Notes

⚠️ **Important**: This tool is for educational and authorized security testing purposes only. Always obtain proper authorization before scanning any API or system you do not own.

- Only scan APIs you have permission to test
- Be aware of rate limits and avoid overwhelming target systems
- Use responsibly and ethically

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is provided for educational and authorized security testing purposes only. The developers assume no liability for misuse or damage caused by this tool. Users are responsible for compliance with all applicable laws and regulations.

## 📧 Contact

For questions or support, please open an issue on GitHub.
