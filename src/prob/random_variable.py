import math
import numpy
import random
import scipy
import scipy.stats


class RandomVariable():
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value


class Normal(RandomVariable):
    def __init__(self, mu, sigma):
        super().__init__(min_value=-numpy.inf, max_value=numpy.inf)

        self.mu = mu
        self.sigma = sigma

        self.dist = scipy.stats.norm(mu, sigma)

    def __repr__(self):
        return f"Normal(mu= {self.mu}, sigma= {self.sigma})"

    def cdf(self, x):
        return self.dist.cdf(x)

    def tail(self, x):
        return 1 - self.cdf(x)

    def mean(self):
        return self.mu

    def sample(self):
        return self.dist.rvs(size=1)[0]


class TruncatedNormal(RandomVariable):
    def __init__(self, mu, sigma):
        super().__init__(min_value=0, max_value=numpy.inf)

        self.mu = mu
        self.sigma = sigma

        lower, upper = 0, mu + 10*sigma
        self.max_value = upper
        self.dist = scipy.stats.truncnorm(
            a=(lower - mu)/sigma, b=(upper - mu)/sigma, loc=mu, scale=sigma
        )

    def __repr__(self):
        return f"TruncatedNormal(mu= {self.mu}, sigma= {self.sigma})"

    def to_latex(self):
        return r'N^+({}, {})'.format(self.mu, self.sigma)

    def cdf(self, x):
        return self.dist.cdf(x)

    def tail(self, x):
        return 1 - self.cdf(x)

    def mean(self):
        return self.dist.mean()

    def std(self):
        return self.dist.std()

    def sample(self):
        return self.dist.rvs(size=1)[0]


class Exponential(RandomVariable):
    def __init__(self, mu, D=0):
        super().__init__(min_value=D, max_value=numpy.inf)
        self.D = D
        self.mu = mu

    def __repr__(self):
        return (
            "Exponential( \n"
            f"\t D= {self.D} \n"
            f"\t mu= {self.mu} \n"
            ") \n"
        )

    def to_latex(self):
        if self.D == 0:
            return r"Exp(\mu={})".format(self.mu)

        return r"{} + Exp(\mu={})".format(self.D, self.mu)

    def tail(self, x):
        if x <= self.min_value:
            return 1

        return math.exp(-self.mu*(x - self.D) )

    def cdf(self, x):
        if x <= self.min_value:
            return 0

        return 1 - math.exp(-self.mu*(x - self.D) )

    def pdf(self, x):
        if x <= self.min_value:
            return 0

        return self.mu*math.exp(-self.mu*(x - self.D) )

    def mean(self):
        return self.D + 1/self.mu

    def var(self):
        return 1/self.mu**2

    def moment(self, i):
        return moment_ith(i, self)

    def laplace(self, s):
        check(self.D > 0, "D should be 0", D=self.D)

        return self.mu/(s + self.mu)

    def sample(self):
        return self.D + random.expovariate(self.mu)


class Uniform(RandomVariable):
    def __init__(self, lb, ub):
        super().__init__(min_value=lb, max_value=ub)

        self.dist = scipy.stats.uniform(loc=lb, scale=ub-lb)

    def __repr__(self):
        return f"Uniform({self.min_value}, {self.max_value})"

    def sample(self):
        return self.dist.rvs()


class DiscreteUniform(RandomVariable):
    def __init__(self, lb, ub):
        super().__init__(min_value=lb, max_value=ub)

        self.v = numpy.arange(self.min_value, self.max_value+1)
        w_l = [1 for v in self.v]
        self.p = [w/sum(w_l) for w in w_l]
        self.dist = scipy.stats.rv_discrete(name='duniform', values=(self.v, self.p) )

    def __repr__(self):
        return f"DiscreteUniform({self.min_value}, {self.max_value})"

    def mean(self):
        return (self.max_value + self.min_value)/2

    def pdf(self, x):
        return self.dist.pmf(x)

    def cdf(self, x):
        if x < self.min_value:
            return 0
        elif x > self.max_value:
            return 1
        return self.dist.cdf(math.floor(x) )

    def tail(self, x):
        return 1 - self.cdf(x)

    def moment(self, i):
        return self.dist.moment(i)

    def sample(self):
        return self.dist.rvs() # [0]


class BoundedZipf(RandomVariable):
    def __init__(self, lb, ub, a=1):
        super().__init__(min_value=lb, max_value=ub)
        self.a = a

        self.v = numpy.arange(self.min_value, self.max_value+1) # values
        w_l = [float(v)**(-a) for v in self.v] # self.v**(-a) # weights
        self.p = [w/sum(w_l) for w in w_l]
        self.dist = scipy.stats.rv_discrete(name='bounded_zipf', values=(self.v, self.p) )

    def __repr__(self):
        return f"BoundedZipf([{self.min_value}, {self.max_value}], a= {self.a})"

    def pdf(self, x):
        return self.dist.pmf(x)

    def cdf(self, x):
        # if x < self.min_value: return 0
        # elif x >= self.max_value: return 1
        # else:
        #   return sum(self.p[:(x-self.min_value+1) ] )
        return self.dist.cdf(x)

    def inv_cdf(self, p):
        return self.dist.ppf(p)

    def tail(self, x):
        return 1 - self.cfd(x)

    def mean(self):
        # return sum([v*self.p(i) for i,v in enumerate(self.v) ] )
        return self.dist.mean()

    def sample(self):
        return self.dist.rvs(size=1)[0]
