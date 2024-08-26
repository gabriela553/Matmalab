.PHONY: build test

build:
	docker-compose up -d --build
test:
	@echo "Running tests..."
	docker compose -f docker-compose.yml run app pytest -s -vv 

