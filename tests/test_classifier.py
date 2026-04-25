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
            "fe80::1%eth0",  # Zone-id (link-local scope)
            "fe80::217:f2ff:fe07:ed62%en0",
            "::ffff:192.168.1.1",  # IPv4-mapped IPv6
            "2001:db8::192.168.1.1",  # IPv6 with embedded IPv4
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

    def test_schemeless_url_variants(self, classifier):
        # The schemeless branch of the URL regex requires the bare host to
        # be followed by at least one of port/path/query/fragment (in that
        # order). Without any trailing component, "example.com" stays a
        # domain.
        schemeless_urls = [
            "example.com:8080",  # host + port
            "example.com/path",  # host + path
            "example.com?q=1",  # host + query
            "example.com#section",  # host + fragment
            # Combined components (URL-spec order: port, path, query, fragment)
            "example.com:8080/path",
            "example.com:8080/path?q=1",
            "example.com:8080/path?q=1#x",
            "sub.example.com:443/api?v=2#x",
            "localhost:3000/foo",
            "192.168.1.1:8080/api",
            "example.com/path?q=1",
            "example.com/path#x",
            "example.com?q=1#x",
        ]
        for url in schemeless_urls:
            result = classifier.classify(url)
            assert (
                result["determined"] is True
            ), f"Failed to classify schemeless URL: {url}"
            assert (
                result["type_pri"] == "url"
            ), f"Wrong classification for schemeless URL: {url}"

    def test_bare_host_is_not_url(self, classifier):
        # A host with no port/path/query/fragment must not match the
        # schemeless URL branch — it should fall through to the domain
        # check (or remain unclassified for trailing-dot etc.).
        result = classifier.classify("example.com")
        assert result["type_pri"] == "domain"


class TestHashClassification:
    def test_valid_hashes(self, classifier):
        valid_hashes = {
            "md5": [
                "d41d8cd98f00b204e9800998ecf8427e",
                "e4d909c290d0fb1ca068ffaddf22cbd0",
                "D41D8CD98F00B204E9800998ECF8427E",  # Uppercase
                "D41d8CD98f00B204e9800998ECF8427e",  # Mixed case
            ],
            "sha1": [
                "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
                "DA39A3EE5E6B4B0D3255BFEF95601890AFD80709",  # Uppercase
            ],
            "sha256": [
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                # Uppercase
                "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
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
            "d41d8cd98f00b204e9800998ecf8427g",  # MD5-length, invalid char
            "da39a3ee5e6b4b0d3255bfef95601890afd8070",  # Too short SHA1
            "da39a3ee5e6b4b0d3255bfef95601890afd80709a",  # Too long SHA1
            # SHA1-length, invalid char ("z" at the end)
            "da39a3ee5e6b4b0d3255bfef95601890afd8070z",
            # Too short SHA256
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85",
            # Too long SHA256
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8555",
            # SHA256-length, invalid char ("z" at the end)
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85z",
            "abcdefghijklmnopqrstuvwxyz123456",  # MD5-length, all non-hex letters
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
            "  192.168.1.1",  # Leading whitespace around an otherwise-valid IP
            "192.168.1.1  ",  # Trailing whitespace
            "\texample.com",  # Leading tab
            "example.com\n",  # Trailing newline
        ]
        for input_value in unclassifiable:
            result = classifier.classify(input_value)
            assert result["determined"] is False
            assert result["type_pri"] is None
            assert result["type_sec"] is None

    def test_non_string_input_raises(self, classifier):
        # classify() accepts str only; non-str inputs surface as TypeError
        # from the underlying re.match call. Pin that contract here.
        for bad_input in [None, 123, 1.5, b"192.168.1.1", ["192.168.1.1"]]:
            with pytest.raises(TypeError):
                classifier.classify(bad_input)


class TestResultContract:
    @pytest.mark.parametrize(
        "query",
        [
            "192.168.1.1",
            "2001:db8::1",
            "d41d8cd98f00b204e9800998ecf8427e",
            "https://example.com/path",
            "example.com",
            "not an IOC",
        ],
    )
    def test_query_field_is_preserved(self, classifier, query):
        # The result dict must echo the input string verbatim, regardless
        # of whether the input was classified.
        result = classifier.classify(query)
        assert result["query"] == query
        assert set(result.keys()) == {"query", "determined", "type_pri", "type_sec"}
