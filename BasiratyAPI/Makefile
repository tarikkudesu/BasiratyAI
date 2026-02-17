NETWORKS		=	$$(docker network ls -q --filter "type=custom")
IMAGES			=	$$(docker image ls -aq)
VOLUMES			=	$$(docker volume ls -q)
CONTAINERS		=	$$(docker ps -aq)
COMPOSEFILE		=	docker-compose.yml
GREEN			=	\033[0;32m
RESET			=	\033[0m
cols			=	$$(tput cols)
SE				=	$$(printf "%-$(cols)s" "_" | tr ' ' '_')

all: up

up:
	@echo -n "" >> ./AI/.env
	@docker compose -f $(COMPOSEFILE) $@ --build -d
	@echo "Generating cloudflare link"
	@echo $(SE)
	@sleep 5 && docker logs ai 2>&1 | grep ".trycloudflare.com"
	@echo $(SE)
down:
	@docker compose -f $(COMPOSEFILE) $@
build:
	@docker compose -f $(COMPOSEFILE) $@
ps:
	@docker compose -f $(COMPOSEFILE) $@ --all
top:
	@docker compose -f $(COMPOSEFILE) $@
stop:
	@docker compose -f $(COMPOSEFILE) $@
restart:
	@docker compose -f $(COMPOSEFILE) $@

ls:
	@echo $(SE) && docker images && echo $(SE) && docker ps --all
	@echo $(SE) && docker volume ls && echo $(SE) && docker network ls --filter "type=custom"

cleancontainers:
	@printf " ✔ cleaning containers ..."
	@docker stop $(CONTAINERS) > /dev/null 2>&1 || true
	@docker rm -f $(CONTAINERS) > /dev/null 2>&1 || true
	@echo "$(GREEN)\tDone$(RESET)"
cleanimages:
	@printf " ✔ cleaning images ..."
	@docker image rm -f $(IMAGES) > /dev/null 2>&1 || true
	@echo "$(GREEN)\t\tDone$(RESET)"
cleannetworks:
	@printf " ✔ cleaning networks ..."
	@docker network rm $(NETWORKS) > /dev/null 2>&1 || true
	@echo "$(GREEN)\tDone$(RESET)"
cleanvolumes:
	@printf " ✔ cleaning volumes ..."
	@docker volume rm -f $(VOLUMES) > /dev/null 2>&1 || true
	@echo "$(GREEN)\t\tDone$(RESET)"

clean:
	@docker compose -f $(COMPOSEFILE) down -v
	@docker image prune -f
	@docker container prune -f
	@docker network prune -f
	@docker volume prune -f

fclean: cleancontainers cleannetworks cleanvolumes

prune: cleancontainers cleannetworks cleanvolumes cleanimages
	@printf " ✔ system prune ..."
	@docker system prune --all --force > /dev/null 2>&1 || true
	@echo "$(GREEN)\t\tDone$(RESET)"

re: clean cleancontainers cleannetworks up

.PHONY: up down build ps top stop restart ls cleancontainers cleanimages cleannetworks cleanvolumes clean fclean prune re