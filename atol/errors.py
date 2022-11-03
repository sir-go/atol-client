# coding=utf8


class AtolException(Exception):
    pass


# web
class ErrorWeb(AtolException):
    pass


class ErrorRequest(ErrorWeb):
    pass


class ErrorResponse(ErrorWeb):
    pass


# server
class TaskNotFound(ErrorRequest):
    pass


class BadRequest(ErrorRequest):
    pass


class TaskIdCollision(ErrorRequest):
    pass


class TaskTimeout(ErrorResponse):
    pass


class TaskError(ErrorResponse):
    pass
