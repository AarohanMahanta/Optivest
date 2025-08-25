# 📈 MPT Optimiser  

A full-stack web application that allows users to **add financial assets**, select them, and run **Modern Portfolio Theory (MPT) optimisation** using a Java + Python backend. The optimisation calculates **expected returns, volatility, Sharpe ratio, and portfolio weights**.  

---

## Features

### Backend (Spring Boot + JPA)  
- REST API for managing assets.  
- Stores assets in a relational database(PostgresSQL).  
- Forwards chosen assets to the Python service for optimisation.  

### Optimisation Service (Python + Flask)  
- Receives tickers + time period.  
- Fetches historical price data (via `yfinance`).  
- Runs MPT calculations (mean returns, covariance matrix, optimisation).  
- Returns optimal portfolio allocation back to Spring Boot.

### Frontend (React)  
- Add assets (tickers) via a simple form.  
- Display all assets stored in the database as selectable boxes.  
- Choose a period (1d, 1mo, 1y, 5y, etc.) for optimisation.  
- View optimisation results: expected return, volatility, Sharpe ratio, and optimal weights.  

---
## ⚙️ Setup Instructions  

### 1️⃣ Database (PostgreSQL)  

This project requires **PostgreSQL** running locally.  

#### Install Postgres  

```bash
brew install postgresql  
sudo apt-get install postgresql
```
Start Postgres service
```bash
pg_ctl -D /usr/local/var/postgres start
```
Create database and user
```bash
CREATE DATABASE mptdb;
CREATE USER mptuser WITH ENCRYPTED PASSWORD 'mptpass';
GRANT ALL PRIVILEGES ON DATABASE mptdb TO mptuser;
```
Configure Spring Boot

Update src/main/resources/application.properties:
```bash
spring.datasource.url=jdbc:postgresql://localhost:5432/mptdb
spring.datasource.username=mptuser
spring.datasource.password=mptpass
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect
```
### 2️⃣ Backend (Spring Boot, Java 17)
```bash
cd backend
./mvnw spring-boot:run
```
Runs on: http://localhost:8080

### 3️⃣ Optimisation Engine (Python Flask)
```bash
cd python-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Runs on: http://localhost:5000/optimise

### 4️⃣ Frontend (React)
```bash
cd frontend
npm install
npm start
```
Runs on: http://localhost:3000

