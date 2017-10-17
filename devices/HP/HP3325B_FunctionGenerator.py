import visa




class function_generator():
	def __init__(self):
		print "test"
		self.frequency = 10000 # in Hz
		self.FuncGen = visa.instrument("GPIB::17", timeout=None) #Function Generator
		self.FuncGen.write("*RST")
		print self.FuncGen.write('FR200KH')
		print self.FuncGen.write('AM0VO')
		
		print self.FuncGen.ask('FR?')
	def test(self):
		self.FuncGen = visa.instrument("GPIB::17", timeout=None) #Function Generator
		print self.FuncGen.ask('FR?')
		#print self.FuncGen.write('FR10kHz')
		
		
obj = function_generator()
#obj.test()
		
		
