# BlockURL
[![Publish Docker image](https://github.com/BeatLink/BlockURL/actions/workflows/build-and-push-docker-image.yml/badge.svg)](https://github.com/BeatLink/BlockURL/actions/workflows/build-and-push-docker-image.yml)

BlockURL is a Firefox extension to block a specific URL or link. Unlike other blockers, it doesn't work on a domain or subdomain but on a specific URL. This is mainly useful for blocking visited articles, videos, pages and other content.

BlockURL uses a self hosted Python Flask server in order to store all of the URLs that are blocked as well as the text for the blocked page. This enables an unlimited number of URLs to be stored, with the only limitations being SQLite and the filesystem. The sync server is hosted on DockerHub.

## Rationale
The internet is vast, but the parts we visit tend to repeat themselves. Recommendation algorithms, shared links, and search results frequently resurface content you have already seen — articles you have already read, videos you have already watched, pages you have already visited. Every time that happens, you have to consciously recognise and skip it, which adds up to a surprising amount of wasted time and mental effort over the course of a day.

BlockURL solves this by permanently hiding content once you have seen it. Rather than blocking entire domains or topics, it targets the exact URL of the specific page or video you want to dismiss, leaving the rest of the site fully accessible. The result is a cleaner, faster browsing experience where your attention is always directed toward something new.

This is particularly useful on content-heavy platforms where the same videos, articles, or posts tend to resurface repeatedly. Instead of relying on your memory to filter out old content, BlockURL does it automatically — so you can spend less time skipping things you have already seen and more time discovering things you have not.

## Features
- Configuration of blocked page
- Import and export of block lists
- One-click blocking
- Blocks specific URL or page instead of domain
- Unlimited storage size for block list
- All data stored on a self hosted sync server, deployed and controlled by you

## Usage

First you will need to install the sync server via DockerHub. Once installed, install the addon and go to settings, then set the sync server URL.

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

#### Notes

- **Persistence** — the `blockurl_data` volume keeps your database intact across restarts and updates. Without it, your blocked URL list will be lost when the container is recreated.
- **Port** — change the left-hand value of `-p 8000:8000` to use a different host port, e.g. `-p 9000:8000`.
- **Updating** — pull the latest image and recreate the container. Your database will be preserved:
```bash
  docker compose pull && docker compose up -d
```

## Development

### Development Sync Server Setup

1. Run the following commands:
```bash
cd sync-server
python3 -m venv venv
source venv/bin/activate
pip install --no-cache-dir --upgrade -r requirements.txt
DATABASE_PATH=blockurl.db python3 -m app.blockurl
```

The development sync server should now be accessible at [http://localhost:8000](http://localhost:8000).

### Loading the Addon

1. Load the addon as a temporary addon in `about:debugging`.
2. Edit the code as needed. Be sure to reload the addon from `about:debugging`.

### Publishing

#### Publishing to DockerHub

Publishing is handled by GitHub Actions.

1. Create a release explaining the changes.
2. GitHub Actions will build and push the sync server image automatically.

#### Publishing to Firefox Addon Store

1. Run the following:
```bash
cd firefox-addon
zip -r -FS ../blockurl.zip * --exclude '*.git*'
```

2. Go to [https://addons.mozilla.org/en-US/developers/addon/blockurl/versions/submit/](https://addons.mozilla.org/en-US/developers/addon/blockurl/versions/submit/)