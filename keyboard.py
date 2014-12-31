__author__ = 'Tin'

import pygame
import sys
from pygame.locals import *

import csv
import time

from midiutil2.MidiFile import MIDIFile

#load_image is used in most pygame programs for loading images
def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()
class Button(pygame.sprite.Sprite):
    """Class used to create a button, use setCords to set 
        position of topleft corner. Method pressed() returns
        a boolean and should be called inside the input loop."""
    def __init__(self, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(filename, -1)
    def setCords(self,x,y):
        self.rect.topleft = x,y
    def pressed(self,mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        return True
                    else: return False
                else: return False
            else: return False
        else: return False


SAMPLE_WIDTH = 16
FRE = 44100
N_CHANNELS = 2
BUFFER = 2**9
fadeout_time=50
repeat = -1
recording = False

channel = 2
start = 0
volume = 100

pygame.init();


black = (0,0,0)
white = (255,255,255)
gray = (190,190,190)
'''
red = (255,0,0)
orange = (255,165,0)
pink = (255,105,180)
yellow = (255,255,0)
cyan = (0,255,255)
green = (0,255,0)
blue = (0,0,255)
indigo = (111, 0, 255)
purple = (255,0,255)
'''

color = {'q':(255,0,0),'w':(255,165,0),'e':(255,105,180),'f':(255,255,0),
'space':(0,255,255),'j':(0,255,0),'i':(0,0,255),'o':(111,0,255),'p':(255,0,255)}

pygame.mixer.pre_init(FRE,-SAMPLE_WIDTH,N_CHANNELS,BUFFER)
pygame.init()
display = pygame.display.set_mode((1000,650))


#idlingB = Button('image/idling.png')
#idlingB.setCords(900,25)
idlingB = pygame.image.load('image/idling.png')
#recordingB = Button('image/recording.png')
#recordingB.setCords(900,25)
recordingB = pygame.image.load('image/recording.png')
buttonQ = pygame.image.load('image/buttonQ.png')
buttonW = pygame.image.load('image/buttonW.png')
buttonE = pygame.image.load('image/buttonE.png')
buttonF = pygame.image.load('image/buttonF.png')
buttonS = pygame.image.load('image/template.png')
buttonJ = pygame.image.load('image/buttonJ.png')
buttonI = pygame.image.load('image/buttonI.png')
buttonO = pygame.image.load('image/buttonO.png')
buttonP = pygame.image.load('image/buttonP.png')

button = display.blit(idlingB,(900,25))
display.blit(buttonQ,(60,550))
display.blit(buttonW,(150,550))
display.blit(buttonE,(240,550))
display.blit(buttonF,(330,550))
display.blit(buttonS,(420,550))
display.blit(buttonJ,(510,550))
display.blit(buttonI,(600,550))
display.blit(buttonO,(690,550))
display.blit(buttonP,(780,550))

key2sound = {}
config = csv.reader(open('configs/aaa.cf', 'rb'), delimiter=',')
for key, soundfile in config:
    key,soundfile = key.strip(' '),soundfile.strip(' ')
    if key is not '#':
    	print soundfile
        key2sound[key] = pygame.mixer.Sound(soundfile)

#currently_playing = {k : False for k in key2sound.iterkeys()}
animation = {'q':[0]*55,'w':[0]*55,'e':[0]*55,'f':[0]*55,'space':[0]*55,'j':[0]*55,'i':[0]*55,'o':[0]*55,'p':[0]*55}
keys = ['q','w','e','f','space','j','i','o','p']
tracks = {'q':0,'w':1,'e':2,'f':3,'j':4,'i':5,'o':6,'p':7}
pitch = {'q':69,'w':71,'e':73,'f':74,'j':76,'i':78,'o':80,'p':81}
record = [0]*8

FPS = 20
fpsTime = pygame.time.Clock()
pygame.key.set_repeat(500)
count = 0
time = 0
while True:
	#event =  pygame.event.wait()
	#event =  pygame.event.poll()
	events = pygame.event.get()
	for event in events:
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type in (pygame.KEYDOWN,pygame.KEYUP):
			key = pygame.key.name(event.key)
			if key in key2sound:
				if event.type == pygame.KEYDOWN:
					key2sound[key].play(repeat)
					#currently_playing[key] = True
					for k in keys:
						if k == key:
							animation[k].append(1)
						else:
							animation[k].append(animation[k][-1])
						animation[k].remove(animation[k][0])
					if recording and key != 'space' and record[tracks[key]] == 0:
						record[tracks[key]] = time
				else:
					key2sound[key].fadeout(fadeout_time)
					for k in keys:
						if k == key:
							animation[k].append(0)
						else:
							animation[k].append(animation[k][-1])
						animation[k].remove(animation[k][0])
					if recording and key != 'space':
						duration = time - record[tracks[key]]
						if duration == 0:
							duration = 1
						print '====='
						print key
						begin = int(record[tracks[key]]/3.5)
						print begin
						print duration
						MyMIDI.addNote(tracks[key],channel,pitch[key],begin,duration,volume)
						record[tracks[key]] = 0
					#currently_playing[key] = False
			count = 0
		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			pos = pygame.mouse.get_pos()
			if button.collidepoint(pos):
				if not recording:
					button = display.blit(recordingB,(900,25))
					MyMIDI = MIDIFile(8)
					time = -1
					for track in range(0,8):
						MyMIDI.addTrackName(track,0,'track' + str(track))
						MyMIDI.addTempo(track,0,240)
					recording = True
				else:
					button = display.blit(idlingB,(900,25))
					binfile = open("output.mid", 'wb')
					MyMIDI.writeFile(binfile)
					binfile.close()
					recording = False
			count = 0

	if count >= 7:
		for k in keys:
			animation[k].append(animation[k][-1])
			animation[k].remove(animation[k][0])
		count = 0
	else:
		count += 1
		
	width = 0
	for k in keys:
		height = 0
		for i in animation[k]:
			paint = black if (i==0) else color[k]
			pygame.draw.rect(display,paint,(65+width,0+height,80,10))
			height += 10
		width += 90
	
	if recording:
		time += 1
	pygame.display.update()
	fpsTime.tick(FPS)

