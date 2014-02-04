#!/usr/bin/env python
#import gobject
import gtk
import appindicator
import string
import math
import sys
import pynotify
import datetime
import re

class UbuntuTimer:
	"""Takes care of time and GUI for the Ubuntu timer"""

	start = None
	end = None

	# This should be a timediff when paused
	pausedAt = None

	# Menu that should be referenceable
	menu = dict(pause=None, resume=None)

	# Is notifications available
	notificationsAvailable = False

	# GUI
	indicator = None

	def __init__(self):
		"""Setup notifications, and gtk"""

		# Initialize Ubuntu notifications
		self.notificationsAvailable = pynotify.init("ubuntu-timer")

		self.indicator = appindicator.Indicator ("example-simple-client",
							"",
							appindicator.CATEGORY_APPLICATION_STATUS)

		self.indicator.set_status (appindicator.STATUS_ACTIVE)
		self.indicator.set_attention_icon ("indicator-messages-new")
		self.indicator.set_label("00:00")

 		self.createMenu()

 		self.notify("Hello toast")

		# Start gtk
		gtk.main()

	def createMenu(self):
		"""Create the menu"""

		menu = gtk.Menu()

		self.menu['pause'] = gtk.MenuItem("Pause")
		menu.append(self.menu['pause'])
		self.menu['pause'].connect("activate", self.pause, "Pause")
		#self.menu['pause'].show()

		self.menu['resume'] = gtk.MenuItem("Resume")
		menu.append(self.menu['resume'])
		self.menu['resume'].connect("activate", self.resume, "Resume")
		#self.menu['resume'].show()

		# Custom time
		inputItem = gtk.MenuItem("Custom")
		menu.append(inputItem)
		inputItem.connect("activate", self.promptCustomTimer, "Prompt")
		inputItem.show()

		# Create labels for nice timings
		for minutes in [60, 45, 30, 20, 15, 10, 5, 3]:
			minutesItem = gtk.MenuItem("{minutes} minutes".format(minutes=minutes))
			menu.append(minutesItem)
			minutesItem.connect("activate", lambda w, buf, minutes=minutes: self.setMinutes(minutes), "")
			minutesItem.show()

		# Quit 
		quitItem = gtk.MenuItem("Quit")
		menu.append(quitItem)
		quitItem.connect("activate", self.quit, "Resume")
		quitItem.show()

		self.indicator.set_menu(menu)

	def promptCustomTimer(self, w, buf):

		prompt = gtk.MessageDialog(
			type=gtk.MESSAGE_QUESTION,
			buttons=gtk.BUTTONS_OK)
		prompt.set_markup("Set custom time")
		prompt.format_secondary_markup("Examples: \n<i>43 min\n2h 3min\n30 minutes\n8m\n38 sec</i>")

		entry = gtk.Entry()
		entry.set_activates_default(True)
		entry.connect("activate", lambda str: prompt.emit("response", gtk.RESPONSE_OK))

		prompt.vbox.add(entry)
		prompt.show_all()

		if prompt.run() != gtk.RESPONSE_OK:
			rval = ""
			return False
		else:
			rval = entry.get_text()

		prompt.destroy()

		# Get values from string
		h = re.search('(\d+)\s?(?:h|hour|hour)s?', rval)
		m = re.search('(\d+)\s?(?:m|min|minute)s?', rval)
		s = re.search('(\d+)\s?(?:s|sec|second)s?', rval)

		hours = 0
		minutes = 0
		seconds = 0

		# Hours
		if h is not None:
			hours = int(h.group(1))

		# Minutes
		if m is not None:
			minutes = int(m.group(1))

		if s is not None:
			seconds = int(s.group(1))

		self.setTimer(hours=hours, minutes=minutes, seconds=seconds)

	def startTimer(self):
		"""Start the timer and set menu state to running"""

		# Callout with a notification
		self.notify("Timer started")

		# Call every second
 		gtk.timeout_add(1000, self.update)

 		# Add pause button
 		self.menu['pause'].show()

 		# Disable pause
 		self.pausedAt = None

	def pause(self, w, buf):
		"""Pause the timer and show the resume button"""

		# Save timediff now
		self.pausedAt = self.end - datetime.datetime.now()

		self.menu['pause'].hide()
		self.menu['resume'].show()
		
	def resume(self, w=None, buf=None):
		"""Resume the timer and show the pause button"""

		# Add pausedAt timediff and unset
		self.end = datetime.datetime.now() + self.pausedAt
		self.pausedAt = None

		self.menu['resume'].hide()
		self.menu['pause'].show()

		self.startTimer()

	def update(self):
		"""Update the timer gtk label"""

		# Check that end and start time exists
		if self.end is None or self.start is None:
			return

		# Check if paused
		if self.pausedAt is not None:
			return False

		# A timediff
		diff = self.end - datetime.datetime.now()

		# Update label
		self.indicator.set_label(self.formatDate(datetime.datetime.now(), self.end))
	
		# If time is up
		if diff.seconds <= 0:
			self.notify("Time is up!")
			return False

		return True

	def formatDate(self, start, end):
		"""Format the timer"""

		# A timediff
		diff = end - start

		hours, reminder = divmod(diff.seconds, 3600)
		minutes, seconds = divmod(reminder, 60)

		if hours > 0:
			return "{hour:02d}:{minute:02d}:{second:02d}".format(hour=int(hours), minute=int(minutes), second=int(seconds))
		else:
			return "{minute:02d}:{second:02d}".format(minute=int(minutes), second=int(seconds))

	def notify(self, message):
		"""Show a ubuntu notification"""

		# Is notifications available?
		if self.notificationsAvailable is False:
			return False

		notification = pynotify.Notification(message, None)
		notification.set_timeout(1000)
		notification.show()

	def setTimer(self, hours=0, minutes=0, seconds=0):
		"""Set timer"""

		self.start = datetime.datetime.now()

		self.end = self.start + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

		self.startTimer()

	def setMinutes(self, minutes):
		"""Set timer for x minutes"""

		self.setTimer(minutes=minutes)

	def quit(self, w, buf):
		"""Quit the application, usable if running in another shell"""

		sys.exit();

# Program
timer = UbuntuTimer()