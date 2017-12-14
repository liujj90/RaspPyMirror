from tkinter import *
from PIL import Image, ImageTk
import random
import requests 
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg") # allow matplotlib to display on tkinter
import seaborn as sns
from speech import *
import duckduckgo
import re
import feedparser
import collections

#overall variables
font1 = 'Proxy 1'

#variables for clock
timeFormat = '%H:%M'
dateFormat = '%d %b %Y'
dayFormat = '%A'

# variables for darksky api
longitude = 138.5957969 # manual latitude and longitude settings to simplfy
latitude = -34.9319672
weatherAPItoken = '2b783784fa6e3d54eafb578294046b01'
weatherUnits = 'si'
weatherLang = 'en'
weatherURL = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weatherAPItoken, latitude,longitude,weatherLang,weatherUnits)

# seaborn plot
sns.set(rc = {'axes.facecolor':'black',
              'figure.facecolor':'black', 
              'axes.labelcolor':'white', 
              'xtick.color':'white', 
              'ytick.color':'white'}, palette = 'Blues',font_scale =1.6)

degree_sign= u'\N{DEGREE SIGN}'

# displays
displayforecast = False
displayNews = ''
searchQuery = ''
messageToDisplay = ''

#icons for weather
icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png"  # hail
}

class clock(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg = 'black')
		self.timedefault = ''
		self.currTime = time.localtime()
		self.timeFormat = timeFormat
		self.dateFormat = dateFormat
		self.dayFormat = dayFormat
		#timeLabel
		self.timeLabel = Label(self, font = (font1, 40, 'bold'), fg = 'white', bg = 'black')
		self.timeLabel.pack(side = TOP, anchor = E)
		#datelabel
		self.date = ''
		self.dateLabel = Label(self, font = (font1, 16, 'bold'), fg = 'white', bg = 'black')
		self.dateLabel.pack(side = TOP, anchor = CENTER)
		#Daylabel
		self.today = ''
		self.dayLabel = Label(self, font = (font1, 16, 'bold'), fg = 'white', bg = 'black')
		self.dayLabel.pack(side = TOP, anchor = CENTER)
		self.tick()
	def tick(self):
		timenow = time.strftime(self.timeFormat, self.currTime)
		daynow = time.strftime(self.dayFormat, self.currTime)
		datenow = time.strftime(self.dateFormat, self.currTime)
		if self.currTime != self.today:
			self.today = daynow
			daynow = time.strftime(self.dayFormat, time.localtime())
			self.today = daynow
			self.dayLabel.config(text = daynow)
		if self.currTime != self.date:
			self.date = datenow
			datenow = time.strftime(self.dateFormat, time.localtime())
			self.date = datenow
			self.dateLabel.config(text = datenow)
		if self.currTime != self.timedefault:
			self.timedefault = timenow
			timenow = time.strftime(self.timeFormat, time.localtime())
			self.timeLabel.config(text = timenow)
			self.timeLabel.after(200, self.tick)

class Weather(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg = 'black')
		self.now = Frame(self, bg = 'black')
		self.temperature = ''
		self.temperatureLabel = Label(self, font = (font1, 40,'bold'), fg = 'white', bg = 'black')
		self.precipitation = ''
		self.precipitationLabel = Label(self, font = (font1, 16, 'bold'), fg = 'white', bg = 'black')
		self.currently= ''
		self.currentlyLabel = Label(self,font = (font1, 16,'bold'), fg = 'white', bg = 'black', wraplength = 200, justify = LEFT)
		self.icon = ''
		self.iconLabel = Label(self, bg = 'black')
		self.forecast = ''
		self.forecastLabel = Label(self, font = (font1, 16, 'bold'), fg = 'white', bg = 'black')
		#layout
		self.temperatureLabel.grid(row = 0, column = 0, rowspan = 2)
		self.iconLabel.grid(row = 0, column = 1, rowspan = 2)
		self.currentlyLabel.grid(row = 0, column = 2)
		self.precipitationLabel.grid(row =1, column = 2)
		self.forecastLabel.grid(row = 2, columnspan = 3, sticky = W)

		self.getWeather()
		self.getForecast()

	def getWeather(self):
		r = requests.get(weatherURL)
		weatherOutput = json.loads(r.text)
		temp = "%s%s" % (str(int(weatherOutput['currently']['temperature'])), degree_sign)
		precip = weatherOutput['currently']['precipProbability']
		current = weatherOutput['currently']['summary']
		iconID = weatherOutput['currently']['icon']
		iconId = None
		
		# input labels
		if iconID in icon_lookup:
			iconId = icon_lookup[iconID]
		if self.icon is not None:
			self.icon = iconId
			image = Image.open(iconId)
			image = image.resize((100,100), Image.ANTIALIAS)
			image = image.convert('RGB')
			photo = ImageTk.PhotoImage(image)
			self.iconLabel.config(image = photo)
			self.iconLabel.image = photo
		else:
			self.iconLabel.config(image = '')
		if self.temperature != temp:
			self.temperature = temp
			self.temperatureLabel.config(text = temp)
		if self.precipitation != precip:
			self.precipitation = precip
			self.precipitationLabel.config(text = 'Rain:'+ str(int(precip*100)) + '%')
		if self.currently != current:
			self.currently = current
			self.currentlyLabel.config(text = current)
		forecastprecip = [v for hour in weatherOutput['hourly']['data'] for k,v in hour.items() if k == 'precipProbability']
		forecastTemp = [v for hour in weatherOutput['hourly']['data'] for k,v in hour.items() if k =='temperature']
		# Make forecast data into df
		df = pd.DataFrame({'Time': range(24), 'Precipitation': forecastprecip[:24], 'Temperature': forecastTemp[:24]})		
		currentHour = int(time.strftime('%H', time.localtime()))
		hoursAfter = [currentHour]
		hourslabel = []
		for i in range (1, 24):
			plus = currentHour + i
			if plus > 23:
				plus = currentHour - (24 - i)
			hoursAfter.append(plus)
		#only include even numbers
		for i in hoursAfter:
			if i % 2 == 0:
				hourslabel.append(str(i))
			else:
				hourslabel.append('')
		#plot forcast and save as PNG
		plt.style.use('dark_background')
		plt.subplot(2,1,1)
		plt.plot(df['Time'], df['Temperature'], 'o')
		plt.xticks(df['Time'], hourslabel)
		plt.ylabel('Temperature')
		plt.subplot(2,1,2)
		plt.plot(df['Time'], df['Precipitation'], 'o')
		plt.ylabel('Precipitation')
		plt.xticks(df['Time'], hourslabel)
		plt.savefig('forecast.png', bbox_inches = 'tight')		
		plt.close()
		self.after(600000, self.getWeather) #call every 10min'
	def getForecast(self):

		if displayforecast == True:
			forecastImage = Image.open('forecast.png')
			forecastImage = forecastImage.resize((450,300), Image.ANTIALIAS)
			forecastImage = forecastImage.convert('RGB')
			forecastPhoto = ImageTk.PhotoImage(forecastImage)
			self.forecastLabel.config(image = forecastPhoto)
			self.forecastLabel.image = forecastPhoto
		else:
			self.forecastLabel.image = ''
		self.after(100, self.getForecast)

class textboxes(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self,parent, bg = 'black')
		self.news = Text(self, font = (font1, 11, 'bold'), fg = 'white', bg = 'black', spacing1 = 5, wrap = WORD, width = 50, height =14, bd =0, highlightthickness=0)
		self.news.pack(anchor = W, side = LEFT)
		self.newsHeadlines=collections.deque(maxlen = 5)#store headlines in here
		self.hackerHeadlines = collections.deque(maxlen=5) #limit to 5
		self.current_headlines = collections.deque(maxlen = 5) 
		self.toDo = []
		self.result = collections.deque(maxlen=1)
		self.searchstring = ''
		self.currentString= 'default'

		#Dictate into textbox to leave messages
		self.dictate= Text(self, font = (font1, 11, 'bold'), fg = 'white', bg ='black', spacing1 = 5, wrap = WORD,width = 50,height =14, bd = 0, highlightthickness = 0)
		self.dictate.pack(side = TOP, anchor = E, fill = X)
		self.dictate.tag_configure('right', justify = 'right')
		self.message=''
		self.currentMessage = 'default'

		#auto-run methods
		self.updateSearch()
		self.getHeadlines()
		self.pushHeadlines()
		self.transcribe_dictation()

	def transcribe_dictation(self):
		if self.message != self.currentMessage:
			self.message = messageToDisplay
			self.currentMessage = messageToDisplay
			self.dictate.delete('1.0',END)
			self.dictate.insert(END, self.message, 'right')
		self.after(1000, self.transcribe_dictation)
	def updateSearch(self):
		if displayNews=='Search':
			if self.searchstring != self.currentString:
				self.searchstring = searchQuery
				self.currentString= searchQuery
				print('going to search now')
				self.getHeadlines()
		self.after(1000, self.updateSearch)

	def pushHeadlines(self):
		# use a dict to store headline type and
		HeadlineTypes = {'News': self.newsHeadlines,
		'Hacker News': self.hackerHeadlines,
		'To Do': self.toDo,
		'Search':self.result}
		post_number=0
		for headlineType, entryList in HeadlineTypes.items():
			if displayNews == headlineType:
				for headline in entryList:
					if headline not in self.current_headlines:
						post_number +=1
						self.news.insert(END, '\n'+str(post_number)+') ')
						self.news.insert(END, headline)
						self.current_headlines.append(headline)
					else:
						break
				self.news.update_idletasks()
			elif displayNews == 'clear':
				self.news.delete(0,END)
				self.news.update_idletasks()
		self.after(1000, self.pushHeadlines)

	def getHeadlines(self):
		try:
			#news headlines
			headlines_url = 'https://news.google.com/news?ned=us&output=rss'
			feed = feedparser.parse(headlines_url)
			self.newsHeadlines= [post.title for post in feed.entries[:5]]
			#hackernews headlines
			hackerNews_url_top = 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty'
			r=requests.get(hackerNews_url_top)
			hackerNews_items = [item for item in json.loads(r.text)[:5]] #top 5
			for newsItem in hackerNews_items:
				HackerNewsItem = newsItem
				hackerNews_URL = 'https://hacker-news.firebaseio.com/v0/item/%s.json?print=pretty'%(HackerNewsItem)	
				request_item = requests.get(hackerNews_URL)
				newsOutput = json.loads(request_item.text)
				self.hackerHeadlines.append(newsOutput['title'])

			#searchAnswer
			if displayNews == 'Search':
				self.result.append(duckduckgo.get_zci(self.searchstring))


		except Exception as e:
			print('Error: %s. Cannot get news'% e)
		self.after(600000, self.getHeadlines)


class pushbutton(Frame):
	#for now this is an on-screen button that activates google cloud speech reognition
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg = 'black')
		self.buttonpush = Button(self,text= 'TALK', command = self.speakNow)
		self.buttonpush.grid(row = 0, pady = 10)
		self.message = ''
		self.printedMessage = Label(self, font = (font1,12,'bold'), fg = 'white', bg = 'black')
		self.printedMessage.grid(row = 1)
		self.getmessages()
	def getmessages(self):
		lines = open('messages.txt').read().splitlines()
		myline = random.choice(lines)
		if self.message!= myline:
			self.message= myline
			self.printedMessage.config(text = myline)
		self.after(60000, self.getmessages)
	def speakNow(self):
		global searchQuery, displayforecast, displayNews, messageToDisplay
		# collects speech output, reognises keywords
		transcribed = mainspeech()
		#transcribed = 'forecast'
		self.printedMessage.config(text = transcribed)
		if re.search(r'message', transcribed, re.I):
			messageToDisplay = ' '.join([i for i in transcribed.split(' ') if i != 'message'])
		elif transcribed == 'forecast':
			displayforecast = True
			self.printedMessage.config(text = 'Displaying forecast')
		elif re.search(r'search', transcribed, re.I):
			#global searchQuery
			searchstring = ' '.join([i for i in transcribed.split(' ') if i != 'search'])
			searchQuery = searchstring
			displayNews = 'Search'
			self.printedMessage.config(text = 'Searching for:' + searchstring)
		elif transcribed == 'news':
			displayNews = 'News'
			self.printedMessage.config(text = 'Displaying top News Headlines')
		elif transcribed == 'hacker':
			displayNews = 'Hacker News'
			self.printedMessage.config(text= 'Displaying Hacker News Headlines')
		elif transcribed =='reset':
			displayforecast = False
			searchQuery = ''
			displayNews = 'clear'
			self.printedMessage.config(text = 'Reset displays')
		elif transcribed == 'clear message':
			messageToDisplay = ''
		else:
			self.printedMessage.config(text = 'Not sure how to help you')

class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background = 'black')
        self.midFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.midFrame.pack(side = TOP, fill = BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        # clock
        self.clock = clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor=N, padx = 100, pady = 10)
        # weather
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx = 100, pady = 10)
        # calender - removing for now
        # self.calender = Calendar(self.bottomFrame)
        # self.calender.pack(side = RIGHT, anchor=S, padx=100, pady=60)
        self.textBox = textboxes(self.midFrame)
        self.textBox.pack(side = LEFT,anchor = N, padx = 100)
        #message box and button
        self.pushbutton = pushbutton(self.bottomFrame)
        self.pushbutton.pack(side = BOTTOM, anchor =S, pady = 10)
         #search results
        
    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"


w = FullscreenWindow()
w.tk.mainloop()