import pytest

from ioc_typing import IOCClassifier


@pytest.fixture
def classifier():
    return IOCClassifier()


class TestIPv4Classification:
    def test_valid_ipv4(self, classifier):
        valid_ips = [
            "192.168.1.1",
            "8.8.8.8",
            "255.255.255.255",
            "0.0.0.0",
            "127.0.0.1",
            "192.168.01.1",  # Leading zeros, hgw
        ]
        for ip in valid_ips:
            result = classifier.classify(ip)
            assert result["determined"] is True
            assert result["type_pri"] == "ip"
            assert result["type_sec"] == "v4"

    def test_invalid_ipv4(self, classifier):
        invalid_ips = [
            "256.1.2.3",  # First octet too large
            "1.2.3.256",  # Last octet too large
            "192.168.1",  # Too few octets
            "192.168.1.1.1",  # Too many octets
            "192.168.1.",  # Trailing dot
            ".192.168.1.1",  # Leading dot
            "192.168.1.1/24",  # CIDR notation
            "192.168.1.abc",  # Invalid characters
        ]
        for ip in invalid_ips:
            result = classifier.classify(ip)
            assert result["determined"] is False or result["type_sec"] != "v4"


class TestIPv6Classification:
    def test_valid_ipv6(self, classifier):
        valid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:db8:85a3:0:0:8a2e:370:7334",
            "2001:db8:85a3::8a2e:370:7334",
            "::1",
            "::",
            "fe80::1",
            "fe80::217:f2ff:fe07:ed62",
        ]
        for ip in valid_ips:
            result = classifier.classify(ip)
            assert result["determined"] is True
            assert result["type_pri"] == "ip"
            assert result["type_sec"] == "v6"

    def test_invalid_ipv6(self, classifier):
        invalid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334:7334",  # Too many segments
            "2001:0db8:85a3",  # Too few segments
            "2001::85a3::7334",  # Multiple ::
            "2001:0db8:85a3:0000:0000:8a2e:0370:xxxx",  # Invalid characters
            "2001:0db8:85a3:0000:0000:8a2e:0370:",  # Trailing colon
        ]
        for ip in invalid_ips:
            result = classifier.classify(ip)
            assert result["determined"] is False or result["type_sec"] != "v6"


class TestDomainClassification:
    def test_valid_domains(self, classifier):
        valid_domains = [
            "example.com",
            "sub.example.com",
            "sub.sub.example.com",
            "example-domain.com",
            "example123.com",
            "example.co.uk",
            "xn--80ak6aa92e.com",  # Punycode domain
        ]
        for domain in valid_domains:
            result = classifier.classify(domain)
            assert (
                result["determined"] is True
            ), f"Failed to classify valid domain: {domain}"
            assert (
                result["type_pri"] == "domain"
            ), f"Wrong classification for domain: {domain}"

    def test_invalid_domains(self, classifier):
        invalid_domains = [
            "example",  # No TLD
            ".example.com",  # Leading dot
            "example.com.",  # Trailing dot
            "-example.com",  # Leading hyphen
            "example-.com",  # Trailing hyphen
            "exam ple.com",  # Space
            "exa&mple.com",  # Special character
            "example.c",  # Single-letter TLD
        ]
        for domain in invalid_domains:
            result = classifier.classify(domain)
            assert result["determined"] is False or result["type_pri"] != "domain"


class TestURLClassification:
    def test_valid_urls(self, classifier):
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://example.com/path",
            "https://example.com/path?param=value",
            "https://example.com:8080",
            "https://sub.example.com",
            "https://example.com/path#fragment",
            "example.com/path",
            "https://192.168.1.1/path",
            "ftp://example.com",  # FTP is a valid protocol
            "sftp://git@github.com",  # Add another protocol example
            "git://github.com/user/repo.git",  # Git protocol example
        ]
        for url in valid_urls:
            result = classifier.classify(url)
            assert result["determined"] is True, f"Failed to classify valid URL: {url}"
            assert result["type_pri"] == "url"

    def test_invalid_urls(self, classifier):
        invalid_urls = [
            "http:/example.com",  # Missing slash
            "https://exam ple.com",  # Space in domain
            "http://.example.com",  # Leading dot
            "https://example",  # No TLD
            "https:example.com",  # Missing slashes
        ]
        for url in invalid_urls:
            result = classifier.classify(url)
            assert result["determined"] is False or result["type_pri"] != "url"

    def test_complex_url_structures(self, classifier):
        complex_urls = [
            # Full URL with all components
            (
                "https://user:password@www.example.com:443/path/to/resource"
                "?param1=value1&param2=value2#section"
            ),
            # Various authentication patterns
            "https://user@example.com",
            "https://user:pass@example.com",
            "ftp://anonymous:password@ftp.example.com",
            # Different port numbers
            "https://example.com:8080",
            "http://localhost:3000",
            "https://192.168.1.1:8443",
            # Complex query parameters
            "https://example.com/path?param=value&array[]=1&array[]=2",
            "https://example.com/search?q=test&lang=en&page=1",
            # Various fragments
            "https://example.com/page#top",
            "https://example.com/docs#section-1.2.3",
            # Mixed case in protocol and domain
            "HTTPS://Example.COM/Path",
            # Unicode in path
            "https://example.com/über/straße",
            # Encoded characters
            "https://example.com/path%20with%20spaces",
            "https://example.com/path?q=hello%20world",
            # Multiple subdomains
            "https://sub1.sub2.sub3.example.com",
            # IP-based URLs with all components
            "http://user:pass@192.168.1.1:8080/path?query=value#fragment",
            # URLs with unusual but valid characters
            "https://example.com/path~with~tildes",
            "https://example.com/path+with+plus",
            # URLs with multiple query parameters and fragments
            "https://example.com/path?a=1&b=2&c=3#section-1?subsection-2",
        ]

        for url in complex_urls:
            result = classifier.classify(url)
            assert result["determined"] is True, f"Failed to classify valid URL: {url}"
            assert result["type_pri"] == "url", f"Wrong classification for URL: {url}"


class TestHashClassification:
    def test_valid_hashes(self, classifier):
        valid_hashes = {
            "md5": [
                "d41d8cd98f00b204e9800998ecf8427e",
                "e4d909c290d0fb1ca068ffaddf22cbd0",
            ],
            "sha1": [
                "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
            ],
            "sha256": [
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
            ],
        }
        for hash_type, hashes in valid_hashes.items():
            for hash_value in hashes:
                result = classifier.classify(hash_value)
                assert result["determined"] is True
                assert result["type_pri"] == "hash"
                assert result["type_sec"] == hash_type

    def test_invalid_hashes(self, classifier):
        invalid_hashes = [
            "d41d8cd98f00b204e9800998ecf8427",  # Too short MD5
            "d41d8cd98f00b204e9800998ecf8427ef",  # Too long MD5
            "d41d8cd98f00b204e9800998ecf8427g",  # Invalid character
            "da39a3ee5e6b4b0d3255bfef95601890afd8070",  # Too short SHA1
            "da39a3ee5e6b4b0d3255bfef95601890afd80709a",  # Too long SHA1
            # Too short SHA256
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85",
            # Too long SHA256
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8555",
            "abcdefghijklmnopqrstuvwxyz123456",  # Valid length but invalid chars
        ]
        for hash_value in invalid_hashes:
            result = classifier.classify(hash_value)
            assert result["determined"] is False or result["type_pri"] != "hash"


class TestMiscClassification:
    def test_unclassifiable_input(self, classifier):
        unclassifiable = [
            "",  # Empty string
            " ",  # Space
            "Hello, World!",  # Plain text
            "123456789",  # Just numbers
            "abcdef",  # Just letters
            "@#$%^&*()",  # Special characters
            "a" * 100,  # Long string
        ]
        for input_value in unclassifiable:
            result = classifier.classify(input_value)
            assert result["determined"] is False
            assert result["type_pri"] is None
            assert result["type_sec"] is None
