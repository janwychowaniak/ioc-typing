"""Property-based tests for :class:`IOCClassifier`.

The category-style tests in ``test_classifier.py`` enumerate hand-picked
positive and negative examples. These tests state the contract as
properties that must hold for *any* well-formed input of a given shape,
and let Hypothesis generate the inputs.
"""

import string
from ipaddress import IPv4Address, IPv6Address

from hypothesis import given
from hypothesis import strategies as st

from ioc_typing import IOCClassifier

_classifier = IOCClassifier()

_HEX_MIXED = string.hexdigits  # "0123456789abcdefABCDEF"


@given(addr=st.ip_addresses(v=4))
def test_any_ipv4_classifies_as_v4(addr: IPv4Address) -> None:
    result = _classifier.classify(str(addr))
    assert result["determined"] is True
    assert result["type_pri"] == "ip"
    assert result["type_sec"] == "v4"


@given(addr=st.ip_addresses(v=6))
def test_any_ipv6_classifies_as_v6(addr: IPv6Address) -> None:
    result = _classifier.classify(str(addr))
    assert result["determined"] is True
    assert result["type_pri"] == "ip"
    assert result["type_sec"] == "v6"


@given(s=st.text(alphabet=_HEX_MIXED, min_size=32, max_size=32))
def test_any_32_hex_string_classifies_as_md5(s: str) -> None:
    result = _classifier.classify(s)
    assert result["determined"] is True
    assert result["type_pri"] == "hash"
    assert result["type_sec"] == "md5"


@given(s=st.text(alphabet=_HEX_MIXED, min_size=40, max_size=40))
def test_any_40_hex_string_classifies_as_sha1(s: str) -> None:
    result = _classifier.classify(s)
    assert result["determined"] is True
    assert result["type_pri"] == "hash"
    assert result["type_sec"] == "sha1"


@given(s=st.text(alphabet=_HEX_MIXED, min_size=64, max_size=64))
def test_any_64_hex_string_classifies_as_sha256(s: str) -> None:
    result = _classifier.classify(s)
    assert result["determined"] is True
    assert result["type_pri"] == "hash"
    assert result["type_sec"] == "sha256"


@given(s=st.text())
def test_query_field_always_echoes_input(s: str) -> None:
    # Regardless of classification outcome, the result must echo the
    # input verbatim and expose exactly the four documented keys.
    result = _classifier.classify(s)
    assert result["query"] == s
    assert set(result.keys()) == {"query", "determined", "type_pri", "type_sec"}
