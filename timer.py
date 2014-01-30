#!/usr/bin/env python
import gobject
import gtk
import appindicator
import time as timelib
import string
import math
import sys

SEC = 1
MIN = 60 * SEC
HOUR = 60 * MIN

def menuitem_response(w, buf):
	print(w, buf)

if __name__ == "__main__":

	# Time in seconds
	endTime = 0
	pauseTime = None
	paused = False
	pauseMenuItem = None

	ind = appindicator.Indicator ("example-simple-client",
							"",
							appindicator.CATEGORY_APPLICATION_STATUS)
	ind.set_status (appindicator.STATUS_ACTIVE)
	ind.set_attention_icon ("indicator-messages-new")

	#help(ind.set_label("Hej"))
	ind.set_label("00:00")

	def update():
		global endTime, HOUR, MIN, SEC
		global pauseTime

		time = endTime - timelib.time()

		if pauseTime is not None:
			return False

		hours = 0
		minutes = 0
		seconds = 0

		if time >  HOUR-1:
			hours = time % HOUR

		if time - hours * HOUR > MIN-1:
			minutes = math.floor((time - hours * HOUR) / MIN);

		if time - hours * HOUR - minutes * MIN > 0:
			seconds = math.floor(time - hours * HOUR - minutes * MIN / SEC)

		# Format string
		if hours > 0:
			ind.set_label("{hour:02d}:{minute:02d}:{second:02d}".format(hour=int(hours), minute=int(minutes), second=int(seconds)))
		else:
			ind.set_label("{minute:02d}:{second:02d}".format(minute=int(minutes), second=int(seconds)))

		if time >= 0:
			return True

		return False

	def start():
		global pauseMenuItem, endTime, pauseTime

		time = endTime - timelib.time()

		pauseTime = None

		if time <= 0:
			return False

		pauseMenuItem.set_label("Pause")

		# Call every second
		gtk.timeout_add(1000, update)

		pauseMenuItem.show()

	def pause(w, buf):
		global pauseTime, pauseMenuItem, endTime

		if pauseTime is not None:
			endTime += timelib.time() - pauseTime
			pauseTime = None
		else:
			pauseTime = timelib.time()

		if pauseTime is None:
			start()
		else:
			pauseMenuItem.set_label("Resume")

		return True

	def setTimeMinutes(t):
		global endTime, MIN
		endTime = timelib.time() + t * MIN

		start()

	# create a menu
	menu = gtk.Menu()
 
 	item1 = "Start a timer below"
 	pauseMenuItem = gtk.MenuItem(item1)
 	menu.append(pauseMenuItem)
 	pauseMenuItem.connect("activate", pause, item1)

 	item2 = "45 minutes"
 	menu_items = gtk.MenuItem(item2)
 	menu.append(menu_items)
 	menu_items.connect("activate", lambda w, buff: setTimeMinutes(45), item2)
 	menu_items.show()

 	item3 = "30 minutes"
 	menu_items = gtk.MenuItem(item3)
 	menu.append(menu_items)
 	menu_items.connect("activate", lambda w, buff: setTimeMinutes(30), item3)
 	menu_items.show()

 	item3 = "15 minutes"
 	menu_items = gtk.MenuItem(item3)
 	menu.append(menu_items)
 	menu_items.connect("activate", lambda w, buff: setTimeMinutes(15), item3)
 	menu_items.show()

 	item4 = "Quit"
 	menu_items = gtk.MenuItem(item4)
 	menu.append(menu_items)
 	menu_items.connect("activate", lambda w, buff: sys.exit("Closing timer app"), item4)
 	menu_items.show()


	# create some
	# for i in range(3):
	# 	buf = "Test-undermenu - %d" % i
 
	# 	menu_items = gtk.MenuItem(buf)
 
	# 	menu.append(menu_items)
 
	# 	# this is where you would connect your menu item up with a function:
 
	# 	menu_items.connect("activate", menuitem_response, buf)
 
	# 	# show the items
	# 	menu_items.show()
 
	ind.set_menu(menu)


	gtk.main()

print("Running")