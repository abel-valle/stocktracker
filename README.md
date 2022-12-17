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

    conda install -c conda-forge ta-lib

##  Setup

###  Execution

    source venv/bin/activate
    # deactivate
    python src/tasks/process.py

###  Database

    mongod --config /usr/local/etc/mongod.conf
    ps aux | grep -v grep | grep mongod
    ps -fea | grep mongo
    
    vi /usr/local/etc/mongod.conf
    
    # To kill the mongod process.
    kill -2 7723
    
    launchctl list | grep mongo
