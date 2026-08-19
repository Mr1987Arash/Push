# docs/Run.md
Local run (development)

1) Copy env file
   cp .env.example .env
   # Edit .env if you like (SECRET_KEY etc.)

2) Start using docker-compose
   docker-compose up --build

3) Open UI via nginx on port 8080 (default)
   http://localhost:8080/login.html

Notes:
- For quick internet exposure use ngrok:
   ngrok http 8080
  and open the generated ngrok URL.
- Database and Redis data are persisted in docker volumes.
