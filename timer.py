#!/usr/bin/env python
#import gobject
import gtk
import appindicator
import string
import math
import sys
import pynotify
import datetime

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

	def setMinutes(self, minutes):
		"""Set timer for x minutes"""

		self.start = datetime.datetime.now()

		self.end = self.start + datetime.timedelta(minutes=minutes)

		self.startTimer()

	def quit(self, w, buf):
		"""Quit the application, usable if running in another shell"""

		sys.exit();

# Program
timer = UbuntuTimer()