#=============================================================================#
# AUTHOR: Jonatan Sundqvist													  #
# DATE: November 12 2013													  #
#																			  #
# NAME: SwiftUtils															  #
# TYPE: module																  #
# DESC: This module encapsulates a motley assortment of utility functions	  #
#=============================================================================#


#=======#  TEMPLATE  #========================================================#
#                                                                             #
#                                                                             #
#                                                                             #
#                                                                             #
#                                                                             #
#=============================================================================#


#=============================================================================#
# NAME: prettyDict														 	  #
# ARGUMENT(S): dict														 	  #
# 																	 	 	  #
# DESCRIPTION: Pretty prints a dictionary								 	  #
#=============================================================================#
def prettyDict(dictionary, delimit=True, heading=''):
	
	''' Pretty prints a dictionary with an optional heading and delimiter '''

	if delimit:
		print ('\n\n%s\n\n' % ('=' * 75))

	print(heading)

	for key, value in dictionary.items():
		print ('%s : %s' % (key, value))


def dictTable(dictionary, heading=('KEY', 'VALUE')):

	''' Represents a dictionary as a table '''
	
	# TODO: Optimize
	# TODO: Improve readability and comment
	# TODO: Enable user-options (eg. alignment, rowSep, colSep, tabs, etc.)
	# Excise redundant code
	# Multi-purpose table generator with arbitrary dimensions
	# Come up with more aesthetical block layouts

	# Parameters
	padding 	= 5 # Minimum padding size
	equalCols 	= True # Columns should be equally wide
	align		= '<^>'[1] # Left, centre, right

	entries = [heading] + [(str(key), str(value)) for key, value in dictionary.items()]
	longest = max([max(len(a), len(b)) for a, b in entries]) + 2*padding
	rowSep = '-'*(longest*2+3)

	#row = '|' + ('{:^%s}|' % longest)*2 # |{:align length}|{:align length}|
	row = '|{2:{1}{0}}|{3:{1}{0}}|' # The format string for each row

	table = '\n'.join([rowSep] + [row.format(longest, align, *entry) + '\n' + rowSep for entry in entries])

	print (table)


def createTable(*rows, **options):

	''' Creates a table string from any number of iterable rows '''

	# NOTE: Due to implementation details, the iterable must be compatible with the len function
	# This constraint will hopefully be removed in future versions
	assert hasattr(rows, '__len__'), 'Iterables of type \'%r\' are currently not supported. Use a list instead.' % type(rows)

	first, *rest = rows
	for row in rest: assert len(first) == len(row), 'The row \'%d\' has %d cells wheras it should have %d (use empty strings for padding)' % (row, len(row), len(first))

	# Configurable parameters
	parameters = {

		'padding' 	: 5, 			# Minimum padding size
		'evenWidth' : True,			# Width of columns should be even (currently ignored)
		'alignment' : '<^>'[1], 	# Left, centre, right

		'colsep': '|',  # Row separator
		'rowsep': '-'	# Column separator

	}

	parameters.update(options) # Override default parameters

	# Dangerous hack?
	#locals().update(parameters) # Seems not to work

	width = max(len(str(cell)) for row in rows for cell in row) + 2 * parameters['padding']
	
	rowLength = (width + 1) * len(first) + 1 # Number of characters in each row
	bar = '\n%s\n' % (parameters['rowsep'] * rowLength) 	 # Horizontal separator

	cellTemplate = '{%s:%s%d}' % ('%d', parameters['alignment'], width)
	rowTemplate = '{sep}{cells}{sep}'.format(**{'sep': parameters['colsep'], 'cells': parameters['colsep'].join([cellTemplate % n for n, v in enumerate(first) ])})

	return bar + bar.join(rowTemplate.format(*row) for row in rows) + bar


def blackhole(x, hole=[]):
	''' This function remembers every argument that is passed to it '''
	hole.append(x)
	return hole


def funcFactory(params):
	''' Generates a list of functions '''
	#funcList = [lambda e: print('%s likes %s' % (e, string)) for string in params]
	#paramList = {string: string for string in params}
	#funcList = {string: lambda e: print('Custom message: ', e, paramList[string]) for string in params}
	funcList = {}
	paramList = {}

	for string in params:
		def func(arg, msg=string):
			#func.__dict__.update(msg=string)
			print('Message: %s' % msg) # func.msg
			#print(func.__dict__)
		funcList[string] = func
	
	print(paramList)
	print(funcList)
	return funcList


#========================================================================#
# NAME: repeat													         #
# ARGUMENT(S): *times												     #
# 																	 	 #
# DESCRIPTION: This decorator repeats a function with an arbitrary       #
# signature a specified number of times                                  #
#========================================================================#
def repeat(*times):
	def wrapper(func):
		def loopFunc(*args):
			for i in range(*times):
				print('(%d)' % i, end=' ')
				func(*args)
		return loopFunc
	return wrapper


#========================================================================#
# NAME: doUntil							       						     # 
# ARGUMENT(S): condition												 #
# 																	 	 #
# DESCRIPTION: This decorator keeps performing a certain task            #
# as long as the given condition is met. The anticipated use case is     #
# creating interactive applications where a function (eg. PlayChess) is  #
# repeated until the user chooses the quit.                              #
#========================================================================#
def doUntil(condition):
	def wrapper(func):
		def until(*args, **kwargs):
			while condition:
				func(*args, **kwargs)
			return until
	return wrapper

# One-line quicksort
def qs(s): return (s if len(s)<2 else (qs([x for x in s[1:] if x<=s[0] ])+[s[0]]+qs([x for x in s[1:] if x>s[0]])))

# Approximates π
def calcPi(n):
	pi = 4
	prod = 0
	for i in range(n):
		prod += (1/(i*2 + 1))*([1, -1][i%2])
	return prod * pi

# Ordinal suffices
def ordinal(n):
	return ['th', 'st', 'nd', 'rd'][n%10 if n%10<4 and not (10<n%100<14) else 0]

# Integer to text
def triplet(n):
    units = [ 'zero', 'one', 'two', 'three', 'four',
    		  'five', 'six', 'seven', 'eight', 'nine',
    		  'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
    		  'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', '']

    tens = [ '', '', 'twenty', 'thirty', 'fourty', 'fifty',
    		 'sixty', 'seventy', 'eighty', 'ninety']

    big  = ['thousand', 'million', 'billion', 'trillion',
    		'quadrillion', 'quintillion', 'sextillion', 'septillion',
    		'octillion', 'nonillion', 'decillion', 'undecillion']
    
    digits = [int(x) for x in str(n)]
    parts = []
    # ' and '.join( ... )

    if digits[0] != 0:
    	digits.append('%s hundred ' % units[0])
    return	(nums[n//100] + ' hundred' if n >= 100 else '') + \
    		(' and ' if (n >= 100) and (n%100 != 0) else '') + \
    		nums[min(n%100, 20)] + tens[(n//10)%10] + ('-'+nums[n%10] if (n//10)%10 > 1 and n%10 > 0 else '')


class BaseConverter:

	''' Various implementations of base-10 to base-2 converters '''

	def first(self, n):
		dec = 0
		for place, digit in enumerate(n):
			dec += int(digit) * 2**(7 - place)
		return dec

	def second(self, n):
		mag = len(n) # Magnitude
		return sum(int(digit) * 2**(mag - place) for place, digit in enumerate(n))

	''' Various implementations of base-2 to base-10 converters '''


# Haskell-style list definitions with the Ellipsis
class HaskellList:
	def __init__(*args):
		pass

# Witchcraft
@repeat(5)
def sayMyName(name):
	print('My name is %s.' % name)

# Lazy and unnecessary (needs to be reconsidered)
def entryPoint(func):
	if __name__ == '__main__':
		func()
	return func

# My implementation of Bunch (roughly equivalent to C-structs or namedtuple )
# NOTE: I believe the current implementation is not immutable
class Bunch:
	''' This utility class allows for dictionary lookups with the dot operator '''
	def __init__(self, **kwargs):
		self.__dict__.update(**kwargs)
	
# Thread decorator goes here
def async(func):
	pass

# Dynamic command invocation
def runtimeInvoke():
	pass

# Riemann zeta function
def ζ(n):
	return sum([1/(x**n) for x in range(1, 1000)])

# C-style printf implementation
def printf(frmt, *args):
	print(frmt % tuple(args))

def sprintf(frmt, *args):
	return frmt % tuple(args)

# Muffles overzealous debugging functions
def restrictInvocations(n):
	def wrapper(func):
		wrapper.calls = 0
		def silencer(*args, **kwargs):
			if wrapper.calls < n:
				wrapper.calls += 1
				func(*args, **kwargs)
			else:
				pass
		return silencer
	return wrapper


# Test for restrictInvocations()
@restrictInvocations(1)
def nag():
	print(', '.join(['bla'] * 5))


# Code utilities
def extractTODOs(fnFrom, fnTo, token='# TODO: ', header=True, append=False, end='\n', callback=None):
	# TODO: Add headlines with the origin of TODOs (✓)
	# TODO: Support markdown (.md) (...)
	# TODO: Find inlined TODOs as well (regex?)
	# re.sub(r'(\[\d+\])(.*)', r'**\1**\2', '[53] Change stuff')
	# TODO: Show context on hover (?)
	# TODO: Deal with nested TODO lists
	# TODO: Take status into account somehow (eg. ?, ...)
	# TODO: Extract project-specific logic (✓)
	# TODO: Callback for processing TODOs (?) (✓)
	# TODO: Return TODOs instead of writing them to file (?)


	callback = callback if (callback != None) else lambda N, TODO: '[%d] %s' % (N, TODO)
	mode = 'a+' if append else 'w+'
	
	with open(fnTo, mode, encoding='utf-8') as to, open(fnFrom, 'r', encoding='utf-8') as fr:
		
		if header:
			to.write('{0}{1}{2}{1}{1}'.format(fnFrom, end, '-'*len(fnFrom)))
		
		for N, ln in enumerate(fr.readlines(), 1):
			if ln.strip().startswith(token):
				to.write(callback(N, ln.strip().replace(token, '') + end))
		
		to.write(end) # Add newline


# Test suite
@entryPoint
def main():
	# Perform module tests or demonstrations hereWWW
	dictTable({'Hello': 'World', 'White': 'Wool', 'Monty': 'Python'})
	dictTable({'Question': 'To Be, or not to Be', 'Answer': 42, 'Why': 'Because'})
	dictTable({'Led Zeppelin': 'Stairway to Heaven', 'Rolling Stones': 'Satisfaction', 'U2': 'Sunday Bloody Sunday'}, ('BAND', 'SONG'))
	# dictTable({u'Δ': 'Delta'}) # TODO: Enable Unicode output to the ST2 console
	dictTable({ 'William Shakespeare': 'A Midsummer Night\'s Dream',
				'Oscar Wilde': 'The Importance of Being Earnest',
				'Henrik Ibsen': 'Peer Gynt',
				'August Strindberg': 'Miss Julie'}, ('PLAYWRIGHT', 'OPUS'))

	print(createTable([1, 2, 3], [4, 5, 6], [7, 8, 9]))
	print(createTable(['Country', 'Population', 'Capital'], ['Sweden', '9m', 'Stockholm'], ['Great Britan', '60m', 'London'], ['Urugay', '?', 'Montevideo']))

	for x in range(10):
		print(blackhole(x**2))

	funcs = funcFactory(['Fudge', 'Ice Cream', 'Fondue', 'Strawberry'])['Fondue']('Jonatan')
	print(funcs)

	sayMyName('Jonatan')

	printf('zeta(3) = %s', ζ(3))

	for i in range(10): nag()
