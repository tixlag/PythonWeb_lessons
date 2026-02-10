# Lesson 6 - Docker Infrastructure

This project demonstrates a Docker-based infrastructure with a Flask backend and vanilla JavaScript frontend.

## Architecture

- **Frontend**: Available at `http://localhost:5000`
- **Backend API**: Available at `http://api.localhost:5000`

## Project Structure

```
lesson_6/
├── backend/
│   ├── Dockerfile          # Backend container configuration
│   ├── server.py           # Flask application
│   ├── utils.py            # Utility functions
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── Dockerfile          # Frontend container configuration
│   └── index.html          # Frontend application with vanilla JS
├── nginx/
│   ├── Dockerfile          # Nginx gateway configuration
│   └── nginx.conf          # Routing configuration
└── docker-compose.yml      # Orchestration file
```

## Prerequisites

- Docker
- Docker Compose

## Setup

### 1. Add api.localhost to your hosts file

For the routing to work properly, you need to add `api.localhost` to your system's hosts file:

**Linux/macOS:**
```bash
sudo echo "127.0.0.1 api.localhost" >> /etc/hosts
```

**Windows:**
1. Open Notepad as Administrator
2. Open `C:\Windows\System32\drivers\etc\hosts`
3. Add the line: `127.0.0.1 api.localhost`
4. Save the file

### 2. Build and run the containers

```bash
cd lesson_6
docker-compose up --build
```

### 3. Access the applications

- **Frontend**: Open http://localhost:5000 in your browser
- **Backend API**: Access via http://api.localhost:5000

## API Endpoints

- `GET /users` - Get all users
- `GET /users/<id>` - Get user by ID
- `POST /users` - Create a new user
- `PUT /users/<id>` - Update a user
- `DELETE /users/<id>` - Delete a user
- `GET /health` - Health check

## Stopping the containers

```bash
docker-compose down
```

## Development

The backend has hot-reload enabled via volume mounting. Changes to Python files in the `backend/` directory will be reflected immediately.

## Troubleshooting

### Port 5000 already in use

If port 5000 is already in use, you can change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "5001:5000"  # Change to use port 5001 instead
```

### api.localhost not resolving

Make sure you've added `127.0.0.1 api.localhost` to your hosts file as described in the setup section.

### Containers not starting

Check the logs:
```bash
docker-compose logs
```

For specific service logs:
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx-gateway
```
