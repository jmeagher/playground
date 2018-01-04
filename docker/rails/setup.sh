
# Inspired by https://docs.docker.com/compose/rails/ with a few tweaks
# This sets up a basic local development environment with docker and jruby/rails

# Skeleton setup so the first pass build will work
touch Gemfile.lock
echo "source 'https://rubygems.org'
gem 'rails', '5.1.4'" > Gemfile
#docker build -t rails:latest .

# Initialize the app with the rails in the just-built docker container
# docker run -v $(pwd):/myapp rails:latest rails new . --force --database sqlite3
docker-compose build
docker-compose run web rails new . --force --database sqlite3

# The lsiten gem was required for me on jruby, but it might not be
echo "gem 'listen', '>3.0'" >> Gemfile

# Rebuild the local image with the generated Gemfile
docker-compose build

docker-compose run web rake db:create
alias rails="docker-compose run web rails"

echo "Use 'docker-compose build' to rebuild as needed when the Gemfile changes."
echo "Use 'docker-compose up' to run the server."
echo "'rails' is now setup as an alias to run via the docker image."
