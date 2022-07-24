upload:
	sh bin/upload.sh

build:
	sh bin/build.sh

docker-build:
	sh bin/docker-build.sh

docker-run:
	docker run --rm -it bq-meta bash

format:
	black .