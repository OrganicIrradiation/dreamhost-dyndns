README
=======

Updates the 'A' record for a server on Dreamhost with a desired IP address. Can be used as a pseudo dyn-dns service.

Setup
-----------------

  * Visit the [DreamHost control panel](https://panel.dreamhost.com/?tree=home.api) and obtain a API key with ability to use the dns-* API
  * Install the requirements with ```pip install -r requirements.txt```
  * Optional: Update `domains.csv` with the domain you wish to modify followed by the API key. Use a comma to separate the two values. No spaces.


Usage
-----------------

```
usage: update_ip.py [--help] [-f FILE] [[-s SERVER] [-k KEY] [-i IP ADDRESS]]

Update your DreamHost DNS records.

optional arguments:
  --help      			Show help message and exit.
  -f, --filename FILE   Comma-separated server,key file. If provided, overrides other options.
  -s, --server SERVER   Server's domain name. Multiple allowed.
  -k, --key KEY        	DreamHost API Key.
  -i, --ip IP ADDRESS 	Desired A record value.
```


License
-----------------

All code, unless specified, is licensed under GPLv3. Copyright 2013 [Víctor Terrón][1].

```
Dreampylib is (c) 2009 by [Laurens Simonis][2] and updated in 2014 by [Eli Ribble][3].
```

Thanks to random internetter for url and regex in `getip.py`

[1]: https://github.com/vterron/dreamhost-dyndns
[2]: http://dreampylib.laurenssimonis.com/
[3]: https://github.com/EliRibble/dreampylib
