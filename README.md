# Optivest (MPT Optimiser)

## Live Demo
Check out the live version here:  
[Optivest](https://optivest-static.onrender.com/)

---

## Overview
Optivest is a **full-stack web application** that allows users to add financial assets, select them, and run **Modern Portfolio Theory (MPT) optimisation**. The optimisation calculates **expected returns, volatility, Sharpe ratio, and portfolio weights**.

The backend is powered by **Java + Spring Boot**, while the optimisation engine runs in **Python + Flask**. The frontend is a lightweight HTML/CSS/JS interface.

> **Note [13.11.2025]:** Due to stricter rate limits by Yahoo Finance, the Python service now fetches historical data via **Stooq CSV downloads** instead of `yfinance`.

---

## Features

### Backend (Spring Boot + JPA)
- REST API for managing assets.
- Stores assets in a relational database (**PostgreSQL**).
- Forwards chosen assets to the Python service for optimisation.

### Optimisation Service (Python + Flask)
- Receives tickers and time period from frontend/backend.
- Fetches historical price data via **Stooq CSV downloads**.
- Runs MPT calculations:
  - Daily returns
  - Mean returns
  - Covariance matrix
  - Portfolio optimisation (Sharpe ratio maximisation)
- Returns optimal portfolio allocation back to Spring Boot.
- JSON response includes:
  - `weights` (asset allocation in %)
  - `expectedReturn`
  - `volatility`
  - `sharpeRatio`
  - `period`
  - `requestedTickers` and `validTickers`

### Frontend (HTML + CSS + JavaScript)
- Responsive UI using **Bootstrap** and custom styles.
- Add assets (tickers) via a form.
- Display selected assets in a list.
- Choose a historical period (1d, 1mo, 1y, 5y, etc.) for optimisation.
- View optimisation results:
  - Expected return
  - Volatility
  - Sharpe ratio
  - Asset weights

---


## Installation

### Backend
1. Ensure **Java 17+** and **Maven** are installed.
2. Configure PostgreSQL database.
3. Set environment variables for DB connection:
   ```bash
   export SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/optivest
   export SPRING_DATASOURCE_USERNAME=your_username
   export SPRING_DATASOURCE_PASSWORD=your_password
   
#### Build and run:
```bash
mvn clean install
mvn spring-boot:run
```
### Optimisation Service
1. Ensure Python 3.11+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run service:
   ```bash
   python app.py
   ```
4. The service will run on http://localhost:5000.
Docker: The Python service can also be containerized using the provided Dockerfile.

### Frontend
1. Open frontend/index.html in a browser.
2. Ensure backend and optimisation service URLs are correctly configured in main.js.

## API Endpoints
### Health Check
```bash
  GET /health
  Response: 200 OK
```

## Dependencies
### Backend:
  - Spring Boot
  - JPA / Hibernate
  - PostgreSQL
### Optimisation Service:
  - Flask
  - NumPy
  - Pandas
  - SciPy
  - Requests
### Frontend
  - HTML / CSS / JS
  - Bootstrap 5

## Notes
The optimiser uses Stooq for fetching historical stock data (free and reliable, no API key required).
Data is limited to ~252 trading days for a "1y" period.
All calculations follow standard Modern Portfolio Theory methods.

## License
MIT License
