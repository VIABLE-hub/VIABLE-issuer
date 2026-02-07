from ..models import VC_Offer
from uuid import uuid4
from .. import db
from src.utils import get_current_server_url
import random
from logging import getLogger
from datetime import datetime, timedelta, timezone

logger = getLogger(__name__)


def get_offer_url(credential_data, validity_seconds=120):
    # Generate unique identifiers
    uuid = str(uuid4())
    issuer_state = uuid
    pre_authorized_code = generate_nonce(32)

    # Calculate expiration
    expires_at = None
    if validity_seconds and int(validity_seconds) > 0:
        # If validity_seconds is explicitly set to a positive number
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(validity_seconds))
    elif validity_seconds == 0 or validity_seconds == "0":
        # If 0, it means indefinite (None)
        expires_at = None
    else:
        # Default fallback if somehow None passed but not intended as indefinite (though default arg handles this)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=120)

    # Save the offer to the database
    new_offer = VC_Offer(
        uuid=uuid,
        issuer_state=issuer_state,
        pre_authorized_code=pre_authorized_code,
        credential_data=credential_data,
        expires_at=expires_at
    )
    logger.debug(f"Saving offer to the database: {new_offer.credential_data}")
    db.session.add(new_offer)
    db.session.commit()

    # Get the server URL (will use ngrok if configured)
    server_url = get_current_server_url()
    logger.info(f"Using server URL for credential offer: {server_url}")

    # Generate the credential offer URI
    credential_offer_uri = f"openid-credential-offer://?credential_offer_uri={server_url}/credential-offer/{uuid}"
    return credential_offer_uri, uuid, expires_at


def generate_nonce(length):
    return "".join(
        random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(length)
    )
