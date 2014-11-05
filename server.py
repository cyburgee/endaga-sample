#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import json, simplekml, numpy

PORT_NUMBER = 8000

kml = simplekml.Kml()
origin = [37.816817,-122.253924]
minRssi = -110
folderDict = {}


def addCoords(tuple1,tuple2):
	return tuple(numpy.add(tuple1,tuple2))

def addDataToKML(data):
	#get data fields
	imsi = data['imsi'] 
	pos_y = float(data['pos_y'])/10000 #scale the positions
	pos_x = float(data['pos_x'])/10000
	time = data['time']
	signal = data['rssi']

	#color polygon according to signal quality
	if signal < -100:
		color = simplekml.Color.red
	elif -100 <= signal < -80:
		color = simplekml.Color.yellow
	else:
		color = simplekml.Color.green

	boxHeight =  (signal - minRssi)*2 #scale the height of the boxes based on minimum rssi
	#create a folder in kml for each phone
	if imsi in folderDict:
		folder = folderDict[imsi]
	else:
		folder = kml.newfolder(name=imsi)
		folderDict[imsi] = folder
		folder.open = 1
	#create polygon to represent signal at space and time
	pol = folder.newpolygon()
	#name the polygon after the time
	pol.name = str(time)
	#want polygon to extend to ground
	pol.extrude = 1;
	#poly altitude is relative to ground level
	pol.altitudemode = simplekml.AltitudeMode.relativetoground
	#create a box around the phone coordinates
	coords = (pos_y + origin[1], pos_x + origin[0], boxHeight)
	polycoords = [addCoords(coords,(-0.0001,-0.0001,0)), addCoords(coords,(0.0001,-0.0001,0)), addCoords(coords,(0.0001,0.0001,0)), addCoords(coords,(-0.0001,0.0001,0)), addCoords(coords,(-0.0001,-0.0001,0))]
	#print polycoords
	pol.outerboundaryis.coords = polycoords
	#give polygon the timestamp
	pol.timestamp.when = time
	#set poly color
	pol.style.polystyle.color = color
	pol.style.polystyle.outline = 1

	kml.save('phones.kml')

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):

	#Handler for the GET requests
	def do_GET(self):
		try:
			if self.path == "/":
				self.send_response(200)
				self.send_header('Content-type','text-html')
				self.end_headers()
				#write the embedded page
				f = open(curdir + sep + "/map.html")
				self.wfile.write(f.read())
				return
			elif self.path == "/served.kml":
				#this serves up the kml that is embedded and links to phones.kml
				kml.save('phones.kml')
				self.send_response(200)
				self.send_header('Content-type','application/vnd.google-earth.kml+xml')
				self.end_headers()
				f = open(curdir + sep + self.path)
				self.wfile.write(f.read())
				return 
			elif self.path == "/phones.kml":
				#this serves up the updated kml with all of the phone data
				kml.save('phones.kml')
				self.send_response(200)
				self.send_header('Content-type','application/vnd.google-earth.kml+xml')
				self.end_headers()
				f = open(curdir + sep + self.path)
				self.wfile.write(f.read())
				return 
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#Handler for POST requests
	def do_POST(self):
		try:
			length = int(self.headers["Content-Length"])
			try:
				data = json.loads(self.rfile.read(length))
			except ValueError, e:
				self.send_error(400, 'Data is in incorrect format.')

			print 'Data:' , json.dumps(data)

			addDataToKML(data)
			self.send_response(200)
			return
		except IOError:
			self.send_error(400, 'Request failed.')

	#quiet server output
	def log_message(self, format, *args):
		return


try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port' , PORT_NUMBER
	#setup the kml to be served
	kmlLink = simplekml.Kml()
	doc = kmlLink.newdocument(name='Phone Signal Strength')
	doc.visibility = 1
	doc.open = 1
	doc.lookat.longitude = origin[1]
	doc.lookat.latitude = origin[0]
	doc.lookat.range = 10000
	netlink = doc.newnetworklink(name='Phone Signal Strength Link')
	netlink.visibility = 1
	netlink.open = 1
	netlink.snippet = simplekml.Snippet("Cellular network signal strengths. Gets updates every 30 seconds.", 1)
	#this kml links to the one being updated
	netlink.link.href = "http://localhost:8000/phones.kml"
	#have the visualization update every 1/2 minute
	netlink.link.refreshmode = simplekml.RefreshMode.oninterval
	netlink.link.refreshinterval = 30 #set this to change update speed
	kmlLink.save('served.kml')
	#Wait forever for incoming http requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()