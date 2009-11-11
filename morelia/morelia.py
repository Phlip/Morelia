# -*- coding: utf-8 -*-

import re


 #  TODO  cron order already!

class Parser:
        def __init__(self):  self.steps = []

        def parse_file(self, filename):
            prose = open(filename, 'r').read()
            return self.parse_features(prose)

        def parse_features(self, prose):
            self.parse_feature(prose)
            return self

        def evaluate(self, suite):
            self.rip(TestVisitor(suite))

        def report(self, suite):
            self.rip(ReportVisitor(suite))

        def rip(self, v):
            if self.steps != []:  self.steps[0].evaluate_steps(v)  #  TODO  fail if it's not a Feature or Scenario

        def parse_feature(self, lines):
            thangs = ['Feature', 'Scenario',
                                'Step', 'Given', 'When', 'Then', 'And']
                        
            #  TODO  preserve and use line numbers

        #  CONSIDER  reconstitute the Given\n\tpredicate syntax

            for line in lines.split('\n'):  #  TODO  deal with pesky \r
                node = None
                line = line.rstrip()
                
                for thang in thangs:
                    rx = '\s*(' + thang + '):?\s*(.*)'  #  TODO  Givenfoo is wrong
                    m = re.compile(rx).match(line)
                    
                    if m and len(m.groups()) > 0:
                        node = self._register_line(m.groups())
                        break

                if not node and 0 < len(self.steps):
                    self._append_to_previous_node(line)
                    
            return self.steps

        def _register_line(self, groups):
            predicate = ''
            if len(groups) > 1:  predicate = groups[1]
            node = eval(groups[0])(predicate, self.steps)
            self.steps.append(node)
            return node
            
        def _append_to_previous_node(self, line):
            #  TODO  if it's the first one, throw a warning
            self.steps[-1].predicate += '\n' + line
            self.steps[-1].predicate = self.steps[-1].predicate.strip()


class ReportVisitor:
    def __init__(self, suite):  self.suite = suite

    def visit(self, node):
        print node.prefix() + node.concept + ': ' + node.predicate # TODO  if verbose


class TestVisitor:
    def __init__(self, suite):  self.suite = suite

    def visit(self, node):
        # print node.concept + ': ' + node.predicate # TODO  if verbose
        node.evaluate_step(self)

class Morelia:
        
    def __init__(self, predicate, list = []):
        self.concept = re.sub('.*\\.', '', str(self.__class__)) # TODO strip!
        self.predicate = predicate
        self.steps = []  #  CONSIDER  parser inherits Morelia to get this - Parser IS Feature
        
        #~ print ['a', 'b', 'c']
        #~ print ['a', 'b', 'c'][::-1]
        
        for s in list[::-1]:
            if issubclass(s.__class__, self.my_parent_type()):
                s.steps.append(self)  #  TODO  squeek if can't find parent
                break

    def prefix(self):  return ''
    def my_parent_type(self):  None    
        
        #  TODO  all files must start with a Feature and contain only one
        
    def evaluate_steps(self, v): 
        v.visit(self)
        for step in self.steps:  step.evaluate_steps(v)
            
    def evaluate_step(self, v):  pass
            

class Viridis(Morelia):

    def prefix(self):  return '  '

    def find_step_name(self, suite):
        self.method = self.find_by_doc_string(suite)  #  TODO  move self.method= inside the finders
        if not self.method: self.method = self.find_by_name(suite)
        if self.method:  return self.method_name

        diagnostic = 'Cannot match step: ' + self.predicate + '\n' + \
                     'suggest:\n\n' + \
                     '    def step_' + re.sub('[^\w]+', '_', self.predicate) + '(self):\n' + \
                     '        "' + self.predicate.replace('"', '\\"') + '"\n\n' + \
                     '        # code\n\n'

        suite.fail(diagnostic)

    def find_by_name(self, suite):
        self.method_name = None
        clean = re.sub(r'[^\w]', '_?', self.predicate)
        self.matches = []
        
        for s in self.find_steps(suite, '^step_' + clean + '$'):  #  NOTE  the ^$ ain't tested
            self.method_name = s
            return suite.__getattribute__(s)
        
        return None

    def find_by_doc_string(self, suite):
        self.method_name = None
        
        for s in self.find_steps(suite, '^step_'):
            self.method_name = s
            method = suite.__getattribute__(s)
            doc = method.__doc__
            
            if doc:
                doc = re.compile('^' + doc + '$')  #  CONSIDER deal with users who put in the ^$
                m = doc.match(self.predicate)

                if m:
                    self.matches = m.groups()
                    return method
        return None

    def find_steps(self, suite, regexp):
        matcher = re.compile(regexp)
        list = []
        
        for s in dir(suite):
            if matcher.match(s):  list.append(s)

        return list

    def evaluate_step(self, v):  pass

    def evaluate(self, suite):  #  TODO  retire me, and quit passing suite around
        self.find_step_name(suite)
        self.method(*self.matches)


class Feature(Morelia):
    def my_parent_type(self):  return None
    def evaluate_step(self, v):  pass


class Scenario(Morelia):
    def my_parent_type(self):  return Feature

    def evaluate_steps(self, visitor):
        name = self.steps[0].find_step_name(visitor.suite)  #  TODO  squeak if there are none
        visitor.suite = visitor.suite.__class__(name)
        visitor.suite.setUp()
        Morelia.evaluate_steps(self, visitor)
        visitor.suite.tearDown()  #  TODO  ensure this!

class Step(Viridis):
    def my_parent_type(self):  return Scenario
        
    def evaluate_step(self, v):
        self.find_step_name(v.suite)
          #  TODO  prompt suggestion if method ain't found
        self.method(*self.matches)  #  TODO  setup, teardown, and nested conclusions


class Given(Step):   pass  #  TODO  distinguish these by fault signatures!
class When(Step):   pass
class Then(Step):  pass
class And(Step):  pass
    
 # hey! Where did the complexity go??


if __name__ == '__main__':
    import os
    os.system('python ../tests/morelia_suite.py')   #  NOTE  this might not return the correct shell value

#  TODO  maximum munch fails - Given must start a line


