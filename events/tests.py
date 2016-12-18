import urllib
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from .models import Event, Venue
from django.utils import timezone
import datetime
import json

# Create your tests here.
class EventAPITests(APITestCase):

	def test_events_webhook_get_events_date(self):
		time_input = timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone())
		event = Event.objects.create(title='Event1',description='Event Description',start_date=time_input,end_date=time_input)

		webhook_url = reverse('events_webhook_api')
		post_data = {}
		post_data['result'] = {}
		post_data['result']['action'] = "get.events.date"
		post_data['result']['parameters'] = {'date':"2016-12-17"}
		post_data_json = json.dumps(post_data)
		response = self.client.post(webhook_url,data=post_data_json,HTTP_EVENT='Event1',content_type='application/json')
		print response
		
	def test_events_webhook_get_events_date_time_range(self):
		time_input = timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone())
		event = Event.objects.create(title='Event1',description='Event Description',start_date=time_input,end_date=time_input)

		webhook_url = reverse('events_webhook_api')
		post_data = {}
		post_data['result'] = {}
		post_data['result']['action'] = "get.events.date.time.range"
		post_data['result']['parameters'] = {'date':"2016-12-17",'time-period':'08:00:00/23:00:00'}
		post_data_json = json.dumps(post_data)
		response = self.client.post(webhook_url,data=post_data_json,HTTP_EVENT='Event1',content_type='application/json')
		print response
	