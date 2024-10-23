# BlockURL
Firefox Extension to block a specific URL or link


## Sync Server
BlockURL requires a sync server to store the list of blocked URLs. The main way of deployment is via docker

### Development

#### Setting Up Development Environment
1. Run the below commands

```bash
cd sync-server
python3 -m venv venv
source venv/bin/activate
pip install --no-cache-dir --upgrade -r requirements.txt
```

2. Start the server with `DATABASE_PATH=blockurl.db python3 app/blockurl/main.py`


3. Next, load the addon as a temporary addon in `about:debugging`.

4. Edit the code as needed. Be sure to reload the addon from `about:debugging`

#### Publishing to Dockerhub
The publishing is handled by Github Actions.

1. Create a release explaining the changes

2. Github Actions should build the sync server automatically
