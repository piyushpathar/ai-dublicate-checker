IMAGE=gujarati-ai-app
PORT=3000

build:
	docker build -t $(IMAGE) .

run:
	docker run -p $(PORT):3000 $(IMAGE)

clean:
	docker rm -f $$(docker ps -aq --filter "ancestor=$(IMAGE)")

rebuild: clean build run
