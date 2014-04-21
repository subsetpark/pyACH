import itertools, math, collections, copy

# Constants
VERY_C = 0
CONSISTENT = 0
VERY_I = 2
INCONSISTENT = 1
MEDIUM = 1
HIGH = math.sqrt(2)
LOW = math.sqrt(2) / 2

DEBUG = False

session_id = itertools.count()

class ACH:
    def __init__(self):
        self.sn = 'A' + str(next(session_id))
        self.matrix = {}
        self.hypotheses = {}
        self.evidences = {}
        self.h_serializer = itertools.count()
        self.e_serializer = itertools.count()
        if DEBUG:
            print("created new ACH session {}".format(self.sn))

    def debug(self):
        print("""
            {} current state
            evidence: {}
            hypotheses: {}
            matrix: {}
            """.format(self.sn, self.evidences, self.hypotheses, self.matrix))

    def __str__(self):
        return "Analysis of Competing Hypotheses: \n{}\n".format(" ".join(self.hypotheses), " ".join(self.evidences))

    def add_hypothesis(self, content=None):
        h = Hypothesis(self, 'H' + str(next(self.h_serializer)), content)
        self.hypotheses[h.sn] = h
        self.matrix[h.sn] = {}
        if DEBUG:
            print("adding hypothesis {}: {}".format(h.sn, h.content))
            self.debug()
        return h.sn

    def add_evidence(self, cred=None, rel=None, content=None):
        e = Evidence(self, 'E' + str(next(self.e_serializer)), content, cred=cred, rel=rel)
        self.evidences[e.sn] = e
        if DEBUG:
            print("adding evidence {}: {}".format(e.sn, e.content))
            self.debug()
        return e.sn

    def name_evidence(self, evidence, content):
        self.evidences[evidence].content = content
        if DEBUG:
            print("naming evidence {}: {}".format(self.evidences[evidence],
                                                  self.evidences[evidence].content))
            self.debug()

    def get_h_cells(self, hypo):
        return (cell for cell in self.matrix[hypo].values())

    def get_e_cells(self, evidence):
        return (row[evidence] for row in self.matrix.values())

    def rate(self, h, e, rating):
        if not self.matrix[h].get(e):
            self.matrix[h][e] = Cell(self.hypotheses[h], self.evidences[e], rating=rating)
        else:
            self.matrix[h][e].rating = rating
        if DEBUG:
            print("rating {}:{} as {}".format(h, e, rating))
            self.debug()

    def get_score(self, hypo):
        return sum(cell.score() for cell in self.get_h_cells(hypo))

    def duplicate(self):
        return copy.deepcopy(self)

class Evidence:
    def __init__(self, ach, sn, content, cred=None, rel=None):
        self.sn = sn
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
    >>> a.get_score('H0')
    0.0
    >>> a.get_score('H1')
    2.0000000000000004
    """

    
    def __init__(self, ach, sn, content):
        self.sn = sn
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

    def get_score(self):
        return self.evidence.relevance * self.evidence.credibility * self.rating

if __name__ == "__main__":
    import doctest
    doctest.testmod()