"""Google HTTPS certificate context.

Purpose: provide a stable CA trust bundle for Google HTTPS requests.
Responsibilities: construct SSL contexts from certifi's Mozilla CA bundle.
Dependencies: certifi and Python ssl.
Extension Notes: add mTLS or custom enterprise CA support here if required.
"""

import ssl

import certifi


def google_ssl_context() -> ssl.SSLContext:
    """Return an SSL context using certifi's CA bundle."""
    return ssl.create_default_context(cafile=certifi.where())
