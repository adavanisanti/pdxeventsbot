from django.shortcuts import render

# Create your views here.
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventSerializer, VenueSerializer
from .models import Event, Venue
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

import datetime
from pytz import timezone
import pytz

class EventAPIView(generics.ListCreateAPIView):
	queryset = Event.objects.all()
	serializer_class = EventSerializer
	filter_backends = (DjangoFilterBackend,)
	filter_fields = ('feed_id',)


class VenueAPIView(generics.ListCreateAPIView):
	queryset = Venue.objects.all()
	serializer_class = VenueSerializer
	filter_backends = (DjangoFilterBackend,)
	filter_fields = ('venueurl','venueid')

class EventRetrieveAPIView(generics.RetrieveUpdateAPIView):
	queryset = Event.objects.all()
	serializer_class = EventSerializer


class VenueRetrieveAPIView(generics.RetrieveUpdateAPIView):
	queryset = Venue.objects.all()
	serializer_class = VenueSerializer

class EventListAPIView(APIView):


	def post(self,request,format=None):

		print request.data

		try:
			self.action = request.data['result']['action']
			self.parameters = request.data['result']['parameters']
		except:
			self.action = 'show.schedule'
			self.parameters = {}

		return Response(self.get_slack_message(),status=status.HTTP_200_OK)


	def get_slack_message(self):

		slack_message = self.create_slack_message()
		# slack_message = {}
		
		slack_final_data = {
			"speech" : "Today is a good day",
			"dispayText" : "Today is a good day",
			"data": {"slack": slack_message},
			"source" : "apiai-eventsbot1-webhook-sample",
		}

		return slack_final_data

	def create_slack_message(self):

		if self.action == 'get.events.date':
			slack_message = self.create_slack_message_for_get_events_date()
		elif self.action == 'get.events.date.time.range':
			slack_message = self.create_slack_message_for_get_events_date_time_range()
		else:
			slack_message = {}


		return slack_message

	
	def get_slack_message_fields(self,events,date):

		date_fmt = '%b %d, %Y'
		fmt = '%b %d, %Y %-I:%M %p'
		fmt1 = '%-I:%M %p'

		fields = []
		for event in events:
			item = {}
			event_title = event.title

			item['title'] = event_title
			start_date_time = event.start_date.astimezone(timezone('US/Pacific'))
			end_date_time   = event.end_date.astimezone(timezone('US/Pacific'))

			if start_date_time.date() == end_date_time.date():
				end_fmt = fmt1
			else:
				end_fmt = fmt
			
			start_time = start_date_time.strftime(fmt)
			end_time = end_date_time.strftime(end_fmt)
			item_value = start_time + ' to ' + end_time

			# if event.description:
				# item_value += '\n' + event.description

			if event.venue:
				item_value += '\nVenue\n'+'<'+event.venue.mapurl+'|'+event.venue.name+'>'

			if event.event_ics:
				item_value += '\n\n<'+event.event_ics + '|Add to calendar>'
			
			item['value'] =  item_value
			item['short'] = 'false'
			fields.append(item)

		if not events:
			item = {}
			item['title'] = 'No events on this date to the best of my knowledge!'
			item['value'] = '<http://www.calagator.org|Check Calgator if you don\'t beleive me!>'
			item['short'] = 'false'
			fields.append(item)


		
		slack_message = {
			"text" : "Below is the schedule for " + date.strftime(date_fmt),
			"attachments" : [
				{
					"title" : "<http://www.calagator.org|Calgator>",
					"title_link" : "www.calgator.org",
					"color" : "#36a64f",
					"fields" : fields,
				}
			],
		}

		return slack_message

	def get_slack_message_fields_formatted(self,events,date):

		date_fmt = '%b %d, %Y'
		fmt = '%b %d, %Y %-I:%M %p'
		fmt1 = '%-I:%M %p'

		fields = []
		attachments = []

		for event in events:
			item = {}
			event_title = event.title

			item['title'] = event_title
			item["color"] = "#36a64f",
			attachments.append(item)
			item["fields"] = []

			# Time
			start_date_time = event.start_date.astimezone(timezone('US/Pacific'))
			end_date_time   = event.end_date.astimezone(timezone('US/Pacific'))

			if start_date_time.date() == end_date_time.date():
				end_fmt = fmt1
			else:
				end_fmt = fmt
			
			start_time = start_date_time.strftime(fmt)
			end_time = end_date_time.strftime(end_fmt)
			
			if start_date_time == end_date_time:
				item_value = start_time
			else:
				item_value = start_time + ' to ' + end_time

			time_field = {}
			time_field['title'] = 'Time'
			time_field['value'] = item_value
			time_field['short'] = 'true'

			item["fields"].append(time_field)

			# Venue
			if event.venue:
				venue_field = {}
				venue_field['title'] = 'Venue'
				venue_field['value'] = '<'+event.venue.mapurl+'|'+event.venue.name+'>'
				venue_field['short'] = 'true'
				item["fields"].append(venue_field)


			# Add to calendar
			if event.event_ics:
				calendar_field = {}
				calendar_field['value'] = '<'+event.event_ics + '|Add to calendar>'
				calendar_field['short'] = 'false'
				item["fields"].append(calendar_field)

		if not events:
			item = {}
			item['title'] = 'No events on this date to the best of my knowledge!'
			item['text'] = '<http://www.calagator.org|Check Calagator or Meetup if you don\'t beleive me!>'
			item['color'] = '#36a64f'
			attachments.append(item)

		
		
		slack_message = {
			"text" : "Below is the schedule for " + date.strftime(date_fmt),
			"attachments" : attachments,
		}

		return slack_message

	def create_slack_message_for_get_events_date(self):
		events = []
		date = datetime.datetime.now()

		try:
			input_date = self.parameters['date']
			date = datetime.datetime.strptime(input_date, "%Y-%m-%d")
			events = Event.objects.filter(start_date__date=date).order_by('start_date')
		except: 
			pass

		return self.get_slack_message_fields_formatted(events,date)
	
	def create_slack_message_for_get_events_date_time_range(self):

		events = []
		date = datetime.datetime.now()

		try:
			input_date = self.parameters['date']
			time_period = self.parameters['time-period']
			date = datetime.datetime.strptime(input_date, "%Y-%m-%d")
			print 'Came in here'
			print time_period
			if time_period:
				time_range = time_period.split("/")
				start_time = input_date+"-"+time_range[0]
				end_time   = input_date+"-"+time_range[1]

				start_date_time = datetime.datetime.strptime(start_time, "%Y-%m-%d-%H:%M:%S")
				end_date_time   = datetime.datetime.strptime(end_time, "%Y-%m-%d-%H:%M:%S")
				events = Event.objects.filter(start_date__range=(start_date_time,end_date_time)).order_by('start_date')
		except:
			pass
			
		return self.get_slack_message_fields_formatted(events,date)

