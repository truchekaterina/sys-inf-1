"""Приём карточки включает или выключает сценарий «реестр молчит».

Это служебный переключатель стенда, не экран сотрудника.
После перезапуска приём снова включён.
"""


class Stand:
    def __init__(self) -> None:
        self.accept = True

    def reset(self) -> None:
        self.accept = True

    def view(self) -> dict:
        return {"accept": self.accept}


STAND = Stand()
