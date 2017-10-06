FROM quay.io/honestbee/locust:0.7.5

# Try to be nice and just capture this once so
# there isn't much load on the source.
# The /corpus folder will serve as the source
# of data to index.
RUN mkdir corpus; cd corpus; \
    wget http://www.bardware.com/files/works.zip ; \
    unzip works.zip; rm works.zip
