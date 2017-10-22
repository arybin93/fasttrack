# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand, CommandError
from notices.clients import FastTrackClient, TourClient

class Command(BaseCommand):
    help = 'Run parser notifier'

    def handle(self, *args, **options):

        # fasttrack client
        ft_client = FastTrackClient()
        users = ft_client.get_users_subscriptions()

        # tour client
        tour_client = TourClient()
        tour_client.send_notification(users)

        self.stdout.write('Done')
