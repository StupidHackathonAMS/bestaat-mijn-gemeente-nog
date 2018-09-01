# bestaat-mijn-gemeente-nog
Bestaat mijn gemeente nog?

Uses [data from CBS](https://www.cbs.nl/en-gb/our-services/open-data) and the downloaded zip files from [this page  at PDOK](https://www.pdok.nl/downloads?articleid=1949811) which should be at `grenzen/<year>/` per year (annoying, yes i know).

## running

1. `docker-compose up -d`
1. `docker exec bmgn_app_1 get_lists.py`
1. `docker exec bmgn_app_1 diff.py`
