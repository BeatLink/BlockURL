# BlockURL

[![Publish Docker image](https://github.com/BeatLink/BlockURL/actions/workflows/build-and-push-docker-image.yml/badge.svg)](https://github.com/BeatLink/BlockURL/actions/workflows/build-and-push-docker-image.yml)

BlockURL is a firefox extension to block a specific URL or link. Unlike other blockers, it doesnt work on a domain or subdomain but a specific url. This is mainly useful for blocking visited articles, videos, pages and other content

BlockURL uses a Python Flask Sync Server in order to store all of the URLs that are blocked as well as the text for the blocked page. This sync server is hosted on DockerHub

## Features
- Configuration of Blocked Page
- Import and Export of Block Lists
- One Click Blocking
- Blocks specific URL or page instead of domain
- Unlimited storage size for blocklist


## Usage
First you will need to install the sync server via dockerhub. Once installed, install the addon and go to settings then set the sync server url.

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