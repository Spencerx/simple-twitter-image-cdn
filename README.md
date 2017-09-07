# Simple Image CDN
Works over SQLite3 and Python 3.X


## Installation
```bash
pip install -r requirements.txt
touch ./data.db
python server.py
```

## Config
By default hostname is `0.0.0.0` and port `80`. If you want to use that port, probably you should be root.
If you want to change that configuration, set the following enviroment variables:
```bash
export HOST="127.0.0.1"
export PORT="5000" 
```