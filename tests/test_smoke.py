"""Smoke tests — verify public API is importable and basic types are correct."""
import pytest
from yadacoin_agent_auth import (
    AuthError,
    AuthResult,
    AgentAuthValidator,
    AgentAuthMixin,
    YadaCoinRestKelProvider,
    YadaCoinNodeKelProvider,
    KelProvider,
)


def test_auth_error_is_exception():
    err = AuthError("test", http_status=401)
    assert isinstance(err, Exception)
    assert err.http_status == 401
    assert str(err) == "test"


def test_auth_error_default_status():
    err = AuthError("bad request")
    assert err.http_status == 401


def test_auth_result_fields():
    result = AuthResult(
        address="1AbcDef",
        pub_key_bytes=bytes(33),
        kel=[],
        scope={"destination": "NYC"},
    )
    assert result.address == "1AbcDef"
    assert result.pub_key_bytes == bytes(33)
    assert result.scope["destination"] == "NYC"
    assert result.kel_txid is None


def test_agent_auth_validator_instantiation():
    provider = YadaCoinRestKelProvider("https://yadacoin.io")
    validator = AgentAuthValidator(
        challenge_secret=b"test-secret",
        kel_provider=provider,
    )
    assert validator is not None


def test_make_challenge_is_deterministic_per_key():
    provider = YadaCoinRestKelProvider("https://yadacoin.io")
    validator = AgentAuthValidator(
        challenge_secret=b"test-secret",
        kel_provider=provider,
    )
    pub = "02" + "a1" * 32
    c1 = validator.make_challenge(pub)
    c2 = validator.make_challenge(pub)
    assert c1["challenge"] == c2["challenge"]
    assert "expires_in" in c1


def test_make_challenge_differs_across_keys():
    provider = YadaCoinRestKelProvider("https://yadacoin.io")
    validator = AgentAuthValidator(
        challenge_secret=b"test-secret",
        kel_provider=provider,
    )
    pub_a = "02" + "a1" * 32
    pub_b = "02" + "b2" * 32
    assert validator.make_challenge(pub_a)["challenge"] != validator.make_challenge(pub_b)["challenge"]


def test_rest_provider_base_url_stored():
    provider = YadaCoinRestKelProvider("https://yadacoin.io")
    assert "yadacoin.io" in provider.base_url


def test_kel_provider_protocol_satisfied():
    """YadaCoinRestKelProvider must satisfy the KelProvider Protocol."""
    provider = YadaCoinRestKelProvider("https://yadacoin.io")
    assert hasattr(provider, "build_from_public_key")
