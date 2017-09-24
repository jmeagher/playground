TAG_BASE=jpmeagher/playground:docker-elasticsearch-kubernetes
TAG_VERSION=$(shell grep FROM Dockerfile | sed "s/^.*://")
TAG=${TAG_BASE}-${TAG_VERSION}

build:
	echo "Building ${TAG}"
	docker build -t ${TAG} .

publish: build
	docker push ${TAG}
