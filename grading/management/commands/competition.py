from django.core.management.base import BaseCommand, CommandError
from django.db.models.query import Q
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

    # Create the competition and save.
    competition = models.Competition(
        id=c["id"], name=c["name"],
        date=date(c["dates"]["competition"]),
        date_registration_start=date(c["dates"]["registration_start"]),
        date_registration_end=date(c["dates"]["registration_end"]),
        date_team_edit_end=date(c["dates"]["team_edit_end"]),
        date_shirt_order_end=date(c["dates"]["shirt_order_end"]))
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

    # Activate the competition if none are activated
    if not models.Competition.current():
        competition.active = True
        competition.save()


class Command(BaseCommand):
    """Import a competition file into the database."""

    def add_arguments(self, parser):
        """Add arguments to the command line parser."""

        subparsers = parser.add_subparsers(dest="command", metavar="command")
        load_parser = subparsers.add_parser("load", help="load a competition file", cmd=self)
        load_parser.add_argument("file", help="competition JSON summary")
        activate_parser = subparsers.add_parser("activate", help="activate a competition", cmd=self)
        activate_parser.add_argument("id", help="competition name, nickname, or index")
        subparsers.add_parser("list", help="list loaded competitions", cmd=self)
        delete_parser = subparsers.add_parser("delete", help="delete a competition", cmd=self)
        delete_parser.add_argument("id", help="competition name, nickname, or index")

    def handle(self, *args, **kwargs):
        """Handle a call to the command."""

        if kwargs["command"] == "list":
            for competition in models.Competition.objects.all():
                print("  {1:<2} {0.id:<12} {0.name:<20}".format(competition, "*" if competition.active else ""))

        if kwargs["command"] == "delete":
            models.Competition.current().delete()

        if kwargs["command"] == "load":
            start = time.time()
            path = kwargs["file"]
            if not os.path.isfile(path):
                raise CommandError("Path is invalid!")
            load(path)
            print("Done in {} seconds!".format(round(time.time() - start, 3)))

        if kwargs["command"] == "activate":
            search = kwargs["id"]
            selected = models.Competition.objects.filter(Q(id=search) | Q(name=search)).first()
            selected.activate()
