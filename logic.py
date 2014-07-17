#
# Hangman - Logic
# Jonatan H Sundqvist
# July 9 2014
#

# TODO | - Add test suite in main (?)
#		 - Debugging, logging, assertions
#		 - Support for whitespace, Unicode
#		 - Validate input in this module (?)

# SPEC | - Underscores (_) are used to represent remaining letters internally (unwise?)
#		 - Guesses are case-insensitive (setting?)
#		 - Guesses are stored in lower-case
#		 - Both lower-case and upper-case letters are allowed in words
#		 - Words must only contain the twenty-six letters of the English alphabet and spaces (for now)


from collections import namedtuple
from enum import Enum
from string import ascii_uppercase

class Logic:
	
	#Phases = Enum('Phase', 'ONGOING LOST WON') # Enum type representing the current phase of the game
	class Phases:
		ONGOING = 0
		LOST = 1
		WON = 2
		
	def __init__(self, chances):
		self.chances = chances  # Wrong guesses allowed before losing
		self.state 	 = None 	# Initialized when starting a new game
		self.characterSet = ascii_uppercase # TODO: Implement character set support


	def createState(self, word):
		return namedtuple('State', [
			'word',		# Word to be guessed
			'unique',	# Unique letters in the guess word
			'guesses',	# Number of guesses made
			'misses',	# Incorrect guesses
			'matches',	# Correct guesses
			'prev',		# Previously guessed letters (misses + matches)
			'phase'		# Current phase
		])(word, set(self.normalize(word)), 0, set(), set(), set(), Logic.Phases.ONGOING)


	def newGame(self, word):
		''' '''
		# TODO: Find a more appropriate name
		self.state = self.createState(word) # Replace the old state


	def guess(self, letter):
		''' '''
		
		# TODO: Deal with repeated guesses, winning and losing (...)
		# TODO: Add docstring
		# TODO: Explain return valus (Enums?)
		# TODO: Return multiple values (eg. 'MATCH|WIN' or 'MISS|LOSE') (?)

		letter = self.normalize(letter) # Normalize input

		if self.isMatch(letter):
			self.addMatch(letter)
			if self.hasWon():
				self.state._replace(phase=Logic.Phases.WON)
				return 'WIN'
			return 'MATCH'
		else:
			self.addMiss(letter)
			if self.hasLost():
				self.state._replace(phase=Logic.Phases.LOST)
				return 'LOSE'
			return 'MISS'


	def isMatch(self, letter):
		''' Determines if a normalized letter is a match '''
		return letter in self.state.unique


	def hasWon(self):
		''' Determines if the current game has been won '''
		return len(self.state.unique) == len(self.state.matches)


	def hasLost(self):
		''' Determines if the current game has been lost '''
		return len(self.state.misses) >= self.chances


	def addMiss(self, letter):
		''' Registers a normalized letter as a miss '''
		self.addGuess(letter)
		self.state.misses.add(letter)


	def addMatch(self, letter):
		''' Registers a normalized letter as a match '''
		# TODO: Use str.replace instead (?)
		self.addGuess(letter)
		self.state.matches.add(letter)


	def addGuess(self, letter):
		''' Registers a normalized letter as guessed '''
		self.state.prev.add(letter)
		self.state._replace(guesses=self.state.guesses+1)


	def hasGuessed(self, letter):
		''' Determines if a letter has already been guessed '''
		# TODO: Extract case-insensitive logic (?)
		return self.normalize(letter) in self.state.prev


	def normalize(self, letter):
		''' Normalizes a guess for comparison purposes '''
		return letter.lower()


	def log(self, *args, **kwargs):
		''' '''
		DEBUG = True # TODO: Make instance-setting
		if DEBUG: print('(Logic) ', *args, **kwargs)


	def __repr__(self):
		''' Currently the same as __str__ '''
		# TODO: Create a more complete representation instead, including ancillary data (?) (✓)
		return 'progress={0!r}, misses={1!r}, matches={2!r}, chances={3!d}'.format(str(self), self.state.misses, self.state.matches, self.chances)


	def __str__(self):
		''' Printable version '''
		return ' '.join(letter if self.hasGuessed(letter) else '_' for letter in self.state.word)


	#def __getattr__(self, attr):
	#	print(attr)
	#	return attr