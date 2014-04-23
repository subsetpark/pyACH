# pyACH

pyACH is a web app written by [Suraj Kapoor](http://surajkapoor.com) and [Zach Smith](http://zdsmith.com) that implements the [ACH](http://en.wikipedia.org/wiki/Analysis_of_competing_hypotheses)(Analysis of Competing Hypotheses) methodology. 

<h2>Instructions</h2>

<p>You can use ACH to help you analyze a situation and avoid cognitive bias. Using ACH you can lay out and weight all the evidence being considered, the hypotheses that are competing to explain the evidence, and finally indicate, according to your own judgment, the degree to which each hypothesis accords with the given evidence.</p>

<p>Enter each piece of available evidence and each competing hypothesis. Rate each piece of evidence for its credibility and its relevance to the overall question. Finally, the intersection of each hypothesis and piece of evidence contains a cell to rank consistency. Indicate, using the dropdown menu, whether a given hypothesis is Very Inconsistent, Inconsistent, Neutral, Consistent, or Very Consistent with the given piece of evidence.</p>

<p>The inconsistency score for each hypothesis is displayed directly above the entry for that hypothesis. The higher it is, the weaker the hypothesis is overall relative to the evidence at hand.</p>

<h2>Colophon</h2>

<p>This app consists of a backend written in Python using the <a href="http://pocoo.org/flask">Flask</a> web microframework, and an AJAX frontend written in <a href="http://jquery.com/">JQuery</a>.</p>