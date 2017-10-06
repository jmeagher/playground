FROM alpine:3.6
LABEL maintainer "John Meagher <docker@jmeagher.net>"

RUN apk update \
 && apk add man man-pages mdocml-apropos less less-doc tar \
 && apk add curl curl-doc ca-certificates lynx lynx-doc \
 && apk add bash bash-doc bash-completion \
 && apk add util-linux coreutils binutils findutils grep \
 && apk add git vim screen tmux jq

RUN apk add python python-dev py2-pip gcc musl-dev \
 && pip install requests

# Install the kubectl cli so it is available in-cluster
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s \
    https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x ./kubectl \
    && mv ./kubectl /usr/local/bin/kubectl

# Hack for a minor command my dotfiles are expecting to be there
RUN mkdir -p /root/bin \
 && touch /root/bin/locale \
 && chmod +x /root/bin/locale

RUN git clone https://github.com/jmeagher/dotfiles.git \
 && ( cd dotfiles && sh setup.sh )

ENV PAGER less

CMD ["sleep", "9999h"]
