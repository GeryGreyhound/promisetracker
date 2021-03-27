import math
import common_functions
# function to generate lucas lehmer series
def lucas_lehmer_series(p):
	ll_seq = [4]
	if p>2:
		for i in range(1, (p-2)+1):
			n_i = ((ll_seq[i-1]) ** 2 - 2) % ((2 ** p) - 1)
			ll_seq.append(n_i)
	return ll_seq
# function to find whether number 'p' is prime or not
def is_prime(number):
	if number <= 1 or (number > 2 and number % 2 == 0):
		return False
	
	for factor in range(2, int(math.sqrt(number))+1):
		if number%factor == 0:
			return False
	return True
# primality test of mersenne number using above generated series
def ll_prime(p):
	if lucas_lehmer_series(p)[-1] == 0:
		return True
	return False

def benchmark(number_of_times=10):

	results = list()

	for x in range(number_of_times):
		sw1 = common_functions.StopWatch(name = "Stopwatch 1")
		series = lucas_lehmer_series(10000)
		sw1.stop()
		results.append(sw1.difference)

	print(results)

if __name__ == "__main__":
	benchmark()