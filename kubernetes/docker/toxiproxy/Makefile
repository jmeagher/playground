TAG_BASE=jpmeagher/playground:toxiproxy
TAG_VERSION=latest
TAG=${TAG_BASE}-${TAG_VERSION}

build:
	echo "Building ${TAG}"
	docker build -t ${TAG} .

publish: build
	docker push ${TAG}
