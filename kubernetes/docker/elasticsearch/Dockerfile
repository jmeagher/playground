FROM quay.io/pires/docker-elasticsearch-kubernetes:5.6.1

# Install x-pack, but remove the ML part
# See https://discuss.elastic.co/t/elasticsearch-failing-to-start-due-to-x-pack/85125/6
RUN NODE_NAME=tmp-for-install-only /elasticsearch/bin/elasticsearch-plugin install --batch x-pack
RUN rm -rf /elasticsearch/plugins/x-pack/platform/linux-x86_64
RUN echo "xpack.ml.enabled: false" >> /elasticsearch/config/elasticsearch.yml
