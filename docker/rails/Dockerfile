FROM jruby:9.1.15-alpine

# Either use jruby above or uncomment both of these
#FROM ruby:2.5.0
#RUN apt-get update -qq && apt-get install -y build-essential libpq-dev nodejs


RUN gem install rails -v '5.1.4'

# RUN rails new trash && cd trash && bundle install && cd .. && rm -rf trash
RUN mkdir /myapp
WORKDIR /myapp
COPY Gemfile /myapp/Gemfile
COPY Gemfile.lock /myapp/Gemfile.lock
RUN bundle install

