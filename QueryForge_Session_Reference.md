# QueryForge Setup & Configuration Reference

> **Session Date**: December 18, 2025  
> **System**: sofubuntu (Ubuntu) with QueryForge development environment

---

## 🏗️ System Architecture

### **Network Topology:**
- **sofubuntu**: `192.168.1.56` - Main development server
- **SOFDEV** (Windows): `192.168.1.55` - SQL Server host
- **sofimac**: `192.168.1.58` - Mac development machine

### **Services Configuration:**

#### **Docker Containers (QueryForge):**
```bash
# Location: /home/gnorm/Documents/Projects/StateofForms/queryForge
docker compose up -d

# Running Services:
- queryforge_frontend   -> 0.0.0.0:8001->8000/tcp (Django)
- queryforge_backend    -> 0.0.0.0:8000->8000/tcp (FastAPI)  
- queryforge_redis      -> 0.0.0.0:6379->6379/tcp
- queryforge_postgres   -> 0.0.0.0:5432->5432/tcp
```

#### **Database Connections:**

##### **PostgreSQL (Local Container):**
```python
host='localhost'
database='queryforge_db'
user='queryforge' 
password='[REDACTED]'
port='5432'
```

##### **SQL Server (Remote Windows):**
```python
server='SOFDEV'
username='sa'
password='[REDACTED]' 
# 17 user databases available for migration
```

---

## 🛠️ Development Environment

### **Python Virtual Environment:**
```bash
# Location: /home/gnorm/Documents/Projects/StateofForms/queryForge/db_migration_env
source db_migration_env/bin/activate

# Installed Packages:
- pyodbc (SQL Server connectivity)
- psycopg2-binary (PostgreSQL connectivity) 
- pandas (data manipulation)
- sqlalchemy (ORM/database abstraction)
```

### **Database Migration Script:**
```bash
# File: database_migration.py
# Features:
- Connects to both SQL Server and PostgreSQL
- Chunked data transfer for large tables
- Comprehensive logging with timestamps
- Error handling and progress tracking
- Flexible filtering by database/table names

# Usage Examples:
python database_migration.py  # Test connections
# Custom migration in Python:
from database_migration import DatabaseMigrator
migrator = DatabaseMigrator()
migrator.run_migration(database_name='YourDatabase')
```

---

## 🔧 Key Commands & Tests

### **Service Status Checks:**
```bash
# Docker containers
docker ps

# Database connections test
source db_migration_env/bin/activate && python database_migration.py

# API endpoints test
curl -s http://localhost:8000/ping-db
curl -s "http://localhost:8000/api/stock/AAPL"
curl -s http://localhost:8000/docs  # API documentation

# Redis test
echo "PING" | nc localhost 6379

# SSH connectivity
ssh 192.168.1.55 "echo 'SSH test successful'"
```

### **API Endpoints Available:**
- `GET /ping-db` - Database health check
- `GET /api/stock/{symbol}` - Stock data retrieval  
- `POST /api/stock/query` - Stock query submission
- `GET /api/crypto/{symbol}` - Crypto data retrieval
- `POST /api/crypto/query` - Crypto query submission  
- `GET /api/queries/` - Query management
- `GET /docs` - FastAPI documentation

---

## 🗄️ SQL Server Database List

**SOFDEV Server** contains 17 user databases:
- 4crASJan2019@Atlanta
- 4crASJul2019@Atlanta  
- 4crHRApr2019@Atlanta
- 4crHRAug2019@Atlanta
- 4crHRFeb2019@Atlanta
- 4crHRJan2019@Atlanta
- 4crHRJul2019@Atlanta
- 4crHRJun2019@Atlanta
- 4crHRMar2019@Atlanta
- 4crHRMay2019@Atlanta
- 4crHRNov2019@Atlanta
- 4crHROct2019@Atlanta
- 4crHRSep2019@Atlanta
- 4crTRDec2019@Atlanta
- 4crTROct2019@Atlanta
- 4crTRSep2019@Atlanta
- 4crXref@Atlanta

---

## 🚀 System Status (Last Verified)

### ✅ **All Systems Operational:**

**🐳 Docker Environment:** All 4 containers running
**🔗 Database Connectivity:** Both PostgreSQL and SQL Server accessible  
**🌐 API Services:** All 6 endpoints functional
**⚙️ Migration Tools:** Environment configured and tested
**🔒 Network:** SSH, Redis, all services networked properly

### **🎯 Ready For:**
- Data cleaning script development
- Database migration execution  
- API development and testing
- Full-stack application development

---

## 📝 Important File Locations

- **Project Root:** `/home/gnorm/Documents/Projects/StateofForms/`
- **QueryForge:** `/home/gnorm/Documents/Projects/StateofForms/queryForge/`
- **Migration Script:** `database_migration.py`
- **Docker Config:** `docker-compose.yml`
- **Documentation:** `README.md` (formatted with status tables)
- **Virtual Env:** `db_migration_env/`

---

## 🔄 Quick Start Commands

```bash
# Navigate to project
cd /home/gnorm/Documents/Projects/StateofForms/queryForge

# Start all services  
docker compose up -d

# Activate Python environment
source db_migration_env/bin/activate

# Test everything
python database_migration.py

# View API docs
curl -s http://localhost:8000/docs
```

---

## 🎓 Key Learnings From Session

1. **Docker Compose:** Modern `docker compose` vs older `docker-compose`
2. **SQL Server Connectivity:** ODBC driver configuration and password handling
3. **Database Migration:** Chunked transfer strategies for large datasets
4. **API Testing:** Systematic endpoint verification methods
5. **Markdown Formatting:** HTML limitations and emoji-based alternatives
6. **Network Diagnostics:** Comprehensive service health checking
7. **Virtual Environments:** Isolated Python package management
8. **Cross-Platform Setup:** Windows SQL Server + Linux development environment

---

**💡 This reference contains everything needed to recreate and continue the QueryForge development environment!**