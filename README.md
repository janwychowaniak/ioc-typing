# IOC Typing (a classifier)

A Python library for identifying and classifying various types of Indicators of Compromise (IOCs). IOCs are forensic artifacts that indicate potential security breaches, malware infections, or other malicious activities in a system or network.

## Installation

From PyPI (stable release):
```bash
pip install ioc-typing
```

For development:
```bash
git clone https://github.com/janwychowaniak/ioc-typing.git
cd ioc-typing
pip install -e ".[dev]"  # or "make dev" for easily creating a local venv
```

## Usage

Basic usage:
```python
from ioc_typing import IOCClassifier

classifier = IOCClassifier()

# Classify different types of IOCs
print(classifier.classify("192.168.1.1"))          # Output: IP_ADDRESS
print(classifier.classify("evil.com"))             # Output: DOMAIN
print(classifier.classify("44d88612fea8a8f36de82e1278abb02f")) # Output: MD5_HASH
```

Batch classification:
```python
iocs = [
    "192.168.1.1",
    "https://pages.info/malware.exe",
    "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
    "not an IOC"
]

for ioc in iocs:
    ioc_type = classifier.classify(ioc)
    print(f"{ioc}: {ioc_type['type_pri']}")
```

## Features

- Identifies multiple IOC types:
  - IP addresses (IPv4 and IPv6)
  - Domain names
  - URLs
  - File hashes (MD5, SHA1, SHA256)
  - as well as non-IOCs (e.g. random strings)
- Fast and accurate classification using optimized regex patterns
- Zero dependencies for core functionality
- Comprehensive test suite ensuring reliability
- Easy integration with existing security tools and SIEM systems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT](LICENSE)
