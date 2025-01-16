.PHONY: install backend frontend all stop  

install:
	@echo "Installing dependencies for all services"
	pip install poetry 
	cd backend && poetry install 
	cd frontend && npm install 

backend:
	@echo "Starting backend"
	cd backend && poetry run uvicorn src.main:app --reload --port 8000 &

frontend:
	@echo "Starting frontend"
	cd frontend && npm run dev &

stop:
	@echo "Stopping all services"
	@echo "Stopping backend"
	-pkill -f 'uvicorn.*8000'

	@echo "Stopping platform"
	-pkill -f 'node.*frontend'

	@echo "\033[1;32m🛑🛑🛑 Everything stopped\033[0m"
