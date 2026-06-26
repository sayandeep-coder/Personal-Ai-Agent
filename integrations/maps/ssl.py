"""Google Maps HTTPS certificate context.

Purpose: provide stable CA trust for Maps HTTPS requests.
Responsibilities: construct SSL contexts from certifi's CA bundle.
Dependencies: certifi and Python ssl.
Extension Notes: add enterprise CA support here if needed.
"""

import ssl

import certifi


def maps_ssl_context() -> ssl.SSLContext:
    """Return an SSL context using certifi's CA bundle."""
    return ssl.create_default_context(cafile=certifi.where())
