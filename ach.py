import itertools, math, collections, copy

# Constants
VERY_C = 0
CONSISTENT = 0
VERY_I = 2
INCONSISTENT = 1
NEUTRAL = 0
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
            evidence: \n{}
            hypotheses: {}
            matrix: {}
            """.format(self.sn, "\t\n".join("\t{}: {} / {} / {}".format(e.sn, e.content, e.credibility, e.relevance) for e in self.evidences.values()), 
                self.hypotheses,{k: {h: w.get_score() for h, w in v.items()} for k, v in self.matrix.items()}))

    def __str__(self):
        return "Analysis of Competing Hypotheses: \n{}\n".format(" ".join(self.hypotheses), " ".join(self.evidences))

    def add_hypothesis(self, content=None):
        h = Hypothesis(self, 'H' + str(next(self.h_serializer)), content)
        self.hypotheses[h.sn] = h

        for e_sn, d in self.matrix.items():
            d[h.sn] = Cell(self.hypotheses[h.sn], self.evidences[e_sn])
        
        if DEBUG:
            print("adding hypothesis {}: {}".format(h.sn, h.content))
            self.debug()
        return h.sn

    def add_evidence(self, cred=MEDIUM, rel=MEDIUM, content=None):
        e = Evidence(self, 'E' + str(next(self.e_serializer)), content, cred=cred, rel=rel)
        self.evidences[e.sn] = e
        d = {}
        for h_sn in self.hypotheses:
            d[h_sn] = Cell(self.hypotheses[h_sn], e)
        self.matrix[e.sn] = d
        if DEBUG:
            print("adding evidence {}: {}".format(e.sn, e.content))
            self.debug()
        return e.sn

    def name_evidence(self, evidence, content):
        e = self.evidences[evidence]
        e.content = content
        if DEBUG:
            print("naming evidence {}: {}".format(e.sn,
                                                  e.content))
            self.debug()

    def name_hypo(self, hypothesis, content):
        h = self.hypotheses[hypothesis]
        h.content = content
        if DEBUG:
            print("Naming hypothesis {}: {}".format(h.sn,
                                                    h.content))
            self.debug()

    def set_cred(self, evidence, level):
        e = self.evidences[evidence]
        e.credibility = level
        if DEBUG:
            print("Setting evidence {} credibility: {}".format(e.sn,
                                                               e.credibility))
            self.debug()

    def set_rel(self, evidence, level):
        e = self.evidences[evidence]
        e.relevance = level
        if DEBUG:
            print("Setting evidence {} relevance: {}".format(e.sn,
                                                               e.relevance))
            self.debug()

    def get_h_cells(self, hypo):
        return (row[hypo] for row in self.matrix.values())

    def get_e_cells(self, evidence):
        return self.matrix[evidence].values()

    def rate(self, h, e, consistency):
        self.matrix[e][h].set_score(consistency)
        if DEBUG:
            print("rating {}:{} as {}".format(h, e, consistency))
            self.debug()

    def get_score(self, hypo):
        return sum(cell.get_score() for cell in self.get_h_cells(hypo))

    def duplicate(self):
        return copy.deepcopy(self)

class Evidence:
    def __init__(self, ach, sn, content, cred, rel):
        self.sn = sn
        self.credibility = cred
        self.relevance = rel
        self.content = content

    def cred(self):
        if self.credibility == HIGH:
            return "high"
        if self.credibility == MEDIUM:
            return "medium"
        if self.credibility == LOW:
            return "low"

    def rel(self):
        if self.relevance == HIGH:
            return "high"
        if self.relevance == MEDIUM:
            return "medium"
        if self.relevance == LOW:
            return "low"

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
    def __init__(self, hypo, evidence, consistency='--'):
        self.evidence = evidence
        self.hypo = hypo
        self.set_score(consistency)
    
    def set_score(self, consistency):
        if consistency == "--":
            self.consistency = "N"
            self.rating = NEUTRAL
        else:
            if consistency == "II":
                self.rating = VERY_I
            elif consistency == "I":
                self.rating = INCONSISTENT
            elif consistency == "N":
                self.rating = NEUTRAL
            elif consistency == "C":
                self.rating = CONSISTENT
            elif consistency == "CC":
                self.rating == VERY_C
            self.consistency = consistency


    def get_score(self):
        score = self.evidence.relevance * self.evidence.credibility * self.rating
        if DEBUG:
            print("Calculating score for {}:{}:\n\tRelevance {}\n\tCredibility {}\n\tRating {}\n\tScore: {}".format(
                                                            self.evidence.sn, self.hypo.sn,
                                                            repr(self.evidence.relevance),
                                                            repr(self.evidence.credibility),
                                                            repr(self.rating),
                                                            repr(score)))
        return score

if __name__ == "__main__":
    import doctest
    doctest.testmod()