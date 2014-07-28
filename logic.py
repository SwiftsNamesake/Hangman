#
# Hangman - Logic
# Jonatan H Sundqvist
# July 9 2014
#

# TODO | - Add test suite in main (?)
#		 - Debugging, logging, assertions
#		 - Support for whitespace, punctuation, Unicode
#		 	-- Whitespace and puncuation should be revealed by default, toggled by setting
#		 - Validate input in this module (✗)
#		 	-- This module should not concern itself with character sets
#		 - Query functions (unguessed, wrong, correct, etc.)

# SPEC | - Underscores (_) are used to represent remaining letters internally (unwise?)
#		 - Guesses are case-insensitive (setting?)
#		 - Guesses are stored in lower-case
#		 - Both lower-case and upper-case letters are allowed in words
#		 - Words must only contain the twenty-six letters of the English alphabet and spaces (for now)
#		 	-- This constraint will definitely be removed in later versions.
#		 	-- This module should not impose any hard-coded limitations on input


from collections import namedtuple 	# Game state
from enum import Enum				# Game phases (currently not used)
from string import ascii_uppercase 	# Allowed characters (cf. SPEC)


class Logic:
	
	'''
	Docstring goes here

	'''

	class Phases:
		ONGOING = 0
		LOST = 1
		WON = 2
	

	def __init__(self, chances):
		''' '''
		#
		self.chances = chances  # Wrong guesses allowed before losing
		self.state 	 = None 	# Initialized when starting a new game

		# Internal settings
		self.DEBUG = True # TODO: Make instance-setting (✓)

		# Game settings
		self.characterSet 	= ascii_uppercase 		# TODO: Implement character set support (?)
		self.nonLetters 	= set(" \t\n,.;:'*-_")	# TODO: Use a Unicode regex instead (?)
		self.ignoreCase 	= True 					# Treat lowercase and uppercase as the same letter (cf. normalize)
		self.showNonLetters	= True 					# Show whitespace and punctuation immediately


	def createState(self, word):
		''' '''
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
		''' Create a new game and replace the previous one '''
		# TODO: Find a more appropriate name
		self.state = self.createState(word) # Replace the old state
		
		if self.showNonLetters:
			for char in self.state.unique & self.nonLetters:
				self.addMatch(char)


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


	def log(self, *args, identify=True, **kwargs):
		''' Prints any number of messages, with optional context (class name, line number) '''
		# TODO: Different categories (eg. error, log, feedback)
		if self.DEBUG:
			print('(Logic) [%s] ' % getouterframes(currentframe())[1][2] if identify else '', end='')
			print(*args, **kwargs)

		#self.messages += [msg for msg in args]


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