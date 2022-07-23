build:
	sh bin/build.sh

container:
	docker run --rm -it bq-meta bash

format:
	autoflake --in-place --remove-all-unused-imports bq_meta/**/*.py
	black .