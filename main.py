
import datetime
import random
import unittest
import pandas as pd
import numpy

import circuits
import genetic


def get_fitness(genes, rules, inputs):
    circuit = nodes_to_circuit(genes)[0]
    sourceLabels = "ABCDEFGHIJ"
    rulesPassed = 0
    
    
    for i in range(len(rules)):
        inputs.clear()
        eachInput = list()
        eachInput.clear()
        for j in range(10):    
            eachInput.append(rules.iloc[i, j])
        inputs.update(zip(sourceLabels, eachInput))
        if circuit.get_output() == rules.iloc[i, -1]:
            rulesPassed += 1


    # for i in range(len(rules)): 
    #     inputs.clear()
    #     inputs.update(zip(sourceLabels, rules.iloc[i, 0] , rules.iloc[i, 1] , rules.iloc[i, 2] , rules.iloc[i, 3] , rules.iloc[i, 4] ,
    #     rules.iloc[i, 5] , rules.iloc[i, 6] , rules.iloc[i, 7] , rules.iloc[i, 8] , rules.iloc[i, 9] ))
    #     if circuit.get_output() == rules.iloc[i, 10]:
    #         rulesPassed += 1

    # for rule in rules.itertuples():
    #     rule.input1

    # for rule in rules:
    #     inputs.clear()
    #     inputs.update(zip(sourceLabels, rule[0]))
    #     if circuit.get_output() == rule[1]:
    #         rulesPassed += 1

    return rulesPassed


def display(candidate, startTime):
    circuit = nodes_to_circuit(candidate.Genes)[0]
    timeDiff = datetime.datetime.now() - startTime
    print("{}\t{}\t{}".format(
        circuit,rulesPassed
        candidate.Fitness,
        timeDiff))


def create_gene(index, gates, sources):
    if index < len(sources):
        gateType = sources[index]
    else:
        gateType = random.choice(gates)
    indexA = indexB = None
    if gateType[1].input_count() > 0:
        indexA = random.randint(0, index)
    if gateType[1].input_count() > 1:
        indexB = random.randint(0, index)
        if indexB == indexA:
            indexB = random.randint(0, index)
    return Node(gateType[0], indexA, indexB)


def mutate(childGenes, fnCreateGene, fnGetFitness, sourceCount):
    count = random.randint(1, 5)
    initialFitness = fnGetFitness(childGenes)
    while count > 0:
        count -= 1
        indexesUsed = [i for i in nodes_to_circuit(childGenes)[1]
                       if i >= sourceCount]
        if len(indexesUsed) == 0:
            return nodes_to_circuit(childGenes)[1]
        index = random.choice(indexesUsed)
        childGenes[index] = fnCreateGene(index)
        if fnGetFitness(childGenes) > initialFitness:
            return

def crossover(parent, otherParent):
    childGenes = parent[:]
    # if len(parent) <= 2 or len(otherParent) < 2:
    #     return childGenes
    length = random.randint(1, len(parent) - 5)
    start = random.randrange(0, len(parent) - length)
    childGenes[start:start + length] = otherParent[start:start + length]
    return childGenes


class CircuitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = dict()
        cls.gates = [[circuits.And, circuits.And],
                     [lambda i1, i2: circuits.Not(i1), circuits.Not]]
        cls.sources = [
            [lambda i1, i2: circuits.Source('A', cls.inputs),
             circuits.Source],
            [lambda i1, i2: circuits.Source('B', cls.inputs),
             circuits.Source]]

    # def test_generate_OR(self):
    #     rules = [[[False, False], False],
    #              [[False, True], True],
    #              [[True, False], True],
    #              [[True, True], True]]

    #     optimalLength = 6
    #     self.find_circuit(rules, optimalLength)

    def test_generate_myCsv(self):
        rules = pd.read_csv("truth_table.csv")
        
        self.gates.append([circuits.Or, circuits.Or])
        self.gates.append([circuits.Xor, circuits.Xor])
        
        self.sources.append(
            [lambda l, r: circuits.Source('C', self.inputs),
             circuits.Source])
        self.sources.append(
            [lambda l, r: circuits.Source('D', self.inputs),
             circuits.Source])
        self.sources.append(
            [lambda l, r: circuits.Source('E', self.inputs),
             circuits.Source])
        self.sources.append(
            [lambda l, r: circuits.Source('F', self.inputs),
             circuits.Source])
        self.sources.append(
            [lambda l, r: circuits.Source('G', self.inputs),
             circuits.Source])
        self.sources.append(
            [lambda l, r: circuits.Source('H', self.inputs),
             circuits.Source])
        self.sources.append(
            [lambda l, r: circuits.Source('I', self.inputs),
             circuits.Source])
        self.sources.append(
            [lambda l, r: circuits.Source('J', self.inputs),
             circuits.Source])
        
        self.find_circuit(rules, 12)


    def find_circuit(self, rules, expectedLength):
        startTime = datetime.datetime.now()

        def fnDisplay(candidate, length=None):
            if length is not None:
                print("-- distinct nodes in circuit:",
                      len(nodes_to_circuit(candidate.Genes)[1]))
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes, rules, self.inputs)

        def fnCreateGene(index):
            return create_gene(index, self.gates, self.sources)

        def fnMutate(genes):
            mutate(genes, fnCreateGene, fnGetFitness, len(self.sources))

        maxLength = 100

        def fnCreate():
            return [fnCreateGene(i) for i in range(maxLength)]

        def fnOptimizationFunction(variableLength):
            nonlocal maxLength
            maxLength = variableLength
            return genetic.get_best(fnGetFitness, None, len(rules), None,
                                    fnDisplay, fnMutate, fnCreate, maxAge=25,
                                    poolSize=3, crossover=crossover, maxSeconds=30)

        def fnIsImprovement(currentBest, child):
            return child.Fitness == len(rules) and \
                   len(nodes_to_circuit(child.Genes)[1]) < \
                   len(nodes_to_circuit(currentBest.Genes)[1])

        def fnIsOptimal(child):
            return child.Fitness == len(rules) and \
                   len(nodes_to_circuit(child.Genes)[1]) <= expectedLength

        def fnGetNextFeatureValue(currentBest):
            return len(nodes_to_circuit(currentBest.Genes)[1])

        best = genetic.hill_climbing(fnOptimizationFunction,
                                     fnIsImprovement, fnIsOptimal,
                                     fnGetNextFeatureValue, fnDisplay,
                                     maxLength)
        self.assertTrue(best.Fitness == len(rules))
        self.assertFalse(len(nodes_to_circuit(best.Genes)[1])
                         > expectedLength)


def nodes_to_circuit(genes):
    circuit = []
    usedIndexes = []
    for i, node in enumerate(genes):
        used = {i}
        inputA = inputB = None
        if node.IndexA is not None and i > node.IndexA:
            inputA = circuit[node.IndexA]
            used.update(usedIndexes[node.IndexA])
            if node.IndexB is not None and i > node.IndexB:
                inputB = circuit[node.IndexB]
                used.update(usedIndexes[node.IndexB])
        circuit.append(node.CreateGate(inputA, inputB))
        usedIndexes.append(used)
    return circuit[-1], usedIndexes[-1]


class Node:
    def __init__(self, createGate, indexA=None, indexB=None):
        self.CreateGate = createGate
        self.IndexA = indexA
        self.IndexB = indexB


if __name__ == '__main__':
    unittest.main()