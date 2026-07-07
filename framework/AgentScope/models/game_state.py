from dataclasses import dataclass


@dataclass
class PlayerState:

    name: str

    role: str

    character: str

    alive: bool = True

    can_vote: bool = True

    can_speak: bool = True

    poisoned: bool = False

    protected: bool = False

    checked: bool = False

    use_antidote: bool = False

    use_poison: bool = False

    shoot_available: bool = False