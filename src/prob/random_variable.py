import math
import numpy
import random
import scipy
import scipy.stats


class RandomVariable():
    def __init__(self, min_value: float, max_value: float):
        self.min_value = min_value
        self.max_value = max_value


class Normal(RandomVariable):
    def __init__(self, mu: float, sigma: float):
        super().__init__(min_value=-numpy.inf, max_value=numpy.inf)

        self.mu = mu
        self.sigma = sigma

        self.dist = scipy.stats.norm(mu, sigma)

    def __repr__(self):
        return f"Normal(mu= {self.mu}, sigma= {self.sigma})"

    def cdf(self, x: float) -> float:
        return self.dist.cdf(x)

    def tail_prob(self, x: float) -> float:
        return 1 - self.cdf(x)

    def mean(self) -> float:
        return self.mu

    def sample(self) -> float:
        return self.dist.rvs(size=1)[0]


class TruncatedNormal(RandomVariable):
    def __init__(self, mu: float, sigma: float):
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

    def to_latex(self) -> str:
        return r"N^+({}, {})".format(self.mu, self.sigma)

    def cdf(self, x: float) -> float:
        return self.dist.cdf(x)

    def tail_prob(self, x: float) -> float:
        return 1 - self.cdf(x)

    def mean(self) -> float:
        return self.dist.mean()

    def std(self) -> float:
        return self.dist.std()

    def sample(self) -> float:
        return self.dist.rvs(size=1)[0]


class Exponential(RandomVariable):
    def __init__(self, mu: float, D: float = 0):
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

    def to_latex(self) -> str:
        if self.D == 0:
            return r"Exp(\mu={})".format(self.mu)

        return r"{} + Exp(\mu={})".format(self.D, self.mu)

    def tail_prob(self, x: float) -> float:
        if x <= self.min_value:
            return 1

        return math.exp(-self.mu*(x - self.D) )

    def cdf(self, x: float) -> float:
        if x <= self.min_value:
            return 0

        return 1 - math.exp(-self.mu*(x - self.D) )

    def pdf(self, x: float) -> float:
        if x <= self.min_value:
            return 0

        return self.mu*math.exp(-self.mu*(x - self.D) )

    def mean(self) -> float:
        return self.D + 1/self.mu

    def var(self) -> float:
        return 1/self.mu**2

    def moment(self, i) -> float:
        return moment_ith(i, self)

    def laplace(self, s) -> float:
        check(self.D > 0, "D should be 0", D=self.D)

        return self.mu/(s + self.mu)

    def sample(self) -> float:
        return self.D + random.expovariate(self.mu)


class Uniform(RandomVariable):
    def __init__(self, min_value: float, max_value: float):
        super().__init__(min_value=min_value, max_value=max_value)

        self.dist = scipy.stats.uniform(loc=min_value, scale=max_value - min_value)

    def __repr__(self):
        return f"Uniform({self.min_value}, {self.max_value})"

    def sample(self) -> float:
        return self.dist.rvs()


class DiscreteUniform(RandomVariable):
    def __init__(self, min_value: float, max_value: float):
        super().__init__(min_value=min_value, max_value=max_value)

        self.value_list = numpy.arange(self.min_value, self.max_value + 1)
        weight_list = [1 for _ in self.value_list]
        self.prob_list = [weight / sum(weight_list) for weight in weight_list]
        self.dist = scipy.stats.rv_discrete(name="duniform", values=(self.value_list, self.prob_list))

    def __repr__(self):
        return f"DiscreteUniform({self.min_value}, {self.max_value})"

    def mean(self) -> float:
        return (self.max_value + self.min_value)/2

    def pdf(self, x: float) -> float:
        return self.dist.pmf(x)

    def cdf(self, x: float) -> float:
        if x < self.min_value:
            return 0
        elif x > self.max_value:
            return 1
        return self.dist.cdf(math.floor(x) )

    def tail_prob(self, x: float) -> float:
        return 1 - self.cdf(x)

    def moment(self, i: int) -> float:
        return self.dist.moment(i)

    def sample(self) -> float:
        return self.dist.rvs() # [0]


class BoundedZipf(RandomVariable):
    def __init__(self, min_value, max_value, a=1):
        super().__init__(min_value=min_value, max_value=max_value)
        self.a = a

        self.value_list = numpy.arange(self.min_value, self.max_value + 1)
        weight_list = [float(value)**(-a) for value in self.value_list]
        self.prob_list = [weight / sum(weight_l) for weight in weight_list]
        self.dist = scipy.stats.rv_discrete(name="bounded_zipf", values=(self.value_list, self.prob_list))

    def __repr__(self):
        return f"BoundedZipf([{self.min_value}, {self.max_value}], a= {self.a})"

    def pdf(self, x: float) -> float:
        return self.dist.pmf(x)

    def cdf(self, x: float) -> float:
        # if x < self.min_value: return 0
        # elif x >= self.max_value: return 1
        # else:
        #   return sum(self.prob_list[:(x-self.min_value+1)])
        return self.dist.cdf(x)

    def inverse_cdf(self, pob: float) -> float:
        return self.dist.ppf(prob)

    def tail_prob(self, x: float) -> float:
        return 1 - self.cfd(x)

    def mean(self) -> float:
        return self.dist.mean()

    def sample(self) -> float:
        return self.dist.rvs(size=1)[0]
