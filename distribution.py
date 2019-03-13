class DDist:
    def __init__(self, dictionary):
        _sum_vals = sum(dictionary.values())
        if abs(_sum_vals - 1) > 1e-6:
            _e = "Probabilities must sum to 1, not %f\n%r"
            raise Exception(_e % (_sum_vals, dictionary))
        _min = min(dictionary.items(), key=lambda x: x[1])
        if _min[1] < 0:
            e = "Probabilities must be nonnegative (element %r has value %f)\n%r"
            raise Exception(e % (_min + (dictionary,)))
        self.d = dictionary

    def prob(self, elt):
        if elt in self.d.keys():
            return self.d[elt]
        return 0

    def support(self):
        newList = []
        for i in self.d:
            if self.d[i] != 0:
                newList.append(i)
        return newList

    def __repr__(self):
        return "DDist(%r)" % self.d
    
    __str__ = __repr__

    def project(self, map_func):
        newDict = {}
        for i in self.support():
            try:
                newDict[map_func(i)] += self.prob(i)
            except:
                newDict[map_func(i)] = self.prob(i)
        return DDist(newDict)

    def condition(self, test_func):
        newDict = {}
        total = 0
        for i in self.support():
            if test_func(i):
                newDict[i] = self.prob(i)
        for i in newDict:
            total += newDict[i]
        for i in newDict:
            newDict[i] = newDict[i] / total
        return DDist(newDict)

def make_joint_distribution(pr_A, pr_B_given_A):
    newDict = {}
    for i in pr_A.support():
        newDist = pr_B_given_A(i)
        for j in newDist.support():
            newDict[(i,j)] = pr_A.prob(i) * newDist.prob(j)
    return DDist(newDict)

def total_probability(pr_A, pr_B_given_A):
    newDist = make_joint_distribution(pr_A, pr_B_given_A)
    newDict = {}
    for i in newDist.support():
        try:
            newDict[i[1]] += newDist.prob(i)
        except:
            newDict[i[1]] = newDist.prob(i)
    return DDist(newDict)

def bayes_rule(pr_A, pr_B_given_A, b):
    newDict = {}
    listA = pr_A.support()
    newJointDist = make_joint_distribution(pr_A, pr_B_given_A)
    print(newJointDist)
    newJointDist = newJointDist.condition(lambda x:  x[1] == b)
    print(newJointDist)
    for i in range(len(listA)):
        newDict[listA[i]] = newJointDist.prob(newJointDist.support()[i])
    return DDist(newDict)


### Test Cases:

### Test case 1
##print("First test of prob method")
##print('Expected:', [0.3,0.5,0.1,0.1])
##x = DDist({'b':0.3, 'c':0.5, 'd':0.1, 'e':0.1})
##result = [x.prob(i) for i in ['b', 'c', 'd', 'e']]
##print('Received:', result)
##
### Test case 2
##print()
##print("Test that d.prob(x) is 0 if x is not in the DDist d")
##print('Expected:', [0,0,0,0])
##result= [x.prob(i) for i in ['a', 'x', 'z', 'y']]
##print('Received:', result)
##
### Test case 3
##print()
##print("First test of support method")
##print('Expected:', ['b', 'c', 'd', 'e'])
##x = DDist({'b':0.3, 'c':0.5, 'd':0.1, 'e':0.1})
##result = list(sorted(x.support()))
##print('Received:', result)
##
### Test case 4
##print()
##print("Second test of support method")
##print('Expected:', False)
##x = DDist({'b':0.3, 'c':0.5, 'd':0.1, 'e':0.1})
##result = 'B' in x.support()
##print('Received:', result)
##
### Test case 5
##print()
##print("Test that d.support() does not contain elements with zero probability")
##x = DDist({'b':0, 'c':0.5, 'd':0, 'e':0.5})
##result = 'b' in x.support() or 'd' in x.support()
##print('Expected:', False)
##print('Received:', result)
##
### Test case 6
##print()
##print("Test for make_joint_distribution")
##print("Expected: ", DDist({(True, "cat"): 0.07,
##                           (True, "dog"): 0.03,
##                           (False, "cat"): 0.18,
##                           (False, "dog"): 0.72}))
##pr_X = DDist({True: 0.1, False: 0.9})
##def pr_Y_given_X(x):
##    if x:
##        return DDist({"cat": 0.7, "dog": 0.3})
##    else:
##        return DDist({"cat": 0.2, "dog": 0.8})
##print("Received:", make_joint_distribution(pr_X, pr_Y_given_X))
##
### Test case 7
##print()
##print("Additional test(s) for make_joint_distribution")
##print("Expected: ", DDist({(0,6):0.14, (0,7):0.56, (1,6):0.27, (1,7):0.03}))
##pr_A = DDist({0 : .7, 1: .3})
##def pr_B_given_A(a):
##    assert a in (0, 1)
##    if a == 1:
##        return DDist({6 : .9, 7 : .1})
##    else:
##        return DDist({6 : .2, 7 : .8})
##print('Received:', make_joint_distribution(pr_A, pr_B_given_A))
##
### Test case 8
##print()
##print("Test for project")
##print('Expected:', DDist({"small": 0.2, "big": 0.8}))
##x = DDist({0: 0.1, 1: 0.05, 2: 0.05, 2000: 0.1, 15: 0.7})
##def map_func(x):
##    if x < 10:
##        return "small"
##    else:
##        return "big"
##result = x.project(map_func)
##print('Received:', result)
##
### Test case 9
##print()
##pr_X = DDist({-2: .1, 2: .3, -1: .4, 1: .1, 3: .1})
##def square(x): return x*x
##pr_Xsquared = pr_X.project(square)
##print("Test case for projection, using square")
##print('Expected:', "DDist({4:0.4, 1:0.5, 9:0.1})")
##print('Received:', pr_Xsquared)
##
### Test case 10
##print()
##print("Test for condition")
##print('Expected:', DDist({2000: 0.4, 5: 0.6}))
##x = DDist({0: 0.1, 1: 0.1, 2: 0.3, 2000: 0.2, 5: 0.3})
##def should_keep(x):
##    return x >= 5
##result = x.condition(should_keep)
##print('Received:', result)
##
### Test case 11
##print()
##pr_X = DDist({-2: .1, 2: .3, -1: .4, 1: .1, 3: .1})
##def pos(x): return x > 0
##pr_Xpos = pr_X.condition(pos)
##print("Additional test case(s) for condition")
##print('Expected:', "DDist({2:0.6, 1:0.2, 3:0.2})")
##print('Received:', pr_Xpos)
##
### Test case 12
##print()
##print("Test for total_probability")
##print("Expected: ", DDist({"cat": 0.25,
##                           "dog": 0.75}))
##pr_X = DDist({True: 0.1, False: 0.9})
##def pr_Y_given_X(x):
##    if x:
##        return DDist({"cat": 0.7, "dog": 0.3})
##    else:
##        return DDist({"cat": 0.2, "dog": 0.8})
##print("Received:", total_probability(pr_X, pr_Y_given_X))
##
### Test case 13
##print()
##pr_A = DDist({0 : .7, 1: .3})
##def pr_B_given_A(a):
##    assert a in (0, 1)
##    if a == 1:
##        return DDist({6 : .9, 7: .1})
##    else:
##        return DDist({6 : .2, 7 : .8})
##print("Additional test case(s) for total_probability")
##print('Expected:', "DDist({6: 0.41, 7:0.59})")
##print('Received:', total_probability(pr_A, pr_B_given_A))

# Test case 14
print()
print("Test(s) for bayes_rule")
pr_A = DDist({'walksUnlikeADuck': 0.9, 'walksLikeADuck': 0.1})
def pr_B_given_A(a):
    if a == "walksUnlikeADuck":
        return DDist({'talksUnlikeADuck': 0.8, 'talksLikeADuck': 0.2})
    else:
        return DDist({'talksUnlikeADuck': 0.3, 'talksLikeADuck': 0.7})
print('Expected:', "I don't know")
print('Received:', bayes_rule(pr_A, pr_B_given_A, "talksUnlikeADuck"))

