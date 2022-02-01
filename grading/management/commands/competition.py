from django.core.management.base import BaseCommand, CommandError
from grading import models

import os
import json
import time
import datetime


def date(string):
    """Parse a date of the format YYYY-MM-DD."""

    return datetime.datetime.strptime(string, "%Y-%m-%d")


def load(path, loader=json.load):
    """Load a competition file."""

    with open(path, "r") as file:
        c = loader(file)

    competition = models.Competition.current()
    competition._grader = c["grader"]
    competition.save()

    # Clear old stuff
    print("Clearing old competition data...")
    for round in competition.rounds.all():
        for question in round.questions.all():
            question.delete()
        round.delete()

    # Add rounds
    for r in c["rounds"]:
        round = models.Round.new(
            competition, r["ref"], name=r["name"],
            grouping=models.ROUND_GROUPINGS[r["grouping"]])

        # Add questions
        qc = 0
        for i, q in enumerate(r["questions"]):
            models.Question.new(
                round, i+1, label=q["label"],
                type=models.QUESTION_TYPES[q["type"]],
                weight=q.get("weight", 1))
            qc += 1
        print("{0.name}: {1} questions".format(round, qc))


class Command(BaseCommand):
    """Import a competition file into the database."""

    def add_arguments(self, parser):
        """Add arguments to the command line parser."""

        subparsers = parser.add_subparsers(dest="command", metavar="command")
        load_parser = subparsers.add_parser("load", help="load a competition file", cmd=self)
        load_parser.add_argument("file", help="competition JSON summary")

    def handle(self, *args, **kwargs):
        """Handle a call to the command."""

        if kwargs["command"] == "load":
            start = time.time()
            path = kwargs["file"]
            if not os.path.isfile(path):
                raise CommandError("Path is invalid!")
            load(path)
            print("Done in {} seconds!".format(round(time.time() - start, 3)))

        else:
            print("The current competition is {}.".format(models.Competition.current().name))
