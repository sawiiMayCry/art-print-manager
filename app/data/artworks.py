import json
from pathlib import Path

from app.models.artwork import Artwork


DEMO_ARTWORKS_PATH = (
    Path(__file__).resolve().parents[2]
    / "demo_data"
    / "artworks.example.json"
)


ARTWORKS: list[Artwork] = []


def load_artworks() -> list[Artwork]:
    with DEMO_ARTWORKS_PATH.open(encoding="utf-8") as file:
        data = json.load(file)

    return [Artwork.model_validate(item) for item in data]


def initialize_demo_artworks() -> None:
    ARTWORKS.clear()
    ARTWORKS.extend(load_artworks())
