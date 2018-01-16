from django.test import TestCase
from django.shortcuts import reverse
from django.utils import timezone

from . import models


class SiteEmptyTests(TestCase):
    """Test the site with no active competition."""

    def test_index_page(self):
        self.client.get(reverse("home:index"))

    def test_rules_page(self):
        self.client.get(reverse("home:rules"))

    def test_info_page(self):
        self.client.get(reverse("home:info"))

    def test_about_page(self):
        self.client.get(reverse("home:about"))

    def test_archive_page(self):
        self.client.get(reverse("home:archive"))

    def test_topics_page(self):
        self.client.get(reverse("home:topics"))


class SiteTests(SiteEmptyTests):
    """Test the site when there is a competition object."""

    @classmethod
    def setUpTestData(cls):
        """Create a competition object for the site."""

        earlier = timezone.now() - timezone.timedelta(days=28)
        later = timezone.now() + timezone.timedelta(days=28)
        models.Competition.objects.create(
            name="MBMT Test",
            date=later,
            active=True,
            date_registration_start=earlier,
            date_registration_end=later,
            date_team_edit_end=later,
            date_shirt_order_end=later)
