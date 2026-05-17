class ErrorCode:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    INVITE_EXPIRED = "INVITE_EXPIRED"
    INVITE_REVOKED = "INVITE_REVOKED"
    INVITE_USAGE_LIMIT_REACHED = "INVITE_USAGE_LIMIT_REACHED"
    ITINERARY_ALREADY_EXISTS = "ITINERARY_ALREADY_EXISTS"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(ErrorCode.VALIDATION_ERROR, message, 400)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(ErrorCode.UNAUTHORIZED, message, 401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(ErrorCode.FORBIDDEN, message, 403)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(ErrorCode.NOT_FOUND, message, 404)


class AlreadyExistsError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(ErrorCode.ALREADY_EXISTS, message, 409)


class ConflictError(AppError):
    def __init__(self, message: str, code: str = ErrorCode.CONFLICT) -> None:
        super().__init__(code, message, 409)


class InternalServerError(AppError):
    def __init__(self, message: str = "An unexpected error occurred") -> None:
        super().__init__(ErrorCode.INTERNAL_SERVER_ERROR, message, 500)


class ItineraryAlreadyExistsError(AppError):
    def __init__(self, message: str = "Itinerary already exists for this trip") -> None:
        super().__init__(ErrorCode.ITINERARY_ALREADY_EXISTS, message, 409)


class InviteExpiredError(AppError):
    def __init__(self, message: str = "Invite has expired") -> None:
        super().__init__(ErrorCode.INVITE_EXPIRED, message, 400)


class InviteRevokedError(AppError):
    def __init__(self, message: str = "Invite has been revoked") -> None:
        super().__init__(ErrorCode.INVITE_REVOKED, message, 400)


class InviteUsageLimitReachedError(AppError):
    def __init__(self, message: str = "Invite usage limit has been reached") -> None:
        super().__init__(ErrorCode.INVITE_USAGE_LIMIT_REACHED, message, 400)
