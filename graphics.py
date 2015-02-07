#
# Hangman - Graphics
# Jonatan H Sundqvist
# July 9 2014
#

# TODO | - Abstract Base Classes (?)
#			-- Or make this class generic enough for subclassing
#		 - Consolidate related methods
#		 - Classes for Word, Alphabet, Gallows (?)
#		 - Error handling, assertions
#		 - Allow for settings, such as colours, sizes, positions, and the like
#		 - Event handling facilities
#		 - Create separate Text class with individually configurable letters (?)
#		 - Allow for generic characterSets (...)
#

# SPEC | - Terminology
#		 	-- Word object: (internally a namedtuple wrapping a Canvas id) (should be renamed)
#		 	-- Word: The word to be guessed (internally a Word object)
#		 	-- Hint: A short sentence relaying some information about the word (internally a Word object)
#		 	-- Alphabet: The list of letters [A-Z] keeping track of guesses (internally a dict of Word objects)
#		 	-- Canvas: (internally a tkinter object used for drawing)


import tkinter as tk #

from utilities import rectangle, rotatedRect, createLogger, Rect, Size 	#
from collections import namedtuple 										#
from math import radians 												#
from string import ascii_uppercase 										#


class Graphics:

	'''
	Handles the drawing.

	'''

	Word = namedtuple('Word', ['word', 'id', 'pos', 'format']) # TODO: Rename, extract (?)

	# High-level interface
	def __init__(self, root, width, height, characterSet=ascii_uppercase):

		'''
		Docstring goes here
		
		'''
		
		# Initialize
		self.canvas = tk.Canvas(width=width, height=height, background='#D5FDF4')
		self.canvas.pack()
		self.size = Size(width, height)

		# Logging
		self.messages 	= []
		self.DEBUG 		= tk.BooleanVar(value=True)
		self.log 		= createLogger('Graphics', self.DEBUG, self.messages)

		# All parts in the correct order
		self.order = ('mound', 'pole', 'beam', 'corbel', 'rope', 'head', 'torso', 'LArm', 'RArm', 'LLeg', 'RLeg', 'noose')
		self.chances = len(self.order)

		# Styling
		# TODO: Extract defaults (?)
		self.wordDefaults 	  = {'anchor': tk.NW, 'width': self.size.width-20, 'fill': '#EE2233', 'font': 'Lucida 20'} 	 # Default formatting for words
		self.alphabetDefaults = {'anchor': tk.SW, 'width': self.size.width-20, 'fill': '#000', 'font': 'Lucida 10 bold'} # Default formatting for alphabet letters
		self.hintDefaults 	  = {'anchor': tk.NW, 'width': self.size.width-20, 'fill': '#000', 'font': 'Helvetica 10'} 	 # Default formatting for hints

		# 
		self.parts 			= self.createParts()	# Initially hidden
		self.feed 			= self.nextPart()		# Initialize parts generator
		self.characterSet 	= characterSet			# Allowed characters # TODO: Temporary fix for Swedish letters
		self.alphabet 		= self.createAlphabet()	# Shows which letters have been guessed

		# Word
		self.word = self.createWord('', (20, 20), **self.wordDefaults) # Initially empty
		self.hint = self.createWord('', (20, self.canvas.bbox(self.word.id)[3]+5), **self.hintDefaults)
		
		# TODO: Wrapping, adapting to Canvas size
		# TODO: Extract layout parameters (no hard-coded values)


	def play(self, word):
		''' Starts a new game '''
		#self.word.word = word
		#self.word.id = canvas.create_text()
		self.reset()
		self.setWord(word)


	def guess(self, letter, matched, word):
		''' Performs all actions needed to reflect a guess '''
		# TODO: Make it flexible, varargs, kwargs (?)
		self.setWord(word)
		if matched:
			self.configureLetter(letter, fill='#EEEEEE') # TODO: Tweak colour
		else:
			self.configureLetter(letter, fill='#FF0102') # TODO: Tweak colour
			self.buildNext()


	def showHint(self, hint):
		''' Displays a hint as a string '''
		self.word._replace(word=hint)						# Yuck, an underscore
		self.canvas.itemconfig(self.hint.id, text=hint)
		#self.configureWord(text=' '.join(l for l in hint))	# Insert spaces between letters


	# Gallows
	def createParts(self):

		''' Generates a dict with each part of the gallows '''

		# TODO: Extract hard-coded coordinates and simplify (helper functions?) (✓)

		# Unpack context
		cv = self.canvas	# Canvas
		w, h = self.size	# Width and height
		cx, cy = w//2+40, h//2 # Centre coordinates

		# Coordinates and parameters for all vertices
		mW, mH = 80, 40 # Mound
		pW, pH = 10, 80 # Pole
		bW, bH = 56, 10 # Beam

		cW, cH, dx, dy = 10, 10, 15, 15 # Corbel
		
		rW, rH = 2, 28 # Rope
		nW, nH = 4, 2  # Noose

		wHead, hHead,	 	= 12, 15 			 # Head
		wTorso, hTorso  	= 4, 24 			 # Torso
		wArm, hArm, θArm	= 1, 20, radians(45) # Arm
		wLeg, hLeg, θLeg 	= 2, 26, radians(25) # Leg


		# Coordinates
		mCoords = rectangle(cx, h+mH, mW, mH*2, snap='CB')					# Mound (double the height to account for 'clipping')
		pCoords = rectangle(cx, mCoords.top, pW, pH, snap='CB')				# Pole
		bCoords = rectangle(pCoords.left, pCoords.top, bW, bH, snap='LB') 	# Beam
		cCoords = ((pCoords.right, pCoords.top+dy), (pCoords.right+dx, bCoords.bottom), (pCoords.right+dx+cW , pCoords.top), (pCoords.right, pCoords.top+dy+cW)) # Corbel

		vX = bCoords.right - rW//2 # Centre X for victim

		rCoords = rectangle(bCoords.right, bCoords.bottom+1, rW, rH, snap='RT') # Rope
		hCoords = rectangle(vX, rCoords.bottom, wHead, hHead, snap='CT') 	 # Head
		nCoords = rectangle(vX, hCoords.bottom+2, nW, nH, snap='CT')	 	 # Noose
		tCoords = rectangle(vX, hCoords.bottom, wTorso, hTorso, snap='CT') 	 # Torso
	
		laCoords = rotatedRect(vX, hCoords.bottom+4, wArm, hArm,  θArm) # Left arm
		raCoords = rotatedRect(vX, hCoords.bottom+4, wArm, hArm, -θArm) # Right arm
	
		llCoords = rotatedRect(vX, tCoords.bottom, wLeg, hLeg,  θLeg) # Left leg
		rlCoords = rotatedRect(vX, tCoords.bottom, wLeg, hLeg, -θLeg) # Right leg

		return {
			# Structure
			'mound':  cv.create_arc(*mCoords, start=0, extent=180, fill='green', state=tk.HIDDEN),	# NOTE: Coordinates are given for the outlines of a presumptive full ellipse
			'pole':   cv.create_rectangle(*pCoords, outline='black', fill='brown', state=tk.HIDDEN),
			'beam':   cv.create_rectangle(*bCoords, outline='black', fill='brown', state=tk.HIDDEN),
			'corbel': cv.create_polygon(*cCoords, outline='black', fill='brown', state=tk.HIDDEN),

			# Victim
			'head':  cv.create_oval(*hCoords, outline='black', width=2, fill='white', state=tk.HIDDEN),
			'torso': cv.create_rectangle(*tCoords, outline='black', fill='black', state=tk.HIDDEN),
			'LArm':  cv.create_polygon(*laCoords, outline='black', fill='black', state=tk.HIDDEN),
			'RArm':  cv.create_polygon(*raCoords, outline='black', fill='black', state=tk.HIDDEN),
			'LLeg':  cv.create_polygon(*llCoords, outline='black', fill='black', state=tk.HIDDEN),
			'RLeg':  cv.create_polygon(*rlCoords, outline='black', fill='black', state=tk.HIDDEN),
			
			# Noose
			'rope': cv.create_rectangle(*rCoords, outline='#F3C785', width=1, fill='#F3C785', state=tk.HIDDEN),
			'noose': cv.create_rectangle(*nCoords, outline='#F3C785', width=1, fill='#F3C785', state=tk.HIDDEN) # NOTE: Due to issue with Z-indices, this has to be the at the bottom
		}


	def nextPart(self):
		''' Retrieves each part in order (generator) '''
		# TODO: Make sure this stays up to date
		for part in self.order:
			yield namedtuple('Part', ['part', 'id'])(part, self.parts[part])


	def buildPart(self, part):
		''' Builds (ie. shows) a particular component of the gallows '''
		self.configurePart(part, state=tk.NORMAL)


	def configurePart(self, part, **attributes):
		''' Configures any number of Canvas attributes for the specified part (id or name) '''
		self.canvas.itemconfig(self.parts[part] if isinstance(part, str) else part, **attributes)


	def buildNext(self):
		''' Builds (ie. shows) the next component of the gallows '''
		self.configurePart(next(self.feed).part, state=tk.NORMAL)


	def buildAll(self):
		''' '''
		for part in self.order:
			self.buildPart(part)


	def hideAll(self):
		''' '''
		for part in self.order:
			self.configurePart(part, state=tk.HIDDEN)


	# Alphabet
	def createAlphabet(self):
		''' '''
		# TODO: Margin, padding, etc. (...)
		# TODO: Itertools, chain, zip, etc.
		# TODO: Generic layout and character handling (...)
		
		rowLength 	= 13		# Characters per row
		padding 	= 15, 20 	# Distance between letters (X, Y)
		margin 		= 10, 10 	# Distance from canvas edge

		alphabet = {}
		rows 	 = reversed([self.characterSet[i:i+rowLength] for i in range(0, len(self.characterSet), rowLength)]) #('ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ')

		for Y, row in enumerate(rows):
			alphabet.update({ letter : self.createLetter(letter, (margin[0]+X*padding[0], self.size.height-margin[1]-padding[1]*Y)) for X, letter in enumerate(row) })

		return alphabet


	def changeCharacterSet(self, characterSet):
		''' Changes the character set and updates the alphabet  '''
		# TODO: Use tags and helper function (?)
		if self.characterSet != characterSet:
			self.log('Changing character set to %s!' % characterSet)
			self.characterSet = characterSet
			for key, value in self.alphabet.items():
				self.canvas.delete(value.id)
			self.alphabet = self.createAlphabet()


	def createLetter(self, letter, pos):
		''' Auxiliary function for createAlphabet '''
		return self.createWord(letter, pos, **self.alphabetDefaults)


	def configureLetter(self, letter, **options):
		''' Configures a letter in the alphabet '''
		self.configureText(self.alphabet[letter.upper()], **options)


	# Word
	def createWord(self, word, pos, **options):
		return Graphics.Word(word, self.canvas.create_text(pos, text=word, **options), pos, options)


	def configureWord(self, **options):
		''' Configures any number of properties of the word. To change the word itself, use setWord '''
		# TODO: Make generic (cf. setHint)
		self.configureText(self.word, **options)


	def setWord(self, word):
		''' Sets the new the word '''
		# TODO: Make generic (cf. setHint)
		self.word._replace(word=word) # Yuck, an underscore
		self.configureWord(text=word) # Insert spaces between letters

		# Adjust hint position
		# TODO: Extract to separate method (?)
		box = Rect(*self.canvas.bbox(self.word.id))
		self.canvas.coords(self.hint.id, *(box.left, box.bottom+5))
		#self.canvas.move(self.hint.id, 0, 20)



	# Auxiliary
	def reset(self):
		# Alphabet
		for letter in self.characterSet:
			self.configureLetter(letter, **self.alphabetDefaults)

		# Parts
		self.feed = self.nextPart()
		self.hideAll()

		# Word
		self.setWord('') # TODO: Decide if this is necessary


	def configureText(self, txt, **options):
		''' Configures a Word object (namedtuple) '''
		# NOTE: Only works for Canvas properties
		txt.format.update(options)
		self.canvas.itemconfig(txt.id, **options)


	# def log(self, *args, **kwargs):
	# 	''' '''
	# 	DEBUG = True # TODO: Make instance-setting
	# 	if DEBUG:
	# 		print('(Graphics) ', *args, **kwargs)



def test():

	''' '''

	R = tk.Tk()
	R.geometry('%dx%d' % (400, 400))
	G = Graphics(R, 400, 400)

	def onKeyUp(e):
		print('Releasing %s' % e.char)
		G.configureLetter(e.char, fill='orange', font='Lucida 10')

	def onKeyDown(e):
		print('Pressing %s' % e.char)
		G.configureLetter(e.char, fill='purple', font='Lucida 12 bold')

	G.buildAll()
	#G.configurePart('head', fill='orange', width=3)
	#G.play('clandestine')

	R.bind('<KeyRelease>', onKeyUp)
	R.bind('<Key>', onKeyDown)

	R.mainloop()


if __name__ == '__main__':
	test()