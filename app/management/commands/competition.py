from django.core.management.base import BaseCommand, CommandError
from django.db.models.query import Q
from app import models

import os
import json
import time


def load(path, loader=json.load):
    """Load a competition file."""

    with open(path, "r") as file:
        c = loader(file)

    competition = models.Competition(c["id"], c["name"], c["year"])
    competition.save()
    for r in c["rounds"]:
        round = models.Round(competition, r["name"], r["grouping"])
        round.save()
        qc = 0
        for q in r["questions"]:
            question = models.Question(round, q["label"], q["type"])
            question.save()
            qc += 1
        print("{0.name}: {1} questions".format(round, qc))


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
            for active in models.Competition.objects.filter(active=True):
                active.active = False
                active.save()
            selected.active = True
            selected.save()
