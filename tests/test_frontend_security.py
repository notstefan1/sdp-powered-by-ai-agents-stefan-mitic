"""Tests for frontend security - XSS prevention in static/index.html"""

import re
from pathlib import Path

_HTML = (Path(__file__).parent.parent / "static" / "index.html").read_text()


def test_fe_security_no_username_interpolated_in_onclick():
    # GIVEN - Story: XSS prevention
    # esc() only escapes HTML entities (&, <, >) but NOT single quotes.
    # Interpolating esc(username) into onclick='...' allows attribute breakout
    # with a username like: '); alert(1); //
    # The fix is to pass data via data-* attributes, not inline JS strings.

    # THEN - no template literal interpolating a username into an onclick handler
    # Pattern: onclick="...'${esc(u.username)}'"  (inside a JS template literal)
    unsafe = re.findall(r"onclick=\\?\"[^\"]*\$\{esc\([^)]*username[^)]*\)\}", _HTML)
    assert (
        unsafe == []
    ), f"XSS risk: username interpolated into onclick attribute: {unsafe}"
