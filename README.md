# Network Ferret discovery parser

NF result parser

- [INSTALLATION](#installation)
- [CONFIGURATION](#configuration)
- [OPTIONS](#options)
- [LOG](#log)


# INSTALLATION

To install it right away for all UNIX users (Linux, OS X, etc.), type:

    sudo apt-get install python3

To install python3 for CentOs/RHEL 5/6(not in repo):

    yum install xz-libs
    yum groupinstall -y 'development tools'
    yum install openssl-devel

    wget http://python.org/ftp/python/3.4.5/Python-3.4.5.tar.xz
    xz -d Python-3.4.5.tar.xz
    tar xvf Python-3.4.5.tar.xz
    cd Python-3.4.5
    sudo ./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
    sudo make
    sudo make altinstall

To install python3 for CentOs/RHEL 7):

    yum install epel
    yum install python3

To install python3 for windows :

    Install python3 installer (https://www.python.org/downloads/)

# CONFIGURATION

# OPTIONS

    usage: nf_parser.py [-d] [-o] [-v] [-h]
        Parse and generate Report Template xml file based on input data file:
        Options:
        -h, --help            show this help message and exit
        -d FILE, --input=FILE
            Input directory containing Layer2_raw, connctivity_raw...
        -o FILE, --output=FILE
            Specify output csv path, default path: output.csv
        -v, --verbose         Enable debug mode


# LOG
    all log are stored under file name nf_parser.log in script folder
