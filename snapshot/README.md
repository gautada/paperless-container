# Paperless

The reader mechanism that extracts the text of a PDF and names the file properly.

## Install and Setup

1. Install python3 from [python.org(https://www.python.org)]
2. $ sudo pip3 install virtualenv
3. $ cd ~/Temporary/
4. $ mkdir paperless
5. $ virtualenv --python=/Library/Frameworks/Python.framework/Versions/3.7/bin/python3 ./paperless
6. $ ln -s ~/Development/Personal/Paperless/paperless.py ./
7. $ ln -s ~/Development/Personal/Paperless/vendors /etc/paperless/vendors

Run:

python3 paperless.py --date=1 --file /Users/aegaeon/Library/Mobile\ Documents/com~apple~CloudDocs/Documents/2013-09-23\ AT\&T.pdf

