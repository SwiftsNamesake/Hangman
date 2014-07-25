# Hangman.py
#
# Jonatan H Sundqvist
# July 10 2014
#

# TODO | - Dictionary databases (sqlite3, JSON?)
#		 	-- Logophile class (?)
#		 - Validate input, words (length, characters, 26 - Unique ≥ Chances,  etc.)
#		 - Complete and thorough documentation (tutorial, rule book, readme?)
#		 - Robustness, debugging, error handling
#		 	-- Dependency check
#		 - Refactor
#		 - Think about overall architecture (cf. MVC)
#		 	-- Create class (...)
#		 	-- Create input class (?)
#		 - Validate input (annotations?)
#		 - Optional verbose logging (...)
#		 - Disable console in release version
#		 - Hints (...)
#		 - Proper UI, menus (...)
#		 	-- Languages flags
#		 	-- Timers, progress bars (?)
#		 - Add quit method (sys.exit?)
#		 - Statistics, difficulty
#		 - Decide if chances should be determined by graphics
#		 - Loading settings (JSON?)
#		 	-- Extract settings from createMenu, hook up menu items to settings
#		 - Learn Git, move Hangman class to Hangman.py (...)
#		 - Improve asset management
#		 	-- Making it less fragile by storing location of each asset type
#		 	-- Separate module, or atleast a set of utility functions
#		 - Look into class decorators (cf. logging)
#		 - Look into function annotations (optional type checking?)
#		 	-- cf. inspect.getarcspec
#		 - PyQT (?)

# SPEC | -
#		 - 


import tkinter as tk # Window creation and event handling
import json 		 # Loading settings and meta data

from tkinter import messagebox
#from tkinter import ttk

from graphics import Graphics
from logic import Logic
from PIL import Image, ImageTk		# Loading png icons to display alongside dictionaries (NOTE: 3rd party, bundle with game?)

from sys import exit 				# Closing the console (only quits the intepreter?)

from string import ascii_letters	# Character set
from collections import namedtuple	# Probably not needed anymore (moved to utilities.py)
from random import choice			# Choosing words (should eventually be superseded by database queries)
#from pygame import mixer			# Audio (NOTE: 3rd party, bundle with game?)
from os import listdir 				# Finding and loading dictionaries

from inspect import currentframe, getouterframes, getframeinfo # Line numbers (for logging)


class Hangman:

	'''
	Doc goes here

	'''

	def __init__(self):

		''' '''

		#
		self.size = Graphics.Size(650, 650)
		self.root = self.createWindow(self.size)
		self.icon = self.loadIcon('icon.png')

		# Internal settings
		self.validState = False 						# Not ready to accept guesses
		self.DEBUG 		= tk.BooleanVar(value=False)	# Print debug messages
		self.VERBOSE 	= tk.BooleanVar(value=True)		# Print verbose debug messages

		# Dictionaries
		# TODO: Generic process-dictionaries method (?)
		self.dictData  = self.loadDictionaries('data/dicts/dictionaries.json')
		
		# Gameplay settings
		self.restartDelay   = 2000 			 # Delay before new round begins (ms)
		self.revealWhenLost = False			 # Reveal the word when the game is lost
		
		self.DICT = tk.StringVar(value=next(iter(self.dictData.keys()))) # Currently selected dictionary (file name) # TODO: Clean this up
		#self.wordLists = 'data/dicts/%s' % self.dictData[name]['file'] for name in self.dictData.keys() } # Dictionary file URIs

		# Menus
		self.menubar = self.createMenus()

		# Events
		self.bindEvents()

		# Game play
		# TODO: Fix geometry bug caused by menubar (Canvas overflows the window)
		self.graphics = Graphics(self.root, self.size.width, self.size.height)
		#self.graphics = Graphics(self.root, 650, 625)
		self.logic 	  = Logic(self.graphics.chances)
		self.wordFeed = self.createWordFeed(self.DICT.get()) # TODO: Make dictionaries appear in menu automatically (...)
		self.chances  = self.graphics.chances # Initial number of chances for each round

		self.word = None
		self.hint = None

		# Audio
		mixer.init()
		self.effects = self.loadAudio()


	def play(self):
		''' '''
		self.restart()
		self.root.mainloop()


	def createWindow(self, size):
		''' '''
		root = tk.Tk()
		root.geometry('%dx%d' % size)
		root.resizable(width=False, height=False)
		root.title('Hangman')

		return root


	def createMenus(self):
		''' '''

		# TODO: Nested dict or JSON menu definition (?)
		# TODO: Desperately needs a clean-up (...)

		menubar = tk.Menu(self.root)

		# New game
		menubar.add_command(label='New', command=self.win)

		# Settings
		settings = tk.Menu(menubar, tearoff=0)
		settings.add_command(label='Difficulty', command=lambda: print('Moderate'))

		# Languages
		languages 		 = tk.Menu(settings, tearoff=0)
		languages.images = self.loadFlags()

		# TODO: Generic variable trace closures (decorator?)
		def changeDict(name):
			def closure(*args):
				self.log('Changing dictionary to %s' % name)
				self.wordFeed = self.createWordFeed(name)
				self.win() # Use win() method to restart for now
			return closure

		self.DICT.trace('w', lambda *args, var=self.DICT: self.setDictionary(var.get()))

		# TODO: Use appropriate flag
		for N, name in enumerate(self.dictData.keys()):
			code = self.dictData[name]['iso'] # Language code is the first to characters in filename
			languages.add_radiobutton(label=name, image=languages.images[code], compound='left', var=self.DICT, value=name)
		else:
			print('Found %d dictionaries.' % (N+1))

		settings.add_cascade(label='Language', menu=languages)
		menubar.add_cascade(label='Settings', menu=settings)

		# About box
		menubar.add_command(label='About', command=self.about) # About box
	
		# Dev menu
		debug = tk.Menu(menubar, tearoff=0)
		debug.add_checkbutton(label='Debug', onvalue=True, offvalue=False, variable=self.DEBUG)
		debug.add_checkbutton(label='Verbose', onvalue=True, offvalue=False, variable=self.VERBOSE)
		menubar.add_cascade(label='Dev', menu=debug)

		# End game
		menubar.add_command(label='Quit', command=self.quit)

		# Attach menu
		self.root.config(menu=menubar)
		
		return menubar


	def bindEvents(self):
		''' '''
		self.root.bind('<Escape>', lambda e: self.quit())
		self.root.bind('<Key>', lambda e: self.onKeyDown(e))


	def onKeyDown(self, event):
		''' '''
		# TODO: Make sure guesses can't be made in a transitory state
		# Validate the guess

		# Make sure the game is in a valid state (eg. not between to rounds)
		if not self.validState:
			self.log('Cannot accept guesses right now')
			return

		if not (event.char in ascii_letters) or len(event.char) != 1:
			self.log('Invalid guess \'%s\'' % event.char)
			return

		# Make sure it's not a repeat guess
		if not self.logic.hasGuessed(event.char):
			self.guess(event.char)
		else:
			self.log('Already guessed \'%s\'.' % event.char)


	def about(self):
		''' Show an about box '''
		messagebox.askyesno('About', 'Hangman\nJonatan H Sundqvist\nJuly 2014') # .format('-'*30)


	def loadAudio(self):
		''' '''
		files = ['strangled.wav', 'ding.wav']
		return namedtuple('Effects', ['lose', 'win'])(*map(lambda fn: mixer.Sound('data/audio/%s' % fn), files))
		#return namedtuple('Effects', ['lose'])(wave.open('data/hangman.wav'))


	def loadFlags(self):
		''' '''
		codes = [('en-uk', 'UK.png'), ('es-es', 'Spain.png'), ('in', 'India.png'), ('sv', 'Sweden.png'), ('en-us', 'USA.png')] # Maps language codes to flags
		return { lang: ImageTk.PhotoImage(Image.open('data/flags/%s' % fn)) for lang, fn in codes } # TODO: Extract to separate method (✓)


	def loadDictionaries(self, fn):
		''' Loads JSON dictionary meta data '''
		with open(fn, 'r') as dicts:
			return json.load(dicts)


	def setDictionary(self, name):
		''' Sets the dictionary specified by the name '''
		self.log('Changing dictionary to %s' % name)
		self.wordFeed = self.createWordFeed(name)
		self.win() # Use win() method to restart for now


	def loadIcon(self, fn):
		''' '''
		icon = ImageTk.PhotoImage(Image.open(fn))
		self.root.call('wm', 'iconphoto', self.root._w, icon)
		return icon


	# TODO: Research Python annotation syntax
	# TOOD: Check if ST3 has support for the same
	#def guess(self : str, letter : str) -> None:
	def guess(self, letter):
		''' '''
		result = self.logic.guess(letter)
		
		self.log('Guessing %s. The guess is a %s' % (letter, result))

		# TODO: Clean up the 'switch' logic
		self.graphics.guess(letter, result in ('MATCH', 'WIN'), str(self.logic)), # TODO: Let Graphics take care of the representation for us (?)
		
		#{'WIN': self.win, 'LOSE': self.lose}.get(result, lambda: None)()
		
		if result == 'WIN':
			self.win()
		elif result == 'LOSE':
			self.lose()


	def win(self):
		''' '''
		# TODO: Extract restart logic (✓)
		self.log('Phew. You figured it out!')
		self.validState = False # Disable guessing between rounds
		self.effects.win.play()
		self.root.after(self.restartDelay, self.restart) # TODO: Extract to restart method (?)
	
	
	def lose(self):
		''' '''
		# TODO: Extract restart logic (✓)
		# TODO: Show correct word before restarting
		self.log('You\'ve been hanged. Requiescat in pace!')
		self.validState = False # Disable guessing between rounds
		self.effects.lose.play()
		self.root.after(self.restartDelay, self.restart)


	def restart(self):
		'''  '''
		self.log('\n{0}\n{1:^40}\n{0}\n'.format('-'*40, 'NEW GAME'), identify=False)
		self.graphics.showHint('It starts with a letter.')

		self.word, self.hint = next(self.wordFeed)
		self.graphics.showHint(self.hint)

		self.logic.newGame(self.word)
		self.graphics.play(str(self.logic))

		self.validState = True # Ready to accept guesses again


	def quit(self, message=None, prompt=False):
		''' '''
		self.root.quit()
		#exit(0)


	def createWordFeed(self, name):
		''' Creates a word feed from the dictionary specified by the name '''
		# TODO: Give class a reference to words (?)
		# TODO: Wise to hard-code path (?)
		fn = self.dictData[name]['file']
		with open('data/dicts/%s' %  fn, 'r') as wordFile:
			words = wordFile.read().split('\n')
		while True:
			#yield choice('treasury|laconic|forboding'.split('|'))
			yield choice(words).split('|') # Word|Hint


	def log(self, *args, identify=True, **kwargs):
		''' '''
		# TODO: Make instance-setting (✓)
		# TODO: Different categories (eg. error, log, feedback)
		if self.DEBUG.get():
			print('(Hangman) [%s] ' % getouterframes(currentframe())[1][2] if identify else '')
			print(*args, **kwargs)



if __name__ == '__main__':
	Hangman().play()