FROM alpine:3.6
LABEL maintainer "John Meagher <docker@jmeagher.net>"

RUN apk update \
 && apk add man man-pages mdocml-apropos less less-doc tar \
 && apk add curl curl-doc ca-certificates lynx lynx-doc \
 && apk add bash bash-doc bash-completion \
 && apk add util-linux coreutils binutils findutils grep \
 && apk add git vim screen tmux jq

# Hack for a minor command my dotfiles are expecting to be there
RUN mkdir -p /root/bin \
 && touch /root/bin/locale \
 && chmod +x /root/bin/locale

RUN git clone https://github.com/jmeagher/dotfiles.git \
 && ( cd dotfiles && sh setup.sh )

ENV PAGER less

ENTRYPOINT ["/bin/bash", "-li"]
