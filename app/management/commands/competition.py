from django.core.management.base import BaseCommand, CommandError
from app import models


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
                print("{0.name:<20} {0.nick:<10} {1}".format(competition, "*" if competition.active else ""))
