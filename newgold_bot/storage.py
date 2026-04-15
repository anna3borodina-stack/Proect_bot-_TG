# Согласие хранится в памяти процесса (после перезапуска бота сбрасывается).

_consented: set[int] = set()


def set_consent(user_id: int, accepted: bool) -> None:
    if accepted:
        _consented.add(user_id)
    else:
        _consented.discard(user_id)


def has_consent(user_id: int) -> bool:
    return user_id in _consented
