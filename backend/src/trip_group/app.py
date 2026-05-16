import json


def lambda_handler(event, context):
    return {
        "statusCode": 501,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "success": False,
            "data": None,
            "error": {
                "code": "NOT_IMPLEMENTED",
                "message": "TripGroupFunction is not yet implemented.",
            },
            "request_id": event.get("requestContext", {}).get("requestId", "unknown"),
        }),
    }
