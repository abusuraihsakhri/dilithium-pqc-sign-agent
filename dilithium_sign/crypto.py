"""ML-DSA signing primitives backed by pqcrypto 1.0.0.

This adapter delegates the cryptographic operations to an external library;
the legacy numeric audit engines are not cryptographic implementations.
"""
from importlib import import_module

ALGORITHMS = ("ml-dsa-44", "ml-dsa-65", "ml-dsa-87")


def _backend(algorithm: str):
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unsupported ML-DSA algorithm: {algorithm}")
    try:
        return import_module("pqcrypto.sign." + algorithm.replace("-", "_"))
    except ImportError as exc:
        raise RuntimeError("ML-DSA support requires pqcrypto==1.0.0") from exc


def _context(context: bytes) -> bytes:
    if not isinstance(context, bytes) or len(context) > 255:
        raise ValueError("Context must contain at most 255 bytes")
    return context


def generate_keypair(algorithm: str = "ml-dsa-44") -> tuple[bytes, bytes]:
    """Return (public_key, secret_key) using a system-randomized backend."""
    return _backend(algorithm).keygen()


def sign_message(secret_key: bytes, message: bytes, algorithm: str = "ml-dsa-44", context: bytes = b"") -> bytes:
    """Sign binary message bytes. The caller must protect the private key."""
    _context(context)
    if not isinstance(message, bytes) or not isinstance(secret_key, bytes):
        raise TypeError("Message and secret key must be bytes")
    return _backend(algorithm).sign(secret_key, message, context)


def verify_message(public_key: bytes, message: bytes, signature: bytes, algorithm: str = "ml-dsa-44", context: bytes = b"") -> bool:
    """Reject invalid keys, contexts and signatures without accepting a mismatch."""
    _context(context)
    if not all(isinstance(x, bytes) for x in (public_key, message, signature)):
        return False
    backend = _backend(algorithm)
    try:
        return backend.verify(public_key, message, signature, context) is not False
    except (ValueError, TypeError):
        return False
    except Exception as exc:
        # pqcrypto raises its own InvalidSignatureError on invalid signatures.
        # Treat an invalid signature as False, but do not mask arbitrary bugs.
        if type(exc).__name__ == "InvalidSignatureError":
            return False
        raise
