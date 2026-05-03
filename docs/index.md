# ioc-typing

A zero-dependency Python library that classifies a string as one of:

- **IPv4 / IPv6** address
- **Domain name** (RFC 1034 FQDN form, including the trailing-dot variant)
- **URL** (with or without scheme; HTTP/HTTPS/FTP/SFTP/SSH/Git/file)
- **Hash** — MD5 / SHA1 / SHA256

Inputs that don't match any category are returned as unclassified rather
than raising. The package ships a `py.typed` marker, so downstream type
checkers consume the inline annotations directly.

## Install

```bash
pip install ioc-typing
```

Requires Python 3.10 or newer.

## Quick example

```python
from ioc_typing import IOCClassifier

classifier = IOCClassifier()

classifier.classify("192.168.1.1")
# {'query': '192.168.1.1', 'determined': True, 'type_pri': 'ip', 'type_sec': 'v4'}

classifier.classify("evil.example.com")
# {'query': 'evil.example.com', 'determined': True, 'type_pri': 'domain', 'type_sec': None}

classifier.classify("d41d8cd98f00b204e9800998ecf8427e")
# {'query': '...', 'determined': True, 'type_pri': 'hash', 'type_sec': 'md5'}

classifier.classify("not an IOC")
# {'query': 'not an IOC', 'determined': False, 'type_pri': None, 'type_sec': None}
```

## Where to next

- [Command line](cli.md) — pipeline-friendly `ioc-classify` shipped with the package.
- [API reference](api.md) — auto-generated from the source docstrings.
