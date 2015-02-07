#
# Hangman - main
#
# Jonatan H Sundqvist
# July 10 2014
#

# TODO | - Dictionary databases (sqlite3, JSON?)
#		 	-- Logophile class (?)
#		 	-- Dynamic wordlists (generators, BeautifulSoup?)
#		 	-- Lazy selects (saves RAM)
#		 	-- Error handling (eg. skipping and reporting invalid entries)
#		 	-- Implement difficulty-based scores
#
#		 - Add more language games
#		 	-- Name that thing
#
#		 - Validate input
#		 	-- words (length, characters, Total - Unique ≥ Chances,  etc.)
#		 	-- annotations (?)
#		 	-- Proper character set handling (adapt to dictionary, allow Unicode, etc.) (...)
#		 	-- Choose character set depending on language, create mapping from language to character set (?)
#		 	-- Treat some characters as equivalent (eg. accented characters)
#		 	-- Inputting non-keyboard characters
#		 	-- Resolve case inconsistencies across modules (...)
#
#		 - Complete and thorough documentation (tutorial, rule book, readme?)
#
#		 - Robustness, debugging, error handling
#		 	-- Dependency check
#		 	-- Optional verbose logging (...)
#
#		 - Refactor
#
#		 - Think about overall architecture (cf. MVC)
#		 	-- Create logic class (...)
#		 	-- Create input class (?)
#
#		 - Disable console in release version
#		 - Hints (...)
#
#		 - Proper UI, menus (...)
#		 	-- Generic variable trace closures (decorator?)
#		 	-- Language flags (✓)
#		 	-- Timers, progress bars (?)
#		 	-- Console option in Dev menu (async, exec with main.py locals)
#
#		 - Add quit method (sys.exit?)
#		 - Statistics, difficulty, profiles, remember state
#		 - Decide if chances should be determined by graphics
#
#		 - Loading settings (JSON?)
#		 	-- Extract settings from createMenu, hook up menu items to settings (...)
#		 	-- Implement setting files, extract strings, allow different UI languages
#		 	-- Remember previous sessions, users, preferences
#
#		 - Learn Git, move Hangman class to Hangman.py (...)
#
#		 - Improve asset management
#		 	-- Making it less fragile by storing location of each asset type
#		 	-- Separate module, or atleast a set of utility functions
#
#		 - Look into class decorators (cf. logging)
#
#		 - Look into function annotations (optional type checking?)
#		 	-- cf. inspect.getarcspec
#
#		 - PyQT (?)
#		 - Fix geometry bug caused by menubar (Canvas overflows the window) (✓)
#		 - Fix noticeable resize delay (hide window?)
#		 - Make dictionaries appear in menu automatically (✓)
#
#		 - Animated Main Menu
#
#		 - Spruce up graphics
#		 	-- SDL, Pyglet, Pygame
#		 	-- Animated background and foreground, music
#
#		 - Gameplay enhancements
#		 	-- Countdown, speed bonuses
#
#		 - Revamp, replace, or retouch the icon

# SPEC | -
#		 - 



import tkinter as tk # Window creation and event handling
import json 		 # Loading settings and meta data

from tkinter import messagebox 	#

from graphics import Graphics 				# 
from logic import Logic 					# 
from utilities import Size, createLogger 	# 

from PIL import Image, ImageTk		# Loading png icons to display alongside dictionaries (NOTE: 3rd party, bundle with game?)

from string import ascii_letters	# Character set
from collections import namedtuple	# Probably not needed anymore (moved to utilities.py)
from random import choice			# Choosing words (should eventually be superseded by database queries)
from pygame import mixer			# Audio (NOTE: 3rd party, bundle with game?)
from os import listdir 				# Finding and loading dictionaries

from SwiftUtils.SwiftUtils import Logger



class Hangman:

	'''
	This class provides the context for the
	graphics and logic modules, as well as
	handling input, menus, events and
	resources.

	The original intent was to let it serve
	as a model-view controller, where Logic
	represented the model and Graphics the
	main view.

	'''

	def __init__(self):

		'''
		Initializes window, canvas, gameplay options and menus,
		loads resources (settings, images, dictionaries)
		and sets up debugging.

		'''

		# Window
		self.size = Size(650, 650)
		self.root = self.createWindow(self.size)
		self.icon = self.loadIcon('icon.png')

		# Internal settings
		self.validState = False 						# Not ready to accept guesses
		self.DEBUG 		= tk.BooleanVar(value=False)	# Print debug messages
		self.VERBOSE 	= tk.BooleanVar(value=True)		# Print verbose debug messages

		# Logging
		self.messages 	= []
		self.logger = Logger('Hangman')

		# Resources
		self.dictData 	= self.loadDictionaries('data/dicts/dictionaries.json')
		self.dictNames 	= [name for name in self.dictData.keys()]
		self.flags 		= self.loadFlags()

		# Gameplay settings
		self.restartDelay   = 1500 	# Delay before new round begins (ms)
		self.revealWhenLost = False	# Reveal the word when the game is lost
		
		# TODO: Save reference to current dict (?)
		self.DICT 			= tk.StringVar(value=choice(self.dictNames)) 	# Select random dictionary
		self.characterSet 	= self.dictData[self.DICT.get()]['characters'] 	# TODO: Make this dictionary-dependent

		# Menus
		self.menubar = self.createMenus()

		# Events
		self.bindEvents()

		# Game play
		self.graphics = Graphics(self.root, *self.size, characterSet=self.characterSet)	# Renderer
		self.logic 	  = Logic(self.graphics.chances)									# Logic
		self.wordFeed = self.createWordFeed(self.DICT.get()) 							# Provides a stream of words and hints
		self.chances  = self.graphics.chances 											# Initial number of chances for each round

		self.word = None # Initialized later on
		self.hint = None # Initialized later on

		# Audio
		self.effects = self.loadAudio()


	def play(self):

		''' Starts the game '''

		self.restart()
		self.root.mainloop()


	def createWindow(self, size):

		''' As per the title '''

		root = tk.Tk()
		root.resizable(width=False, height=False)
		root.title('Hangman')

		return root


	def createMenus(self):

		''' As per the title '''

		# TODO: Nested dict or JSON menu definition (?)
		# TODO: Desperately needs a clean-up (...)

		menubar = tk.Menu(self.root)

		# New game
		menubar.add_command(label='New', command=self.restart)

		# Settings
		settings = tk.Menu(menubar, tearoff=0)
		settings.add_command(label='Difficulty', command=lambda: print('Moderate'))

		# Languages
		languages = tk.Menu(settings, tearoff=0)

		self.DICT.trace('w', lambda *args, var=self.DICT: self.setDictionary(var.get())) # TODO: Extract traces

		# TODO: Use appropriate flag
		for N, name in enumerate(self.dictData.keys()):
			code = self.dictData[name]['iso'] # Language code
			languages.add_radiobutton(label=name, image=self.flags[code], compound='left', var=self.DICT, value=name)
		else:
			self.logger.log('Found %d dictionaries.' % (N+1), kind='log')

		settings.add_cascade(label='Language', menu=languages)
		menubar.add_cascade(label='Settings', menu=settings)

		# About box
		menubar.add_command(label='About', command=self.about)
	
		# Dev menu
		debug = tk.Menu(menubar, tearoff=0)
		debug.add_checkbutton(label='Debug', onvalue=True, offvalue=False, variable=self.DEBUG)
		debug.add_checkbutton(label='Verbose', onvalue=True, offvalue=False, variable=self.VERBOSE)
		menubar.add_cascade(label='Dev', menu=debug)

		# Quit
		menubar.add_command(label='Quit', command=self.quit)

		# Attach to window
		self.root.config(menu=menubar)
		
		return menubar


	def bindEvents(self):
		''' Binds callbacks to events '''
		self.root.bind('<Escape>', lambda e: self.quit())
		self.root.bind('<Key>', lambda e: self.onKeyDown(e))


	def onKeyDown(self, event):

		''' Responds to key presses '''
		
		# TODO: Make sure guesses can't be made in a transitory state (✓)
		# TODO: Tidy up
		# TODO: Shortcuts, key bindings with JSON (?)
		# Validate the guess

		# Make sure the game is in a valid state (eg. not between to rounds)
		if not self.validState:
			self.logger.log('Cannot accept guesses right now', kind='log')
			return
		elif not self.validGuess(event.char):
			return
		else:
			self.guess(event.char)


	def about(self):
		''' Shows an about box '''
		messagebox.askokcancel('About', 'Hangman\nJonatan H Sundqvist\nJuly 2014')


	def loadAudio(self):
		''' Initializes mixer and loads sound effects '''
		mixer.init()
		files = ['strangled.wav', 'ding.wav']
		return namedtuple('Effects', ['lose', 'win'])(*map(lambda fn: mixer.Sound('data/audio/%s' % fn), files))


	def loadFlags(self):
		''' Loads all flag files and creates a map between those and their respective ISO language codes '''
		codes = [('en-uk', 'UK.png'), ('es-es', 'Spain.png'), ('in', 'India.png'), ('sv-sv', 'sv.png'), ('en-us', 'USA.png')] # Maps language codes to flags
		flags = {}
		for iso, fn in codes:
			image = Image.open('data/flags/%s' % fn)
			image.thumbnail((16,16), Image.ANTIALIAS)
			
			flags[iso] = ImageTk.PhotoImage(image)
		return flags


	def loadIcon(self, fn):
		''' Loads and sets the title bar icon '''
		icon = ImageTk.PhotoImage(Image.open(fn))
		self.root.call('wm', 'iconphoto', self.root._w, icon)
		return icon


	def loadDictionaries(self, fn):
		''' Loads JSON dictionary meta data '''
		# TODO: Dot notation
		# TODO: Load associated resources for convenience (?)
		with open(fn, 'r', encoding='utf-8') as dicts:
			return json.load(dicts)


	def setDictionary(self, name):
		''' Sets the dictionary specified by the name and restarts '''
		self.logger.log('Changing dictionary to %s' % name, kind='log')
		self.wordFeed = self.createWordFeed(name)
		self.characterSet = self.dictData[name]['characters']
		self.graphics.changeCharacterSet(self.characterSet)
		self.restart()


	# TODO: Research Python annotation syntax
	# TOOD: Check if ST3 has support for the same
	#def guess(self : str, letter : str) -> None:
	def guess(self, letter):
		
		''' Guesses one letter '''

		# TODO: Write a slightly more helpful docstring
		# TODO: Clean this up

		result = self.logic.guess(letter)
		
		self.logger.log('\'%s\' is a %s!' % (letter.upper(), result), kind='log')

		self.graphics.guess(letter, result in ('MATCH', 'WIN'), str(self.logic)), # TODO: Let Graphics take care of the representation for us (?)
		
		# TODO: Clean up the 'switch' logic
		#{'WIN': self.win, 'LOSE': self.lose}.get(result, lambda: None)()
		# return { ('MATCH', 'WIN'):  }
		
		if result == 'WIN':
			self.win()
		elif result == 'LOSE':
			self.lose()


	def validGuess(self, letter):
		''' Determines if a letter is a valid guess '''

		# TODO: Make this configurable (list of requirements?)

		# Normalize input
		letter = letter.upper()

		# Check all requirements
		if letter not in self.characterSet:
			# Make sure the character is a guessable letter
			self.logger.log('\'%s\' is not in the character set!' % letter, kind='log')
			return False
		elif len(letter) != 1:
			# Make sure the guess is only one letter
			self.logger.log('\'%s\' does not have exactly one letter!' % letter, kind='log')
			return False
		elif self.logic.hasGuessed(letter):
			# Make sure it's not a repeat guess
			self.logger.log('\'%s\' has already been guessed!' % letter, kind='log')
			return False
		else:
			return True


	def win(self):
		''' Victorious feedback, schedules the next round '''
		self.logger.log('Phew. You figured it out!', kind='log')
		self.effects.win.play()
		self.scheduleRestart()
	
	
	def lose(self):
		''' Failure feedback, schedules the next round '''
		# TODO: Show correct word before restarting (?)
		self.logger.log('You\'ve been hanged. Requiescat in pace!', kind='log')
		self.effects.lose.play()
		if self.revealWhenLost:
			self.graphics.setWord(self.word) # Reveal answer
		self.scheduleRestart()


	def scheduleRestart(self):
		''' Schedules a new round and disables guessing in the interim '''
		self.validState = False # Disable guessing between rounds
		self.root.after(self.restartDelay, self.restart)
		

	def restart(self):
		''' Starts a new game '''
		self.logger.log('\n{0}\n{1:^40}\n{0}\n'.format('-'*40, 'NEW GAME'), kind='log', identify=False) # TODO: Enable identify options in Logger.log

		self.word, self.hint = next(self.wordFeed)
		self.graphics.showHint(self.hint)

		self.logic.new(self.word)
		self.graphics.play(str(self.logic))

		self.validState = True # Ready to accept guesses again


	def quit(self, message=None, prompt=False):
		''' Exits the application '''
		# TODO: Find a way to close Python
		#print('\n'.join(self.messages))
		self.root.quit()


	def createWordFeed(self, name):
		''' Creates a word feed from the dictionary specified by the name '''
		# TODO: Give class a reference to words (?)
		# TODO: Wise to hard-code path (?)
		# TODO: Handle incorrectly structured dictionaries
		self.logger.log('Creating word feed from \'{name}\'.'.format(name=name), kind='log')
		fn = self.dictData[name]['file']
		with open('data/dicts/%s' %  fn, 'r', encoding='utf-8') as wordFile:
			words = wordFile.read().split('\n')
		while True:
			try:
				line = choice(words)
				word, hint = line.split('|') # Word|Hint
				yield word, hint
			except ValueError as e:
				words.remove(line) # Remove the culprit from the word feed
				self.logger.log('Removing invalid definition ({0}).'.format(line), kind='error')




if __name__ == '__main__':
	Hangman().play()