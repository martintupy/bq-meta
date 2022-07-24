upload:
	sh bin/upload.sh

build:
	sh bin/build.sh

docker-build:
	sh bin/docker-build.sh

docker-run:
	docker run --rm -it bq-meta bash

format:
	autoflake --in-place --remove-all-unused-imports bq_meta/**/*.py
	black .