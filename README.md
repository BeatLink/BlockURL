# BlockURL

[![Publish Docker image](https://github.com/BeatLink/BlockURL/actions/workflows/build-and-push-docker-image.yml/badge.svg)](https://github.com/BeatLink/BlockURL/actions/workflows/build-and-push-docker-image.yml)

## Table of Contents
- [BlockURL](#blockurl)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Rationale](#rationale)
  - [Features](#features)
  - [Firefox Addon](#firefox-addon)
    - [Addon Installation](#addon-installation)
    - [Addon Development](#addon-development)
      - [Publishing to Firefox Addon Store](#publishing-to-firefox-addon-store)
  - [Sync Server](#sync-server)
    - [Installation](#installation)
      - [Docker](#docker)
        - [Docker Run](#docker-run)
        - [Docker Compose](#docker-compose)
        - [Notes](#notes)
      - [Nix](#nix)
        - [NixOS Module](#nixos-module)
        - [Configuration Options](#configuration-options)
    - [Development](#development)
      - [Python venv Setup](#python-venv-setup)
      - [Nix Development Environment](#nix-development-environment)
      - [Publishing](#publishing)
        - [Publishing to DockerHub](#publishing-to-dockerhub)
  - [AI Use Policy](#ai-use-policy)


## Overview

BlockURL is a Firefox extension to block a specific URL or link. Unlike other blockers, it doesn't work on a domain or subdomain but on a specific URL. This is mainly useful for blocking visited articles, videos, pages and other content.

BlockURL uses a self hosted Python Flask server in order to store all of the URLs that are blocked as well as the text for the blocked page. This enables an unlimited number of URLs to be stored, with the only limitations being SQLite and the filesystem. The sync server is hosted on DockerHub.

## Rationale

The internet is vast, but the parts we visit tend to repeat themselves. Recommendation algorithms, shared links, and search results frequently resurface content you have already seen — articles you have already read, videos you have already watched, pages you have already visited. Every time that happens, you have to consciously recognise and skip it, which adds up to a surprising amount of wasted time and mental effort over the course of a day.

BlockURL solves this by permanently hiding content once you have seen it. Rather than blocking entire domains or topics, it targets the exact URL of the specific page or video you want to dismiss, leaving the rest of the site fully accessible. The result is a cleaner, faster browsing experience where your attention is always directed toward something new.

This is particularly useful on content-heavy platforms where the same videos, articles, or posts tend to resurface repeatedly. Instead of relying on your memory to filter out old content, BlockURL does it automatically — so you can spend less time skipping things you have already seen and more time discovering things you have not.

## Features

* **One-click blocking** — block any page instantly from your browser toolbar, without interrupting your browsing flow.
* **URL-level precision** — unlike traditional blockers that target entire domains, BlockURL targets the exact URL of a specific page, article, or video, leaving the rest of the site fully accessible.
* **Permanent dismissal** — blocked pages are replaced with a customisable blocked page, so previously seen content stays out of sight permanently.
* **Customisable blocked page** — configure the heading, body text, and button to match your preferences.
* **Import and export** — back up your block list or transfer it between devices with a simple import and export.
* **Unlimited block list** — store as many URLs as you need, with no artificial limits beyond your own storage.
* **Self hosted sync server** — all data lives on a server you own and control, with no third party involvement and no data sharing.

--- 

## Firefox Addon

### Addon Installation

Install the addon from [https://addons.mozilla.org/en-US/firefox/addon/blockurl/](https://addons.mozilla.org/en-US/firefox/addon/blockurl/)

### Addon Development

1. Clone the repository
2. Load the addon as a temporary addon in [about:debugging](about:debugging) by selecting the `manifest.json` file in the firefox-addon folder.
3. Edit the code as needed. Be sure to reload the addon from [about:debugging](about:debugging).


#### Publishing to Firefox Addon Store

1. Run the following:

```bash
cd firefox-addon
zip -r -FS ../blockurl.zip * --exclude '*.git*'
```

2. Go to [https://addons.mozilla.org/en-US/developers/addon/blockurl/versions/submit/](https://addons.mozilla.org/en-US/developers/addon/blockurl/versions/submit/)

---

## Sync Server

### Installation

First you will need to install the sync server via DockerHub. Once installed, install the addon and go to settings, then set the sync server URL.

#### Docker

##### Docker Run

```bash
docker run -d \
  --name blockurl \
  -p 8000:8000 \
  -v blockurl_data:/app/database \
  --restart unless-stopped \
  beatlink/blockurl:latest
```

##### Docker Compose

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

##### Notes

- **Persistence** — the `blockurl_data` volume keeps your database intact across restarts and updates. Without it, your blocked URL list will be lost when the container is recreated.
- **Port** — change the left-hand value of `-p 8000:8000` to use a different host port, e.g. `-p 9000:8000`.
- **Updating** — pull the latest image and recreate the container. Your database will be preserved:

```bash
  docker compose pull && docker compose up -d
```

#### Nix

##### NixOS Module

Add BlockURL to your NixOS configuration by including the flake as an input and enabling the module:

**`flake.nix`**

nix

```nix
{
    inputs ={
        nixpkgs.url ="github:NixOS/nixpkgs/nixos-unstable";
        blockurl.url ="github:BeatLink/BlockURL";
    };

    outputs ={ nixpkgs, blockurl,...}:{
        nixosConfigurations.your-hostname = nixpkgs.lib.nixosSystem {
            modules = [
                blockurl.nixosModules.default
                {
                  services.blockurl.enable =true;
                }
            ];
        };
    };
}
```

Then rebuild your system:

bash

```bash
sudo nixos-rebuild switch
```

##### Configuration Options

All options are set under `services.blockurl` in your NixOS configuration:

nix

```nix
services.blockurl = {
  enable = true;
  host = "0.0.0.0"; # Address to bind to (default: 0.0.0.0)
  port = 8000; # Port to listen on (default: 8000)
  dataDir = "/var/lib/blockurl"; # Directory for the SQLite database
  databaseFile = "blockurl.db"; # Database filename
  openFirewall = true; # Open the port in the firewall (default: false)
  extraEnv = {}; # Additional environment variables
};
```

### Development

#### Python venv Setup

1. Run the following commands:

```bash
cd sync-server
python3 -m venv venv
source venv/bin/activate
pip install --no-cache-dir -e .
DATABASE_PATH=blockurl.db blockurl-server
```

The development sync server should now be accessible at [http://localhost:8000](http://localhost:8000).


#### Nix Development Environment

A dev shell is included with all dependencies preconfigured. To enter it:

bash

```bash
nix develop
```

To run the server directly without entering the shell:

bash

```bash
nix run
```

To build the package:

bash

```bash
nix build
```

The built binary will be available at `./result/bin/blockurl-server`.

#### Publishing

##### Publishing to DockerHub

Publishing is handled by GitHub Actions.

1. Create a release explaining the changes.
2. GitHub Actions will build and push the sync server image automatically.

---

## AI Use Policy

This project makes use of AI assistance during development. Specifically, Claude Sonnet 4.6 by Anthropic is used to help with code development, documentation, and written content including this README.

All AI-generated output is reviewed, edited, and approved by a human (BeatLink) before being incorporated into the project. AI is used as a development aid, not a replacement for human judgement — final decisions on code correctness, security, and content accuracy rest with the project maintainers (BeatLink).
