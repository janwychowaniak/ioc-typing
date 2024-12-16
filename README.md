# IOC Classifier

A Python library for identifying and classifying various types of Indicators of Compromise (IOCs).

## Installation

```bash
pip install ioc-classifier
```

## Usage

```python
from ioc_typing import IOCClassifier

classifier = IOCClassifier()
ioc_type = classifier.classify("192.168.1.1")
print(ioc_type)
```

## Features

- Identifies multiple IOC types including IP addresses, domains, hashes, etc.
- Fast and accurate classification
- Easy to integrate into existing security tools

## License

[MIT](LICENSE)
