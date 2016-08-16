# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand


class Command(BaseCommand):
  # args = '<target_id target_id ...>'
  help = u'django command test'

  def handle(self, *args, **options):
    print("django test")