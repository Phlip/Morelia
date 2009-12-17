# -*- coding: utf-8 -*-
#            __  __                _ _
#           |  \/  | ___  _ __ ___| (_) __ _
#           | |\/| |/ _ \| '__/ _ \ | |/ _` |
#           | |  | | (_) | | |  __/ | | (_| |
#           |_|  |_|\___/|_|  \___|_|_|\__,_|
#                             o        o     |  o
#                                 ,_       __|      ,
#                        |  |_|  /  |  |  /  |  |  / \_
#                         \/  |_/   |_/|_/\_/|_/|_/ \/

import re

#  ERGO  Morelia should raise a form in any state!
#  ERGO  get Morelia working with more Pythons - virtualenv it!
#  ERGO  moralia should try the regex first then the step name


class Morelia:

    def __init__(self):  self.parent = None

    def _parse(self, predicate, list = [], line_number = 0):
        self.concept = self.my_class_name()
        self.predicate = predicate
        self.steps = []
        self.line_number = line_number

        for s in list[::-1]:
            if issubclass(s.__class__, self.my_parent_type()):
                s.steps.append(self)  #  TODO  squeek if can't find parent
                self.parent = s
                break

        return self

    def my_class_name(self):  return re.sub(r'.*\.', '', str(self.__class__))
    def prefix(self):  return ''
    def my_parent_type(self):  None

        #  TODO  all files must start with a Feature and contain only one

    def evaluate_steps(self, v):
        v.visit(self)
        for step in self.steps:  step.evaluate_steps(v)

    def evaluate_step(self, v):  pass  #  TODO  rename
    def i_look_like(self):  return self.my_class_name()

    def count_dimensions(self):  
        return sum([step.count_dimension() for step in self.steps])

    def count_dimension(self):    # TODO  beautify this crud!
        return 0

    def validate_predicate(self):
        return  # looks good! (-:


class Viridis(Morelia):

    def prefix(self):  return '  '

    def find_step_name(self, suite):
        self.method = None
        self.find_by_doc_string(suite)
        if not self.method:  self.find_by_name(suite)
        if self.method:  return self.method_name
        doc_string = self.suggest_doc_string()
        arguments = '(self' + self.extra_arguments + ')'  #  note this line ain't tested! C-:
        method_name = 'step_' + re.sub('[^\w]+', '_', self.predicate)

        diagnostic = 'Cannot match step: ' + self.predicate + '\n' + \
                     'suggest:\n\n' + \
                     '    def ' + method_name + arguments + ':\n' + \
                     '        ' + doc_string + '\n\n' + \
                     '        # code\n\n'

        suite.fail(diagnostic)  #  TODO  are linefeeds tooken out of the method_name?

#  ERGO  river is to riparian as pond is to ___?

    def suggest_doc_string(self, predicate = None):  #  CONSIDER  invent Ruby scan here, to dazzle the natives
        self.extra_arguments = ''
        if not predicate:  predicate = self.predicate
        predicate = predicate.replace("'", "\\'")
        predicate = predicate.replace('\n', '\\n')
        self._add_extra_args(r'\<(.+?)\>', predicate)
        predicate = re.sub(r'\<.+?\>', '(.+)', predicate)
        self._add_extra_args(r'"(.+?)"', predicate)
        predicate = re.sub(r'".+?"', '"([^"]+)"', predicate)
        return "r'" + predicate + "'"

    def _add_extra_args(self, matcher, predicate):
        args = re.findall(matcher, predicate)
        for arg in args:  self.extra_arguments += ', ' + arg

    def find_by_name(self, suite):
        self.method_name = None
        clean = re.sub(r'[^\w]', '_?', self.predicate)
        self.matches = []

        for s in self.find_steps(suite, '^step_' + clean + '$'):  #  NOTE  the ^$ ain't tested
            self.method_name = s
            self.method = suite.__getattribute__(s)
            return

    def find_by_doc_string(self, suite):
        self.method_name = None

        for s in self.find_steps(suite, '^step_'):
            self.method_name = s
            method = suite.__getattribute__(s)
            doc = method.__doc__
            
            if doc:
                doc = re.compile('^' + doc + '$', re.MULTILINE)  #  CONSIDER deal with users who put in the ^$   TODO  is re.MULTILINE needed?
                m = doc.match(self.augment_predicate())

                if m:
                    self.matches = m.groups()
                    self.method = method
                    return

    def find_steps(self, suite, regexp):
        matcher = re.compile(regexp)
        list = []
        
        for s in dir(suite):
            if matcher.match(s):  list.append(s)

        return list

    def evaluate_step(self, v):  pass  #  TODO rename me!

    def evaluate(self, suite):
        self.find_step_name(suite)
        self.method(*self.matches)


class Parser:  
    def __init__(self):  
        self.thangs = [ Feature, Scenario,
                                    Step, Given, When, Then, And,
                                       Row, Comment ]
        self.steps = []

    def parse_file(self, filename):
        prose = open(filename, 'r').read()
        return self.parse_features(prose)

    def parse_features(self, prose):
        self.parse_feature(prose)
        return self  #  TODO  what happens when these ain't scenes?

    def evaluate(self, suite):
        self.rip(TestVisitor(suite))  #  CONSIDER  rename to Viridis

    def report(self, suite):
        self.rip(ReportVisitor(suite))

    def rip(self, v):
        if self.steps != []:
            self.steps[0].evaluate_steps(v)  #  TODO  fail if it's not a Feature or Scenario

    def parse_feature(self, lines):    #  TODO  preserve and use line numbers
        self.line_number = 0
        
        for self.line in lines.split('\n'):      #  TODO  deal with pesky \r
            self.line_number += 1
            
            if not self._parse_line() and \
                    0 < len(self.steps):
                self._append_to_previous_node()
        
        return self.steps
        
    def _parse_line(self):
        self.line = self.line.rstrip()
        
        for klass in self.thangs:
            self.thang = klass()
            name = self.thang.i_look_like()
            rx = '\s*(' + name + '):?\s*(.*)'  #  TODO  Givenfoo is wrong
            
            m = re.compile(rx).match(self.line)

            if m and len(m.groups()) > 0:
                return self._register_line(m.groups())

    def _register_line(self, groups):
        predicate = ''
        if len(groups) > 1:  predicate = groups[1]
        node = self.thang
        node._parse(predicate, self.steps, self.line_number)
        self.steps.append(node)
        return node

    def _append_to_previous_node(self):   #  TODO  if it's the first one, throw a warning
        previous = self.steps[-1]
        previous.predicate += '\n' + self.line.strip()
        previous.predicate = previous.predicate.strip()
        previous.validate_predicate()


class ReportVisitor:
    def __init__(self, suite):  self.suite = suite

    def visit(self, node):
        print node.prefix() + node.concept + ': ' + node.predicate # TODO  if verbose


class TestVisitor:
    def __init__(self, suite):  self.suite = suite

    def visit(self, node):
        # print node.concept + ': ' + node.predicate # TODO  if verbose
        self.suite.step = node
        node.evaluate_step(self)


class Feature(Morelia):
    def my_parent_type(self):  return None
        
    def evaluate_step(self, v):  
        if 0 == len(self.steps):
            raise SyntaxError('Feature without Scenario(s)')


class Scenario(Morelia):
    def my_parent_type(self):  return Feature

    def evaluate_steps(self, visitor):
        schedule = self.permute_schedule()
        
        for indices in schedule:
            self.row_indices = indices
            self.evaluate_test_case(visitor)  #  note this works on reports too!
        
    def evaluate_test_case(self, visitor):  #  note this permutes reports too!
        
        if 0 == len(self.steps):  #  TODO  simplify!
            raise SyntaxError('Scenario without step(s) - Step, Given, When, Then, And, |, or #')

        name = self.steps[0].find_step_name(visitor.suite)  #  TODO  squeak if there are none
        visitor.suite = visitor.suite.__class__(name)
        # print self.predicate  #  CONSIDER  if verbose
        visitor.suite.setUp()  #  TODO  does this belong inside the try: ? match what pyunit does (or call the pyunit runner directly)

        try:
            Morelia.evaluate_steps(self, visitor)
        finally:
            visitor.suite.tearDown()

    def permute_schedule(self):
        dims = self.count_Row_dimensions()
        return _permute_indices(dims)

    def _embellish(self):
        self.row_indices = []
        
        for step in self.steps:
            rowz = int(step.steps != [] and step.steps[0].__class__ is Row)
            self.row_indices.append(rowz)
        
        return self.row_indices.count(1) > 0

    def count_Row_dimensions(self):
        return [step.count_dimensions() for step in self.steps]


class Step(Viridis):
    def my_parent_type(self):  return Scenario

    def evaluate_step(self, v):
        self.find_step_name(v.suite)
        self.method(*self.matches)

    def augment_predicate(self):  #  TODO  unsucktacularize me pleeeeeeze
        if self.parent == None:  return self.predicate
        dims = self.parent.count_Row_dimensions()
        if set(dims) == set([0]):  return self.predicate
        rep = re.compile(r'\<(\w+)\>')
        replitrons = rep.findall(self.predicate)
        if replitrons == []:  return self.predicate
        self.copy = self.predicate[:]

        for self.replitron in replitrons:
            for x in range(0, len(self.parent.row_indices)):
                self.table = self.parent.steps[x].steps
            
                if self.table != []:
                    q = 0

                    for self.title in self.table[0].harvest():
                        self.replace_replitron(x, q)
                        q += 1

        return self.copy

    def replace_replitron(self, x, q):
        if self.title != self.replitron:  return
        at = self.parent.row_indices[x] + 1
        if at >= len(self.table):  return  #  TODO  this should never happen
        stick = self.table[at].harvest()
        found = stick[q]
            #  TODO  only if it's not nothing?
        self.copy = self.copy.replace('<'+self.replitron+'>', found)

        # TODO  mix replitrons and matchers!


class Given(Step):   pass  #  TODO  distinguish these by fault signatures!
class When(Step):   pass
class Then(Step):  pass
class And(Step):  pass

class Row(Morelia):
    def i_look_like(self):  return r'\|'
    def my_parent_type(self):  return Step

    def count_dimension(self):
        if self is self.parent.steps[0]:  return 0
        return 1  #  TODO  raise an error (if the table has one row!)

    def harvest(self):
        row = [s.strip() for s in re.sub(r'\|$', '', self.predicate).split('|')]
        return row

#  TODO  sample data with "post-it haiku"
#  TODO  trailing comments

class Comment(Morelia):
    def i_look_like(self):  return r'\#'
    def my_parent_type(self):  return Morelia # aka "any"

    def validate_predicate(self):
        if self.predicate.count('\n') > 0:
            complaint = 'linefeed in comment! Line %i' % self.line_number
            raise SyntaxError(complaint)  #  CONSIDER format in editor-ready syntax??


if __name__ == '__main__':
    import os
    os.system('python ../tests/morelia_suite.py')   #  NOTE  this might not return the correct shell value

#  TODO  maximum munch fails - Given must start a line


def _special_range(n):  #  TODO  better name
    return xrange(n) if n else [0]


def _permute_indices(arr):
    return list(_product(*_imap(_special_range, arr)))
      #  tx to Chris Rebert, et al, on the Python newsgroup for curing my brainlock here!!


#  TODO  something was wrong with this:
#~ Scenario: Don't send Clan Membership purchase to Prolog!
  #~ Given the prowares_settings file contains MEMBERSHIP = "Clan_Membership"
   #~ # And a SKU, Clan_Membership, Clan_Membership, $2.00, which is a Clan Item
   #~ # And my cart contains these SKUs
   #~ #When I check out my cart
   #~ #Then no Purchase Order goes to Prolog

#~ Traceback (most recent call last):
  #~ File "/Users/philipplumlee/projects/celtek/prowares/tests.py", line 696, in test_features
    #~ morelia.Parser().parse_file('prowares/features/prowares.feature').evaluate(self) # TODO relative path
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 41, in evaluate
    #~ self.rip(TestVisitor(suite))  #  CONSIDER  rename to Viridis
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 48, in rip
    #~ self.steps[0].evaluate_steps(v)  #  TODO  fail if it's not a Feature or Scenario
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 124, in evaluate_steps
    #~ for step in self.steps:  step.evaluate_steps(v)
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 247, in evaluate_steps
    #~ self.evaluate_test_case(visitor)  #  note this works on reports too!
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 256, in evaluate_test_case
    #~ Morelia.evaluate_steps(self, visitor)
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 124, in evaluate_steps
    #~ for step in self.steps:  step.evaluate_steps(v)
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 123, in evaluate_steps
    #~ v.visit(self)
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 97, in visit
    #~ node.evaluate_step(self)
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 281, in evaluate_step
    #~ self.find_step_name(v.suite)
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 177, in find_step_name
    #~ self.method = self.find_by_doc_string(suite)  #  TODO  move self.method= inside the finders
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 210, in find_by_doc_string
    #~ m = doc.match(self.augment_predicate())
  #~ File "/Users/philipplumlee/projects/celtek/prowares/features/morelia.py", line 159, in augment_predicate
    #~ for self.title in self.table[0].harvest():
#~ AttributeError: Comment instance has no attribute 'harvest'

def _product(*args, **kwds):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod) 
        
def _imap(function, *iterables):
    iterables = map(iter, iterables)
    while True:
        args = [i.next() for i in iterables]
        if function is None:
            yield tuple(args)
        else:
            yield function(*args)
