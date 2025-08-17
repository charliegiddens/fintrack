# Tech Stack
**Frontend:** React

**Backend:** Python (Flask) + Auth0

**Cache:** Redis

**Database:** Postgres

# How to Run Locally
1. Clone the repository
   `git clone https://github.com/heychoogle/fintrack.git`
2. Move to the project dir
   `cd fintrack`
3. Spin up the containers for the frontend, backend, database, and cache
   `docker-compose up --build`
4. Access the frontend at http://localhost:3000

# Notes
- The persistent Postgres data store is found in folder `postgres-data`, created in the project root