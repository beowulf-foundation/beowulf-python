# Official Python BEOWULF Library

`beowulf-python` is the official Beowulf library for Python. It comes with a
BIP38 encrypted wallet and a practical CLI utility called `beowulfpy`.

This library currently works on Python 2.7, 3.5 and 3.6. Python 3.3 and 3.4 support forthcoming.

# Installation

From Source:

```
git clone https://github.com/beowulf-foundation/beowulf-python.git
cd beowulf-python

python3 setup.py install        # python setup.py install for 2.7
or
make install
```

## Homebrew Build Prereqs

If you're on a mac, you may need to do the following first:

```
brew install openssl
export CFLAGS="-I$(brew --prefix openssl)/include $CFLAGS"
export LDFLAGS="-L$(brew --prefix openssl)/lib $LDFLAGS"
```

# CLI tools bundled

The library comes with a few console scripts.

* `beowulfpy`:
    * rudimentary blockchain CLI (needs some TLC and more TLAs)
* `beowulftail`:
    * useful for e.g. `beowulftail -f -j | jq --unbuffered --sort-keys .`

# Documentation

Documentation is available at **https://beowulfchain.com/developer-guide/python**


# TODO

* more unit tests
* 100% documentation coverage, consistent documentation
* migrate to click CLI library

# Notice

This library is *under development*.  Beware.
