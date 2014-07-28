# Hangman.py
#
# Jonatan H Sundqvist
# June 29 2014

# TODO | -
#		 -

# SPEC | - Initial Hangman implementation
#		 - Now defunct (cf. main.py and related modules)
 


import tkinter as tk
import time
from collections import namedtuple
from math import sin, cos, floor, radians


def createContext():
	
	''' Initializes the window and canvas '''

	# TODO: Allow for flexibility

	# Paremeters
	size = namedtuple('Size', ['width', 'height'])(400, 400)

	# Create and configure
	root = tk.Tk()
	root.geometry('%dx%d' % size)
	cv = tk.Canvas(bg='white', width=size.width, height=size.height) # TODO: Size to fit window automatically (?)
	cv.pack()

	# Bind events
	root.bind('<Escape>', lambda e: ctx.root.quit())

	return namedtuple('Context', ['root', 'canvas', 'size'])(root, cv, size)


def createParts(ctx):

	''' Generates a dict parts '''

	# TODO: Should this be a generator?
	# TODO: Extract hard-coded coordinates and simplify (helper functions?)
	# TODO: Caching, saving object IDs

	# Unpack context
	cv = ctx.canvas
	w, h = ctx.size
	cx, cy = w//2, h//2

	# Width and height for all components (widths are divided by two for convenience)
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


	def rectangle(x, y, w, h, snap='CB'):

		''' Calculates rectangle coordinates based on a fixpoint (X-centre and Y-bottom by default), width and height '''

		# TODO: Use named tuples (?)
		# TODO: Explain the arguments more thoroughly, allow for flexibility

		left, top = {'L': x, 'C': x-w//2, 'R': x-w}[snap[0]], {'T': y, 'C': y-h//2, 'B': y-h}[snap[1]] # Left, Centre, Right | Top, Centre, Bottom

		return namedtuple('rect', ['left', 'top', 'right', 'bottom'])(left, top, left+w, top+h) # TODO: Extract class definition (?)


	def rotatedRect(x, y, w, h, angle):

		''' Calculates the coordinates of a rotated rectangle '''

		# TODO: Clarify meaning of variables and arguments (illustration?)
		# TODO: Flexible arguments, error handling, validation
		# TODO: Move to SwiftUtils (?)
		# TODO: Use named tuples (?)

		# NOTE: Pivot is assumed to be centred on the short 'shoulder side', which is convenient when making limbs

		dx, dy = round(w*cos(angle)), round(w*sin(angle)) # Distance from pivot (x,y) to closest vertices
		ox, oy = round(h*sin(angle)), round(h*cos(angle)) # Distance between pivot and the centre of the opposite edge

		return ((x-dx,  y-dy), (x+dx,  y+dy), (x+dx-ox, y+dy+oy), (x-dx-ox,  y-dy+oy)) # Left arm


	# Coordinates
	mCoords = rectangle(cx, h+mH, mW, mH*2) 																													# Mound (double the height to account for 'clipping')
	pCoords = rectangle(cx, mCoords[1], pW, pH) 																												# Pole
	bCoords = rectangle(pCoords[0], pCoords[1], bW, bH, snap='LB') 																								# Beam
	cCoords = ((pCoords.right, pCoords.top+dy), (pCoords.right+dx, bCoords.bottom), (pCoords.right+dx+cW , pCoords.top), (pCoords.right, pCoords.top+dy+cW)) 	# Corbel

	vX = bCoords.right - rW//2

	rCoords = rectangle(bCoords[2], bCoords[3]+1, rW, rH, snap='RT') # Rope
	hCoords = rectangle(vX, rCoords[3], wHead, hHead, snap='CT') 	 # Head
	nCoords = rectangle(vX, hCoords[3]+2, nW, nH, snap='CT')	 	 # Noose
	tCoords = rectangle(vX, hCoords[3], wTorso, hTorso, snap='CT') 	 # Torso
	
	laCoords = rotatedRect(vX, hCoords[3]+4, wArm, hArm,  θArm) # Left arm
	raCoords = rotatedRect(vX, hCoords[3]+4, wArm, hArm, -θArm) # Right arm
	
	llCoords = rotatedRect(vX, tCoords[3], wLeg, hLeg,  θLeg) # Left leg
	rlCoords = rotatedRect(vX, tCoords[3], wLeg, hLeg, -θLeg) # Right leg

	return {
		# Structure
		'mound':  cv.create_arc(*mCoords, start=0, extent=180, fill='green', state=tk.HIDDEN),	# NOTE: Coordinates are given for the outlines of a presumptive full ellipse
		'pole':   cv.create_rectangle(*pCoords, outline='black', fill='brown', state=tk.HIDDEN),
		'beam':   cv.create_rectangle(*bCoords, outline='black', fill='brown', state=tk.HIDDEN),
		'corbel': cv.create_polygon(*cCoords, outline='black', fill='brown', state=tk.HIDDEN),
	
		# Noose
		'rope': cv.create_rectangle(*rCoords, outline='#F3C785', width=1, fill='#F3C785', state=tk.HIDDEN),
		'noose': cv.create_rectangle(*nCoords, outline='#F3C785', width=1, fill='#F3C785', state=tk.HIDDEN),

		# Victim
		'head':  cv.create_oval(*hCoords, outline='black', width=2, fill='white', state=tk.HIDDEN),
		'torso': cv.create_rectangle(*tCoords, outline='black', fill='black', state=tk.HIDDEN),
		'LArm':  cv.create_polygon(*laCoords, outline='black', fill='black', state=tk.HIDDEN),
		'RArm':  cv.create_polygon(*raCoords, outline='black', fill='black', state=tk.HIDDEN),
		'LLeg':  cv.create_polygon(*llCoords, outline='black', fill='black', state=tk.HIDDEN),
		'RLeg':  cv.create_polygon(*rlCoords, outline='black', fill='black', state=tk.HIDDEN)
	}


def createCards(cvs, word, padding=50+15j, **kwOptions):

	''' Creates a list of cards, one for each letter '''

	# TODO: Rename, better documentation
	# TODO: Make a class (?)
	# TODO: Immediate evaluation (?)
	# TODO: Error handling, flexible arguments, validation
	# TODO: Named tuples, multidicts (?)

	width, height, margin, pad = 14, 22, 10, padding

	options = {
		'text': '_',
		'justify': tk.CENTER,
		'fill': '#EE2233',
		'font': 'Lucida 20'
	}

	for key in kwOptions:
		assert key in options, 'Invalid key word \'{kw}\''.format(kw=key)

	options.update(**kwOptions)

	def makeCard(index, letter):
		L = cvs.create_text((pad.real+(margin+width)*index, pad.imag+height), **options) 	# Letter
		#B = cvs.create_rectangle(cvs.bbox(L), fill='#AA00FF')	 							# Background
		#cvs.tag_lower(B, L)
		return namedtuple('Card', ['id', 'letter'])(L, letter) # (L, B, letter)

	return [makeCard(N, L) for N, L in enumerate(word)]


def showCard(cvs, card):

	''' Shows the letter of a card '''

	if not isShown(cvs, card): # This check isn't really needed
		cvs.itemconfig(card.id, text=card.letter)


def isShown(cvs, card):
	return cvs.itemcget(card.id, 'text') != '_'


def hasWon(state):
	return len(state['unique']) == len(state['matches'])


def hasLost(state):
	return len(state['misses']) >= state['chances']


def isMatch(state, letter):
	return letter in state['word']


def nextPart(parts):

	''' Yields the function for each part in the correct order '''

	# TODO: Make sure this stays up to date

	for part in ('mound', 'pole', 'beam', 'corbel', 'rope', 'head', 'torso',  'LArm', 'RArm', 'LLeg', 'RLeg', 'noose'):
		yield parts[part]


def showNext(cvs, feed):

	''' Shows the next piece from the generator '''

	cvs.itemconfig(next(feed), state=tk.NORMAL)



def play(ctx, words):

	''' Plays the game once for each word '''

	# TODO: Implement reset, clean, win and lose, etc (replace onGuess temporarily?).
	# TODO: Figure out of to best deal with the asyncronous nature of tkinter
	# TODO: Error handling, argument validation
	# TODO: Debugging, logging
	# TODO: Menus, feedback, displaying an alphabet (green/red/black?), etc.
	# TODO: Choosing words, dictionaries, languages
	# TODO: Statistics, difficulty
	# TODO: Model-view controller, PyQT, Pyglet, graphics, animation, sound

	# Setup
	pieces = createParts(ctx)
	words = iter(words)

	# Initialize game state
	def newGame(word, pieces, cards=[]):

		''' '''

		# Any cards that are passed in will be destroyed

		print('\n{0}\n{1:^40}\n{0}\n'.format('-'*40, 'NEW GAME')) # TODO: Use formatting to centre (✓)
		
		for piece, ID in pieces.items():
			ctx.canvas.itemconfig(ID, state=tk.HIDDEN)

		for card in cards:
			ctx.canvas.delete(card.id) # Remove cards from last round

		return {

			'word': word,
			'feed': nextPart(pieces), # Yields each part in the correct order

			'cards': createCards(ctx.canvas, word),
			#'alpha': createCards(ctx.canvas, "ABCDEFGHIJKL", padding=50+55j),
			#'beta': createCards(ctx.canvas, "MNOPQRSTUVWXYZ", padding=50+95j),

			'chances': 	len(pieces.keys()), 	# Number of allowed guesses (exclusive)
			'guesses': 	0,						# Number of guessed letters
			'unique': 	set(word),				# Unique letters
			'misses': 	set(),					#
			'matches': 	set(),					#
			'prev': 	set()					# Previously guessed letters

		}

	def win(state):
		print('You\'ve won! Phew...')
		return newGame(next(words), pieces, state['cards'])

	def lose(state):
		print('You\'ve been hanged.')
		return newGame(next(words), pieces, state['cards'])

	state = newGame(next(words), pieces)

	# Play
	def onGuess(letter):
		
		''' '''

		# TODO: Refactor
		nonlocal state

		if letter in state['prev']:
			return # How to handle repeated guesses?
		else:
			state['prev'].add(letter)
			print('Guessing \'%s\'' % letter)

		if isMatch(state, letter): # TODO: Remove shown cards from the list (?)
			for card in filter(lambda c: c.letter == letter, state['cards']): # Show all matching cards
				print('Showing card')
				showCard(ctx.canvas, card)
			state['matches'].add(letter)
			if hasWon(state):
				state = win(state)
				return
		else:
			state['misses'].add(letter)
			showNext(ctx.canvas, state['feed']) # Draw next piece
			if hasLost(state): # Oh no!
				# TODO: Invoke lose function
				state = lose(state) # TODO: Cleanup, reset
				return

		print() # Add newline after completed guess
		state['guesses'] += 1

	# TODO: onKeyUp, onKeyDown
	cbID = ctx.root.bind('<Key>', lambda e: onGuess(e.char)) # Bind our guess function to the key event and store the callback ID


def main():

	''' Entry point (simple test script) '''

	ctx = createContext()
	play(ctx, ['dog', 'cat', 'mouse', 'zebra'])
	ctx.root.mainloop()


if __name__ == '__main__':
	main()