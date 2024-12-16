import re
from typing import Dict, Union, Pattern


class IOCClassifier:
    """
    Classifier for identifying various types of IOCs (Indicators of Compromise).

    This class provides functionality to classify different types of indicators commonly 
    found in threat intelligence and security analysis, including:

    - IP addresses (IPv4 and IPv6)
    - Domain names
    - URLs (including various protocols and complex structures)
    - Cryptographic hashes (MD5, SHA1, SHA256)

    The classifier uses regular expressions to identify and validate each type of indicator.
    For each input, it returns a dictionary containing:
        - determined: Boolean indicating if the input was successfully classified
        - type_pri: Primary type (e.g., "ip", "domain", "url", "hash")
        - type_sec: Secondary type where applicable (e.g., "v4"/"v6" for IPs, hash types)

    The class is designed to be strict in its classifications to minimize false positives,
    while still being flexible enough to handle common variations in format.
    """

    def __init__(self):
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, Pattern]:
        """
        Compile all regex patterns used for classification.
        Returns a dictionary of compiled patterns for better performance and organization.
        """
        # IP patterns
        ipv4_pattern = (
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )

        ipv6_pattern = (
            r'^(?:'
            r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|'
            r'(?:[0-9a-fA-F]{1,4}:){1,7}:|'
            r'(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
            r'(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|'
            r'(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|'
            r'(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|'
            r'(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|'
            r'[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|'
            r':(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|'
            r'fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|'
            r'::(?:ffff(?::0{1,4}){0,1}:){0,1}'
            r'(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}'
            r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|'
            r'(?:[0-9a-fA-F]{1,4}:){1,4}:'
            r'(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}'
            r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'
        )

        # Hash patterns
        hash_patterns = {
            'md5': r'^[a-fA-F0-9]{32}$',
            'sha1': r'^[a-fA-F0-9]{40}$',
            'sha256': r'^[a-fA-F0-9]{64}$'
        }

        # Domain pattern
        domain_pattern = (
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'
            r'+[a-zA-Z]{2,}$'
        )

        # URL components
        url_components = {
            'protocol': r'(?:(?:https?|ftp|sftp|ftps|ssh|git|file)://)',
            'auth': r'(?:(?:[A-Za-z0-9\-._~!$&\'()*+,;=:]|%[0-9A-Fa-f]{2})*@)',
            'host': (
                r'(?:(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)'
                r'+[A-Za-z]{2,}\.?|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            ),
            'port': r'(?::\d+)',
            'path': r'(?:/[^\s?#]*)',
            'query': r'(?:\?[A-Za-z0-9\-._~!$&\'()*+,;=:@%/\[\]]*)',
            'fragment': r'(?:#[^\s]*)'
        }

        # Construct URL pattern
        url_pattern = (
            r'^(?:' +
            url_components['protocol'] + 
            url_components['auth'] + r'?' +
            url_components['host'] + 
            url_components['port'] + r'?' +
            url_components['path'] + r'?' +
            url_components['query'] + r'?' +
            url_components['fragment'] + r'?|' +
            r'(?!' + url_components['protocol'] + r')' +
            url_components['host'] +
            r'(?:' + url_components['port'] + r'|' +
            url_components['path'] + r'+|' +
            url_components['query'] + r'|' +
            url_components['fragment'] + r')' +
            r')$'
        )

        # Compile all patterns
        return {
            'ipv4': re.compile(ipv4_pattern),
            'ipv6': re.compile(ipv6_pattern),
            'md5': re.compile(hash_patterns['md5']),
            'sha1': re.compile(hash_patterns['sha1']),
            'sha256': re.compile(hash_patterns['sha256']),
            'domain': re.compile(domain_pattern),
            'url': re.compile(url_pattern, re.IGNORECASE)
        }

    def classify(self, query: str) -> Dict[str, Union[str, bool, None]]:
        """
        Classify a given string into various cybersecurity-related types.
        
        Args:
            query (str): The string to classify
            
        Returns:
            dict: Classification result containing query, determined status, and type information
        """

        # Check IP addresses first (most specific)
        if self.patterns['ipv4'].match(query):
            return self._create_result(query, "ip", "v4")
        if self.patterns['ipv6'].match(query):
            return self._create_result(query, "ip", "v6")

        # Check hashes (specific patterns)
        for hash_type in ['md5', 'sha1', 'sha256']:
            if self.patterns[hash_type].match(query):
                return self._create_result(query, "hash", hash_type)

        # Check URL before domain (URLs are more specific)
        if self.patterns['url'].match(query):
            return self._create_result(query, "url", None)

        # Check domain last (most general)
        if self.patterns['domain'].match(query):
            return self._create_result(query, "domain", None)

        return {
            "query": query,
            "determined": False,
            "type_pri": None,
            "type_sec": None
        }

    def _create_result(self, query: str, type_pri: str, type_sec: str | None) -> Dict[str, Union[str, bool, None]]:
        """Helper method to create a result dictionary."""
        return {
            "query": query,
            "determined": True,
            "type_pri": type_pri,
            "type_sec": type_sec
        }
