# BlockURL

[![Publish Docker image](https://github.com/BeatLink/BlockURL/actions/workflows/build-and-push-docker-image.yml/badge.svg)](https://github.com/BeatLink/BlockURL/actions/workflows/build-and-push-docker-image.yml)

BlockURL is a firefox extension to block a specific URL or link. Unlike other blockers, it doesnt work on a domain or subdomain but a specific url. This is mainly useful for blocking visited articles, videos, pages and other content

BlockURL uses a self hosted Python Flask Sync Server in order to store all of the URLs that are blocked as well as the text for the blocked page. This enables an infinite number of urls to be stored with the only limitations being SQlite and the filesystem. The sync server is hosted on DockerHub

## Features
- Configuration of Blocked Page
- Import and Export of Block Lists
- One Click Blocking
- Blocks specific URL or page instead of domain
- Unlimited storage size for blocklist
- All data stored on a self hosted sync server, deployed and controlled by you


## Usage
First you will need to install the sync server via dockerhub. Once installed, install the addon and go to settings then set the sync server url.


### Sync Server Installation

#### Docker Run
```bash
docker run -d \
  --name blockurl \
  -p 8000:8000 \
  -v blockurl_data:/app/database \
  --restart unless-stopped \
  beatlink/blockurl:latest
```

#### Docker Compose

Create a `docker-compose.yml` file with the following content:
```yaml
services:
  blockurl:
    image: beatlink/blockurl:latest
    container_name: blockurl
    ports:
      - "8000:8000"
    volumes:
      - blockurl_data:/app/database
    restart: unless-stopped

volumes:
  blockurl_data:
```

Then start the server:
```bash
docker compose up -d
```

### Notes

- **Persistence** — the `blockurl_data` volume keeps your database intact across restarts and updates. Without it, your blocked URL list will be lost when the container is recreated.
- **Port** — change the left-hand value of `-p 8000:8000` to use a different host port, e.g. `-p 9000:8000`.
- **Updating** — pull the latest image and recreate the container. Your database will be preserved:
```bash
  docker compose pull && docker compose up -d
```



## Development

### Development Sync Server Setup
1. Run the below commands

```bash
cd sync-server
python3 -m venv venv
source venv/bin/activate
pip install --no-cache-dir --upgrade -r requirements.txt
DATABASE_PATH=blockurl.db python3 -m app.blockurl
```
The development sync server should now be accessible at [http://localhost:8000](http://localhost:8000)

### Loading the Addon
1. Load the addon as a temporary addon in `about:debugging`.
2. Edit the code as needed. Be sure to reload the addon from `about:debugging`

#### Publishing to Dockerhub
The publishing is handled by Github Actions.

1. Create a release explaining the changes
2. Github Actions should build the sync server automatically

#### Publishing to Firefox Addon Store
1. Run the Following
```bash
cd firefox-addon
zip -r -FS ../blockurl.zip * --exclude '*.git*'.
```
2. Go to [https://addons.mozilla.org/en-US/developers/addon/blockurl/versions/submit/](https://addons.mozilla.org/en-US/developers/addon/blockurl/versions/submit/)