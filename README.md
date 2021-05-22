# Promise Tracker

Keep track of politicians fulfilling their campaign promises or not.

Read this in other languages: [Hungarian](README.hu.md)

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes.

### Prerequisites

You need to install the following tools:
- [Python 3](https://www.python.org/) (minimum 3.4)
- [PostgreSQL](https://www.postgresql.org/)

### Installing

1. Install dependencies with `pip install -r requirements.txt`
2. Copy env template `cp .env.example .env` then fill in missing keys
3. Create database with `createdb igeretfigyelo`
4. Load database schema with `psql -f db/schema.sql -d igeretfigyelo`

## Running locally

1. Start the server with `python __init__.py`
2. Visit `127.0.0.1:8080` or `localhost:8080`
3. Enjoy development :)

## Running the tests

The project does not have tests yet :(

### Style test

The project does not have style tests yet :(

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code
of conduct, and the process for submitting pull requests to us.

## License

The project doesn't have explicit license yet :(
