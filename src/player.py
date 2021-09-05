import dataclasses


@dataclasses.dataclass
class Player:
    discord_id: int
    rating: float

    def __hash__(self):
        return hash(self.discord_id)