# BlockURL
Firefox Extension to block a specific URL or link


## Sync Server
BlockURL requires a sync server to store the list of blocked URLs. The main way of deployment is via docker

### Development
cd sync-server
python3 -m venv venv
source venv/bin/activate
pip install --no-cache-dir --upgrade -r requirements.txt
DATABASE_PATH=blockurl.db python3 app/blockurl/main.py
