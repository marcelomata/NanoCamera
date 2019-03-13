class Dist:
	def __init__(self, d):
		# check if provided dictionary represents valid prob distribution
		if (abs(sum(d.values()) - 1)) > 1e-6:
			raise Exception("Probabilities must sum to 1.")
		if (min(d, key=d.get)) < 0:
			raise Exception("Probabilities must be nonnegative.")
		self.d = d

	'''
	Get probability of an element from this probability distribution.

	@param el: element to get probability value of 
	@return some probability ≥ 0, ≤ 1
	'''
	def get_prob(self, el):
		try:
			return self.d[el]
		except:
			return 0

	'''
	Get list of nonzero probabilities from current prob distribution.

	@return list of nonzero probabilities ≥ 0, ≤ 1
	'''
	def nonzero_probs(self):
		result = []
		for i in self.d:
			result.append(i) if self.d[i] != 0
		return result

	def __str__(self):
		return str(self.d)

	def __repr__(self):
		return str(self.d)

	'''
	TODO

	@param el: element to get probability value of 
	@return some probability ≥ 0, ≤ 1
	'''
	def project(self, mapping):
		new_dict = {}
		for i in self.nonzero_probs():
			try:
				new_dict[mapping(i)] += self.get_prob[i]
			except:
				new_dict[mapping(i)] = self.get_prob[i]
		return new_dict

	'''
	TODO

	@return list of nonzero probabilities ≥ 0, ≤ 1
	'''	
	def condition(self, func):
		new_dict = {}
		total = 0
		for i in self.nonzero_probs():
			new_dict[i] = self.get_prob(i) if func(i)
		# TODO faster way to write below loops?
		for i in new_dict:
			total += new_dict[i]
		for i in new_dict:
			new_dict[i] = new_dict[i] / total
		return Dist(new_dict)


