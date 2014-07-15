# Hangman.py
#
# Jonatan H Sundqvist
# July 10 2014
#

# TODO | - Dictionary databases (sqlite3, JSON?)
#		 - Validate input, words (length, characters, 26 - unique letters > chances,  etc.)
#		 - Complete and thorough documentation (tutorial, readme?)
#		 - Refactor
#		 - Create class (...)
#		 - Create input class (?)
#		 - Validate input (annotations?)
#		 - Optional verbose logging (...)
#		 - Disable console in release version
#		 - Hints (...)
#		 - Proper UI, menus (...)
#		 - Timers, progress bars (?)
#		 - Add quit method
#		 - Statistics, difficulty
#		 - Decide if chances should be determined by graphics
#		 - Loading settings (JSON?)
#		 - Learn Git, move Hangman class to Hangman.py

# SPEC | -
#		 - 


import tkinter as tk
import wave

from graphics import Graphics
from logic import Logic
from string import ascii_letters
from collections import namedtuple
from random import choice
from pygame import mixer


class Hangman:
	''' '''
	def __init__(self):
		#
		self.size = Graphics.Size(650, 650)
		self.root = self.createWindow(self.size)

		# Menus
		self.menubar = self.createMenus()

		# Events
		self.bindEvents()

		# Game play
		self.graphics = Graphics(self.root, self.size.width, self.size.height)
		self.logic = Logic(self.graphics.chances)
		self.wordFeed = self.createWordFeed('data/en_dict_thetoohardforyouversion.txt') # TODO: Make dictionaries appear in menu automatically

		self.word = None
		self.hint = None

		# Gameplay settings
		self.chances = self.graphics.chances # Initial number of chances for each round
		self.restartDelay = 2000 			 # Delay before new round begins (ms)
		self.revealWhenLost = False			 # Reveal the word when the game is lost

		# Audio
		mixer.init()
		self.effects = self.loadAudio()

		# 
		self.validState = False # Not ready to accept guesses


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
		menubar = tk.Menu(self.root)

		menubar.add_command(label='New', command=lambda: print('Not implemented'))

		# Settings
		settings = tk.Menu(menubar, tearoff=0)
		settings.add_command(label='Difficulty', command=lambda: print('Moderate'))
		settings.add_command(label='Language', command=lambda: print('English for now'))
		menubar.add_cascade(label='Settings', menu=settings)

		menubar.add_command(label='About', command=lambda: print('\n{0}\nHangman\nJonatan H Sundqvist\nJuly 2014\n{0}\n'.format('-'*30))) # About box
	
		# Debugging
		def onToggle(variable, message): return lambda *args: print(message % ['dis', 'en'][variable.get()])

		self.DEBUG = tk.BooleanVar()
		self.DEBUG.trace('w', onToggle(self.DEBUG, 'Debugging is %sabled.'))

		self.VERBOSE = tk.BooleanVar()
		self.VERBOSE.trace('w', onToggle(self.VERBOSE, 'Verbose is %sabled.'))

		debug = tk.Menu(menubar, tearoff=0)
		debug.add_checkbutton(label='Debug', onvalue=True, offvalue=False, variable=self.DEBUG)
		debug.add_checkbutton(label='Verbose', onvalue=True, offvalue=False, variable=self.VERBOSE)
		menubar.add_cascade(label='Debug', menu=debug)

		# End game
		menubar.add_command(label='Quit', command=self.root.quit)

		# Attach menu
		self.root.config(menu=menubar)
		
		return menubar


	def bindEvents(self):
		''' '''
		self.root.bind('<Escape>', lambda e: self.root.quit())
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
		return namedtuple('Effects', ['lose', 'win'])(*map(mixer.Sound, ['data/strangled.wav', 'data/ding.wav']))
		#return namedtuple('Effects', ['lose'])(wave.open('data/hangman.wav'))


	def guess(self, letter):
		''' '''
		result = self.logic.guess(letter)
		
		self.log('Guessing %s. The guess is a %s' % (letter, result))

		self.graphics.guess(letter, result in ('MATCH', 'WIN'), str(self.logic)), # TODO: Let Graphics take care of the representation for us (?)

		if result == 'WIN':
			self.win()
		elif result == 'LOSE':
			self.lose()
			self.bla = 'six'


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
		''' '''
		print('\n{0}\n{1:^40}\n{0}\n'.format('-'*40, 'NEW GAME'))
		self.graphics.showHint('It starts with a letter.')

		self.word, self.hint = next(self.wordFeed)
		self.graphics.showHint(self.hint)

		self.logic.newGame(self.word)
		self.graphics.play(str(self.logic))

		self.validState = True # Ready to accept guesses again


	def createWordFeed(self, dictionary):
		''' '''
		# TODO: Give class a reference to words (?)
		# NOTE: Currently, the entire file is kept in memory
		with open(dictionary, 'r') as wordFile:
			words = wordFile.read().split('\n')
		while True:
			#yield choice('treasury|laconic|forboding'.split('|'))
			yield choice(words).split('|') # Word|Hint


	def log(self, *args, **kwargs):
		''' '''
		DEBUG = True # TODO: Make instance-setting
		if DEBUG: print('(Hangman) ', *args, **kwargs)



if __name__ == '__main__':
	Hangman().play()