# StockTracker
StockTracker repository.

## Requirements
TA-Lib must be installed as system library.

- [TA-Lib Library installation 1](https://blog.quantinsti.com/install-ta-lib-python/)
- [TA-Lib Library installation 2](https://rohan09.medium.com/how-to-install-ta-lib-in-python-86e4edb80934)
- [TA-Lib Python wrapper reference](https://mrjbq7.github.io/ta-lib/install.html)

To install Ta-Lib easily, you can follow these steps:

- Open the Anaconda prompt
- Write the code:
`conda install -c conda-forge ta-lib`
- Press the "Enter" key

##  Setup

###  Install MongoDB

[MongoDB Community Server](https://www.mongodb.com/try/download/community)

If any error like:
`error: Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual
C++ Build Tools":`


Install it from:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

###  Create and use Python evironment

```
# Create environment
python -m venv venv
```

###  Execution
```
# Activate the environment
source venv/bin/activate

# Activate Windows
venv\Scripts\activate
# Deactivate Windows
venv\Scripts\deactivate

# Install dependencies
pip install -r requirements.txt

# Execute process
python src/tasks/process.py
```
###  Database
```
mongod --config /usr/local/etc/mongod.conf
ps aux | grep -v grep | grep mongod
ps -fea | grep mongo

vi /usr/local/etc/mongod.conf

# To kill the mongod process.
kill -2 7723
    
launchctl list | grep mongo
```
