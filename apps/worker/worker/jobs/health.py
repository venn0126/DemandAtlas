import dramatiq


@dramatiq.actor
def ping() -> str:
    return "pong"
