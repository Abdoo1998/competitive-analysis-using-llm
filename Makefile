.PHONY: build run stop clean nohup-run nohup-stop

build:
	docker-compose build

run:
	docker-compose up

stop:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f

nohup-run:
	nohup docker-compose up > docker.log 2>&1 &
	@echo "Services started in background. Check docker.log for output."

nohup-stop:
	docker-compose down
	@echo "Stopping background services..."
	@pkill -f "docker-compose up"
	@echo "Background services stopped."