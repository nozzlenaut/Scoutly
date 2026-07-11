import hashlib
import os

from fastapi import APIRouter, HTTPException, Query, Response, status

router = APIRouter(prefix="/ebay", tags=["eBay"])


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Missing required environment variable: {name}",
        )
    return value


@router.get("/notifications")
def verify_ebay_notification_endpoint(
    challenge_code: str = Query(..., min_length=1),
) -> dict[str, str]:
    """Respond to eBay's Marketplace Account Deletion challenge request.

    eBay verifies ownership of the notification endpoint by sending a
    challenge_code query parameter. The response must be the SHA-256 hash of:

    challengeCode + verificationToken + endpointUrl
    """

    verification_token = _required_env("EBAY_NOTIFICATION_VERIFICATION_TOKEN")
    endpoint_url = _required_env("EBAY_NOTIFICATION_ENDPOINT_URL")
    challenge_response = hashlib.sha256(
        f"{challenge_code}{verification_token}{endpoint_url}".encode("utf-8")
    ).hexdigest()
    return {"challengeResponse": challenge_response}


@router.post("/notifications", status_code=status.HTTP_204_NO_CONTENT)
def receive_ebay_account_deletion_notification() -> Response:
    """Acknowledge eBay Marketplace Account Deletion notifications.

    Scoutly does not currently store eBay user data, so there is no deletion
    workflow to perform yet. We still acknowledge the notification so eBay does
    not keep retrying delivery.
    """

    return Response(status_code=status.HTTP_204_NO_CONTENT)
