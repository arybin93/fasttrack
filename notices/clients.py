# -*- coding: UTF-8 -*-
import requests
from django.conf import settings
import logging

logger = logging.getLogger('command')


class FastTrackClient:
    """ Chat bot client """
    request_chats = 'https://dashboard.fstrk.io/api/partners/chats/?api_key={bot_key}' \
                    '&cookie_dict__anextour_filter__isnull=False'

    request_subscription = 'https://dashboard.fstrk.io/api/partners/chats/{uuid}/variables/'

    def __init__(self):
        logger.info('create ft client object')

    def get_chats(self):
        """ Get list UUID of chats """

        url = self.request_chats.format(bot_key=settings.BOT_KEY)

        try:
            r = requests.get(url)
        except requests.exceptions.Timeout:
            logger.error('timeout')
            return []
        else:
            if r.status_code == 200:
                answer = r.json()
                try:
                    return answer['results']
                except AttributeError:
                    return []
            else:
                logger.error(r.status_code)
                return []

    def get_users_subscriptions(self):
        """ Get users subscriptions by uuid """
        users_settings = []

        # get uuid for users:
        uuid_list = self.get_chats()

        # get users settings
        for obj in uuid_list:
            result = self.get_user(obj['uuid'])
            if result:
                obj = {
                    'uuid': obj['uuid'],
                    'subscription': result
                }
                users_settings.append(obj)

        return users_settings

    def get_user(self, uuid):
        # get url
        url = self.request_subscription.format(uuid=uuid)

        try:
            r = requests.get(url)
        except requests.exceptions.Timeout:
            logger.error('timeout')
            return {}
        else:
            if r.status_code == 200:
                answer = r.json()
                try:
                    answer['anextour_filter']
                except AttributeError:
                    return {}
                else:
                    if answer['anextour_filter']:
                        return answer
                    else:
                        return {}
            else:
                logger.error(r.status_code)
                return {}


class TourClient:
    """ Tour operator client """

    request_tour = 'http://searchtour.anextour.com:9999/lct/tour.php?api={tour_key}'

    def __init__(self):
        print('create anex client object')

    def send_notification(self, users):
        """ Send notification about tour """

        # get tour for chats
        for user in users:
            try:
                params = user['subscription']
                uuid = user['uuid']
            except AttributeError:
                pass
            else:
                tours = self.__tours__(params)

                # send tours to chat
                if settings.DEBUG:
                    # only logging
                    logger.info(uuid + ' ' + str(tours))
                else:
                    # send tours
                    pass

    def __tours__(self, params):
        """ Get tour by subscription params """
        url = self.request_tour.format(tour_key=settings.TOUR_KEY)
        payload = {}

        # get stars
        try:
            stars = params['anextour_filter']['stars']
        except AttributeError:
            stars = None

        # get dates
        try:
            dates = params['anextour_filter']['date']['beginDate']
        except AttributeError:
            begin_date = None
        else:
            year = dates['year']
            month = dates['month']
            day = dates['day']
            begin_date = '{year}-{month}-{day}'.format(year=year, month=month, day=day)

        # get dates
        try:
            dates = params['anextour_filter']['date']['endDate']
        except AttributeError:
            begin_end = None
        else:
            year = dates['year']
            month = dates['month']
            day = dates['day']
            begin_end = '{year}-{month}-{day}'.format(year=year, month=month, day=day)

        if stars:
            payload['STAR'] = stars

        if begin_date:
            payload['CHECKIN_BEG'] = begin_date

        if begin_end:
            payload['CHECKIND_END'] = begin_date

        try:
            r = requests.get(url, params=payload)
        except requests.exceptions.Timeout:
            logger.error('timeout')
            return {}
        else:
            if r.status_code == 200:
                answer = r.json()
                return answer
            else:
                logger.error(r.status_code)
                return {}