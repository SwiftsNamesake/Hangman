#
# Hangman - Utilities
# Jonatan H Sundqvist
# July 10 2014
#

# TODO | -
#		 -

# SPEC | -
#		 - 


import tkinter as tk

from collections import namedtuple
from math import sin, cos


Rect = namedtuple('Rect', 'left top right bottom')
Size = namedtuple('Size', 'width, height')
Point = namedtuple('Point', 'x y')


def rectangle(x, y, w, h, snap='CB'):

	''' Calculates rectangle coordinates based on a fixpoint (X-centre and Y-bottom by default), width and height '''

	# TODO: Use named tuples (?) (✓)
	# TODO: Explain the arguments more thoroughly, allow for flexibility

	left, top = {'L': x, 'C': x-w//2, 'R': x-w}[snap[0]], {'T': y, 'C': y-h//2, 'B': y-h}[snap[1]] # Left, Centre, Right | Top, Centre, Bottom

	return Rect(left, top, left+w, top+h) # TODO: Extract class definition (?)


def rotatedRect(x, y, w, h, angle):

	''' Calculates the coordinates of a rotated rectangle '''

	# TODO: Clarify meaning of variables and arguments (illustration?)
	# TODO: Flexible arguments, error handling, validation
	# TODO: Move to SwiftUtils (?)
	# TODO: Use named tuples (?)

	# NOTE: Pivot is assumed to be centred on the short 'shoulder side', which is convenient when making limbs
	# NOTE: Angles should be given in radians

	dx, dy = round(w*cos(angle)), round(w*sin(angle)) # Distance from pivot (x,y) to closest vertices
	ox, oy = round(h*sin(angle)), round(h*cos(angle)) # Distance between pivot and the centre of the opposite edge

	return ((x-dx,  y-dy), (x+dx,  y+dy), (x+dx-ox, y+dy+oy), (x-dx-ox,  y-dy+oy)) # Left arm


class Text:

	# TODO: Callbacks
	# TODO: Animation (colours, movement, curves, etc.)
	# TODO: Apply styles to different regions
	# TODO: String manipulations (indeces, replace, regex, etc.)
	# TODO: Rename (?)

	def __init__(self, canvas, text, pos, style):
		self.canvas = canvas
		self.text = text
		self.pos = pos
		self.style = style

		self.id = canvas.create_text(pos, text=text, **style) # Canvas item id
		self.box = Rect(*self.canvas.bbox(self.id))  # Bounding box


	def set(self, text):
		''' Update contents '''
		self.text = text
		self.canvas.itemconfig(self.id, options)


	def setStyle(self, **options):
		''' Update Canvas styling options '''
		self.style.update(options)
		self.canvas.itemconfig(self.id, **options)


	def height(self):
		 return self.box.bottom - self.box.top


	def width(self):
		return self.box.right - self.box.left


	def move(self, x=None, y=None, dx=None, dy=None, anchor='NW'):
		''' '''
		# TODO: Use complex numbers instead (?)
		assert (x is None or dx is None) and (y is None or dy is None), 'Cannot set both relative and absolute coordinates for the same axis'
		
		dx = dx if x is 0 else x - {'W': self.box.left, 'E': self.box.right}
		dy = dy if y is 0 else y - {'N': self.box.top,  'W': self.box.bottom}

		self.canvas.coords(self.id, (self.box.left+dx, ))
		self.box = Rect(*self.canvas.bbox(self.id))


	def animate(self, root, duration, dt, **kwargs):
		''' Animates any number of smooth properties '''
		#colour = 255, 255, 255
		# TODO: Use generator (?)
		I = 255 # Colour intensity
		def onAnimate():
			nonlocal I
			self.setStyle(fill=('#%s' % (('%02x' % int(I))*3)))
			I -= (255 * dt / duration)
			if I >= 0: root.after(dt, onAnimate)
		onAnimate()


	def moveTo(self, x=None, y=None, anchor='NW'):
		pass


if __name__ == '__main__':
	# Text
	root = tk.Tk()
	root.geometry('200x200')
	cvs = tk.Canvas(root, background='white')
	cvs.pack()

	text = Text(cvs, 'Fading...', (10, 10), { 'anchor': tk.NW, 'font': 'Helvetica 12' })
	text.animate(root, 6000, 1000//30)

	root.mainloop()