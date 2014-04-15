import itertools, math, collections

# Constants
VERY_C = 0
CONSISTENT = 0
VERY_I = 2
INCONSISTENT = 1
MEDIUM = 1
HIGH = math.sqrt(2)
LOW = math.sqrt(2) / 2


class ACH:
    def __init__(self):
        self.matrix = {}
        self.hypotheses = {}
        self.evidences = {}

    def add_hypothesis(self, content=None):
        h = Hypothesis(self, content)
        self.hypotheses[h.sn] = h
        self.matrix[h.sn] = {}
        return h.sn

    def add_evidence(self, cred=None, rel=None, content=None):
        e = Evidence(self, content, cred=cred, rel=rel)
        self.evidences[e.sn] = e
        return e.sn

    def get_h_cells(self, hypo):
        return (cell for _, cell in self.matrix[hypo].items())

    def get_e_cells(self, evidence):
        return (row[evidence] for _, row in self.matrix.items())

    def rate(self, h, e, rating):
        if not self.matrix[h].get(e):
            self.matrix[h][e] = Cell( self.hypotheses[h], self.evidences[e], rating=rating)
        else:
            self.matrix[h][e].rating = rating

    def score(self, hypo):
        return sum(cell.score() for cell in self.get_h_cells(hypo))

class Evidence:
    serializer = itertools.count()
    def __init__(self, ach, content, cred=None, rel=None):
        self.sn = 'E'+str(next(Evidence.serializer))
        self.credibility = cred
        self.relevance = rel
        self.content = content

    def __repr__(self):
        return "Evidence {}".format(self.sn)

    def __str__(self):
        return "Evidence: {}".format(self.content)

class Hypothesis:
    """
    >>> a = ACH()
    >>> a.add_hypothesis(content="Rasputin was Jesus")
    'H0'
    >>> a.add_hypothesis(content="Rasputin was a crook")
    'H1'
    >>> a.add_evidence(cred=HIGH, rel=HIGH, content="He was drowned in the river")
    'E0'
    >>> a.add_evidence(cred=MEDIUM, rel=HIGH, content="He survived murder attempts")
    'E1'
    >>> a.rate('H1', 'E0', INCONSISTENT)
    >>> a.rate('H1', 'E1', VERY_C)
    >>> a.rate('H0', 'E0', VERY_C)
    >>> a.rate('H0', 'E1', CONSISTENT)
    >>> a.score('H0')
    0.0
    >>> a.score('H1')
    2.0000000000000004
    """

    serializer = itertools.count()
    def __init__(self, ach, content):
        self.sn = 'H'+str(next(Hypothesis.serializer))
        self.content = content
        self.ach = ach

    def __repr__(self):
        return "Hypothesis {}".format(self.sn)

    def __str__(self):
        return "Hypothesis: {}".format(self.content)

class Cell:
    def __init__(self, hypo, evidence, rating=None):
        self.evidence = evidence
        self.hypo = hypo
        self.rating = rating

    def score(self):
        return self.evidence.relevance * self.evidence.credibility * self.rating

if __name__ == "__main__":
    import doctest
    doctest.testmod()