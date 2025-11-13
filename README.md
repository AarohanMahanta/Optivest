# Optivest (MPT Optimiser)  

A full-stack web application that allows users to **add financial assets**, select them, and run **Modern Portfolio Theory (MPT) optimisation** using a **Java + Python backend** with a **lightweight HTML/CSS/JS frontend**. The optimisation calculates **expected returns, volatility, Sharpe ratio, and portfolio weights**.  

## Live Demo
Check out the live version here:  
[Optivest](https://optivest-static.onrender.com/)

---

## Features  

### Backend (Spring Boot + JPA)  
- REST API for managing assets.  
- Stores assets in a relational database (**PostgreSQL**).  
- Forwards chosen assets to the Python service for optimisation.  

### Optimisation Service (Python + Flask)  
- Receives tickers + time period.  
- Fetches historical price data (via `yfinance`).  
- Runs MPT calculations (mean returns, covariance matrix, optimisation).  
- Returns optimal portfolio allocation back to Spring Boot.  

### Frontend (HTML + CSS + JavaScript)  
- Simple, responsive UI (Bootstrap + custom styles).  
- Add assets (tickers) via a form.  
- Display selected assets in a list.  
- Choose a historical period (1d, 1mo, 1y, 5y, etc.) for optimisation.  
- View optimisation results: expected return, volatility, Sharpe ratio, and asset weights.
