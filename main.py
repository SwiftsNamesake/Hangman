# Hangman.py
#
# Jonatan H Sundqvist
# July 10 2014
#

# TODO | - Dictionary databases (sqlite3, JSON?)
#		 - Validate input, words (length, characters, 26 - Unique ≥ Chances,  etc.)
#		 - Complete and thorough documentation (tutorial, rule book, readme?)
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
#		 - Learn Git, move Hangman class to Hangman.py (...)
#		 - Improve asset management
#		 	-- Making it less fragile by storing location of each asset type
#		 - Look into class decorators (cf. logging)
#		 - Look into function annotations (optional type checking?)
#		 - PyQT (?)

# SPEC | -
#		 - 


import tkinter as tk # Window creation and event handling

from tkinter import messagebox

from graphics import Graphics
from logic import Logic
from PIL import Image, ImageTk		# Loading png icons to display alongside dictionaries (NOTE: 3rd party, bundle with game?)

from sys import exit # Closing the console

from string import ascii_letters	# Character set
from collections import namedtuple	# Probably not needed anymore (moved to utilities.py)
from random import choice			# Choosing words (should eventually be superseded by database queries)
from pygame import mixer			# Audio (NOTE: 3rd party, bundle with game?)
from os import listdir 				# Finding and loading dictionaries

from inspect import currentframe, getouterframes, getframeinfo # Line numbers (for logging)


class Hangman:
	''' '''
	def __init__(self):
		''' '''

		#
		self.size = Graphics.Size(650, 650)
		self.root = self.createWindow(self.size)

		# Internal settings
		self.validState = False # Not ready to accept guesses
		self.DEBUG = tk.BooleanVar()
		self.VERBOSE = tk.BooleanVar()

		# Dictionaries
		# TODO: Move to separate method
		self.wordLists = [ 'data/dicts/%s' % uri for uri in listdir('data/dicts') if uri.endswith('.txt') ] # Dictionary file URIs
		
		# Menus
		self.menubar = self.createMenus()

		# Events
		self.bindEvents()

		# Game play
		self.graphics = Graphics(self.root, self.size.width, self.size.height)
		self.logic = Logic(self.graphics.chances)
		self.wordFeed = self.createWordFeed('data/dicts/en_dict_thetoohardforyouversion.txt') # TODO: Make dictionaries appear in menu automatically (...)

		self.word = None
		self.hint = None

		# Gameplay settings
		self.chances = self.graphics.chances # Initial number of chances for each round
		self.restartDelay = 2000 			 # Delay before new round begins (ms)
		self.revealWhenLost = False			 # Reveal the word when the game is lost

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

		# TODO: Nested dict menu definition (?)
		# TODO: Desperately needs a clean-up

		menubar = tk.Menu(self.root)

		# New game
		menubar.add_command(label='New', command=lambda: print('Not implemented'))

		# Settings
		settings = tk.Menu(menubar, tearoff=0)
		settings.add_command(label='Difficulty', command=lambda: print('Moderate'))

		# Languages
		languages = tk.Menu(settings, tearoff=0)
		languages.var = tk.IntVar()
		languages.image = ImageTk.PhotoImage(Image.open('data/flags/UK.png'))

		def closure(fn):
			def callback(*args):
				self.log('Changing dictionary to %s' % fn)
				self.wordFeed = self.createWordFeed(fn)
				self.win() # Use win() method to restart for now
			return callback

		for N, name in enumerate(self.wordLists):
			languages.add_radiobutton(label=name, image=languages.image, compound='left', var=languages.var, value=N, command=closure(name))

		settings.add_cascade(label='Language', menu=languages)
		menubar.add_cascade(label='Settings', menu=settings)

		# About box
		def about():
			messagebox.askyesno('About', 'Hangman\nJonatan H Sundqvist\nJuly 2014') # .format('-'*30)

		menubar.add_command(label='About', command=about) # About box
	
		# Debugging
		def onToggle(variable, message): return lambda *args: print(message % ['dis', 'en'][variable.get()])

		self.DEBUG.trace('w', onToggle(self.DEBUG, 'Debugging is %sabled.'))
		self.VERBOSE.trace('w', onToggle(self.VERBOSE, 'Verbose is %sabled.'))

		debug = tk.Menu(menubar, tearoff=0)
		debug.add_checkbutton(label='Debug', onvalue=True, offvalue=False, variable=self.DEBUG)
		debug.add_checkbutton(label='Verbose', onvalue=True, offvalue=False, variable=self.VERBOSE)
		menubar.add_cascade(label='Debug', menu=debug)

		# End game
		# menubar.add_command(label='Quit', command=self.root.quit)
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


	def loadAudio(self):
		''' '''
		return namedtuple('Effects', ['lose', 'win'])(*map(lambda fn: mixer.Sound('data/audio/%s' % fn), ['strangled.wav', 'ding.wav']))
		#return namedtuple('Effects', ['lose'])(wave.open('data/hangman.wav'))


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


	def createWordFeed(self, dictionary):
		''' '''
		# TODO: Give class a reference to words (?)
		# NOTE: Currently, the entire file is kept in memory
		with open(dictionary, 'r') as wordFile:
			words = wordFile.read().split('\n')
		while True:
			#yield choice('treasury|laconic|forboding'.split('|'))
			yield choice(words).split('|') # Word|Hint


	def log(self, *args, identify=True, **kwargs):
		''' '''
		# TODO: Make instance-setting (✓)
		# TODO: Different categories (eg. error, log, feedback)
		if self.DEBUG.get():
			prefix = '(Hangman) [%s] ' % getouterframes(currentframe())[1][2] if identify else ''
			print(prefix, *args, **kwargs)



if __name__ == '__main__':
	Hangman().play()