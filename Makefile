.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser collectstatic test clean

help:
	@echo "Comandos disponibles:"
	@echo "  make build          - Construir las imágenes Docker"
	@echo "  make up             - Levantar los servicios"
	@echo "  make down           - Detener los servicios"
	@echo "  make restart        - Reiniciar los servicios"
	@echo "  make logs           - Ver logs en tiempo real"
	@echo "  make shell          - Acceder al shell de Django"
	@echo "  make migrate        - Aplicar migraciones"
	@echo "  make makemigrations - Crear migraciones"
	@echo "  make createsuperuser- Crear superusuario"
	@echo "  make collectstatic  - Recolectar archivos estáticos"
	@echo "  make test           - Ejecutar tests"
	@echo "  make clean          - Limpiar contenedores y volúmenes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Servicios iniciados en:"
	@echo "  - Frontend: http://localhost"
	@echo "  - Admin: http://localhost/admin"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

test:
	docker-compose exec web python manage.py test

clean:
	docker-compose down -v
	docker system prune -f
