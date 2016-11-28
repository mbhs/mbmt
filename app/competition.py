import os
import yaml
import datetime

from app import models


ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
COMPETITIONS = os.path.join(ROOT, "competitions")
TYPES = {"correct": "co", "estimation": "es"}


def load(path, deserializer=yaml.load):
    """Load a competition from a file with a specific deserializer."""

    if not os.path.isabs(path):
        path = os.path.join(COMPETITIONS, path)
    with open(path, "rb") as file:
        tree = deserializer(file)

    competition = models.Competition(tree["name"], datetime.datetime.now().year)
    for r in tree["rounds"]:
        round = models.Round(competition, r["name"], r["individual"])
        for q in tree["questions"]:
            question = models.Question(round, q["label"], TYPES[q["type"]])
            question.save()
        round.save()
    competition.save()
