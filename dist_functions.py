'''
Create joint distribution of A and B.

@param prA: probability distribution of A 
@param prB_givenA: function constructing probability B given A value prob.
@return new probability distribution representing joint distribution of A and B.
'''
def joint_distribution(prA, prB_givenA):
    new_dict = {}
    for i in prA.nonzero_probs():
        # get all P(b|a)
        new_dist = prB_givenA(i)
        for j in new_dist.nonzero_probs():
            # P(a, b) = P(a) * P(b|a)
            new_dict[(i,j)] = prA.prob(i) * new_dist.prob(j)
    return Dist(new_dict)

'''
Create total probability distribution of B.

@param prA: probability distribution of A 
@param prB_givenA: function constructing probability B given A value prob.
@return new probability distribution representing total distribution of B.
'''
def total_prob(prA, prB_givenA):
    # get all P(a, b)
    new_dist = joint_distribution(prA, prB_givenA)
    new_dict = {}
    for i in new_dist.nonzero_probs():
        # P(b) = summation(P(a) * P(b|a))
        try:
            new_dict[i[1]] += new_dist.prob(i)
        except:
            new_dict[i[1]] = new_dist.prob(i)
    return Dist(new_dict)

'''
TODO

@param prA: probability distribution of A 
@param prB_givenA: function constructing probability B given A value prob.
@param b: evidence of random variable B
@return new probability distribution representing total distribution of A and B.
'''
def bayes_rule(prA, prB_givenA, b):
    new_dict = {}
    a_nonzero_prob = prA.nonzero_probs()
    new_joint_dist = joint_distribution(prA, prB_givenA)
    # 
    new_joint_dist = new_joint_dist.condition(lambda x:  x[1] == b)
    for i in range(len(a_nonzero_prob)):
        new_dict[a_nonzero_prob[i]] = new_joint_dist.prob(new_joint_dist.nonzero_probs()[i])
    return Dist(new_dict)

'''
Make a distribution from mixture of given distributions

todo params
'''
def mixture_dist(d1, d2, p):
    dist1 = d1.nonzero_probs()
    dist2 = d2.nonzero_probs()
    dist_dict = {}
    # iterate through dist1
    for i in dist1:
        if i in dist2:
            dist_dict[i] = p*dist1[i]+(1-p)*dist2[i]
        else:
            dist_dict[i] = p*dist1[i]
    #iterate through dist2 for things not present
    for j in dist2:
        if j not in dist_dict:
            if j in dist2:
                dist_dict[j] = p*dist1[j]+(1-p)*dist2[j]
            else:
                dist_dict[j] = (1-p)*dist2[j]
    return Dist(dist_dict)
'''
Make a uniform distribution

todo params
'''
def uniform_dist(li):
    dist_dict  = {}
    # each element has probability 1/(num elements)
    for i in li:
        dist_dict[i] = 1/len(li)
    return Dist(dist_dict)

'''
Make a triangular distribution

todo params
specify half-width
'''
def triangle_dist(peak, width):
    dist_dict = {}
    a = peak-width
    b = peak+width
    for i in range(a+1, b):
        if i < peak:
            dist_dict[i] = 2*(i-a)/((b-a)*(peak-a))
        else:
            dist_dict[i] = 2*(b-i)/((b-a)*(b-peak))
    return Dist(dist_dict)


