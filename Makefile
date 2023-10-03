.PHONY: build

upload:
	sh bin/upload.sh

build:
	sh bin/build.sh

install:
	sh bin/install.sh

docker-build:
	sh bin/docker-build.sh

docker-run:
	docker run --rm -it bq-meta bash

format:
	black .

tag:
	sh bin/tag.sh

tag-dev:
	sh bin/tag-dev.sh