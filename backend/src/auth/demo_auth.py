"""
Demo / Auto-Login Bypass for VIABLE Credentials Issuer.

Gated by environment variable DEMO_MODE=true. When enabled, GET /demo
seeds a deterministic demo user (password not exposed), logs them in,
and redirects to the showcased flow.

Designed for investor pitches and the embedded marketing-site iframe.
Production deployments must leave DEMO_MODE unset (or false) so this
blueprint refuses to register and the route 404s.

Author: VIABLE Identity Infrastructure
"""

import os
from logging import getLogger
from flask import Blueprint, redirect, url_for, request, abort, current_app
from flask_login import login_user
from werkzeug.security import generate_password_hash
from ..models import User
from .. import db

logger = getLogger("LOGGER")


DEMO_USERNAME = "demo"
# Password is internal — never displayed; only used so the seed row is
# not malformed if some future code path inspects it.
DEMO_PASSWORD = "viable-demo-do-not-expose"


demo_auth_bp = Blueprint("demo_auth", __name__)


def _demo_mode_enabled() -> bool:
    return os.environ.get("DEMO_MODE", "false").lower() == "true"


def _ensure_demo_user() -> User:
    """Idempotently create the seeded demo user."""
    user = User.query.filter_by(name=DEMO_USERNAME).first()
    if user is None:
        user = User(
            name=DEMO_USERNAME,
            password_hash=generate_password_hash(DEMO_PASSWORD),
        )
        db.session.add(user)
        db.session.commit()
        logger.info("Seeded demo user for DEMO_MODE")
    return user


@demo_auth_bp.route("/demo", methods=["GET"])
def demo_login():
    """
    Frictionless investor-demo entrypoint.

    Logs the visitor in as the seeded demo user and redirects to the
    target (?next=...) or to the issuer home. 404 if DEMO_MODE is off.
    """
    if not _demo_mode_enabled():
        abort(404)

    user = _ensure_demo_user()
    login_user(user, remember=False)
    logger.info("DEMO auto-login granted to %s", request.remote_addr)

    next_url = request.args.get("next")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    target = url_for("home.index")
    if request.args.get("embed"):
        target += "?embed=1"
    return redirect(target)


def register_demo_routes(app):
    """Register the demo blueprint if DEMO_MODE is enabled."""
    if _demo_mode_enabled():
        app.register_blueprint(demo_auth_bp, url_prefix="/")
        logger.info("DEMO_MODE active — /demo auto-login route registered")
    else:
        logger.debug("DEMO_MODE disabled — /demo route NOT registered")
