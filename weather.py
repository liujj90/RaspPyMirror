from tkinter import *
from PIL import Image, ImageTk

import requests 
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import seaborn as sns





# variables for darksky api
longitude = 138.5957969 # manual latitude and longitude settings to simplfy
latitude = -34.9319672
weatherAPItoken = '2b783784fa6e3d54eafb578294046b01'
weatherUnits = 'si'
weatherLang = 'en'
weatherURL = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weatherAPItoken, latitude,longitude,weatherLang,weatherUnits)



degree_sign= u'\N{DEGREE SIGN}'

icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
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



class Weather(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent, bg = 'black')
		
		self.now = Frame(self, bg = 'black')
		self.temperature = ''
		self.temperatureLabel = Label(self, font = ('Proxy 1', 40,'bold'), fg = 'white', bg = 'black')
		self.precipitation = ''
		self.precipitationLabel = Label(self, font = ('Proxy 1', 16, 'bold'), fg = 'white', bg = 'black')
		self.currently= ''
		self.currentlyLabel = Label(self,font = ('Proxy 1', 40,'bold'), fg = 'white', bg = 'black')
		self.icon = ''
		self.iconLabel = Label(self, bg = 'black')
		self.forecast = ''
		self.forecastLabel = Label(self, bg = 'black')
		#layout
		#self.temperatureLabel.grid(side = LEFT,anchor = W)
		#self.iconLabel.pack(side = LEFT, anchor = W)
		#self.currentlyLabel.pack(side = TOP, anchor = CENTER)
		#self.precipitationLabel.pack(side = RIGHT, anchor = CENTER)
		#self.forecastLabel.pack(side = LEFT, anchor = W)
		self.temperatureLabel.grid(row = 0, column = 0, rowspan = 2)
		self.iconLabel.grid(row = 0, column = 1, rowspan = 2)
		self.currentlyLabel.grid(row = 0, column = 2)
		self.precipitationLabel.grid(row =1, column = 2)
		self.forecastLabel.grid(row = 2, columnspan = 3, pady = 25)

		self.getWeather()

	def getWeather(self):
		r = requests.get(weatherURL)
		weatherOutput = json.loads(r.text)
		temp = "%s%s" % (str(int(weatherOutput['currently']['temperature'])), degree_sign)
		precip = weatherOutput['currently']['precipProbability']
		current = weatherOutput['currently']['summary']
		iconID = weatherOutput['currently']['icon']
		iconId = None
		#forcast
		forecastprecip = [v for hour in weatherOutput['hourly']['data'] for k,v in hour.items() if k == 'precipProbability']
		forecastTemp = [v for hour in weatherOutput['hourly']['data'] for k,v in hour.items() if k =='temperature']
		df = pd.DataFrame({'Time': range(24), 'Precipitation': forecastprecip[:24], 'Temperature': forecastTemp[:24]})
		hours = '%H'
		currentHour = int(time.strftime(hours, time.localtime()))
		hoursAfter = [currentHour]

		for i in range (1, 49):
			plus = currentHour + i
			if plus > 23:
				plus = currentHour - (24 - i)
			hoursAfter.append(plus)

		hourslabel = [str(x) for x in hoursAfter[:24]]
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
			self.precipitationLabel.config(text = 'Rain:'+ str(precip) + '%')
		if self.currently != current:
			self.currently = current
			self.currentlyLabel.config(text = current)
		forecastImage = Image.open('forecast.png')
		forecastImage = forecastImage.resize((450,300), Image.ANTIALIAS)
		forecastImage = forecastImage.convert('RGB')
		forecastPhoto = ImageTk.PhotoImage(forecastImage)
		self.forecastLabel.config(image = forecastPhoto)
		self.forecastLabel.image = forecastPhoto
		self.after(300000, self.getWeather) #call every half-hour


#forecastprecip = [v for hour in weatherOutput['hourly']['data'] for k,v in hour.items() if k == 'precipProbability']
#forecastTemp = [v for hour in weatherOutput['hourly']['data'] for k,v in hour.items() if k =='temperature']
# get hour from time to form x-axis 



class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        # clock
        #self.clock = Clock(self.topFrame)
        #self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)
        # weather
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)
        # news
        #self.news = News(self.bottomFrame)
        #self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)
        # calender - removing for now
        # self.calender = Calendar(self.bottomFrame)
        # self.calender.pack(side = RIGHT, anchor=S, padx=100, pady=60)

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




#plt.style.use('dark_background')
#plt.subplot(2,1,1)
#plt.plot(df['Time'], df['Temperature'], 'o')
#plt.xticks(df['Time'], hourslabel)
#plt.ylabel('Temperature')
#plt.subplot(2,1,2)
#plt.plot(df['Time'], df['Precipitation'], 'o')
#plt.ylabel('Precipitation')
#plt.xticks(df['Time'], hourslabel)
#plt.show()