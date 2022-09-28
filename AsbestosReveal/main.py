import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askopenfilenames

from PIL import Image, ImageSequence, ImageTk



from rdflib.namespace import FOAF, RDF
from rdflib.plugins.sparql import prepareQuery
from unidecode import unidecode

import pprint   # For proper print of sequences.

from owlready2 import *

import csv

import rdflib

from difflib import SequenceMatcher

import random

import os, shutil

from datetime import datetime as dt


import csv

from owlready2 import *
import rdflib
import owlready2
import os.path
import time
from joblib import Parallel, delayed
import multiprocessing
import threading
import random

owlready2.JAVA_EXE = "C:\\Program Files\\Java\\jdk-15.0.2\\bin\\java.exe"

# s = set([1,2,3])
# strs = repr(s)
# print(strs)
# # 'set([1, 2, 3])'
# print(eval(strs))
# # set([1, 2, 3])


# graph = Graph(store=HDTStore("mltest/ASBESTOS_ONTOLOGY_SETTLEMENT.hdt"))
# #print("end")

# fileName = "data/0/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT"
# k_onto = get_ontology("file://" + fileName + ".owl").load()
# k = Graph(store=HDTStore(fileName + ".hdt"))

# # Load the ontology -----------------------------------------
# ontoIn = get_ontology("file://ML_Tests\\data/t\\tIn.owl").load()
#
# with ontoIn:
#     rule = Imp()
#     rule.set_as_rule(
#         """has_calculated_characteristic(?PR1, ?C1), has_calculated_characteristic(?PR2, ?C2), has_calculation_year(?C1, ?Y1), has_calculation_year(?C2, ?Y2), greaterThanOrEqual(?Y2, ?Y1), Enduit(?PR1), Enduit(?PR2), has_product_class(?C1, "Low") -> has_product_class(?C2, "Low")""")
#     rule = Imp()
#     rule.set_as_rule(
#         "Enduit(?PR1) -> Enduit(?PR2)")
#     rule = Imp()
#     rule.set_as_rule(
#         'Enduit(?PR2) -> Enduit(?PR3)')
#     # sync_reasoner_pellet()
#     sync_reasoner_pellet(infer_data_property_values=True)
#
# ontoIn.save(file="ML_Tests\\data/t\\tOut.owl", format="rdfxml")
#
# #print('END')


###----------------------------------- ALGORITHM -----------------------------------###
# # fileName = "ML_Tests\\data/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"

# fileName = "data/0/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
# fileName = "data/0/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
# # fileName = "ML_Tests\\data/ML_test - new.owl"
# # Load the KB -----------------------------------------
# k_onto = get_ontology("file://" + fileName).load()
# # #print(iri)
# k = rdflib.Graph()
# k.load(fileName)

# f=open("ML_Tests\\data/test.txt", "r")
# contents =f.read().replace('), (', ')\n(')
# #print(contents)
# #print('end')


# individuals = list(k_onto.individuals())
# individualsF = []
# for individual in individuals:
#     if ':'  not in str(individual):
#         individualsF.append(str(individual)[len('ML_Tests\data/ASBESTOS_ONTOLOGY_SETTLEMENT.'):])
# for individualF in individualsF:
#     #print(individualF)
# #print(len(individualsF))

patternGeneral = "Product(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, class)"


def SelectProductHearchy(k, iri, p):
    q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?x . ?x rdfs:subClassOf* ?h . }'
    qres = k.query(q, initBindings={'h': rdflib.term.URIRef(iri + p)})

    productList = []
    for row in qres:
        productList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    if p in productList:
        productList.remove(p)
    return productList


# #print(SelectProductHearchy(k, k_onto, 'revetement'))


def SelectLocationHearchy(k, iri, l):
    q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Location rdf:type ?x . ?x rdfs:subClassOf* ?h . }'
    qres = k.query(q, initBindings={'h': rdflib.term.URIRef(iri + l)})

    locationList = []
    for row in qres:
        locationList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    if l in locationList:
        locationList.remove(l)
    return locationList


# #print(SelectLocationHearchy(k, k_onto, 'porte'))


def SelectProduct(k, iri):
    q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
    qres = k.query(q)

    productList = []
    for row in qres:
        productList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    hList = []
    for p in productList:
        hList += SelectProductHearchy(k, iri, p)

    return list(set(productList) - set(hList))


def SelectLocation(k, iri, p):
    q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?p . ?Location rdf:type ?x . ?x rdfs:subClassOf* :Location . }'
    qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p)})

    locationList = []
    for row in qres:
        locationList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    hList = []
    for l in locationList:
        hList += SelectLocationHearchy(k, iri, l)

    return list(set(locationList) - set(hList))


def SelectStructure(k, iri, p):
    q = 'SELECT DISTINCT ?x WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product rdf:type ?p . ?Structure rdf:type ?x . ?x rdfs:subClassOf* :Structure . }'
    qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p)})

    structureList = []
    for row in qres:
        structureList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    return structureList


def suppCalculate(k, iri, pattern):
    supp = 0
    # #print(pattern)
    p = pattern[:pattern.find('(')]
    # #print(p)
    l = pattern[pattern.find("?P), ") + len("?P), "):pattern.find('(?L')]
    # #print(l)
    s = pattern[pattern.find("?L), ") + len("?L), "):pattern.find('(?S')]
    # #print(s)
    d = 0
    compare = '>='
    if "HIGH" in pattern:
        d = 1
        compare = '<='

    # date = '-1'
    if "??Y" not in pattern and ('greaterThanOrEqual' in pattern or 'lessThanOrEqual' in pattern):
        existDate = True
        date = pattern[pattern.find("(?Y, ") + len("(?Y, "):pattern.find(') ->')]
    else:
        existDate = False

    pBrother = ""
    if "(?P2)" in pattern:
        num = pattern.count("contain(?L, ?P")
        # #print(num)
        for i in range(num, 1, -1):
            if i == num:
                pBrother += "?Location :contain ?Product" + str(i) + " . ?Product" + str(i) + " rdf:type ?pt" + str(
                    i) + " . ?pt" + str(i) + " rdfs:subClassOf* :" + pattern[
                                                                     pattern.find("contain(?L, ?P), ") + len(
                                                                         "contain(?L, ?P), "):pattern.find(
                                                                         '(?P' + str(i) + '),')] + " . "
            else:
                pBrother += "?Location :contain ?Product" + str(i) + " . ?Product" + str(i) + " rdf:type ?pt" + str(
                    i) + " . ?pt" + str(i) + " rdfs:subClassOf* :" + pattern[pattern.find(
                    "contain(?L, ?P" + str(i + 1) + "), ") + len(
                    "contain(?L, ?P" + str(i + 1) + "), "):pattern.find('(?P' + str(i) + '),')] + " . "
        # #print(pBrother)

    lBrother = ""
    if "(?L2)" in pattern:
        numl = pattern.count("has_location(?S, ?L")
        # #print(numl)
        for i in range(numl, 1, -1):
            if i == numl:
                lBrother += "?Structure :has_location ?Location" + str(i) + " . ?Location" + str(
                    i) + " rdf:type ?lt" + str(i) + " . ?lt" + str(i) + " rdfs:subClassOf* :" + pattern[
                                                                                                pattern.find(
                                                                                                    "has_location(?S, ?L), ") + len(
                                                                                                    "has_location(?S, ?L), "):pattern.find(
                                                                                                    '(?L' + str(
                                                                                                        i) + '),')] + " . "
            else:
                lBrother += "?Structure :has_location ?Location" + str(i) + " . ?Location" + str(
                    i) + " rdf:type ?lt" + str(i) + " . ?lt" + str(i) + " rdfs:subClassOf* :" + pattern[
                                                                                                pattern.find(
                                                                                                    "has_location(?S, ?L" + str(
                                                                                                        i + 1) + "), ") + len(
                                                                                                    "has_location(?S, ?L" + str(
                                                                                                        i + 1) + "), "):pattern.find(
                                                                                                    '(?L' + str(
                                                                                                        i) + '),')] + " . "
        # #print(lBrother)

    buildingTypeQ = ''
    if '?T' not in pattern:
        buildingType = pattern[pattern.find('has_type(?B, ') + len('has_type(?B, '):pattern.find('), has_region')]
        # #print(buildingType)
        buildingTypeQ = '?Building :has_type ?type . '

    buildingRegionQ = ''
    if '?R' not in pattern:
        buildingRegion = pattern[pattern.find('has_region(?B, ') + len('has_region(?B, '):pattern.find(
            '), has_diagnostic_characteristc')]
        buildingRegionQ = '?Building :has_region ?region . '

    if l != 'Location':
        if s != 'Structure':
            if existDate:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s . ?Location rdf:type ?lt . ?lt rdfs:subClassOf* ?l . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year ' + compare + ' ?y) . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print(q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
            else:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s. ?Location rdf:type ?lt . ?lt rdfs:subClassOf* ?l . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('*' + q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d)})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
        else:
            if existDate:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Location rdf:type ?lt . ?lt rdfs:subClassOf* ?l . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year ' + compare + ' ?y) . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('**' + q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
            else:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Location rdf:type ?lt . ?lt rdfs:subClassOf* ?l . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('***' + q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d)})
                    else:
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))})
                    else:
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))})
    else:
        if s != 'Structure':
            if existDate:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ' + pBrother + '?Structure rdf:type ?s . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year ' + compare + ' ?y) . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('****'+q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q,
                                       initBindings={'s': rdflib.term.URIRef(iri + s),
                                                     'p': rdflib.term.URIRef(iri + p),
                                                     'd': rdflib.term.Literal(d),
                                                     'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q,
                                       initBindings={'s': rdflib.term.URIRef(iri + s),
                                                     'p': rdflib.term.URIRef(iri + p),
                                                     'd': rdflib.term.Literal(d),
                                                     'region': rdflib.term.Literal(buildingRegion,
                                                                                   datatype=rdflib.term.URIRef(
                                                                                       'http://www.w3.org/2001/XMLSchema#string')),
                                                     'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q,
                                       initBindings={'s': rdflib.term.URIRef(iri + s),
                                                     'p': rdflib.term.URIRef(iri + p),
                                                     'd': rdflib.term.Literal(d),
                                                     'type': rdflib.term.Literal(buildingType,
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#string')),
                                                     'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q,
                                       initBindings={'s': rdflib.term.URIRef(iri + s),
                                                     'p': rdflib.term.URIRef(iri + p),
                                                     'd': rdflib.term.Literal(d),
                                                     'type': rdflib.term.Literal(buildingType,
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#string')),
                                                     'region': rdflib.term.Literal(buildingRegion,
                                                                                   datatype=rdflib.term.URIRef(
                                                                                       'http://www.w3.org/2001/XMLSchema#string')),
                                                     'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
            else:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ' + pBrother + '?Structure rdf:type ?s . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('*****' + q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d)})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
        else:
            if existDate:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ' + pBrother + '?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year ' + compare + ' ?y) . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('****'+q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q,
                                       initBindings={'p': rdflib.term.URIRef(iri + p),
                                                     'd': rdflib.term.Literal(d),
                                                     'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q,
                                       initBindings={'p': rdflib.term.URIRef(iri + p),
                                                     'd': rdflib.term.Literal(d),
                                                     'region': rdflib.term.Literal(buildingRegion,
                                                                                   datatype=rdflib.term.URIRef(
                                                                                       'http://www.w3.org/2001/XMLSchema#string')),
                                                     'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q,
                                       initBindings={'p': rdflib.term.URIRef(iri + p),
                                                     'd': rdflib.term.Literal(d),
                                                     'type': rdflib.term.Literal(buildingType,
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#string')),
                                                     'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q,
                                       initBindings={'p': rdflib.term.URIRef(iri + p),
                                                     'd': rdflib.term.Literal(d),
                                                     'type': rdflib.term.Literal(buildingType,
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#string')),
                                                     'region': rdflib.term.Literal(buildingRegion,
                                                                                   datatype=rdflib.term.URIRef(
                                                                                       'http://www.w3.org/2001/XMLSchema#string')),
                                                     'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
            else:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ' + pBrother + '?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('*****' + q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d)})
                    else:
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
                    else:
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'd': rdflib.term.Literal(d),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))
                                                        })

    # supp = len(qres)
    for row in qres:
        # #print(row)
        supp = int(row[len(row) - 1])

    return supp


# #print("supp")
# #print(suppCalculate(k, k_onto, 'bois(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)'))
# #print("supp")
# #print(suppCalculate(k, k_onto, 'revetement(P), Location(L), Structure(S), has_location(S, L), contain(L, P), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) , lessThanOrEqual(?Y, 1990) -> has_Diagnisis(D, HIGH)'))
# #print(suppCalculate(k, k_onto, 'bois(P), Location(L), Structure(S), has_location(S, L), contain(L, P), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) , greaterThanOrEqual(?Y, 1947) -> has_Diagnisis(D, LOW)'))
# #print('-------------------')
# #print(suppCalculate(k, k_onto, 'peinture(?P), murs(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, test2), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1970) -> has_Diagnisis(?D, HIGH)'))
# #print('-------------------')
# #print(suppCalculate(k, k_onto, 'peinture(P), Location(L), Structure(S), has_location(S, L), contain(L, P), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) , lessThanOrEqual(?Y, 1970) -> has_Diagnisis(D, HIGH)'))


def headSize(k, iri, pattern):
    if 'LOW' in pattern:
        c = "0"
    elif 'HIGH' in pattern:
        c = "1"
    q = 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> SELECT DISTINCT ?Diagnostic WHERE { ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic "' + c + '"^^xsd:integer . }'
    qres = k.query(q)

    return len(qres)


def supportBySize(k, iri, supp, pattern):
    hSize = headSize(k, iri, pattern)
    if hSize == 0:
        return 0
    return supp / hSize


def confCalculate(k, iri, pattern, supp):
    occ = 0
    p = pattern[:pattern.find('(')]
    # #print(p)
    l = pattern[pattern.find("?P), ") + len("?P), "):pattern.find('(?L')]
    # #print(l)
    s = pattern[pattern.find("?L), ") + len("?L), "):pattern.find('(?S')]
    # #print(s)

    if "greaterThan" in pattern:
        # d = False
        compare = '>='
    else:
        # d = True
        compare = '<='

    if "??Y" not in pattern and ('greaterThanOrEqual' in pattern or 'lessThanOrEqual' in pattern):
        existDate = True
        date = pattern[pattern.find("(?Y, ") + len("(?Y, "):pattern.find(') ->')]
    else:
        existDate = False

    pBrother = ""
    if "(?P2)" in pattern:
        num = pattern.count("contain(?L, ?P")
        # #print(num)
        for i in range(num, 1, -1):
            if i == num:
                pBrother += "?Location :contain ?Product" + str(i) + " . ?Product" + str(i) + " rdf:type ?pt" + str(
                    i) + " . ?pt" + str(i) + " rdfs:subClassOf* :" + pattern[pattern.find("contain(?L, ?P), ") + len(
                    "contain(?L, ?P), "):pattern.find('(?P' + str(i) + '),')] + " . "
            else:
                pBrother += "?Location :contain ?Product" + str(i) + " . ?Product" + str(i) + " rdf:type ?pt" + str(
                    i) + " . ?pt" + str(i) + " rdfs:subClassOf* :" + pattern[pattern.find(
                    "contain(?L, ?P" + str(i + 1) + "), ") + len("contain(?L, ?P" + str(i + 1) + "), "):pattern.find(
                    '(?P' + str(i) + '),')] + " . "
        # #print(pBrother)

    lBrother = ""
    if "(?L2)" in pattern:
        numl = pattern.count("has_location(?S, ?L")
        # #print(numl)
        for i in range(numl, 1, -1):
            if i == numl:
                lBrother += "?Structure :has_location ?Location" + str(i) + " . ?Location" + str(
                    i) + " rdf:type ?lt" + str(i) + " . ?lt" + str(i) + " rdfs:subClassOf* :" + pattern[pattern.find(
                    "has_location(?S, ?L), ") + len("has_location(?S, ?L), "):pattern.find('(?L' + str(i) + '),')] + " . "
            else:
                lBrother += "?Structure :has_location ?Location" + str(i) + " . ?Location" + str(
                    i) + " rdf:type ?lt" + str(i) + " . ?lt" + str(i) + " rdfs:subClassOf* :" + pattern[pattern.find(
                    "has_location(?S, ?L" + str(i + 1) + "), ") + len(
                    "has_location(?S, ?L" + str(i + 1) + "), "):pattern.find('(?L' + str(i) + '),')] + " . "
        # #print(lBrother)

    buildingTypeQ = ''
    if '?T' not in pattern:
        buildingType = pattern[pattern.find('has_type(?B, ') + len('has_type(?B, '):pattern.find('), has_region')]
        # #print(buildingType)
        buildingTypeQ = '?Building :has_type ?type . '

    buildingRegionQ = ''
    if '?R' not in pattern:
        buildingRegion = pattern[pattern.find('has_region(?B, ') + len('has_region(?B, '):pattern.find(
            '), has_diagnostic_characteristc')]
        buildingRegionQ = '?Building :has_region ?region . '

    if l != 'Location':
        if s != 'Structure':
            if existDate:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s . ?Location rdf:type ?lt . ?lt rdfs:subClassOf* ?l . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year ' + compare + ' ?y) . ' + buildingTypeQ + buildingRegionQ + '}'
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
            else:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s. ?Location rdf:type ?lt . ?lt rdfs:subClassOf* ?l . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ' + buildingTypeQ + buildingRegionQ + '}'
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p)})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
        else:
            if existDate:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Location rdf:type ?lt . ?lt rdfs:subClassOf* ?l . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year ' + compare + ' ?y) . ' + buildingTypeQ + buildingRegionQ + '}'
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))
                                                        })
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
            else:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Location rdf:type ?lt . ?lt rdfs:subClassOf* ?l . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ' + buildingTypeQ + buildingRegionQ + '}'
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p)})
                    else:
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))})
                    else:
                        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
    else:
        if s != 'Structure':
            if existDate:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year ' + compare + ' ?y) . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('//' + q)
                # #print(date)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))
                                                        })
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
            else:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s . ?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print(q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p)})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))})
                    else:
                        qres = k.query(q, initBindings={'s': rdflib.term.URIRef(iri + s),
                                                        'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
        else:
            if existDate:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year ' + compare + ' ?y) . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print('//' + q)
                # #print(date)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))
                                                        })
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
                    else:
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string')),
                                                        'y': rdflib.term.Literal(date + '-01-01T00:00:00',
                                                                                 datatype=rdflib.term.URIRef(
                                                                                     'http://www.w3.org/2001/XMLSchema#dateTime'))})
            else:
                q = 'SELECT (count(?Product) as ?COUNT) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Product rdf:type ?pt . ?pt rdfs:subClassOf* ?p . ' + buildingTypeQ + buildingRegionQ + '}'
                # #print(q)
                if buildingTypeQ == '':
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p)})
                    else:
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })
                else:
                    if buildingRegionQ == '':
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string'))})
                    else:
                        qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p),
                                                        'type': rdflib.term.Literal(buildingType,
                                                                                    datatype=rdflib.term.URIRef(
                                                                                        'http://www.w3.org/2001/XMLSchema#string')),
                                                        'region': rdflib.term.Literal(buildingRegion,
                                                                                      datatype=rdflib.term.URIRef(
                                                                                          'http://www.w3.org/2001/XMLSchema#string'))
                                                        })

    # occ = len(qres)
    for row in qres:
        # #print(row)
        occ = int(row[len(row) - 1])
        # #print(occ)

    if occ > 0:
        return (supp / occ)
    else:
        return 0


# #print('supp=' + str(suppCalculate(k, k_onto, 'bois(P), Location(L), Structure(S), has_location(S, L), contain(L, P), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) -> has_Diagnisis(D, LOW)')))
# #print('conf=' + str(confCalculate(k, k_onto, 'bois(P), Location(L), Structure(S), has_location(S, L), contain(L, P), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) -> has_Diagnisis(D, LOW)', suppCalculate(k, k_onto, 'bois(P), Location(L), Structure(S), has_location(S, L), contain(L, P), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) -> has_Diagnisis(D, LOW)'))))
# #print('supp=' + str(suppCalculate(k, k_onto, 'colle(?P), Location(?L), cuisine(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1989) -> has_Diagnisis(?D, HIGH)')))
# #print('conf=' + str(confCalculate(k, k_onto, 'colle(?P), Location(?L), cuisine(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1989) -> has_Diagnisis(?D, HIGH)', suppCalculate(k, k_onto, 'colle(?P), Location(?L), cuisine(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1989) -> has_Diagnisis(?D, HIGH)'))))
# #print('*************************************************************************')
# #print('supp=' + str(suppCalculate(k, k_onto, 'peinture(?P), murs(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, test2), has_region(?B, Paris), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1970) -> has_Diagnisis(?D, HIGH)')))
# #print('conf=' + str(confCalculate(k, k_onto, 'peinture(?P), murs(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, test2), has_region(?B, Paris), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1970) -> has_Diagnisis(?D, HIGH)', suppCalculate(k, k_onto, 'peinture(?P), murs(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, test2), has_region(?B, Paris), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1970) -> has_Diagnisis(?D, HIGH)'))))
# #print('conf=' + str(confCalculate(k, k_onto, 'enduits(P), Location(L), Structure(S), has_location(S, L), contain(L, P), peintures(P2), contain(L, P2), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) , lessThanOrEqual(?Y, 1960) -> has_Diagnisis(D, HIGH)', suppCalculate(k, k_onto, 'enduits(P), Location(L), Structure(S), has_location(S, L), contain(L, P), peintures(P2), contain(L, P2), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) , lessThanOrEqual(?Y, 1960) -> has_Diagnisis(D, HIGH)'))))


# def Specialize_Product_Paralel(k, iri, pattern, p, minSupp, num_cores):
#     inputs = ['LOW', 'HIGH']
#     results = Parallel(n_jobs=num_cores)(delayed(Specialize_Product)(k, iri, pattern, p, minSupp, proba) for proba in inputs)
#     output = set()
#     for r in results:
#         output.update(r)
#
#     return output
#
#
# def Specialize_Product(k, iri, pattern, p, minSupp, proba):
#     patternSet = set()
#     pattern_p = pattern.replace("Product", p)
#     # for proba in ['LOW', 'HIGH']:
#     pattern_c = pattern_p.replace('class', proba)
#     print("-"+pattern_c)
#     supp0 = suppCalculate(k, iri, pattern_c)
#     supp = supportBySize(k, iri, supp0, pattern_c)
#     print(supp)
#     if supp >= minSupp:
#         conf = confCalculate(k, iri, pattern_c, supp0)
#         patternSet.add(tuple([pattern_c, supp, conf]))
#     return patternSet


def Specialize_Product_Threaded(k, iri, pattern, p, minSupp, patternSet, proba):
    # patternSet = set()
    pattern_p = pattern.replace("Product", p)
    # for proba in ['LOW', 'HIGH']:
    pattern_c = pattern_p.replace('class', proba)
    #print("-"+pattern_c)
    supp0 = suppCalculate(k, iri, pattern_c)
    supp = supportBySize(k, iri, supp0, pattern_c)
    #print(supp)
    if supp >= minSupp:
        conf = confCalculate(k, iri, pattern_c, supp0)
        patternSet.add(tuple([pattern_c, supp, conf]))
    return patternSet


def Specialize_Product(k, iri, pattern, p, minSupp):
    patternSet = set()
    pattern_p = pattern.replace("Product", p)

    threads = map(lambda proba: threading.Thread(
        target=lambda: Specialize_Product_Threaded(k, iri, pattern, p, minSupp, patternSet, proba)), ['LOW', 'HIGH'])
    for t in threads:
        t.start()
        t.join()

    return patternSet


def Specialize_Product_withoutThreads(k, iri, pattern, p, minSupp):
    patternSet = set()
    pattern_p = pattern.replace("Product", p)
    for proba in ['LOW', 'HIGH']:
        pattern_c = pattern_p.replace('class', proba)
        #print("-"+pattern_c)
        supp0 = suppCalculate(k, iri, pattern_c)
        supp = supportBySize(k, iri, supp0, pattern_c)
        #print(supp)
        if supp >= minSupp:
            conf = confCalculate(k, iri, pattern_c, supp0)
            patternSet.add(tuple([pattern_c, supp, conf]))
    return patternSet


# def Specialize_Location_Paralel(k, iri, patternSet, lSet, minConf, minSupp, maxConf, num_cores):# probleme d'inbrication !!!
#     results = Parallel(n_jobs=num_cores)(delayed(Specialize_Location)(k, iri, lSet, minConf, minSupp, maxConf, num_cores, pattern) for pattern in patternSet)
#     output = set()
#     for r in results:
#         output.update(r)
#
#     print('output')
#     print(output)
#     return output


# def Specialize_Location(k, iri, lSet, minConf, minSupp, maxConf, num_cores, pattern):
#     conf = pattern[2]
#     output = set()
#     if conf < maxConf:
#         results = Parallel(n_jobs=num_cores)(
#             delayed(Specialize_Location_l)(k, iri, minConf, minSupp, maxConf, pattern, l) for l in
#             lSet)
#
#         for r in results:
#             output.update(r)
#
#     return output
#
#
# def Specialize_Location_l(k, iri, minConf, minSupp, maxConf, pattern, l):
#     patternSet_l = set()
#     # for pattern in patternSet:
#     pattern_p = pattern[0]
#     supp = pattern[1]
#     conf = pattern[2]
#     lAdd = False
#     # if conf < maxConf:
#     #     for l in lSet:
#     pattern_l = pattern_p.replace("Location", l)
#     su0 = suppCalculate(k, iri, pattern_l)
#     su = supportBySize(k, iri, su0, pattern_l)
#     if su >= minSupp:
#         c = confCalculate(k, iri, pattern_l, su0)
#         if c > conf:  ######################################################## >= pour couvrir toutes les cas possibles; ou bien > pour limiter l'espace de recherche
#             # print("1- c="+str(c)+" ... conf="+str(conf))
#             conf = c
#             lAdd = True
#             if 'ThanOrEqual(?Y' not in pattern_l:  ######################################################## pour recalculer la date aprés
#                 if 'has_Diagnisis(?D, LOW)' in pattern_l:
#                     pattern_l = pattern_l.replace(', greaterThanOrEqual(?Y, ??Y) ->', '->')
#                 else:
#                     pattern_l = pattern_l.replace(', lessThanOrEqual(?Y, ??Y) ->', '->')
#                 su0 = suppCalculate(k, iri, pattern_l)
#                 su = supportBySize(k, iri, su0, pattern_l)
#                 c = confCalculate(k, iri, pattern_l, su0)
#             patternSet_l.add(tuple([pattern_l, su, c]))
#
#     return patternSet_l


def Specialize_Location(k, iri, patternSet, lSet, minConf, minSupp, maxConf):
    patternSet_l = set()

    threads = map(lambda pattern: threading.Thread(
        target=lambda: Specialize_Location_Threaded(k, iri, lSet, minConf, minSupp, maxConf, patternSet_l, pattern)),
                  patternSet)
    for t in threads:
        t.start()
        t.join()

    return patternSet_l

def Specialize_Location_Threaded(k, iri, lSet, minConf, minSupp, maxConf, patternSet_l, pattern):
    conf = pattern[2]
    if conf < maxConf:
        threads = map(lambda l: threading.Thread(
            target=lambda: Specialize_Location_Threaded_l(k, iri, minConf, minSupp, maxConf, patternSet_l,
                                                        pattern, l)),
                      lSet)
        for t in threads:
            t.start()
            t.join()

    return patternSet_l


def Specialize_Location_Threaded_l(k, iri, minConf, minSupp, maxConf, patternSet_l, pattern, l):
    pattern_p = pattern[0]
    supp = pattern[1]
    conf = pattern[2]
    lAdd = False
    pattern_l = pattern_p.replace("Location", l)
    su0 = suppCalculate(k, iri, pattern_l)
    su = supportBySize(k, iri, su0, pattern_l)
    if su >= minSupp:
        c = confCalculate(k, iri, pattern_l, su0)
        if c > conf:  ######################################################## >= pour couvrir toutes les cas possibles; ou bien > pour limiter l'espace de recherche
            # #print("1- c="+str(c)+" ... conf="+str(conf))
            conf = c
            lAdd = True
            if 'ThanOrEqual(?Y' not in pattern_l:  ######################################################## pour recalculer la date aprés
                if 'has_Diagnisis(?D, LOW)' in pattern_l:
                    pattern_l = pattern_l.replace(', greaterThanOrEqual(?Y, ??Y) ->', '->')
                else:
                    pattern_l = pattern_l.replace(', lessThanOrEqual(?Y, ??Y) ->', '->')
                su0 = suppCalculate(k, iri, pattern_l)
                su = supportBySize(k, iri, su0, pattern_l)
                c = confCalculate(k, iri, pattern_l, su0)
            patternSet_l.add(tuple([pattern_l, su, c]))

    return patternSet_l


def Specialize_Location_withoutthreads(k, iri, patternSet, lSet, minConf, minSupp, maxConf, timeOut):
    patternSet_l = set()
    startTime = time.time()
    for pattern in patternSet:
        pattern_p = pattern[0]
        supp = pattern[1]
        conf = pattern[2]
        lAdd = False
        if conf < maxConf:
            for l in lSet:
                pattern_l = pattern_p.replace("Location", l)
                su0 = suppCalculate(k, iri, pattern_l)
                su = supportBySize(k, iri, su0, pattern_l)
                if su >= minSupp:
                    c = confCalculate(k, iri, pattern_l, su0)
                    if c > conf:  ######################################################## >= pour couvrir toutes les cas possibles; ou bien > pour limiter l'espace de recherche
                        # #print("1- c="+str(c)+" ... conf="+str(conf))
                        conf = c
                        lAdd = True
                        if 'ThanOrEqual(?Y' not in pattern_l:  ######################################################## pour recalculer la date aprés
                            if 'has_Diagnisis(?D, LOW)' in pattern_l:
                                pattern_l = pattern_l.replace(', greaterThanOrEqual(?Y, ??Y) ->', '->')
                            else:
                                pattern_l = pattern_l.replace(', lessThanOrEqual(?Y, ??Y) ->', '->')
                            su0 = suppCalculate(k, iri, pattern_l)
                            su = supportBySize(k, iri, su0, pattern_l)
                            c = confCalculate(k, iri, pattern_l, su0)
                        patternSet_l.add(tuple([pattern_l, su, c]))
                if time.time() - startTime > timeOut: break
        if time.time() - startTime > timeOut:
            break
        # if not lAdd:
        #     patternSet_l.add(tuple([pattern_p, supp, conf]))
    # patternSet_l.update(patternSet)
    return patternSet_l


def Specialize_Structure(k, iri, patternSet, sSet, minConf, minSupp, maxConf):
    patternSet_s = set()

    threads = map(lambda pattern: threading.Thread(
        target=lambda: Specialize_Structure_Threaded(k, iri, sSet, minConf, minSupp, maxConf, patternSet_s, pattern)), patternSet)
    for t in threads:
        t.start()
        t.join()

    return patternSet_s


def Specialize_Structure_Threaded(k, iri, sSet, minConf, minSupp, maxConf, patternSet_s, pattern):
    conf = pattern[2]
    if conf < maxConf:
        threads = map(lambda s: threading.Thread(
            target=lambda: Specialize_Structure_Threaded_s(k, iri, minConf, minSupp, maxConf, patternSet_s,
                                                         pattern, s)), sSet)
        for t in threads:
            t.start()
            t.join()

    return patternSet_s


def Specialize_Structure_Threaded_s(k, iri, minConf, minSupp, maxConf, patternSet_s, pattern, s):
    # #print('p')
    pattern_l = pattern[0]
    supp = pattern[1]
    conf = pattern[2]
    sAdd = False

    # #print(s)
    pattern_s = pattern_l.replace("Structure", s)
    su0 = suppCalculate(k, iri, pattern_s)
    su = supportBySize(k, iri, su0, pattern_s)
    if su > minSupp:
        c = confCalculate(k, iri, pattern_s, su0)
        if c >= conf:
            # #print("1- c="+str(c)+" ... conf="+str(conf))
            conf = c
            sAdd = True
            if 'ThanOrEqual(?Y' not in pattern_s:  ######################################################## pour recalculer la date aprés
                if 'has_Diagnisis(?D, LOW)' in pattern_s:
                    pattern_s = pattern_s.replace(', greaterThanOrEqual(?Y, ??Y) ->', '->')
                else:
                    pattern_s = pattern_s.replace(', lessThanOrEqual(?Y, ??Y) ->', '->')
                su0 = suppCalculate(k, iri, pattern_l)
                su = supportBySize(k, iri, su0, pattern_l)
                c = confCalculate(k, iri, pattern_l, su0)
            patternSet_s.add(tuple([pattern_s, su, c]))

    return patternSet_s


def Specialize_Structure_withoutthreads(k, iri, patternSet, sSet, minConf, minSupp, maxConf, timeOut):
    patternSet_s = set()
    startTime = time.time()
    for pattern in patternSet:
        # #print('p')
        pattern_l = pattern[0]
        supp = pattern[1]
        conf = pattern[2]
        sAdd = False
        if conf < maxConf:
            for s in sSet:
                # #print(s)
                pattern_s = pattern_l.replace("Structure", s)
                su0 = suppCalculate(k, iri, pattern_s)
                su = supportBySize(k, iri, su0, pattern_s)
                if su > minSupp:
                    c = confCalculate(k, iri, pattern_s, su0)
                    if c >= conf:
                        # #print("1- c="+str(c)+" ... conf="+str(conf))
                        conf = c
                        sAdd = True
                        if 'ThanOrEqual(?Y' not in pattern_s:  ######################################################## pour recalculer la date aprés
                            if 'has_Diagnisis(?D, LOW)' in pattern_s:
                                pattern_s = pattern_s.replace(', greaterThanOrEqual(?Y, ??Y) ->', '->')
                            else:
                                pattern_s = pattern_s.replace(', lessThanOrEqual(?Y, ??Y) ->', '->')
                            su0 = suppCalculate(k, iri, pattern_l)
                            su = supportBySize(k, iri, su0, pattern_l)
                            c = confCalculate(k, iri, pattern_l, su0)
                        patternSet_s.add(tuple([pattern_s, su, c]))
                if time.time() - startTime > timeOut: break
        if time.time() - startTime > timeOut:
            break
        # if not sAdd:
        #     patternSet_s.add(tuple([pattern_l, supp, conf]))
    # patternSet_s.update(patternSet)
    return patternSet_s


def TemporalGeneralization_old(k, k_onto, patternSet, minConf, minSupp, maxConf, startDate):
    patternSet_T = set()
    # #print('temps')
    for patternInfo in patternSet:
        # #print('0')
        tAdd = False
        pattern = patternInfo[0]
        if patternInfo[2] < maxConf or 'ThanOrEqual(?Y' in pattern:
            if 'ThanOrEqual(?Y' not in pattern:
                # #print('1')
                if 'has_Diagnisis(?D, LOW)' in pattern:
                    pattern = pattern.replace('->', ', greaterThanOrEqual(?Y, ??Y) ->')
                    # #print('g')
                else:
                    pattern = pattern.replace('->', ', lessThanOrEqual(?Y, ??Y) ->')
            else:
                year = re.findall(r'\d\d\d\d', pattern)
                pattern = pattern.replace(year[0], '??Y')
                # #print('r')
            date = startDate
            # #print(date)
            pattern_d = pattern.replace("??Y", str(date))
            # #print("-"+pattern_d)
            supp0 = suppCalculate(k, k_onto, pattern_d)
            supp = supportBySize(k, k_onto, supp0, pattern_d)
            # #print(supp)
            conf = confCalculate(k, k_onto, pattern_d, supp0)
            # #print(conf)
            s = supp
            c = conf
            d = date
            if 'has_Diagnisis(?D, LOW)' in pattern:
                # #print(2)
                if conf >= minConf:
                    # #print(3)
                    while supp < minSupp and date > 1946:
                        date -= 1
                        supp0 = suppCalculate(k, k_onto, pattern.replace("??Y", str(date)))
                        supp = supportBySize(k, k_onto, supp0, pattern.replace("??Y", str(date)))
                        # #print('-'+str(supp) + str(date))
                    if supp >= minSupp:
                        # #print(4)
                        conf = confCalculate(k, k_onto, pattern.replace("??Y", str(date)), supp0)
                        maxConf = conf
                        while conf >= maxConf and supp >= minSupp and date >= 1946:
                            d = date
                            s = supp
                            c = conf
                            date -= 1
                            supp0 = suppCalculate(k, k_onto, pattern.replace("??Y", str(date)))
                            supp = supportBySize(k, k_onto, supp0, pattern.replace("??Y", str(date)))
                            conf = confCalculate(k, k_onto, pattern.replace("??Y", str(date)), supp0)
                            # #print(str(date)+str(supp)+str(conf))
                        pattern = pattern.replace("??Y", str(d))
                        tAdd = True
                # else:
                #     continu = False
            elif 'has_Diagnisis(?D, HIGH)' in pattern:
                # #print(conf)
                if supp >= minSupp:
                    while conf < maxConf and supp >= minSupp and date >= 1946:
                        # #print('date' + str(date))
                        # #print(conf)
                        d = date
                        s = supp
                        c = conf
                        date -= 1
                        supp0 = suppCalculate(k, k_onto, pattern.replace("??Y", str(date)))
                        supp = supportBySize(k, k_onto, supp0, pattern.replace("??Y", str(date)))
                        conf = confCalculate(k, k_onto, pattern.replace("??Y", str(date)), supp0)
                    if c >= minConf:
                        pattern = pattern.replace("??Y", str(d))
                        tAdd = True
                #     else:
                #         continu = False
                # else:
                #    continu = False
        if tAdd:
            patternSet_T.add(tuple([pattern, s, c]))
        else:
            patternSet_T.add(tuple([patternInfo[0], patternInfo[1], patternInfo[2]]))

    return patternSet_T


def TemporalGeneralization(k, iri, patternSet, minConf, minSupp, maxConf, startDate, timeOut):
    patternSet_T = set()
    startTime = time.time()
    # #print('temps')

    threads = map(lambda patternInfo: threading.Thread(
        target=lambda: TemporalGeneralization_Threaded(k, iri, minConf, minSupp, maxConf, startDate, timeOut, patternSet_T, patternInfo)),
                  patternSet)
    for t in threads:
        t.start()
        t.join()

    return patternSet_T


def TemporalGeneralization_Threaded(k, iri, minConf, minSupp, maxConf, startDate, timeOut, patternSet_T, patternInfo):
    # patternSet_T = set()
    startTime = time.time()
    # #print('temps')
    # for patternInfo in patternSet:
    # #print('0')
    tAdd = False
    pattern = patternInfo[0]
    if patternInfo[2] < maxConf or 'ThanOrEqual(?Y' in pattern:
        if 'ThanOrEqual(?Y' not in pattern:
            # #print('1')
            if 'has_Diagnisis(?D, LOW)' in pattern:
                pattern = pattern.replace('->', ', greaterThanOrEqual(?Y, ??Y) ->')
                # #print('g')
            else:
                pattern = pattern.replace('->', ', lessThanOrEqual(?Y, ??Y) ->')
        else:
            year = re.findall(r'\d\d\d\d', pattern)
            pattern = pattern.replace(year[0], '??Y')
            # #print('r')
        date = startDate
        # #print(date)
        pattern_d = pattern.replace("??Y", str(date))
        # #print("-"+pattern_d)
        supp0 = suppCalculate(k, iri, pattern_d)
        supp = supportBySize(k, iri, supp0, pattern_d)
        # #print(supp)
        conf = confCalculate(k, iri, pattern_d, supp0)
        # #print(conf)
        s = supp
        c = conf
        d = date
        # #print(pattern)
        if 'has_Diagnisis(?D, LOW)' in pattern:
            # print('LOW')
            # #print(2)
            # print(conf)
            # print(supp)
            while supp < minSupp and date > 1946:
                if time.time() - startTime > timeOut:
                    break
                date -= 1
                supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                # #print('-'+str(supp) + str(date))
            if supp >= minSupp:
                conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                # print(3)
                # while supp < minSupp and date > 1946:
                #     if time.time() - startTime > timeOut:
                #         break
                #     date -= 1
                #     supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                #     supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                #     # #print('-'+str(supp) + str(date))
                # print(supp)
                if conf >= minConf:
                    # print(4)
                    conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                    maxConf = conf
                    # print(maxConf)
                    while conf >= maxConf and supp >= minSupp and date >= 1946:
                        if time.time() - startTime > timeOut:
                            break
                        # print('date' + str(date))
                        # print(conf)
                        # print(supp)
                        d = date
                        s = supp
                        c = conf
                        date -= 1
                        supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                        supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                        conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                        # #print(str(date)+str(supp)+str(conf))
                    pattern = pattern.replace("??Y", str(d))
                    tAdd = True
            # else:
            #     continu = False
        elif 'has_Diagnisis(?D, HIGH)' in pattern:
            #print('HIGH')
            # #print(conf)
            if supp >= minSupp:
                # while conf < minConf and date > 1946:
                #     if time.time() - startTime > timeOut:
                #         break
                #     date -= 1
                #     # #print('d' + str(date))
                #     supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                #     conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                if conf >= minConf:
                    # print('dd')
                    # print(conf)
                    # print(supp)
                    supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                    suppmc = suppCalculate(k, iri, pattern.replace("??Y", str(date - 1)))
                    maxConf = confCalculate(k, iri, pattern.replace("??Y", str(date - 1)), suppmc)
                    # print(conf)
                    # print(maxConf)
                    # print(supp)
                    take = False
                    while conf <= maxConf and conf < 1 and supp >= minSupp and date >= 1946:
                        if time.time() - startTime > timeOut:
                            break
                        # print('date' + str(date))
                        # print(conf)
                        # print(supp)
                        if conf < maxConf:
                            d = date
                            take = True
                        # s = supp
                        # c = conf
                        date -= 1
                        supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                        supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                        conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                        suppmc = suppCalculate(k, iri, pattern.replace("??Y", str(date - 1)))
                        maxConf = confCalculate(k, iri, pattern.replace("??Y", str(date - 1)), suppmc)
                        if take:
                            s = supp
                            c = conf
                            take = False
                    if c >= minConf:#and c > conf initial
                        pattern = pattern.replace("??Y", str(d))
                        tAdd = True
            #     else:
            #         continu = False
            # else:
            #    continu = False
    if tAdd:
        patternSet_T.add(tuple([pattern, s, c]))
    else:
        patternSet_T.add(tuple([patternInfo[0], patternInfo[1], patternInfo[2]]))

    return patternSet_T


def TemporalGeneralization_withoutthreads(k, iri, patternSet, minConf, minSupp, maxConf, startDate, timeOut):
    patternSet_T = set()
    startTime = time.time()
    # #print('temps')
    for patternInfo in patternSet:
        # #print('0')
        tAdd = False
        pattern = patternInfo[0]
        if patternInfo[2] < maxConf or 'ThanOrEqual(?Y' in pattern:
            if 'ThanOrEqual(?Y' not in pattern:
                # #print('1')
                if 'has_Diagnisis(?D, LOW)' in pattern:
                    pattern = pattern.replace('->', ', greaterThanOrEqual(?Y, ??Y) ->')
                    # #print('g')
                else:
                    pattern = pattern.replace('->', ', lessThanOrEqual(?Y, ??Y) ->')
            else:
                year = re.findall(r'\d\d\d\d', pattern)
                pattern = pattern.replace(year[0], '??Y')
                # #print('r')
            date = startDate
            # #print(date)
            pattern_d = pattern.replace("??Y", str(date))
            # #print("-"+pattern_d)
            supp0 = suppCalculate(k, iri, pattern_d)
            supp = supportBySize(k, iri, supp0, pattern_d)
            # #print(supp)
            conf = confCalculate(k, iri, pattern_d, supp0)
            # #print(conf)
            s = supp
            c = conf
            d = date
            # #print(pattern)
            if 'has_Diagnisis(?D, LOW)' in pattern:
                # #print('LOW')
                # #print(2)
                if conf >= minConf:
                    # #print(3)
                    # while supp < minSupp and date > 1946:
                    #     if time.time() - startTime > timeOut:
                    #         break
                    #     date -= 1
                    #     supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                    #     supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                    #     # #print('-'+str(supp) + str(date))
                    if supp >= minSupp:
                        # #print(4)
                        conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                        maxConf = conf
                        while conf >= maxConf and supp >= minSupp and date >= 1946:
                            if time.time() - startTime > timeOut:
                                break
                            d = date
                            s = supp
                            c = conf
                            date -= 1
                            supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                            supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                            conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                            # #print(str(date)+str(supp)+str(conf))
                        pattern = pattern.replace("??Y", str(d))
                        tAdd = True
                # else:
                #     continu = False
            elif 'has_Diagnisis(?D, HIGH)' in pattern:
                # #print('HIGH')
                # #print(conf)
                if supp >= minSupp:
                    # while conf < minConf and date > 1946:
                    #     if time.time() - startTime > timeOut:
                    #         break
                    #     date -= 1
                    #     # #print('d' + str(date))
                    #     supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                    #     conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                    if conf >= minConf:
                        # #print('dd')
                        supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                        suppmc = suppCalculate(k, iri, pattern.replace("??Y", str(date - 1)))
                        maxConf = confCalculate(k, iri, pattern.replace("??Y", str(date - 1)), suppmc)
                        while conf < maxConf and supp >= minSupp and date >= 1946:
                            if time.time() - startTime > timeOut:
                                break
                            # #print('date' + str(date))
                            # #print(conf)
                            d = date
                            s = supp
                            c = conf
                            date -= 1
                            supp0 = suppCalculate(k, iri, pattern.replace("??Y", str(date)))
                            supp = supportBySize(k, iri, supp0, pattern.replace("??Y", str(date)))
                            conf = confCalculate(k, iri, pattern.replace("??Y", str(date)), supp0)
                            suppmc = suppCalculate(k, iri, pattern.replace("??Y", str(date - 1)))
                            maxConf = confCalculate(k, iri, pattern.replace("??Y", str(date - 1)), suppmc)
                        if c >= minConf:
                            pattern = pattern.replace("??Y", str(d))
                            tAdd = True
                #     else:
                #         continu = False
                # else:
                #    continu = False
        if tAdd:
            patternSet_T.add(tuple([pattern, s, c]))
        else:
            patternSet_T.add(tuple([patternInfo[0], patternInfo[1], patternInfo[2]]))

    return patternSet_T


# #print(TemporalGeneralization(k, k_onto, {('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), peinture(?P2), contain(?L, ?P2), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1951) -> has_Diagnisis(?D, LOW)', 1, 1.0)}, 0, 1, 1, 1997))
# #print(TemporalGeneralization(k, k_onto, {('colle(?P), Location(?L), cuisine(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 1, 1.0)}, 0, 1, 1, 1997))




def SelectProductBrother(k, iri, lSet, p):
    brothersList = []

    threads = map(lambda l: threading.Thread(
        target=lambda: SelectProductBrother_Threaded(k, iri, brothersList, l)), lSet)
    for t in threads:
        t.start()
        t.join()

    brothersList.remove(p)

    return brothersList


def SelectProductBrother_Threaded(k, iri, brothersList, l):
    # for l in lSet:
    q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Location rdf:type ?l . ?l rdfs:subClassOf* :Location . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
    qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l)})

    productList = []
    for row in qres:
        brothersList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    return brothersList


def SelectProductBrother_withouthreads(k, iri, lSet, p):
    brothersList = []
    for l in lSet:
        q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Location rdf:type ?l . ?l rdfs:subClassOf* :Location . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l)})

        productList = []
        for row in qres:
            brothersList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    brothersList.remove(p)

    return brothersList


def SelectLocationBrother(k, iri, lSet):
    brothersList = []

    threads = map(lambda l: threading.Thread(
        target=lambda: SelectLocationBrother_Threaded(k, iri, brothersList, l)), lSet)
    for t in threads:
        t.start()
        t.join()

    return brothersList


def SelectLocationBrother_Threaded(k, iri, brothersList, l):
    # for l in lSet:
    q = 'SELECT DISTINCT ?x WHERE { ?Structure :has_location ?Location . ?Structure :has_location ?Location2 . ?Location rdf:type ?l . ?l rdfs:subClassOf* :Location . ?Location2 rdf:type ?x . ?x rdfs:subClassOf* :Location .}'
    qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l)})

    productList = []
    for row in qres:
        brothersList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    brothersList.remove(l)

    return brothersList


def SelectLocationBrother_withoutthreads(k, iri, lSet):
    brothersList = []
    for l in lSet:
        q = 'SELECT DISTINCT ?x WHERE { ?Structure :has_location ?Location . ?Structure :has_location ?Location2 . ?Location rdf:type ?l . ?l rdfs:subClassOf* :Location . ?Location2 rdf:type ?x . ?x rdfs:subClassOf* :Location .}'
        qres = k.query(q, initBindings={'l': rdflib.term.URIRef(iri + l)})

        productList = []
        for row in qres:
            brothersList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        brothersList.remove(l)

    return brothersList


def SelectType(k, iri, p):
    q = 'SELECT DISTINCT ?x WHERE { ?Building :has_structure ?Structure . ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product rdf:type ?p . ?Building :has_type ?x . }'
    qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p)})

    typeList = []
    for row in qres:
        typeList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    return typeList


def SelectRegion(k, iri, p):
    q = 'SELECT DISTINCT ?x WHERE { ?Building :has_structure ?Structure . ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product rdf:type ?p . ?Building :has_region ?x . }'
    qres = k.query(q, initBindings={'p': rdflib.term.URIRef(iri + p)})

    regionList = []
    for row in qres:
        regionList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    return regionList


def EnrichmentData(k, iri, R_initial, minConf, minSupp, maxConf, timeOut):
    patternSet = set()
    patternSetT = set()
    startTime = time.time()

    threads = map(lambda ri: threading.Thread(
        target=lambda: EnrichmentData_Threaded_type(k, iri, R_initial, minConf, minSupp, maxConf, timeOut, patternSetT, ri)),
                  R_initial)
    for t in threads:
        t.start()
        t.join()

    # patternSetT.update(R_initial) # a little bit longer with this one

    threads = map(lambda pt: threading.Thread(
        target=lambda: EnrichmentData_Threaded_region(k, iri, R_initial, minConf, minSupp, maxConf, timeOut, patternSet, pt)),
                  patternSetT)
    for t in threads:
        t.start()
        t.join()

    patternSet.update(patternSetT)
    return patternSet


def EnrichmentData_Threaded_type(k, iri, R_initial, minConf, minSupp, maxConf, timeOut, patternSetT, ri):
    # patternSet = set()
    # patternSetT = set()
    # startTime = time.time()
    # for ri in R_initial:
    r = ri[0]
    # su = ri[1]
    c = ri[2]
    p = r[:r.find('(')]
    if c < maxConf:
        tSet = SelectType(k, iri, p)

        threads = map(lambda t: threading.Thread(
            target=lambda: EnrichmentData_Threaded_type_t(k, iri, R_initial, minConf, minSupp, maxConf, timeOut,
                                                        patternSetT, ri, t)),
                      tSet)
        for t in threads:
            t.start()
            t.join()

    return patternSetT


def EnrichmentData_Threaded_type_t(k, iri, R_initial, minConf, minSupp, maxConf, timeOut, patternSetT, ri, t):
    # patternSet = set()
    # patternSetT = set()
    # startTime = time.time()
    # for ri in R_initial:
    r = ri[0]
    # su = ri[1]
    c = ri[2]
    # p = r[:r.find('(')]
    # if c < maxConf:
    #     tSet = SelectType(k, iri, p)
    #     for t in tSet:
    pattern = r.replace('?T', t)
    supp0 = suppCalculate(k, iri, pattern)
    supp = supportBySize(k, iri, supp0, pattern)
    if supp > minSupp:
        conf = confCalculate(k, iri, pattern, supp0)
        if conf > c:
            patternSetT.add(tuple([pattern, supp, conf]))
    # if time.time() - startTime > timeOut:
    #     break
    return patternSetT


def EnrichmentData_Threaded_region(k, iri, R_initial, minConf, minSupp, maxConf, timeOut, patternSet, pt):
    # patternSet = set()
    # patternSetT = set()
    # startTime = time.time()

    # for pt in patternSetT:
    r = pt[0]
    # su = pt[1]
    c = pt[2]
    p = r[:r.find('(')]
    if c < maxConf:
        rSet = SelectRegion(k, iri, p)

        threads = map(lambda region: threading.Thread(
            target=lambda: EnrichmentData_Threaded_region_r(k, iri, R_initial, minConf, minSupp, maxConf, timeOut,
                                                          patternSet, pt, region)),
                      rSet)
        for t in threads:
            t.start()
            t.join()

    return patternSet


def EnrichmentData_Threaded_region_r(k, iri, R_initial, minConf, minSupp, maxConf, timeOut, patternSet, pt, region):
    # patternSet = set()
    # patternSetT = set()
    # startTime = time.time()

    # for pt in patternSetT:
    r = pt[0]
    # su = pt[1]
    c = pt[2]
    # p = r[:r.find('(')]
    # if c < maxConf:
    #     rSet = SelectRegion(k, iri, p)
    #     for region in rSet:
    pattern = r.replace('?R', region)
    supp0 = suppCalculate(k, iri, pattern)
    supp = supportBySize(k, iri, supp0, pattern)
    if supp > minSupp:
        conf = confCalculate(k, iri, pattern, supp0)
        if conf > c:
            patternSet.add(tuple([pattern, supp, conf]))

    return patternSet


def EnrichmentData_withoutthreads(k, iri, R_initial, minConf, minSupp, maxConf, timeOut):
    patternSet = set()
    patternSetT = set()
    startTime = time.time()
    for ri in R_initial:
        r = ri[0]
        su = ri[1]
        c = ri[2]
        p = r[:r.find('(')]
        if c < maxConf:
            tSet = SelectType(k, iri, p)
            for t in tSet:
                pattern = r.replace('?T', t)
                supp0 = suppCalculate(k, iri, pattern)
                supp = supportBySize(k, iri, supp0, pattern)
                if supp > minSupp:
                    conf = confCalculate(k, iri, pattern, supp0)
                    if conf > c:
                        patternSetT.add(tuple([pattern, supp, conf]))
                if time.time() - startTime > timeOut:
                    break
    # patternSetT.update(R_initial)
    for pt in patternSetT:
        r = pt[0]
        su = pt[1]
        c = pt[2]
        p = r[:r.find('(')]
        if c < maxConf:
            rSet = SelectRegion(k, iri, p)
            for region in rSet:
                pattern = r.replace('?R', region)
                supp0 = suppCalculate(k, iri, pattern)
                supp = supportBySize(k, iri, supp0, pattern)
                if supp > minSupp:
                    conf = confCalculate(k, iri, pattern, supp0)
                    if conf > c:
                        patternSet.add(tuple([pattern, supp, conf]))
                if time.time() - startTime > timeOut:
                    break
    patternSet.update(patternSetT)
    return patternSet


def EnrichmentObject(k, iri, R_initial, lSet, p, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut):
    patternSet = set()
    stratTime = time.time()

    threads = map(lambda ri: threading.Thread(
        target=lambda: EnrichmentObject_Threaded(k, iri, lSet, p, minConf, minSupp, maxConf, maxBrotherP,
                                                 maxBrotherL, timeOut, patternSet, ri)),
                  R_initial)
    for t in threads:
        t.start()
        t.join()


    return patternSet


def EnrichmentObject_Threaded(k, iri, lSet, p, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut, patternSet, ri):
    stratTime = time.time()
    # for ri in R_initial:
    found = False
    numP = 2
    r = ri[0]
    su = ri[1]
    c = ri[2]
    if c < maxConf:
        pBrotherSet = SelectProductBrother(k, iri, lSet, p)
        lBrotherSet = SelectLocationBrother(k, iri, lSet)
        pBrotherNum = 0
        for b in pBrotherSet:
            rf = r.replace("contain(?L, ?P), ",
                           "contain(?L, ?P), " + b + "(?P" + str(numP) + "), contain(?L, ?P" + str(numP) + "), ")
            # #print("**"+rf)
            supp0 = suppCalculate(k, iri, rf)
            supp = supportBySize(k, iri, supp0, rf)
            # #print(supp)
            conf = confCalculate(k, iri, rf, supp0)
            # #print(conf)
            if supp >= minSupp and conf > c:
                found = True
                numP += 1
                r = rf
                su = supp
                c = conf
                pBrotherNum += 1
                if pBrotherNum == maxBrotherP:
                    break
            if time.time() - stratTime > timeOut:
                break
        numL = 2
        lBrotherNum = 0
        for lb in lBrotherSet:
            rf = r.replace("has_location(?S, ?L), ",
                           "has_location(?S, ?L), " + lb + "(?L" + str(numL) + "), has_location(?S, ?L" + str(
                               numL) + "), ")
            # #print("--"+rf)
            supp0 = suppCalculate(k, iri, rf)
            supp = supportBySize(k, iri, supp0, rf)
            # #print(supp)
            conf = confCalculate(k, iri, rf, supp0)
            # #print(conf)
            if supp >= minSupp and conf > c:
                found = True
                numL += 1
                r = rf
                su = supp
                c = conf
                lBrotherNum += 1
                if lBrotherNum == maxBrotherL:
                    break
            if time.time() - stratTime > timeOut:
                break

    if (found):
        patternSet.add(tuple([r, su, c]))

    return patternSet


def EnrichmentObject_withoutthreads(k, iri, R_initial, lSet, p, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut):
    patternSet = set()
    stratTime = time.time()
    for ri in R_initial:
        found = False
        numP = 2
        r = ri[0]
        su = ri[1]
        c = ri[2]
        if c < maxConf:
            pBrotherSet = SelectProductBrother(k, iri, lSet, p)
            lBrotherSet = SelectLocationBrother(k, iri, lSet)
            pBrotherNum = 0
            for b in pBrotherSet:
                rf = r.replace("contain(?L, ?P), ",
                               "contain(?L, ?P), " + b + "(?P" + str(numP) + "), contain(?L, ?P" + str(numP) + "), ")
                # #print("**"+rf)
                supp0 = suppCalculate(k, iri, rf)
                supp = supportBySize(k, iri, supp0, rf)
                # #print(supp)
                conf = confCalculate(k, iri, rf, supp0)
                # #print(conf)
                if supp >= minSupp and conf > c:
                    found = True
                    numP += 1
                    r = rf
                    su = supp
                    c = conf
                    pBrotherNum += 1
                    if pBrotherNum == maxBrotherP:
                        break
                if time.time() - stratTime > timeOut:
                    break
            numL = 2
            lBrotherNum = 0
            for lb in lBrotherSet:
                rf = r.replace("has_location(?S, ?L), ",
                               "has_location(?S, ?L), " + lb + "(?L" + str(numL) + "), has_location(?S, ?L" + str(
                                   numL) + "), ")
                # #print("--"+rf)
                supp0 = suppCalculate(k, iri, rf)
                supp = supportBySize(k, iri, supp0, rf)
                # #print(supp)
                conf = confCalculate(k, iri, rf, supp0)
                # #print(conf)
                if supp >= minSupp and conf > c:
                    found = True
                    numL += 1
                    r = rf
                    su = supp
                    c = conf
                    lBrotherNum += 1
                    if lBrotherNum == maxBrotherL:
                        break
                if time.time() - stratTime > timeOut:
                    break

        if (found):
            patternSet.add(tuple([r, su, c]))

    return patternSet


def VerifyHearchyProduct(k, iri, R_initial, minSupp, minConf, maxConf, timeOut):
    R_initial_Hearchy = set()
    startTime = time.time()
    for pattern in R_initial:
        if pattern[1] >= minSupp and pattern[2] >= minConf and pattern[2] < maxConf:
            product = pattern[0][0:pattern[0].find('(?P)')]
            productHearchy = SelectProductHearchy(k, iri, product)
            for p in productHearchy:
                patt = pattern[0].replace(product + '(?P)', p + '(?P)', 1)
                supp0 = suppCalculate(k, iri, patt)
                supp = supportBySize(k, iri, supp0, patt)
                if supp >= minSupp:
                    conf = confCalculate(k, iri, patt, supp0)
                    if conf > pattern[2]:
                        R_initial_Hearchy.add(tuple([patt, supp, conf]))
        if time.time() - startTime > timeOut:
            break
    return R_initial_Hearchy


def VerifyHearchyLocation(k, iri, R_initial, minSupp, minConf, maxConf, timeOut):
    R_initial_Hearchy = set()
    startTime = time.time()
    for pattern in R_initial:
        if pattern[1] >= minSupp and pattern[2] >= minConf and pattern[2] < maxConf:
            location = pattern[0][pattern[0].find('(?P), ') + len('(?P), '):pattern[0].find('(?L)')]
            locationHearchy = SelectLocationHearchy(k, iri, location)
            for l in locationHearchy:
                patt = pattern[0].replace(location + '(?L)', l + '(?L)', 1)
                supp0 = suppCalculate(k, iri, patt)
                supp = supportBySize(k, iri, supp0, patt)
                if supp >= minSupp:
                    conf = confCalculate(k, iri, patt, supp0)
                    if conf > pattern[2]:
                        R_initial_Hearchy.add(tuple([patt, supp, conf]))
        if time.time() - startTime > timeOut:
            break
    return R_initial_Hearchy


def ALGO_full(k, k_onto, pattern, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL):
    ruleSetFiltred = set()
    ruleSet = set()
    pSet = SelectProduct(k, k_onto)
    # #print(pSet)
    #print(len(pSet))
    i = 0
    for p in pSet:
        #print('**************************************************************')
        #print(p)
        #print(i)
        i += 1
        #print('Step1:')

        lSet = SelectLocation(k, k_onto, p)
        sSet = SelectStructure(k, k_onto, p)
        ruleSet_P = Specialize_Product(k, k_onto, pattern, p, minSupp)
        #print(ruleSet_P)
        ruleSet_PT = TemporalGeneralization(k, k_onto, ruleSet_P, minConf, minSupp, maxConf, 1997)
        #print(ruleSet_PT)
        ruleSet_subP = VerifyHearchyProduct(k, k_onto, ruleSet_P, minSupp, minConf, maxConf)
        ruleSet_subPT = TemporalGeneralization(k, k_onto, ruleSet_subP, minConf, minSupp, maxConf, 1997)
        ruleSet_PT.update(ruleSet_subPT)

        #print(ruleSet_PT)
        #print('Step2:')

        ruleSet_L = Specialize_Location(k, k_onto, ruleSet_PT, lSet, minConf, minSupp, maxConf)
        #print(ruleSet_L)
        ruleSet_LT = TemporalGeneralization(k, k_onto, ruleSet_L, minConf, minSupp, maxConf, 1997)
        #print(ruleSet_LT)
        ruleSet_subL = VerifyHearchyLocation(k, k_onto, ruleSet_L, minSupp, minConf, maxConf)
        ruleSet_subLT = TemporalGeneralization(k, k_onto, ruleSet_subL, minConf, minSupp, maxConf, 1997)
        ruleSet_LT.update(ruleSet_subLT)

        #print(ruleSet_LT)
        #print('Step3:')

        ruleSet_S = Specialize_Structure(k, k_onto, ruleSet_LT, sSet, minConf, minSupp, maxConf)
        #print('sFF')
        ruleSet_ST = TemporalGeneralization(k, k_onto, ruleSet_S, minConf, minSupp, maxConf, 1997)

        #print(ruleSet_ST)
        #print('Step4:')

        R_d = EnrichmentData(k, k_onto, ruleSet_ST, minConf, minSupp, maxConf)
        #print('rd')
        R_f = EnrichmentObject(k, k_onto, R_d, lSet, p, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL)
        #print('rf')
        R_ft = TemporalGeneralization(k, k_onto, R_f, minConf, minSupp, maxConf, 1997)
        #print('rft')
        ruleSet.update(R_ft)

    #print(ruleSet)

    for rule in ruleSet:
        if rule[1] >= minSupp and rule[2] >= minConf:
            ruleSetFiltred.add(rule)

        # R_initial = Instantiate(k, k_onto, pattern, p, lSet, sSet, minConf, minSupp, maxConf)
        # # #print(R_initial)
        # if R_initial:
        #     # #print('-')
        #     # #print(R_initial)
        #     # #print(VerifyHearchyProduct(k, k_onto, R_initial, minSupp, minConf, maxConf))
        #     # #print(VerifyHearchyLocation(k, k_onto, R_initial, minSupp, minConf, maxConf))
        #     # R_initial_Hearchy = VerifyHearchy(k, k_onto, R_initial, minSupp, minConf, maxConf) #################################################
        #     pBrotherSet = SelectProductBrother(k, k_onto, lSet, p)
        #     # #print(pBrotherSet)
        #     lBrotherSet = SelectLocationBrother(k, k_onto, lSet)
        #     # #print(lBrotherSet)
        #
        #     R_f = Combine(k, k_onto, R_initial, pBrotherSet, lBrotherSet, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL)
        #     ruleSet.update(R_f)

    return ruleSetFiltred


def ALGO_optimized_Paralel(k, iri, pattern, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut, num_cores):
    ruleSetFiltred = set()
    ruleSet = set()
    pSet = SelectProduct(k, iri)
    # print(pSet)
    print(len(pSet))

    results = Parallel(n_jobs=num_cores)(
        delayed(ALGO_optimized)(k, iri, pattern, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut, num_cores, p) for p in pSet)

    for r in results:
        ruleSet.update(r)

    for rule in ruleSet:
        if rule[1] >= minSupp and rule[2] >= minConf:
            ruleSetFiltred.add(rule)

    return ruleSetFiltred


def ALGO_optimized(k, iri, pattern, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut, num_cores, p):
    ruleSet = set()
    # for p in pSet:
    print('**************************************************************')
    print(p)
    print('Step1:')

    lSet = SelectLocation(k, iri, p)
    sSet = SelectStructure(k, iri, p)
    # ruleSet_P = Specialize_Product_Paralel(k, iri, pattern, p, minSupp, num_cores)
    ruleSet_P = Specialize_Product(k, iri, pattern, p, minSupp)
    print(ruleSet_P)
    print('*ruleSet_P')
    ruleSet_PT = TemporalGeneralization(k, iri, ruleSet_P, minConf, minSupp, maxConf, 1997, timeOut)
    print(ruleSet_PT)
    print('*ruleSet_PT')
    ruleSet_subP = VerifyHearchyProduct(k, iri, ruleSet_P, minSupp, minConf, maxConf, timeOut)
    print(ruleSet_subP)
    print('*ruleSet_subP')
    ruleSet_subPT = TemporalGeneralization(k, iri, ruleSet_subP, minConf, minSupp, maxConf, 1997, timeOut)
    print(ruleSet_subPT)
    print('*ruleSet_subPT')
    ruleSet_PT.update(ruleSet_subPT)

    print(ruleSet_PT)
    print('Step2:')

    ruleSet_L = Specialize_Location(k, iri, ruleSet_PT, lSet, minConf, minSupp, maxConf)
    print(ruleSet_L)
    print('*ruleSet_L')
    ruleSet_LT = TemporalGeneralization(k, iri, ruleSet_L, minConf, minSupp, maxConf, 1997, timeOut)
    print(ruleSet_LT)
    print('*ruleSet_LT')
    ruleSet_subL = VerifyHearchyLocation(k, iri, ruleSet_L, minSupp, minConf, maxConf, timeOut)
    print(ruleSet_subL)
    print('*ruleSet_subL')
    ruleSet_subLT = TemporalGeneralization(k, iri, ruleSet_subL, minConf, minSupp, maxConf, 1997, timeOut)
    print(ruleSet_subLT)
    print('*ruleSet_subLT')
    ruleSet_L.update(ruleSet_subLT)
    ruleSet_L.update(ruleSet_PT)

    print(ruleSet_LT)
    print('Step3:')

    ruleSet_S = Specialize_Structure(k, iri, ruleSet_L, sSet, minConf, minSupp, maxConf)
    print(ruleSet_S)
    print('*ruleSet_S')
    ruleSet_ST = TemporalGeneralization(k, iri, ruleSet_S, minConf, minSupp, maxConf, 1997, timeOut)
    print(ruleSet_ST)
    print('*ruleSet_ST')
    ruleSet_S.update(ruleSet_L)

    print(ruleSet_S)
    print('Step4:')

    R_d = EnrichmentData(k, iri, ruleSet_S, minConf, minSupp, maxConf, timeOut)
    print(R_d)
    print('*R_d')
    R_dt = TemporalGeneralization(k, iri, R_d, minConf, minSupp, maxConf, 1997, timeOut)
    print(R_dt)
    print('*R_dt')
    ruleSet_S.update(R_dt)
    R_f = EnrichmentObject(k, iri, ruleSet_S, lSet, p, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut)
    print(R_f)
    print('*R_f')

    ruleSet_S.update(R_f)

    print(ruleSet_S)
    ruleSet.update(ruleSet_S)

    print(ruleSet)

    # f = open(p + ".txt", "w")
    # f.write(str(ruleSet))
    # f.close()


    return ruleSet

# def ALGO_optimized(k, iri, pattern, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut):
#     ruleSetFiltred = set()
#     ruleSet = set()
#     pSet = SelectProduct(k, iri)
#     # #print(pSet)
#     #print(len(pSet))
#     i = 0
#     for p in pSet:
#         #print('**************************************************************')
#         #print(p)
#         #print(i)
#         i += 1
#         #print('Step1:')
#
#         lSet = SelectLocation(k, iri, p)
#         sSet = SelectStructure(k, iri, p)
#         ruleSet_P = Specialize_Product(k, iri, pattern, p, minSupp)
#         #print(ruleSet_P)
#         #print('*ruleSet_P')
#         ruleSet_PT = TemporalGeneralization(k, iri, ruleSet_P, minConf, minSupp, maxConf, 1997, timeOut)
#         #print(ruleSet_PT)
#         #print('*ruleSet_PT')
#         ruleSet_subP = VerifyHearchyProduct(k, iri, ruleSet_P, minSupp, minConf, maxConf, timeOut)
#         #print(ruleSet_subP)
#         #print('*ruleSet_subP')
#         ruleSet_subPT = TemporalGeneralization(k, iri, ruleSet_subP, minConf, minSupp, maxConf, 1997, timeOut)
#         #print(ruleSet_subPT)
#         #print('*ruleSet_subPT')
#         ruleSet_PT.update(ruleSet_subPT)
#
#         #print(ruleSet_PT)
#         #print('Step2:')
#
#         ruleSet_L = Specialize_Location(k, iri, ruleSet_PT, lSet, minConf, minSupp, maxConf, timeOut)
#         #print(ruleSet_L)
#         #print('*ruleSet_L')
#         ruleSet_LT = TemporalGeneralization(k, iri, ruleSet_L, minConf, minSupp, maxConf, 1997, timeOut)
#         #print(ruleSet_LT)
#         #print('*ruleSet_LT')
#         ruleSet_subL = VerifyHearchyLocation(k, iri, ruleSet_L, minSupp, minConf, maxConf, timeOut)
#         #print(ruleSet_subL)
#         #print('*ruleSet_subL')
#         ruleSet_subLT = TemporalGeneralization(k, iri, ruleSet_subL, minConf, minSupp, maxConf, 1997, timeOut)
#         #print(ruleSet_subLT)
#         #print('*ruleSet_subLT')
#         ruleSet_L.update(ruleSet_subLT)
#         ruleSet_L.update(ruleSet_PT)
#
#         #print(ruleSet_LT)
#         #print('Step3:')
#
#         ruleSet_S = Specialize_Structure(k, iri, ruleSet_L, sSet, minConf, minSupp, maxConf, timeOut)
#         #print(ruleSet_S)
#         #print('*ruleSet_S')
#         ruleSet_ST = TemporalGeneralization(k, iri, ruleSet_S, minConf, minSupp, maxConf, 1997, timeOut)
#         #print(ruleSet_ST)
#         #print('*ruleSet_ST')
#         ruleSet_S.update(ruleSet_L)
#
#         #print(ruleSet_S)
#         #print('Step4:')
#
#         R_d = EnrichmentData(k, iri, ruleSet_S, minConf, minSupp, maxConf, timeOut)
#         #print(R_d)
#         #print('*R_d')
#         R_dt = TemporalGeneralization(k, iri, R_d, minConf, minSupp, maxConf, 1997, timeOut)
#         #print(R_dt)
#         #print('*R_dt')
#         ruleSet_S.update(R_dt)
#         R_f = EnrichmentObject(k, iri, ruleSet_S, lSet, p, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut)
#         #print(R_f)
#         #print('*R_f')
#
#         ruleSet_S.update(R_f)
#
#         #print(ruleSet_S)
#         ruleSet.update(ruleSet_S)
#
#     # #print(ruleSet)
#
#     for rule in ruleSet:
#         if rule[1] >= minSupp and rule[2] >= minConf:
#             ruleSetFiltred.add(rule)
#
#     return ruleSetFiltred


def ALGO_naive(k, iri, pattern, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL):
    ruleSetFiltred = set()
    ruleSet = set()
    pSet = SelectProduct(k, iri)
    # #print(pSet)
    # #print(len(pSet))
    # i = 0
    for p in pSet:
        # #print('*******************************************')
        # #print(p)
        # #print(i)
        # i += 1
        # #print('Step1:')

        lSet = SelectLocation(k, iri, p)
        sSet = SelectStructure(k, iri, p)
        ruleSet_P = Specialize_Product(k, iri, pattern, p, minSupp)
        # #print(ruleSet_P)
        ruleSet_PT = TemporalGeneralization(k, iri, ruleSet_P, minConf, minSupp, maxConf, 1997)

        ruleSet.update(ruleSet_PT)

    for rule in ruleSet:
        if rule[1] >= minSupp and rule[2] >= minConf:
            ruleSetFiltred.add(rule)

    return ruleSetFiltred


# def ALGO(k, k_onto, pattern, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL):
#     ruleSet = set()
#     pSet = SelectProduct(k)
#     # #print(pSet)
#     for p in pSet:
#         lSet = SelectLocation(k, k_onto, p)
#         sSet = SelectStructure(k, k_onto, p)
#         R_initial = Instantiate(k, k_onto, pattern, p, lSet, sSet, minConf, minSupp, maxConf)
#         # #print(R_initial)
#         if R_initial:
#             # #print('-')
#             # #print(R_initial)
#             # #print(VerifyHearchyProduct(k, k_onto, R_initial, minSupp, minConf, maxConf))
#             # #print(VerifyHearchyLocation(k, k_onto, R_initial, minSupp, minConf, maxConf))
#             # R_initial_Hearchy = VerifyHearchy(k, k_onto, R_initial, minSupp, minConf, maxConf) #################################################
#             pBrotherSet = SelectProductBrother(k, k_onto, lSet, p)
#             # #print(pBrotherSet)
#             lBrotherSet = SelectLocationBrother(k, k_onto, lSet)
#             # #print(lBrotherSet)
#
#             R_f = Combine(k, k_onto, R_initial, pBrotherSet, lBrotherSet, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL)
#             ruleSet.update(R_f)
#
#     #print("END")
#     #print(ruleSet)


# fileName = "data/0/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
# # Load the KB -----------------------------------------
# k_onto = get_ontology("file://" + fileName).load()
# k = rdflib.Graph()
# k.load(fileName)
# descovredRules = ALGO(k, k_onto, patternGeneral, 0.3, 5, 0.8, 3, 3)
# #print(descovredRules)


# lSet = SelectLocation(k, k_onto, p)
# if 'NamedIndividual' in lSet:
#     lSet.remove('NamedIndividual')
# # #print(lSet)
# for l in lSet:
#     sSet = SelectStructure(k, k_onto, l)
#     if 'NamedIndividual' in sSet:
#         sSet.remove('NamedIndividual')
#     # #print(sSet)
#     continu = True
#     for s in sSet:
#         R_initial = Instantiate(k, k_onto, pattern, p, l, s, minConf, minSupp, maxConf, continu)


def getClassFromRule(rule):
    productClasses = []
    locationClasses = []
    structureClasses = []

    productClasses.append(rule[:rule.find('(?P)')])
    i = 1
    product = '(?P' + str(i) + ')'
    while product in rule:
        productClasses.append((rule[rule.find('contain(?L, ?P), ') + len('contain(?L, ?P), '):rule.find(product)]))

    locationClasses.append(rule[rule.find('(?P), ') + len('(?P), '):rule.find('(?L)')])
    i = 1
    location = '(?L' + str(i) + ')'
    while location in rule:
        locationClasses.append(
            (rule[rule.find('has_location(?S, ?L), ') + len('has_location(?S, ?L), '):rule.find(location)]))

    structureClasses.append(rule[rule.find('(?L), ') + len('(?L), '):rule.find('(?S)')])

    return productClasses + locationClasses + structureClasses


# #print(ALGO_full(k, k_onto, patternGeneral, 0.4, 0.02, 0.8, 3, 3))

def main(minConf, minSupp, maxBrotherP, maxBrotherL):
    # minConf = 0.4
    # minSupp = 0.02
    maxConf = 0.8
    # maxBrotherP = 3
    # maxBrotherL = 3
    timeOut = 5000
    # num_cores = multiprocessing.cpu_count()
    num_cores = 1
    # num_cores = 2
    print("core = " + str(num_cores))
    # while minConf >= 0.2:
    #print(minConf)
    i = 0
    # for i in range(0, 43):
    #print('+++++++-----------------------------------------------------------------------------------')
    #print('*' + str(i))
    # fileName = "data/" + str(i) + "/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    # fileName = "mltest/ml"
    # fileName = "save"
    # fileName = "ML_Tests/ml.owl"
    fileName = "ONTOLOGY_SETTLEMENT\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    # fileName = "ML_Tests\\data/ML_test - new.owl"
    # fileName = "ML_Tests\\data/t\\tIn.owl"
    # Load the KB -----------------------------------------
    k_onto = get_ontology("file://" + fileName).load()
    iri = k_onto.base_iri
    # iri = "http://www.semanticweb.org/akatosh/ontologies/2018/11/untitled-ontology-6#"
    # #print(iri)
    k = rdflib.Graph()
    k.load(fileName)
    # k = Graph(store=HDTStore(fileName + ".hdt"))

    # #print('supp=' + str(suppCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)')))
    # #print('conf=' + str(confCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', suppCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)'))))

    #print('-')
    startTime = time.time()
    descovredRules = ALGO_optimized_Paralel(k, iri, patternGeneral, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut, num_cores)
    ft = open("ONTOLOGY_SETTLEMENT/CRAMinerResults/runtime.txt", "w")
    ft.write("--- %s seconds ---" % (time.time() - startTime))
    ft.close()
    #print(time.time() - startTime)
    #print('-')
    #print('RULES:')
    #print(descovredRules)
    #print('-------------------------------------------------')
    f = open("ONTOLOGY_SETTLEMENT/CRAMinerResults/learningRules_0.6_0.001.txt", "w")
    f.write(str(descovredRules))
    f.close()
    # #print('-')
    # Delete old individuals
    # for individual in list(k_onto.individuals()):
    #     destroy_entity(individual)
    #
    # # Load the ontology -----------------------------------------
    # ontoTest = get_ontology("file://ONTOLOGY_SETTLEMENT/ASBESTOS_ONTOLOGY_SETTLEMENT.owl").load()
    #
    # with ontoTest:
    #     ontoClassList = []
    #     for cl in list(ontoTest.classes()):
    #         ontoClassList.append(str(cl)[str(cl).rfind('.') + 1:])
    #     # #print(ontoClassList)
    #
    #     # #print(SelectAllProduct(ontoK, ontoTest))
    #     # descovredRules = {('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('calorifugeage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 8, 1.0), ('conduitsenamianteciment(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 7, 1.0), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 88, 1.0), ('plafond(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('panneauxcollésouvisés(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 5, 1.0), ('bois(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('carrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('revetementdesolcarrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 12, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 72, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 6, 0.07692307692307693), ('faiencesmurales(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 0.8333333333333334), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 112, 1.0), ('linoléum(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('faiencemurale(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 17, 1.0), ('mur(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 10, 1.0), ('revetementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 7, 1.0), ('plaquederesiliencebitumineusesousevier(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('papierspeints(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 16, 1.0), ('plâtrépeint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('dalledesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 11, 1.0), ('revêtementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0)}
    #     j = 0
    #     for descovredRule in descovredRules:
    #         # #print(j)
    #         j += 1
    #         # #print(descovredRule)
    #         classList = getClassFromRule(descovredRule[0])
    #         check = True
    #         for c in classList:
    #             if c not in ontoClassList:
    #                 check = False
    #                 break
    #         # #print(classList)
    #         # #print(descovredRule[0])
    #         # rule = Imp()
    #         # rule.set_as_rule("""ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_predicted_characteristic(?P, ?D) -> has_predicted_class(?D, 0)""")
    #         if check:
    #             # #print('add')
    #             rule = Imp()
    #             # #print('2')
    #             r = descovredRule[0].replace('has_diagnostic_characteristc(?P, ?D)',
    #                                          'has_predicted_characteristic(?P, ?D)').replace(
    #                 '-> has_Diagnisis(?D, HIGH)', '-> has_predicted_class(?D, 1)').replace('-> has_Diagnisis(?D, LOW)',
    #                                                                                        '-> has_predicted_class(?D, 0)').replace(
    #                 ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '')
    #             # #print(r)
    #             rule.set_as_rule(r)
    #             # #print('3')
    #         # #print('4')
    #     # rule = Imp()
    #     # rule.set_as_rule(
    #     #     """has_calculated_characteristic(?PR1, ?C1), has_calculated_characteristic(?PR2, ?C2), has_calculation_year(?C1, ?Y1), has_calculation_year(?C2, ?Y2), greaterThanOrEqual(?Y2, ?Y1), Enduit(?PR1), Enduit(?PR2), has_product_class(?C1, "Low") -> has_product_class(?C2, "Low")""")
    #     # rule = Imp()
    #     # rule.set_as_rule(
    #     #     "Enduit(?PR1) -> Enduit(?PR2)")
    #     # rule = Imp()
    #     # rule.set_as_rule(
    #     #     'Enduit(?PR4) -> Enduit(?PR3)')
    #     # sync_reasoner_pellet()
    #     sync_reasoner_pellet(infer_data_property_values=True)
    #
    # ontoTest.save(file="CRAMinerResults/ASBESTOS_ONTOLOGY_RESULTS_" + str(minConf) + "_" + str(minSupp) + ".owl",
    #               format="rdfxml")
    #
    # # Delete old individuals
    # for individual in list(ontoTest.individuals()):
    #     destroy_entity(individual)
    #
    # # minConf -= 0.1




###----------------------------------- ALGORITHM -----------------------------------###

# main()


def applyRules():
    minConf = 0.4
    minSupp = 0.02
    maxConf = 0.8
    maxBrotherP = 3
    maxBrotherL = 3
    timeOut = 5000
    # num_cores = multiprocessing.cpu_count()
    # num_cores = 2
    # print("core = " + str(num_cores))
    # while minConf >= 0.2:
    #print(minConf)
    # i = 0
    for i in range(0, 80):
        # if i not in {65, 54, 53, 44, 20, 14, 13, 10, 9, 2}:
        if i not in {1000}:
            #print('+++++++-----------------------------------------------------------------------------------')
            #print('*' + str(i))
            fileName = "data/" + str(i) + "/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
            # fileName = "mltest/ml"
            # fileName = "save"
            # fileName = "ML_Tests/ml.owl"
            # fileName = "ML_Tests\\data/ML_test - new.owl"
            # fileName = "ML_Tests\\data/t\\tIn.owl"
            # Load the KB -----------------------------------------
            k_onto = get_ontology("file://" + fileName).load()
            iri = k_onto.base_iri
            # iri = "http://www.semanticweb.org/akatosh/ontologies/2018/11/untitled-ontology-6#"
            # #print(iri)
            k = rdflib.Graph()
            k.load(fileName)
            # k = Graph(store=HDTStore(fileName + ".hdt"))

            # #print('supp=' + str(suppCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)')))
            # #print('conf=' + str(confCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', suppCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)'))))

            #print('-')
            startTime = time.time()
            # descovredRules = ALGO_optimized_Paralel(k, iri, patternGeneral, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut, num_cores)
            # ft = open("data/" + str(i) + "/learningSet/runtime.txt", "w")
            # ft.write("--- %s seconds ---" % (time.time() - startTime))
            # ft.close()
            #print(time.time() - startTime)
            #print('-')
            #print('RULES:')
            #print(descovredRules)
            #print('-------------------------------------------------')
            # f = open("data/" + str(i) + "/learningSet/learningRules" + str(minConf) + "_" + str(minSupp) + ".txt", "r")
            f = open("data/0/learningSet/learningRules0.4_0.001.txt", "r")
            # print(f.read())
            rulesF = f.read()
            # print(rulesF)
            # print(eval(rulesF))
            descovredRules = eval(rulesF)
            # descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}
            # exec("descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}")
            print(descovredRules)

            # f.write(str(descovredRules))
            f.close()
            # #print('-')
            # Delete old individuals
            for individual in list(k_onto.individuals()):
                destroy_entity(individual)

            # Load the ontology -----------------------------------------
            ontoTest = get_ontology("file://data/" + str(i) + "/testingSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl").load()

            with ontoTest:
                ontoClassList = []
                for cl in list(ontoTest.classes()):
                    ontoClassList.append(str(cl)[str(cl).rfind('.') + 1:])
                # #print(ontoClassList)

                # #print(SelectAllProduct(ontoK, ontoTest))
                # descovredRules = {('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('calorifugeage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 8, 1.0), ('conduitsenamianteciment(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 7, 1.0), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 88, 1.0), ('plafond(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('panneauxcollésouvisés(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 5, 1.0), ('bois(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('carrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('revetementdesolcarrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 12, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 72, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 6, 0.07692307692307693), ('faiencesmurales(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 0.8333333333333334), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 112, 1.0), ('linoléum(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('faiencemurale(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 17, 1.0), ('mur(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 10, 1.0), ('revetementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 7, 1.0), ('plaquederesiliencebitumineusesousevier(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('papierspeints(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 16, 1.0), ('plâtrépeint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('dalledesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 11, 1.0), ('revêtementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0)}
                j = 0
                for descovredRule in descovredRules:
                    # #print(j)
                    j += 1
                    # #print(descovredRule)
                    classList = getClassFromRule(descovredRule[0])
                    check = True
                    for c in classList:
                        if c not in ontoClassList:
                            check = False
                            break
                    # #print(classList)
                    # #print(descovredRule[0])
                    # rule = Imp()
                    # rule.set_as_rule("""ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_predicted_characteristic(?P, ?D) -> has_predicted_class(?D, 0)""")
                    if check:
                        # #print('add')
                        rule = Imp()
                        # #print('2')
                        r = descovredRule[0].replace('has_diagnostic_characteristc(?P, ?D)',
                                                     'has_predicted_characteristic(?P, ?D)').replace(
                            '-> has_Diagnisis(?D, HIGH)', '-> has_predicted_class(?D, 1)').replace('-> has_Diagnisis(?D, LOW)',
                                                                                                   '-> has_predicted_class(?D, 0)').replace(
                            ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '')
                        # #print(r)
                        rule.set_as_rule(r)
                        # #print('3')
                    # #print('4')
                # rule = Imp()
                # rule.set_as_rule(
                #     """has_calculated_characteristic(?PR1, ?C1), has_calculated_characteristic(?PR2, ?C2), has_calculation_year(?C1, ?Y1), has_calculation_year(?C2, ?Y2), greaterThanOrEqual(?Y2, ?Y1), Enduit(?PR1), Enduit(?PR2), has_product_class(?C1, "Low") -> has_product_class(?C2, "Low")""")
                # rule = Imp()
                # rule.set_as_rule(
                #     "Enduit(?PR1) -> Enduit(?PR2)")
                # rule = Imp()
                # rule.set_as_rule(
                #     'Enduit(?PR4) -> Enduit(?PR3)')
                # sync_reasoner_pellet()
                sync_reasoner_pellet(infer_data_property_values=True)

            ontoTest.save(file="data/" + str(i) + "/testingSet/ASBESTOS_ONTOLOGY_TEST" + str(minConf) + "_" + str(minSupp) + ".owl",
                          format="rdfxml")

            # Delete old individuals
            for individual in list(ontoTest.individuals()):
                destroy_entity(individual)


# applyRules()


def applyRules9010():
    minConf = 0.4
    minSupp = 0.02
    maxConf = 0.8
    maxBrotherP = 3
    maxBrotherL = 3
    timeOut = 5000
    # num_cores = multiprocessing.cpu_count()
    # num_cores = 2
    # print("core = " + str(num_cores))
    # while minConf >= 0.2:
    #print(minConf)
    # i = 0
    # for i in range(0, 80):
    #     # if i not in {65, 54, 53, 44, 20, 14, 13, 10, 9, 2}:
    #     if i not in {1000}:
    #print('+++++++-----------------------------------------------------------------------------------')
    #print('*' + str(i))
    # fileName = "test3000_results/test3000/data/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    # # fileName = "mltest/ml"
    # # fileName = "save"
    # # fileName = "ML_Tests/ml.owl"
    # # fileName = "ML_Tests\\data/ML_test - new.owl"
    # # fileName = "ML_Tests\\data/t\\tIn.owl"
    # # Load the KB -----------------------------------------
    # k_onto = get_ontology("file://" + fileName).load()
    # iri = k_onto.base_iri
    # # iri = "http://www.semanticweb.org/akatosh/ontologies/2018/11/untitled-ontology-6#"
    # # #print(iri)
    # k = rdflib.Graph()
    # k.load(fileName)
    # k = Graph(store=HDTStore(fileName + ".hdt"))

    # #print('supp=' + str(suppCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)')))
    # #print('conf=' + str(confCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', suppCalculate(k, iri, 'revetement(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)'))))

    #print('-')
    # startTime = time.time()
    # descovredRules = ALGO_optimized_Paralel(k, iri, patternGeneral, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL, timeOut, num_cores)
    # ft = open("data/" + str(i) + "/learningSet/runtime.txt", "w")
    # ft.write("--- %s seconds ---" % (time.time() - startTime))
    # ft.close()
    #print(time.time() - startTime)
    #print('-')
    #print('RULES:')
    #print(descovredRules)
    #print('-------------------------------------------------')
    # f = open("data/" + str(i) + "/learningSet/learningRules" + str(minConf) + "_" + str(minSupp) + ".txt", "r")
    f = open("test3000_results/test3000/data/0/learningSet/learningRules0.4_0.001.txt", "r")
    # print(f.read())
    rulesF = f.read()
    # print(rulesF)
    # print(eval(rulesF))
    descovredRules = eval(rulesF)
    # descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}
    # exec("descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}")
    print(descovredRules)

    # f.write(str(descovredRules))
    f.close()
    # #print('-')
    # Delete old individuals
        # for individual in list(k_onto.individuals()):
        #     destroy_entity(individual)

    # Load the ontology -----------------------------------------
    ontoTest = get_ontology("file://test3000_results/test3000/data/0/testingSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl").load()

    with ontoTest:
        ontoClassList = []
        for cl in list(ontoTest.classes()):
            ontoClassList.append(str(cl)[str(cl).rfind('.') + 1:])
        # #print(ontoClassList)

        # #print(SelectAllProduct(ontoK, ontoTest))
        # descovredRules = {('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('calorifugeage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 8, 1.0), ('conduitsenamianteciment(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 7, 1.0), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 88, 1.0), ('plafond(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('panneauxcollésouvisés(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 5, 1.0), ('bois(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('carrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('revetementdesolcarrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 12, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 72, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 6, 0.07692307692307693), ('faiencesmurales(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 0.8333333333333334), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 112, 1.0), ('linoléum(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('faiencemurale(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 17, 1.0), ('mur(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 10, 1.0), ('revetementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 7, 1.0), ('plaquederesiliencebitumineusesousevier(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('papierspeints(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 16, 1.0), ('plâtrépeint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('dalledesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 11, 1.0), ('revêtementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0)}
        j = 0
        for descovredRule in descovredRules:
            # #print(j)
            j += 1
            # #print(descovredRule)
            classList = getClassFromRule(descovredRule[0])
            check = True
            for c in classList:
                if c not in ontoClassList:
                    check = False
                    break
            # #print(classList)
            # #print(descovredRule[0])
            # rule = Imp()
            # rule.set_as_rule("""ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_predicted_characteristic(?P, ?D) -> has_predicted_class(?D, 0)""")
            if check:
                # #print('add')
                rule = Imp()
                # #print('2')
                r = descovredRule[0].replace('has_diagnostic_characteristc(?P, ?D)',
                                             'has_predicted_characteristic(?P, ?D)').replace(
                    '-> has_Diagnisis(?D, HIGH)', '-> has_predicted_class(?D, 1)').replace('-> has_Diagnisis(?D, LOW)',
                                                                                           '-> has_predicted_class(?D, 0)').replace(
                    ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '')
                # #print(r)
                rule.set_as_rule(r)
                # #print('3')
            # #print('4')
        # rule = Imp()
        # rule.set_as_rule(
        #     """has_calculated_characteristic(?PR1, ?C1), has_calculated_characteristic(?PR2, ?C2), has_calculation_year(?C1, ?Y1), has_calculation_year(?C2, ?Y2), greaterThanOrEqual(?Y2, ?Y1), Enduit(?PR1), Enduit(?PR2), has_product_class(?C1, "Low") -> has_product_class(?C2, "Low")""")
        # rule = Imp()
        # rule.set_as_rule(
        #     "Enduit(?PR1) -> Enduit(?PR2)")
        # rule = Imp()
        # rule.set_as_rule(
        #     'Enduit(?PR4) -> Enduit(?PR3)')
        # sync_reasoner_pellet()
        sync_reasoner_pellet(infer_data_property_values=True)

    ontoTest.save(file="test3000_results/test3000/data/0/testingSet/ASBESTOS_ONTOLOGY_TEST0.4_0.001.owl", format="rdfxml")

    # Delete old individuals
    for individual in list(ontoTest.individuals()):
        destroy_entity(individual)


# applyRules9010()


def applyRulesHybride():
    f = open("HybrideRules.txt", "r")
    # print(f.read())
    ruleHigh = f.readline().replace("\n", "")
    ruleLow = f.readline().replace("\n", "")
    f.close()
    # Load the ontology -----------------------------------------
    ontoTest = get_ontology("file://HybridApproachResults/third1/LeaveOneThirdOutTestsThird1/data/0/testingSet/ASBESTOS_ONTOLOGY_SETTLEMENT_RESULT.owl").load()
    k = rdflib.Graph()
    k.load("HybridApproachResults/third1/LeaveOneThirdOutTestsThird1/data/0/testingSet/ASBESTOS_ONTOLOGY_SETTLEMENT_RESULT.owl")
    iri = ontoTest.base_iri

    with ontoTest:
        hybrideRules = []
        rule = Imp()

        q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
        qres = k.query(q)

        productList = []
        for row in qres:
            productName = f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')]
            productList.append(productName)
            rHigh = ruleHigh.replace("T(?", productName + "(?")
            rLow = ruleLow.replace("T(?", productName + "(?")
            hybrideRules.append(rHigh)
            hybrideRules.append(rLow)
            print(rHigh)
            print(rLow)

            rule.set_as_rule(rHigh)
            rule.set_as_rule(rLow)

        sync_reasoner_pellet(infer_data_property_values=True)

    ontoTest.save(file="HybridApproachResults/third1/LeaveOneThirdOutTestsThird1/data/0/testingSet/ASBESTOS_ONTOLOGY_SETTLEMENT_propagation.owl", format="rdfxml")

    # Delete old individuals
    for individual in list(ontoTest.individuals()):
        destroy_entity(individual)


# applyRulesHybride()


def applyRules9010minConfSeuilTest():
    minConf = 0.6
    minSupp = 0.001
    maxConf = 0.8
    maxBrotherP = 3
    maxBrotherL = 3
    timeOut = 5000

    f = open("ONTOLOGY_SETTLEMENT/CRAMinerResults/learningRules_0.6_0.001.txt", "r")

    # print(f.read())
    rulesF = f.read()

    # print(eval(rulesF))
    descovredRules = eval(rulesF)
    # descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}
    # exec("descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}")
    print(descovredRules)

    # f.write(str(descovredRules))
    f.close()
    # #print('-')
    # Delete old individuals
        # for individual in list(k_onto.individuals()):
        #     destroy_entity(individual)

    # Load the ontology -----------------------------------------
    ontoTest = get_ontology("file://ONTOLOGY_SETTLEMENT/ASBESTOS_ONTOLOGY_SETTLEMENT.owl").load()

    with ontoTest:
        ontoClassList = []
        for cl in list(ontoTest.classes()):
            ontoClassList.append(str(cl)[str(cl).rfind('.') + 1:])
        # #print(ontoClassList)

        # #print(SelectAllProduct(ontoK, ontoTest))
        # descovredRules = {('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('calorifugeage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 8, 1.0), ('conduitsenamianteciment(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 7, 1.0), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 88, 1.0), ('plafond(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('panneauxcollésouvisés(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 5, 1.0), ('bois(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('carrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('revetementdesolcarrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 12, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 72, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 6, 0.07692307692307693), ('faiencesmurales(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 0.8333333333333334), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 112, 1.0), ('linoléum(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('faiencemurale(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 17, 1.0), ('mur(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 10, 1.0), ('revetementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 7, 1.0), ('plaquederesiliencebitumineusesousevier(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('papierspeints(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 16, 1.0), ('plâtrépeint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('dalledesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 11, 1.0), ('revêtementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0)}
        j = 0
        for descovredRule in descovredRules:
            # #print(j)
            j += 1
            # #print(descovredRule)
            classList = getClassFromRule(descovredRule[0])
            check = True
            for c in classList:
                if c not in ontoClassList:
                    check = False
                    break
            # #print(classList)
            # print(descovredRule[0])
            # print(descovredRule[1])
            # print(descovredRule[2])
            # print(check)
            # rule = Imp()
            # rule.set_as_rule("""ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_predicted_characteristic(?P, ?D) -> has_predicted_class(?D, 0)""")
            if check and descovredRule[2] >= minConf and descovredRule[1] >= minSupp and 'ThanOrEqual' not in descovredRule[0]:
                # #print('add')
                rule = Imp()
                # #print('2')
                # r = descovredRule[0].replace('has_diagnostic_characteristc(?',
                #                              'has_predicted_characteristic(?').replace(
                #     '-> has_Diagnisis(?D, HIGH)', '-> has_predicted_class(?D, 1)').replace('-> has_Diagnisis(?D, LOW)',
                #                                                                            '-> has_predicted_class(?D, 0)').replace(
                #     ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '')

                print(descovredRule[0])
                year = re.findall(r'\d\d\d\d', descovredRule[0])
                print(year)
                r = descovredRule[0].replace('has_diagnostic_characteristc(?',
                                             'has_predicted_characteristic(?').replace('-> has_Diagnisis',
                                                                                       '-> has_predicted_class').replace(
                    ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '').replace('HIGH', '1').replace('LOW', '0')
                print(r)
                if len(year) > 0:
                    # r = r.replace(year[0], '"' + year[0] + '-01-01T00:00:00"^^xsd:dateTime')
                    r = r.replace(year[0], '"' + year[0] + '-01-01T00:00:00"')
                    print(r)
                # r = '"""' + r + '"""'
                # print(r)

                # print('------:')
                # print(r)
                # print('------:')
                rule.set_as_rule(r)
                # #print('3')
            # #print('4')
        # rule = Imp()
        # rule.set_as_rule(
        #     """has_calculated_characteristic(?PR1, ?C1), has_calculated_characteristic(?PR2, ?C2), has_calculation_year(?C1, ?Y1), has_calculation_year(?C2, ?Y2), greaterThanOrEqual(?Y2, ?Y1), Enduit(?PR1), Enduit(?PR2), has_product_class(?C1, "Low") -> has_product_class(?C2, "Low")""")
        # rule = Imp()
        # rule.set_as_rule(
        #     "Enduit(?PR1) -> Enduit(?PR2)")
        # rule = Imp()
        # rule.set_as_rule(
        #     'Enduit(?PR4) -> Enduit(?PR3)')
        # sync_reasoner_pellet()

        # sync_reasoner_pellet(infer_data_property_values=True)#!!!!!!!!!!!!!!!!!!!!!!!!! wthout year

    ontoTest.save(file="ONTOLOGY_SETTLEMENT/CRAMinerResults/ASBESTOS_ONTOLOGY_TEST_0.6_0.001.owl", format="rdfxml")

    # Delete old individuals
    for individual in list(ontoTest.individuals()):
        destroy_entity(individual)


# applyRules9010minConfSeuilTest()


def applyRules9010minConfSeuilTestRunRaisoneur():
    # read input file
    fin = open("ONTOLOGY_SETTLEMENT/CRAMinerResults/ASBESTOS_ONTOLOGY_TEST_0.6_0.001.owl", "rt")
    # read file contents to string
    data = fin.read()
    # replace all occurrences of the required string
    data = data.replace('<rdf:first rdf:datatype="http://www.w3.org/2001/XMLSchema#string">19', '<rdf:first rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">19')
    # close the input file
    fin.close()
    # open the input file in write mode
    fin = open("ONTOLOGY_SETTLEMENT/CRAMinerResults/ASBESTOS_ONTOLOGY_TEST_0.6_0.001.owl", "wt")
    # overrite the input file with the resulting data
    fin.write(data)
    # close the file
    fin.close()

    # Load the ontology -----------------------------------------
    ontoTest = get_ontology("file://ONTOLOGY_SETTLEMENT/CRAMinerResults/ASBESTOS_ONTOLOGY_TEST_0.6_0.001.owl").load()

    with ontoTest:
        sync_reasoner_pellet(infer_data_property_values=True)
    ontoTest.save(file="ONTOLOGY_SETTLEMENT/CRAMinerResults/ASBESTOS_ONTOLOGY_RESULTS.owl", format="rdfxml")

    # Delete old individuals
    for individual in list(ontoTest.individuals()):
        destroy_entity(individual)


# applyRules9010minConfSeuilTestRunRaisoneur()



def amieRulesTransformation(infileName, outfileName):
    result = '{(\''
    inputFile = open(infileName, "r")
    line = inputFile.readline()
    while line:
        if '*' not in line and 'http://www.w3.org/2000/01/rdf-schema#domain' not in line and 'http://www.w3.org/2000/01/rdf-schema#range' not in line and '<has_type>' not in line and '<has_owner>' not in line and '<has_address>' not in line and 'has_department_number' not in line and 'has_region' not in line and ('<0>)' in line or '<1>)' in line) and 'has_predicted_characteristic' not in line and line.count('has_diagnostic_characteristic') == 1 and 'subClassOf' not in line:
            line = line.replace(') <', '), <').replace('0,', '0.').replace('	', ', ').replace('<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>(', 'type(').replace('<0>)', 'LOW)\'').replace('<1>)', 'HIGH)\'').replace('<', '').replace('>(', '(').replace('>)', ')').replace('http://www.w3.org/2000/01/rdf-schema#subClassOf(', 'subClassOf(').replace('has_diagnostic(', 'has_Diagnisis(').replace('has_diagnostic_characteristic(', 'has_diagnostic_characteristc(')
            while 'type(' in line:
                pos1 = line.find(' type(')
                pos2 = line.find(')', pos1)
                # print(pos1)
                # print(pos2)
                productType = line[pos1 + len(' type(') + 3:pos2]
                # print(productType)
                line = line.replace(line[pos1 + len(' type(') + 2:pos2], '', 1)
                line = line.replace(' type', ' ' + productType, 1)

            result = result + line
        line = inputFile.readline()

    inputFile.close()
    # result = result.replace(' =>', '->').replace(', ?a\n', '\n').replace(', ?a', '').replace('\n', '), (\'') + ')}'
    result = result.replace(' =>', '->').replace(', ?a\n', '\n').replace(', ?a', '').replace('\n', '),\n(\'') + ')}'
    outputFile = open(outfileName, "w")
    # outputFile.write(result.replace(', (\')}', '}'))
    outputFile.write(result.replace(',\n(\')}', '}'))
    outputFile.close()


# amieRulesTransformation('amieTests/AMIEThirds/Third3/6.txt', 'amieTests/AMIEThirds/Third3/6OUT.txt')


def getClassFromRuleAMIE(rule):
    # print(rule)
    classes = []
    pos1 = 0
    pos2 = rule.find('(?', pos1)
    # print(pos2)
    while pos2 != -1:
        # print(rule[pos1:pos2])
        classes.append(rule[pos1:pos2])
        pos1 = rule.find('), ', pos2)
        if pos1 != -1:
            pos1 = pos1 + len('), ')
        pos2 = rule.find('(?', pos1)
        # print(pos1)
        # print(pos2)

    return classes


# print(getClassFromRuleAMIE('has_diagnostic_characteristc(?c,?a), bandescalicot(?c) -> has_Diagnisis(?a,HIGH)'))


def applyRules9010minConfSeuilTestAmie():
    minConf = 0.6
    minSupp = 0.001
    maxConf = 0.8
    maxBrotherP = 3
    maxBrotherL = 3
    timeOut = 5000

    f = open("amieTests/AMIEThirds/Third3/6OUT.txt", "r")
    # f = open("amieTests/6notype.txt", "r")


    rulesF = f.read()
    # while 'type(' in rulesF:
    #     pos1 = rulesF.find(' type(')
    #     pos2 = rulesF.find(')', pos1)
    #     # print(pos1)
    #     # print(pos2)
    #     productType = rulesF[pos1 + len(' type(') + 3:pos2]
    #     # print(productType)
    #     rulesF = rulesF.replace(rulesF[pos1 + len(' type(') + 2:pos2], '', 1)
    #     rulesF = rulesF.replace(' type', ' ' + productType, 1)


    # print(eval(rulesF))
    descovredRules = eval(rulesF)
    # descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}
    # exec("descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}")
    print(descovredRules)

    # f.write(str(descovredRules))
    f.close()
    # #print('-')
    # Delete old individuals
        # for individual in list(k_onto.individuals()):
        #     destroy_entity(individual)

    # Load the ontology -----------------------------------------
    ontoTest = get_ontology("file://third3/LeaveOneThirdOutTestsThird3/data/0/testingSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl").load()

    with ontoTest:
        ontoClassList = []
        for cl in list(ontoTest.classes()):
            ontoClassList.append(str(cl)[str(cl).rfind('.') + 1:])
        for ob in list(ontoTest.object_properties()):
            ontoClassList.append(str(ob)[str(ob).rfind('.') + 1:])
        for dt in list(ontoTest.data_properties()):
            ontoClassList.append(str(dt)[str(dt).rfind('.') + 1:])
        print(ontoClassList)

        # #print(SelectAllProduct(ontoK, ontoTest))
        # descovredRules = {('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('calorifugeage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 8, 1.0), ('conduitsenamianteciment(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 7, 1.0), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 88, 1.0), ('plafond(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('panneauxcollésouvisés(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 5, 1.0), ('bois(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('carrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('revetementdesolcarrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 12, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 72, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 6, 0.07692307692307693), ('faiencesmurales(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 0.8333333333333334), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 112, 1.0), ('linoléum(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('faiencemurale(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 17, 1.0), ('mur(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 10, 1.0), ('revetementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 7, 1.0), ('plaquederesiliencebitumineusesousevier(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('papierspeints(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 16, 1.0), ('plâtrépeint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('dalledesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 11, 1.0), ('revêtementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0)}
        j = 0
        for descovredRule in descovredRules:
            # #print(j)
            j += 1
            # #print(descovredRule)

            classList = getClassFromRuleAMIE(descovredRule[0].replace('has_diagnostic_characteristc(?', 'has_predicted_characteristic(?').replace('-> has_Diagnisis', '-> has_predicted_class').replace(', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '').replace('HIGH', '1').replace('LOW', '0').replace('has_year(?o,', 'has_year(?o,"').replace('-01-01T00:00:00)', '-01-01T00:00:00")'))
            check = True
            for c in classList:
                print(c)
                if c not in ontoClassList:
                    print('.............................')
                    check = False
                    break
            # #print(classList)
            print(descovredRule[0])
            print(descovredRule[1])
            print(descovredRule[2])
            print(check)
            # rule = Imp()
            # rule.set_as_rule("""ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_predicted_characteristic(?P, ?D) -> has_predicted_class(?D, 0)""")
            # check=True#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if check and descovredRule[2] >= minConf and descovredRule[1] >= minSupp and '), ?' not in descovredRule[0]:
                # #print('add')
                rule = Imp()
                # #print('2')
                # r = descovredRule[0].replace('has_diagnostic_characteristc(?',
                #                              'has_predicted_characteristic(?').replace(
                #     '-> has_Diagnisis(?D, HIGH)', '-> has_predicted_class(?D, 1)').replace('-> has_Diagnisis(?D, LOW)',
                #                                                                            '-> has_predicted_class(?D, 0)').replace(
                #     ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '')
                r = descovredRule[0].replace('has_diagnostic_characteristc(?',
                                             'has_predicted_characteristic(?').replace(
                    '-> has_Diagnisis', '-> has_predicted_class').replace(
                    ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '').replace('HIGH', '1').replace('LOW', '0').replace('has_year(?o,', 'has_year(?o,"').replace('-01-01T00:00:00)', '-01-01T00:00:00")')
                print('------:')
                print(r)
                print('------:')
                rule.set_as_rule(r)
                # break
                # #print('3')
            # #print('4')
        # rule = Imp()
        # rule.set_as_rule(
        #     """has_calculated_characteristic(?PR1, ?C1), has_calculated_characteristic(?PR2, ?C2), has_calculation_year(?C1, ?Y1), has_calculation_year(?C2, ?Y2), greaterThanOrEqual(?Y2, ?Y1), Enduit(?PR1), Enduit(?PR2), has_product_class(?C1, "Low") -> has_product_class(?C2, "Low")""")
        # rule = Imp()
        # rule.set_as_rule(
        #     "Enduit(?PR1) -> Enduit(?PR2)")
        # rule = Imp()
        # rule.set_as_rule(
        #     'Enduit(?PR4) -> Enduit(?PR3)')
        # sync_reasoner_pellet()

        # sync_reasoner_pellet(infer_data_property_values=True)

    ontoTest.save(file="amieTests/AMIEThirds/Third3/ASBESTOS_ONTOLOGY_TEST6.owl", format="rdfxml")

    # Delete old individuals
    for individual in list(ontoTest.individuals()):
        destroy_entity(individual)


# applyRules9010minConfSeuilTestAmie()


def applyRules9010minConfSeuilTestRunRaisoneurAMIE():
    # read input file
    fin = open("amieTests/AMIEThirds/Third3/ASBESTOS_ONTOLOGY_TEST6.owl", "rt")
    # read file contents to string
    data = fin.read()
    # replace all occurrences of the required string
    data = data.replace('<swrl:argument2 rdf:datatype="http://www.w3.org/2001/XMLSchema#string">19', '<swrl:argument2 rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">19')
    # close the input file
    fin.close()
    # open the input file in write mode
    fin = open("amieTests/AMIEThirds/Third3/ASBESTOS_ONTOLOGY_TEST6.owl", "wt")
    # overrite the input file with the resulting data
    fin.write(data)
    # close the file
    fin.close()

    # Load the ontology -----------------------------------------
    ontoTest = get_ontology("file://amieTests/AMIEThirds/Third3/ASBESTOS_ONTOLOGY_TEST6.owl").load()

    with ontoTest:
        sync_reasoner_pellet(infer_data_property_values=True)
    ontoTest.save(file="amieTests/AMIEThirds/Third3/ASBESTOS_ONTOLOGY_TEST6RUN.owl", format="rdfxml")

    # Delete old individuals
    for individual in list(ontoTest.individuals()):
        destroy_entity(individual)


# applyRules9010minConfSeuilTestRunRaisoneurAMIE()


def countPositiveNegativeIndividual(kt, iri):
    positiveNegativeP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    positiveNegativePqres = kt.query(positiveNegativeP, initBindings={'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(0)})

    positiveNegativePro = len(positiveNegativePqres)

    positiveP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    positivePqres = kt.query(positiveP, initBindings={'d': rdflib.term.Literal(1)})

    positivePro = len(positivePqres)

    negativeP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    negativePqres = kt.query(negativeP, initBindings={'d': rdflib.term.Literal(0)})

    negativePro = len(negativePqres)

    tpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . }'
    tpqres = kt.query(tpq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1)})

    # tpnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    # tpnqres = kt.query(tpnq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(0)})

    tp = len(tpqres)
    # tp = len(tpqres) - len(tpnqres)

    tnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . }'
    tnqres = kt.query(tnq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(0)})

    tnpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    tnpqres = kt.query(tnpq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(0), 'pc2': rdflib.term.Literal(1)})

    tn = len(tnqres) - len(tnpqres)

    fpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . }'
    fpqres = kt.query(fpq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(1)})

    # fpnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    # fpnqres = kt.query(fpnq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(0)})

    fp = len(fpqres)
    # fp = len(fpqres) - len(fpnqres)

    fnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . }'
    fnqres = kt.query(fnq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(0)})

    fnpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    fnpqres = kt.query(fnpq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(0), 'pc2': rdflib.term.Literal(1)})

    fn = len(fnqres) - len(fnpqres)

    return [tp, tn, fp, fn, positivePro, negativePro, positiveNegativePro, tpqres, tnqres, fpqres, fnqres, positivePqres, negativePqres, positiveNegativePqres]


def testDataSet():
    fileName = "LeaveOneThirdOutTestsThird1/data/0/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    # #print(fileName)
    k_onto_test = get_ontology("file://" + fileName).load()
    # print(len(list(k_onto_test.classes())))
    print(len(list(k_onto_test.get_triples())))
    # print(len(list(k_onto_test.individuals())))
    # print(len(list(k_onto_test.object_properties())))
    # print(len(list(k_onto_test.data_properties())))
    # print(len(list(k_onto_test.properties())))
    print('-')
    kt = rdflib.Graph()
    kt.load(fileName)
    iri = k_onto_test.base_iri
    # #print('-')

    subProduct = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
    subProductqres = kt.query(subProduct)
    subProductnb = len(subProductqres)
    print('subProduct: ' + str(subProductnb))

    subLocation = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?p . ?Location rdf:type ?x . ?x rdfs:subClassOf* :Location . }'
    subLocationqres = kt.query(subLocation)
    subLocationnb = len(subLocationqres)
    print('subLocation: ' + str(subLocationnb))

    subStructure = 'SELECT DISTINCT ?x WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product rdf:type ?p . ?Structure rdf:type ?x . ?x rdfs:subClassOf* :Structure . }'
    subStructureqres = kt.query(subStructure)
    subStructurenb = len(subStructureqres)
    print('subStructure: ' + str(subStructurenb))

    positiveP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    positivePqres = kt.query(positiveP, initBindings={'d': rdflib.term.Literal(1)})

    positivePro = len(positivePqres)

    negativeP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    negativePqres = kt.query(negativeP, initBindings={'d': rdflib.term.Literal(0)})

    negativePro = len(negativePqres)

    print('positive: ' + str(positivePro))
    print('negative: ' + str(negativePro))

    lq = 'SELECT DISTINCT ?Location WHERE { ?Location :contain ?Product . ?Location rdf:type ?x . ?x rdfs:subClassOf* :Location . }'
    lqres = kt.query(lq)

    print('locations: ' + str(len(lqres)))

    sq = 'SELECT DISTINCT ?Structure WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Structure rdf:type ?x . ?x rdfs:subClassOf* :Structure . }'
    sqres = kt.query(sq)

    print('structures: ' + str(len(sqres)))

    bq = 'SELECT DISTINCT ?Building WHERE { ?Building :has_structure ?Structure . ?Structure rdf:type ?x . ?x rdfs:subClassOf* :Structure . }'
    bqres = kt.query(bq)

    print('buildings: ' + str(len(bqres)))

    # sq = 'SELECT DISTINCT ?Structure WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Structure rdf:type ?x . ?x rdfs:subClassOf* :Structure . ?b1 :has_structure ?Structure . ?b2 :has_structure ?Structure . ?b1 rdfs:sameAs ?b2 . }'
    # sqres = kt.query(sq)
    #
    # print('erreur: ' + str(len(sqres)))


# testDataSet()


def testResult():
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    positivePro = 0
    negativePro = 0
    positiveNegativePro = 0
    for i in range(80):
        if i not in {65, 54, 53, 44, 20, 14, 13, 10, 9, 2}:
        # if i != 1000:
            print('+++++++-----------------------------------------------------------------------------------')
            print(i)
            fileName = "data/" + str(i) + "/testingSet/ASBESTOS_ONTOLOGY_TEST0.4_0.02.owl"
            # #print(fileName)
            k_onto_test = get_ontology("file://" + fileName).load()
            iri = k_onto_test.base_iri
            # #print('-')
            kt = rdflib.Graph()
            kt.load(fileName)
            # #print('-')
            result = countPositiveNegativeIndividual(kt, iri)
            tp += result[0]
            tn += result[1]
            fp += result[2]
            fn += result[3]
            positivePro += result[4]
            negativePro += result[5]
            positiveNegativePro += result[6]

            # Delete old individuals
            for individual in list(k_onto_test.individuals()):
                destroy_entity(individual)

    up = positivePro - (tp + fn)
    un = negativePro - (tn + fp)

    print("positveNegative =", positiveNegativePro)
    print("positve =", positivePro)
    print("negative =", negativePro)
    print("tp =", tp)
    print("tn =", tn)
    print("fp =", fp)
    print("fn =", fn)
    print("up =", up)
    print("un =", un)

    if tp + fp == 0:
        precisionP = 0
    else:
        precisionP = tp / (tp + fp)
    if tp + fn + up == 0:
        rappelP = 0
    else:
        rappelP = tp / (tp + fn + up)
    if rappelP == 0 or precisionP == 0:
        FmesureP = 0
    else:
        FmesureP = 2 * (precisionP * rappelP) / (precisionP + rappelP)

    if tn + fn == 0:
        precisionN = 0
    else:
        precisionN = tn / (tn + fn)
    if tn + fp + un == 0:
        rappelN = 0
    else:
        rappelN = tn / (tn + fp + un)
    if rappelN == 0 or precisionN == 0:
        FmesureN = 0
    else:
        FmesureN = 2 * (precisionN * rappelN) / (precisionN + rappelN)

    accuracy = (tp + tn) / (tp + fp + up + tn + fn + un)

    print('precisionP =', precisionP)
    print('rappelP =', rappelP)
    print('FmesureP =', FmesureP)
    print('precisionN =', precisionN)
    print('rappelN =', rappelN)
    print('FmesureN =', FmesureN)
    print('accuracy =', accuracy)


# testResult()


def testResult9010():
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    positivePro = 0
    negativePro = 0
    positiveNegativePro = 0

    print('+++++++-----------------------------------------------------------------------------------')
    # print(i)
    fileName = "TILDE_Result/ASBESTOS_ONTOLOGY_TEST2RUN.owl"
    # #print(fileName)
    k_onto_test = get_ontology("file://" + fileName).load()
    iri = k_onto_test.base_iri
    # #print('-')
    kt = rdflib.Graph()
    kt.load(fileName)
    # #print('-')
    result = countPositiveNegativeIndividual(kt, iri)
    tp += result[0]
    tn += result[1]
    fp += result[2]
    fn += result[3]
    positivePro += result[4]
    negativePro += result[5]
    positiveNegativePro += result[6]
    print('PosNeglist product list:')
    PosNeglist = set()
    for row in result[13]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        PosNeglist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(PosNeglist))
    print('TP product list:')
    TPlist = set()
    for row in result[7]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        TPlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(TPlist))
    # print(result[7])
    print('TN product list:')
    TNlist = set()
    for row in result[8]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        TNlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(TNlist))
    # print(result[8])
    print('FP product list:')
    FPlist = set()
    for row in result[9]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        FPlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(FPlist))
    # print(result[9])
    print('FN product list:')
    FNlist = set()
    for row in result[10]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        FNlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(FNlist))
    # print(result[10])
    print('Positive product list:')
    Positivelist = set()
    for row in result[11]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        Positivelist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(Positivelist))
    # print(result[11])
    print('Negalive product list:')
    Negativelist = set()
    for row in result[12]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        Negativelist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(Negativelist))
    # print(result[12])
    print('UP product list:')
    UPlist = Positivelist.difference(TPlist.union(FNlist))
    print(len(TPlist.union(FNlist)))
    print(UPlist)
    print(len(UPlist))
    for row in UPlist:
        print(row)
    # print(list(set(result[11]).difference(set(result[7] + result[10]))))
    print('UN product list:')
    UNlist = Negativelist.difference(TNlist.union(FPlist))
    print(len(TNlist.union(FPlist)))
    print(UNlist)
    print(len(UNlist))
    for row in UNlist:
        print(row)
    # print(list(set(result[12]).difference(set(result[8] + result[9]))))

    # Delete old individuals
    for individual in list(k_onto_test.individuals()):
        destroy_entity(individual)

    # up = positivePro - (tp + fn)
    # un = negativePro - (tn + fp)
    up = len(UPlist)
    un = len(UNlist)


    print("positveNegative =", positiveNegativePro)
    print("positve =", positivePro)
    print("negative =", negativePro)
    print("tp =", tp)
    print("tn =", tn)
    print("fp =", fp)
    print("fn =", fn)
    print("up =", up)
    print("un =", un)

    if tp + fp == 0:
        precisionP = 0
    else:
        precisionP = tp / (tp + fp)
    if tp + fn + up == 0:
        rappelP = 0
    else:
        rappelP = tp / (tp + fn + up)
    if rappelP == 0 or precisionP == 0:
        FmesureP = 0
    else:
        FmesureP = 2 * (precisionP * rappelP) / (precisionP + rappelP)

    if tn + fn == 0:
        precisionN = 0
    else:
        precisionN = tn / (tn + fn)
    if tn + fp + un == 0:
        rappelN = 0
    else:
        rappelN = tn / (tn + fp + un)
    if rappelN == 0 or precisionN == 0:
        FmesureN = 0
    else:
        FmesureN = 2 * (precisionN * rappelN) / (precisionN + rappelN)

    # accuracy = (tp + tn) / (tp + fp + up + tn + fn + un)
    accuracy = (tp + tn) / (tp + fp + tn + fn)

    print('precisionP =', precisionP)
    print('rappelP =', rappelP)
    print('FmesureP =', FmesureP)
    print('precisionN =', precisionN)
    print('rappelN =', rappelN)
    print('FmesureN =', FmesureN)
    print('accuracy =', accuracy)


# testResult9010()


def countPositiveNegativeIndividualHybrid(kt, iri):
    positiveNegativeP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_calculated_characteristic ?Prediction . ?Prediction :has_class ?pc . ?Prediction :has_class ?pc2 . }'
    positiveNegativePqres = kt.query(positiveNegativeP, initBindings={'pc': rdflib.term.Literal(2), 'pc2': rdflib.term.Literal(1)})

    positiveNegativePro = len(positiveNegativePqres)

    positiveP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    positivePqres = kt.query(positiveP, initBindings={'d': rdflib.term.Literal(1)})

    positivePro = len(positivePqres)

    negativeP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    negativePqres = kt.query(negativeP, initBindings={'d': rdflib.term.Literal(0)})

    negativePro = len(negativePqres)

    tpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_class ?pc . }'
    tpqres = kt.query(tpq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(2)})

    # tpnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    # tpnqres = kt.query(tpnq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(0)})

    tp = len(tpqres)
    # tp = len(tpqres) - len(tpnqres)

    tnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_class ?pc . }'
    tnqres = kt.query(tnq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(1)})

    tnpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_class ?pc . ?Prediction :has_class ?pc2 . }'
    tnpqres = kt.query(tnpq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(2)})

    tn = len(tnqres) - len(tnpqres)

    fpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_class ?pc . }'
    fpqres = kt.query(fpq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(2)})

    # fpnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    # fpnqres = kt.query(fpnq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(0)})

    fp = len(fpqres)
    # fp = len(fpqres) - len(fpnqres)

    fnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_class ?pc . }'
    fnqres = kt.query(fnq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1)})

    fnpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_class ?pc . ?Prediction :has_class ?pc2 . }'
    fnpqres = kt.query(fnpq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(2)})

    fn = len(fnqres) - len(fnpqres)

    return [tp, tn, fp, fn, positivePro, negativePro, positiveNegativePro, tpqres, tnqres, fpqres, fnqres, positivePqres, negativePqres, positiveNegativePqres]



def testResultHybrid():
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    positivePro = 0
    negativePro = 0
    positiveNegativePro = 0

    print('+++++++-----------------------------------------------------------------------------------')
    # print(i)
    fileName = "HybridApproachResults/third3/LeaveOneThirdOutTestsThird3/data/0/testingSet/ASBESTOS_ONTOLOGY_SETTLEMENT_RESULT.owl"
    # #print(fileName)
    k_onto_test = get_ontology("file://" + fileName).load()
    iri = k_onto_test.base_iri
    # #print('-')
    kt = rdflib.Graph()
    kt.load(fileName)
    # #print('-')
    result = countPositiveNegativeIndividualHybrid(kt, iri)
    tp += result[0]
    tn += result[1]
    fp += result[2]
    fn += result[3]
    positivePro += result[4]
    negativePro += result[5]
    positiveNegativePro += result[6]
    print('PosNeglist product list:')
    PosNeglist = set()
    for row in result[13]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        PosNeglist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(PosNeglist))
    print('TP product list:')
    TPlist = set()
    for row in result[7]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        TPlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(TPlist))
    # print(result[7])
    print('TN product list:')
    TNlist = set()
    for row in result[8]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        TNlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(TNlist))
    # print(result[8])
    print('FP product list:')
    FPlist = set()
    for row in result[9]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        FPlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(FPlist))
    # print(result[9])
    print('FN product list:')
    FNlist = set()
    for row in result[10]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        FNlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(FNlist))
    # print(result[10])
    print('Positive product list:')
    Positivelist = set()
    for row in result[11]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        Positivelist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(Positivelist))
    # print(result[11])
    print('Negalive product list:')
    Negativelist = set()
    for row in result[12]:
        print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        Negativelist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(Negativelist))
    # print(result[12])
    print('UP product list:')
    UPlist = Positivelist.difference(TPlist.union(FNlist))
    print(len(TPlist.union(FNlist)))
    print(UPlist)
    print(len(UPlist))
    for row in UPlist:
        print(row)
    # print(list(set(result[11]).difference(set(result[7] + result[10]))))
    print('UN product list:')
    UNlist = Negativelist.difference(TNlist.union(FPlist))
    print(len(TNlist.union(FPlist)))
    print(UNlist)
    print(len(UNlist))
    for row in UNlist:
        print(row)
    # print(list(set(result[12]).difference(set(result[8] + result[9]))))

    # Delete old individuals
    for individual in list(k_onto_test.individuals()):
        destroy_entity(individual)

    # up = positivePro - (tp + fn)
    # un = negativePro - (tn + fp)
    up = len(UPlist)
    un = len(UNlist)


    print("positveNegative =", positiveNegativePro)
    print("positve =", positivePro)
    print("negative =", negativePro)
    print("tp =", tp)
    print("tn =", tn)
    print("fp =", fp)
    print("fn =", fn)
    print("up =", up)
    print("un =", un)

    if tp + fp == 0:
        precisionP = 0
    else:
        precisionP = tp / (tp + fp)
    if tp + fn + up == 0:
        rappelP = 0
    else:
        rappelP = tp / (tp + fn + up)
    if rappelP == 0 or precisionP == 0:
        FmesureP = 0
    else:
        FmesureP = 2 * (precisionP * rappelP) / (precisionP + rappelP)

    if tn + fn == 0:
        precisionN = 0
    else:
        precisionN = tn / (tn + fn)
    if tn + fp + un == 0:
        rappelN = 0
    else:
        rappelN = tn / (tn + fp + un)
    if rappelN == 0 or precisionN == 0:
        FmesureN = 0
    else:
        FmesureN = 2 * (precisionN * rappelN) / (precisionN + rappelN)

    # accuracy = (tp + tn) / (tp + fp + up + tn + fn + un)
    accuracy = (tp + tn) / (tp + fp + tn + fn)

    print('precisionP =', precisionP)
    print('rappelP =', rappelP)
    print('FmesureP =', FmesureP)
    print('precisionN =', precisionN)
    print('rappelN =', rappelN)
    print('FmesureN =', FmesureN)
    print('accuracy =', accuracy)


# testResultHybrid()


def test9010():
    fileName = "data10000/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    onto = get_ontology("file://" + fileName).load()
    k = rdflib.Graph()
    k.load(fileName)

    fileNameLearning = "data10000/ASBESTOS_ONTOLOGY_LEARNING_SET.owl"
    fileNameTesting = "data10000/ASBESTOS_ONTOLOGY_TESTING_SET.owl"

    q = 'SELECT ?Product WHERE { ?Location :contain ?Product . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
    qres = k.query(q)

    productList = set()
    for row in qres:
        productList.add("ASBESTOS_ONTOLOGY_SETTLEMENT." + f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    print(len(productList))
    print(productList)

    testingNumber =  int(len(productList) * 10 / 100)
    learningNumber = len(productList) - testingNumber

    testing_list = random.sample(productList, testingNumber)
    learning_list = productList.difference(testing_list)

    # for individual in list(onto.individuals()):
    #     if str(individual) in testing_list:
    #         destroy_entity(individual)
    #
    # onto.save(file=fileNameLearning, format="rdfxml")


    # for individual in list(onto.individuals()):
    #     if str(individual) in learning_list:
    #         destroy_entity(individual)
    #
    # onto.save(file=fileNameTesting, format="rdfxml")


# test9010()


def testLeaveOneThirdOut():
    fileName = "data3000/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    onto = get_ontology("file://" + fileName).load()
    k = rdflib.Graph()
    k.load(fileName)

    fileNameLearning = "data3000/LeaveOneThirdOut/ASBESTOS_ONTOLOGY_LEARNING_SET.owl"
    fileNameTesting = "data3000/LeaveOneThirdOut/ASBESTOS_ONTOLOGY_TESTING_SET.owl"


    q = 'SELECT ?Product WHERE { ?Location :contain ?Product . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
    qres = k.query(q)

    productList = set()
    for row in qres:
        productList.add("ASBESTOS_ONTOLOGY_SETTLEMENT." + f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])

    print(len(productList))
    print(productList)


    # Third 1 ******************************************************************************************************

    # # Testing Set *************************************************************************
    # testingNumber =  int(len(productList) * 1 / 3)
    # # learningNumber = len(productList) - testingNumber
    # testing_list = random.sample(productList, testingNumber)
    # # print(len(testing_list))
    # learning_list = productList.difference(testing_list)
    # f = open("data3000/LeaveOneThirdOut/testing_list.txt", "w")
    # f.write(str(testing_list))
    # f.close()
    # for individual in list(onto.individuals()):
    #     if str(individual) in learning_list:
    #         destroy_entity(individual)
    # onto.save(file=fileNameTesting, format="rdfxml")

    # # Learning Set *************************************************************************
    # f = open("data3000/LeaveOneThirdOut/testing_list.txt", "r")
    # individualText = f.read()
    # testing_individual_list = eval(individualText)
    # # print(testing_individual_list)
    # f.close()
    # for individual in list(onto.individuals()):
    #     if str(individual) in testing_individual_list:
    #         destroy_entity(individual)
    # onto.save(file=fileNameLearning, format="rdfxml")


    # Third 2 ******************************************************************************************************

    # # Testing Set *************************************************************************
    # testingNumber =  int(len(productList) * 1 / 3)
    #
    # f1 = open("data3000/LeaveOneThirdOut/Third1/testing_list.txt", "r")
    # individualText = f1.read()
    # testing_individual_list_Third1 = eval(individualText)
    # # print(testing_individual_list)
    # f1.close()
    #
    # testing_list = random.sample(productList.difference(testing_individual_list_Third1), testingNumber)
    # print(len(testing_list))
    # learning_list = productList.difference(testing_list)
    # f = open("data3000/LeaveOneThirdOut/testing_list.txt", "w")
    # f.write(str(testing_list))
    # f.close()
    # for individual in list(onto.individuals()):
    #     if str(individual) in learning_list:
    #         destroy_entity(individual)
    # onto.save(file=fileNameTesting, format="rdfxml")

    # # Learning Set *************************************************************************
    # f = open("data3000/LeaveOneThirdOut/testing_list.txt", "r")
    # individualText = f.read()
    # testing_individual_list = eval(individualText)
    # # print(testing_individual_list)
    # f.close()
    # for individual in list(onto.individuals()):
    #     if str(individual) in testing_individual_list:
    #         destroy_entity(individual)
    # onto.save(file=fileNameLearning, format="rdfxml")

    # Third 3 ******************************************************************************************************

    # # Testing Set *************************************************************************
    # f1 = open("data3000/LeaveOneThirdOut/Third1/testing_list.txt", "r")
    # individualText1 = f1.read()
    # testing_individual_list_Third1 = eval(individualText1)
    # # print(testing_individual_list)
    # f1.close()
    #
    # f2 = open("data3000/LeaveOneThirdOut/Third2/testing_list.txt", "r")
    # individualText2 = f2.read()
    # testing_individual_list_Third2 = eval(individualText2)
    # # print(testing_individual_list)
    # f2.close()
    #
    # testing_list = productList.difference(testing_individual_list_Third1).difference(testing_individual_list_Third2)
    # print(len(testing_list))
    # learning_list = productList.difference(testing_list)
    # f = open("data3000/LeaveOneThirdOut/testing_list.txt", "w")
    # f.write(str(testing_list))
    # f.close()
    # for individual in list(onto.individuals()):
    #     if str(individual) in learning_list:
    #         destroy_entity(individual)
    # onto.save(file=fileNameTesting, format="rdfxml")

    # # Learning Set *************************************************************************
    # f = open("data3000/LeaveOneThirdOut/testing_list.txt", "r")
    # individualText = f.read()
    # testing_individual_list = eval(individualText)
    # # print(testing_individual_list)
    # f.close()
    # for individual in list(onto.individuals()):
    #     if str(individual) in testing_individual_list:
    #         destroy_entity(individual)
    # onto.save(file=fileNameLearning, format="rdfxml")


# testLeaveOneThirdOut()


def nt2pso(inputFileName, outputFileName):
    fileOut = open(outputFileName, 'w')

    file1 = open(inputFileName, 'r')
    Lines = file1.readlines()

    # Strips the newline character
    for line in Lines:
        line = line.replace('http://www.w3.org/1999/02/22-rdf-syntax-ns#', '').replace('http://www.semanticweb.org/akatosh/ontologies/2018/11/untitled-ontology-6#', '').replace('http://www.w3.org/2001/XMLSchema#string', '').replace('http://www.w3.org/2001/XMLSchema#integer', '').replace('http://www.w3.org/2001/XMLSchema#dateTime', '').replace('http://www.w3.org/2001/XMLSchema#', '').replace('http://www.w3.org/2000/01/rdf-schema#', '').replace('http://www.w3.org/2002/07/owl#', '').replace('-01-01T00:00:00"^^<', '').replace('"^^<', '').replace('*', '_').replace('-', '_').replace('"', '<').replace(':', '_').lower()
        if 'http://www.semanticweb.org/akatosh/ontologies/2018/11/untitled_ontology_6' not in line and 'namedindividual' not in line and '\\u' not in line:
            words = line.strip().split()
            # print(words)
            # print(line.strip())
            if len(words) > 0:
                arg1 = words[0][words[0].find('<') + len('<'):words[0].find('>')]
                predicate = words[1][words[1].find('<') + len('<'):words[1].find('>')]
                arg2 = words[2][words[2].find('<') + len('<'):words[2].find('>')]
                sep = ''
                # if predicate in ['type', 'has_registration_number', 'has_diagnostic', 'has_year',
                #                  'has_type', 'has_owner', 'has_address', 'has_asbestos_type', 'has_building_class', 'has_building_probability',
                #                  'has_building_diagnostic', 'has_calculation_year', 'has_category', 'has_class', 'has_department_number',
                #                  'has_end_date', 'has_extracted_probability', 'has_location_diagnostic', 'has_structure_diagnostic',
                #                  'has_location_class', 'has_location_probability', 'has_newName', 'has_precision', 'has_predicted_class',
                #                  'has_probability', 'has_provider', 'has_reference', 'has_region', 'has_source', 'has_start_date',
                #                  'has_structure_class', 'has_structure_probability']:
                #     sep = '"'
                l = predicate + '(' + arg1 + ', ' + sep + arg2 + sep + ') .' + '\n'
                fileOut.writelines(l)

    fileOut.close()
    file1.close()


# nt2pso('TILDE_Result\\testing\\ASBESTOS_ONTOLOGY_SETTLEMENT2.nt', 'TILDE_Result\\testing\\pso2.txt')
# nt2pso('TILDE_Result\\learning\\ASBESTOS_ONTOLOGY_SETTLEMENT1.nt', 'TILDE_Result\\learning\\pso1.txt')


def creatTILDfiles(inputFileName, bgFileName, kbFileName):
    bgFile = open(bgFileName, 'w')
    kbFile = open(kbFileName, 'w')

    file = open(inputFileName, 'r')
    Lines = file.readlines()
    data = ''.join(Lines)
    # print(data)

    i=0
    j=0
    k=0
    s=set()
    s2 = set()


    for lin in Lines:
        if not any(ext in lin.lower() for ext in ['extract_from', 'has_registration_number', 'has_category', 'sourcedocument', 'has_address', 'has_region']) and ', )' not in lin:
            line = lin.replace(') .', ').').lower()
            if 'has_diagnostic(' in line:
                productIns = line[len('has_diagnostic(diagnosticfeature_1_'):line.find(',')].replace('_', '_x_')
                # print(productIns)
                if 'has_diagnostic_characteristic(' + productIns + ',' in data and productIns not in s:
                    s.add(productIns)
                    i+=1
                    kbFile.writelines(line)
                else:
                    j+=1
            else:
                if 'has_diagnostic_characteristic(' in line:
                    s2.add(line[len('has_diagnostic_characteristic('):line.find(',')])
                    k+=1
                bgFile.writelines(line)
    # bgFile.write('gty(X,Y) :- has_year(_,X),\n\
    #         has_year(_,Y),\n\
    #      X>Y.')
    file.close()
    kbFile.close()
    bgFile.close()
    print(i)
    print(j)
    print(k)
    # print(s)
    print(len(s))
    print(len(s2))
    print(len(s.difference(s2)))
    print(s.difference(s2))


# creatTILDfiles('TILDE_Result\\testing\\pso3.txt', 'TILDE_Result\\testing\\asbestos3.bg', 'TILDE_Result\\testing\\asbestos3.kb')
# creatTILDfiles('TILDE_Result\\learning\\pso3.txt', 'TILDE_Result\\learning\\asbestos3.bg', 'TILDE_Result\\learning\\asbestos3.kb')


def tilde2swrl(inputFileName, outputFileName):
    inputFile = open(inputFileName, 'r')
    outputFile = open(outputFileName, "w")
    outputFile.write('{')
    line = inputFile.readline()
    while line:
        line = re.sub(r'([A-Z])', r'?\1', line)

        head = line[:line.find(' :-')]
        body = line[line.find(' :- ') + len(' :- '):line.find(', !.')]
        while 'type(' in body:
            pos1 = body.find('type(')
            pos2 = body.find(')', pos1)
            # print(pos1)
            # print(pos2)
            productType = body[pos1 + len('type(') + 3:pos2]
            # print(productType)
            body = body.replace(body[pos1 + len('type(') + 2:pos2], '', 1)
            body = body.replace('type', productType, 1)
        hc = '1.0'
        line = inputFile.readline()
        conf = line[line.find('=')+len('='):line.find('\n')]

        result = '(\'' + body.replace('gty', 'greaterThanOrEqual') + '->' + head.replace('[0]', '0').replace('[1]', '1') + '\', ' + hc + ', ' + conf + '),\n'

        outputFile.write(result.replace('.),\n', '.0)}'))

        line = inputFile.readline()

    inputFile.close()
    outputFile.close()

# tilde2swrl('TILDE_Result\\asbestos2.out', 'TILDE_Result\\asbestos2.txt')


def applyRules9010minConfSeuilTestTILDE():
    minConf = 0.6
    minSupp = 0.001


    f = open("TILDE_Result\\asbestos2.txt", "r")

    # print(f.read())
    rulesF = f.read()

    # print(eval(rulesF))
    descovredRules = eval(rulesF)
    # descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}
    # exec("descovredRules = {('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12131147540983607, 0.6568047337278107), ('dallesdesol(?P), revetementsdesols(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.7314285714285714), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.29562841530054645, 0.9575221238938053), ('na(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.10765027322404372, 0.9949494949494949), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.13224043715846995, 0.9758064516129032), ('bitume(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 0.032679738562091505, 0.9375), ('collesetjointsdecarrelageragreagesprimairesdaccrochage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.06393442622950819, 0.8602941176470589), ('collesnonbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02622950819672131, 0.8), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , greaterThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, LOW)', 0.023497267759562842, 0.9148936170212766), ('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) , lessThanOrEqual(?Y, 1997) -> has_Diagnisis(?D, HIGH)', 0.2788671023965142, 0.6956521739130435), ('collesbitumineuses(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.026775956284153007, 0.8032786885245902), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), Location(?L2), has_location(?S, ?L2), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.12896174863387977, 0.6704545454545454), ('flocages(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 0.02896174863387978, 0.7464788732394366)}")
    print(descovredRules)

    # f.write(str(descovredRules))
    f.close()
    # #print('-')
    # Delete old individuals
        # for individual in list(k_onto.individuals()):
        #     destroy_entity(individual)

    # Load the ontology -----------------------------------------
    ontoTest = get_ontology("file://TILDE_Result/ASBESTOS_ONTOLOGY_SETTLEMENT2.owl").load()

    with ontoTest:
        ontoClassList = []
        for cl in list(ontoTest.classes()):
            ontoClassList.append(str(cl)[str(cl).rfind('.') + 1:])
        # #print(ontoClassList)

        # #print(SelectAllProduct(ontoK, ontoTest))
        # descovredRules = {('dallesdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('calorifugeage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('joint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 8, 1.0), ('conduitsenamianteciment(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 7, 1.0), ('peinture(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 88, 1.0), ('plafond(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('panneauxcollésouvisés(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 5, 1.0), ('bois(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('carrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 9, 1.0), ('revetementdesolcarrelage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 12, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 72, 0.9230769230769231), ('colle(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, HIGH)', 6, 0.07692307692307693), ('faiencesmurales(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 0.8333333333333334), ('enduit(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 112, 1.0), ('linoléum(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 6, 1.0), ('faiencemurale(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 17, 1.0), ('mur(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 10, 1.0), ('revetementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 7, 1.0), ('plaquederesiliencebitumineusesousevier(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0), ('papierspeints(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 16, 1.0), ('plâtrépeint(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 23, 1.0), ('dalledesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 11, 1.0), ('revêtementdesol(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_diagnostic_characteristc(?P, ?D) -> has_Diagnisis(?D, LOW)', 5, 1.0)}
        j = 0
        for descovredRule in descovredRules:
            # #print(j)
            j += 1
            # #print(descovredRule)
            classList = getClassFromRule(descovredRule[0])
            check = True
            for c in classList:
                if c not in ontoClassList:
                    check = False
                    break
            # #print(classList)
            # print(descovredRule[0])
            # print(descovredRule[1])
            # print(descovredRule[2])
            # print(check)
            # rule = Imp()
            # rule.set_as_rule("""ragreage(?P), Location(?L), Structure(?S), has_location(?S, ?L), contain(?L, ?P), has_structure(?B, ?S), has_year(?B, ?Y), has_type(?B, ?T), has_region(?B, ?R), has_predicted_characteristic(?P, ?D) -> has_predicted_class(?D, 0)""")
            if True and descovredRule[2] >= minConf and descovredRule[1] >= minSupp:# and 'ThanOrEqual' not in descovredRule[0]:
                # #print('add')
                rule = Imp()
                # #print('2')
                # r = descovredRule[0].replace('[0]', '0').replace('[1]', '1')#.replace(
                    # 'HIGH', '1').replace(
                    # 'LOW', '0')#.replace(
                    # ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '')

                print(descovredRule[0])
                year = re.findall(r'\d\d\d\d', descovredRule[0])
                print(year)
                r = descovredRule[0].replace('->has_diagnostic', '->has_predicted_class').replace('has_diagnostic_characteristic(?','has_predicted_characteristic(?')
                                             # 'has_predicted_characteristic(?').replace('-> has_Diagnisis',
                                             #                                           '-> has_predicted_class').replace(
                    # ', has_type(?B, ?T)', '').replace(', has_region(?B, ?R)', '').replace('HIGH', '1').replace('LOW', '0')
                print(r)
                for y in year:
                    # r = r.replace(year[0], '"' + year[0] + '-01-01T00:00:00"^^xsd:dateTime')
                    r = r.replace(y, '"' + y + '-01-01T00:00:00"')
                    print(r)
                # r = '"""' + r + '"""'
                # print(r)

                # print('------:')
                # print(r)
                # print('------:')
                rule.set_as_rule(r)
                # #print('3')
            # #print('4')
        # rule = Imp()
        # rule.set_as_rule(
        #     """has_calculated_characteristic(?PR1, ?C1), has_calculated_characteristic(?PR2, ?C2), has_calculation_year(?C1, ?Y1), has_calculation_year(?C2, ?Y2), greaterThanOrEqual(?Y2, ?Y1), Enduit(?PR1), Enduit(?PR2), has_product_class(?C1, "Low") -> has_product_class(?C2, "Low")""")
        # rule = Imp()
        # rule.set_as_rule(
        #     "Enduit(?PR1) -> Enduit(?PR2)")
        # rule = Imp()
        # rule.set_as_rule(
        #     'Enduit(?PR4) -> Enduit(?PR3)')
        # sync_reasoner_pellet()

        # sync_reasoner_pellet(infer_data_property_values=True)#!!!!!!!!!!!!!!!!!!!!!!!!! wthout year

    ontoTest.save(file="TILDE_Result/ASBESTOS_ONTOLOGY_TEST2.owl", format="rdfxml")

    # Delete old individuals
    for individual in list(ontoTest.individuals()):
        destroy_entity(individual)


# applyRules9010minConfSeuilTestTILDE()


def applyRules9010minConfSeuilTestRunRaisoneurTILDE():
    # read input file
    fin = open("TILDE_Result/ASBESTOS_ONTOLOGY_TEST2.owl", "rt")
    # read file contents to string
    data = fin.read()
    # replace all occurrences of the required string
    data = data.replace('rdf:datatype="http://www.w3.org/2001/XMLSchema#string">19', 'rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">19')
    # close the input file
    fin.close()
    # open the input file in write mode
    fin = open("TILDE_Result/ASBESTOS_ONTOLOGY_TEST2.owl", "wt")
    # overrite the input file with the resulting data
    fin.write(data)
    # close the file
    fin.close()

    # Load the ontology -----------------------------------------
    ontoTest = get_ontology("file://TILDE_Result/ASBESTOS_ONTOLOGY_TEST2.owl").load()

    with ontoTest:
        sync_reasoner_pellet(infer_data_property_values=True)
    ontoTest.save(file="TILDE_Result/ASBESTOS_ONTOLOGY_TEST2RUN.owl", format="rdfxml")

    # Delete old individuals
    for individual in list(ontoTest.individuals()):
        destroy_entity(individual)


# applyRules9010minConfSeuilTestRunRaisoneurTILDE()


def countIndividualCRAvsHybride(kt, iri):
    # cra pos hyb neg
    pnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    pnqres = kt.query(pnq, initBindings={'pc': rdflib.term.Literal(1), 'cc': rdflib.term.Literal(1)})
    pn = len(pnqres)
    print("cra pos hyb neg: ", pn)

    # cra neg hyb pos
    npq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    npqres = kt.query(npq, initBindings={'pc': rdflib.term.Literal(0), 'cc': rdflib.term.Literal(2)})
    npqDouble = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . ?Calculated :has_class ?cc . }'
    npqresDouble = kt.query(npqDouble, initBindings={'pc': rdflib.term.Literal(0), 'pc2': rdflib.term.Literal(1), 'cc': rdflib.term.Literal(2)})
    np = len(npqres) - len(npqresDouble)
    print("cra neg hyb pos: ", np)

    # cra pos hyb pos
    ppq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    ppqres = kt.query(ppq, initBindings={'pc': rdflib.term.Literal(1), 'cc': rdflib.term.Literal(2)})
    pp = len(ppqres)
    print("cra pos hyb pos: ", pp)

    # cra neg hyb neg
    nnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    nnqres = kt.query(nnq, initBindings={'pc': rdflib.term.Literal(0), 'cc': rdflib.term.Literal(1)})
    nnqDouble = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . ?Calculated :has_class ?cc . }'
    nnqresDouble = kt.query(nnqDouble, initBindings={'pc': rdflib.term.Literal(0), 'pc2': rdflib.term.Literal(1), 'cc': rdflib.term.Literal(1)})
    nn = len(nnqres) - len(nnqresDouble)
    print("cra neg hyb neg: ", nn)


    # diag pos cra pos hyb pos
    pppq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    pppqres = kt.query(pppq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1),
                                           'cc': rdflib.term.Literal(2)})
    ppp = len(pppqres)
    print("diag pos cra pos hyb pos: ", ppp)

    # diag pos cra pos hyb neg
    ppnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    ppnqres = kt.query(ppnq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1),
                                           'cc': rdflib.term.Literal(1)})
    ppn = len(ppnqres)
    print("diag pos cra pos hyb neg: ", ppn)

    # diag pos cra neg hyb pos
    pnpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    pnpqres = kt.query(pnpq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(0),
                                           'cc': rdflib.term.Literal(2)})
    pnpqDouble = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . ?Calculated :has_class ?cc . }'
    pnpqresDouble = kt.query(pnpqDouble, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(0), 'pc2': rdflib.term.Literal(1),
                                           'cc': rdflib.term.Literal(2)})
    pnp = len(pnpqres) - len(pnpqresDouble)
    print("diag pos cra neg hyb pos: ", pnp)

    # diag neg cra neg hyb neg
    nnnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    nnnqres = kt.query(nnnq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(0),
                                           'cc': rdflib.term.Literal(1)})
    nnnqDouble = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . ?Calculated :has_class ?cc . }'
    nnnqresDouble = kt.query(nnnqDouble, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(0), 'pc2': rdflib.term.Literal(1),
                                           'cc': rdflib.term.Literal(1)})
    nnn = len(nnnqres) - len(nnnqresDouble)
    print("diag neg cra neg hyb neg: ", nnn)

    # diag neg cra neg hyb pos
    nnpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    nnpqres = kt.query(nnpq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(0),
                                           'cc': rdflib.term.Literal(2)})
    nnpqDouble = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . ?Calculated :has_class ?cc . }'
    nnpqresDouble = kt.query(nnpqDouble, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(0), 'pc2': rdflib.term.Literal(1),
                                           'cc': rdflib.term.Literal(2)})
    nnp = len(nnpqres) - len(nnpqresDouble)
    print("diag neg cra neg hyb pos: ", nnp)

    # diag neg cra pos hyb neg
    npnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    npnqres = kt.query(npnq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(1),
                                           'cc': rdflib.term.Literal(1)})
    npn = len(npnqres)
    print("diag neg cra pos hyb neg: ", npn)



    # # cra pos hyb neg
    # pnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    # pnqres = kt.query(pnq, initBindings={'pc': rdflib.term.Literal(1), 'cc': rdflib.term.Literal(1)})
    # pn = len(pnqres)
    #
    # # cra neg hyb pos
    # npq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    # npqres = kt.query(npq, initBindings={'pc': rdflib.term.Literal(0), 'cc': rdflib.term.Literal(2)})
    # np = len(npqres)
    #
    # # cra pos hyb pos
    # ppq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    # ppqres = kt.query(ppq, initBindings={'pc': rdflib.term.Literal(1), 'cc': rdflib.term.Literal(2)})
    # pp = len(ppqres)
    #
    # # cra neg hyb neg
    # nnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . ?Calculated :has_class ?cc . }'
    # nnqres = kt.query(nnq, initBindings={'pc': rdflib.term.Literal(0), 'cc': rdflib.term.Literal(1)})
    # nn = len(nnqres)



    return [ppp, ppn, pnp, nnn, nnp, npn]#pn, np, pp, nn, #, pu, up, nu, un




    # # cra pos hyb unknown
    # puq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Calculated :has_class ?cc .  NOT EXISTS { ?Prediction :has_predicted_class ?pc . } }'
    # puqres = kt.query(puq, initBindings={'pc': rdflib.term.Literal(1)})
    # pu = len(puqres)
    #
    # # cra unknown hyb pos
    # upq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . NOT EXISTS { ?Calculated :has_class ?cc .  } }'
    # upqres = kt.query(upq, initBindings={'cc': rdflib.term.Literal(2)})
    # up = len(upqres)
    #
    # # cra neg hyb unknown
    # nuq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Calculated :has_class ?cc .  NOT EXISTS { ?Prediction :has_predicted_class ?pc . } }'
    # nuqres = kt.query(nuq, initBindings={'pc': rdflib.term.Literal(0)})
    # nu = len(nuqres)
    #
    # # cra unknown hyb neg
    # unq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_predicted_characteristic ?Prediction . ?Product :has_calculated_characteristic ?Calculated . ?Prediction :has_predicted_class ?pc . NOT EXISTS { ?Calculated :has_class ?cc .  } }'
    # unqres = kt.query(unq, initBindings={'cc': rdflib.term.Literal(1)})
    # un = len(unqres)
    # return [pu, up, nu, un]


def testIndividualCRAvsHybride():
    print('+++++++-----------------------------------------------------------------------------------')
    # print(i)
    fileName = "thirdsCRA_Hybrid/1/ASBESTOS_ONTOLOGY_SETTLEMENT_RESULT.owl"
    # #print(fileName)
    k_onto_test = get_ontology("file://" + fileName).load()
    iri = k_onto_test.base_iri
    # #print('-')
    kt = rdflib.Graph()
    kt.load(fileName)
    # #print('-')
    result = countIndividualCRAvsHybride(kt, iri)
    print('+++++++-----------------------------------------------------------------------------------')
    ppp = result[0]
    ppn = result[1]
    pnp = result[2]
    nnn = result[3]
    nnp = result[4]
    npn = result[5]


    print('ppp', ppp)
    print('ppn', ppn)
    print('pnp', pnp)
    print('nnn', nnn)
    print('nnp', nnp)
    print('npn', npn)

    # result = countPositiveNegativeIndividualHybrid(kt, iri)
    #
    # pu = result[0]
    # up = result[1]
    # nu = result[2]
    # un = result[3]
    #
    # print('pu', pu)
    # print('up', up)
    # print('nu', nu)
    # print('un', un)


# testIndividualCRAvsHybride()


def test23iccs():
    fileName = "third2\\LeaveOneThirdOutTestsThird2\\data\\0\\learningSet\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    # Load the KB -----------------------------------------
    k_onto = get_ontology("file://" + fileName).load()
    iri = k_onto.base_iri
    k = rdflib.Graph()
    k.load(fileName)

    q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
    qres = k.query(q)

    productList = set()
    for row in qres:
        productList.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
    print(len(productList))

    for p in productList:
        print(p)
        q = 'SELECT DISTINCT ?Product WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product rdf:type ?p . ?Building :has_structure ?Structure . ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
        qres = k.query(q, initBindings={
            'p': rdflib.term.URIRef(iri + p),
            'd': rdflib.term.Literal(0)})

        # for row in qres:
        #     print(row)
        print('neg:', len(qres))

        q = 'SELECT DISTINCT ?Product WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product rdf:type ?p . ?Building :has_structure ?Structure . ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
        qres = k.query(q, initBindings={
            'p': rdflib.term.URIRef(iri + p),
            'd': rdflib.term.Literal(1)})

        # for row in qres:
        #     print(row)
        print('pos:', len(qres))

# test23iccs()

# print('END OF ALGORITHME')




# ###----------------------------------- ALGORITHM -----------------------------------###
# # Load the KB -----------------------------------------
# k_onto = get_ontology("file://ML_Tests\\DATA\\ML_test.owl").load()
# # print(K_onto.base_iri)
# k = rdflib.Graph()
# k.load("ML_Tests\\DATA\\ML_test.owl")
#
# pattern = "Product(P), Location(L), Structure(S), has_location(S, L), contain(L, P), has_structure(B, S), has_year(B, Y), has_type(B, T), has_region(B, R), has_diagnostic_characteristc(P, D) -> has_Diagnisis(D, class)"
#
#
# def SelectProduct(k):
#     q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
#     qres = k.query(q)
#
#     productList = []
#     for row in qres:
#         productList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
#
#     return productList
#
#
# def SelectLocation(k, k_onto, p):
#     q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Product rdf:type ?p . ?Location rdf:type ?x . ?x rdfs:subClassOf* :Location . }'
#     qres = k.query(q, initBindings={'p': rdflib.term.URIRef(k_onto.base_iri + p)})
#
#     locationList = []
#     for row in qres:
#         locationList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
#
#     return locationList
#
#
# def SelectStructure(k, k_onto, p):
#     q = 'SELECT DISTINCT ?x WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product rdf:type ?p . ?Structure rdf:type ?x . ?x rdfs:subClassOf* :Structure . }'
#     qres = k.query(q, initBindings={'p': rdflib.term.URIRef(k_onto.base_iri + p)})
#
#     structureList = []
#     for row in qres:
#         structureList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
#
#     return structureList
#
#
# def suppCalculate(k, k_onto, pattern):
#     supp = 0
#     p = pattern[:pattern.find('(')]
#     # print(p)
#     l = pattern[pattern.find("P), ") + len("P), "):pattern.find('(L')]
#     # print(l)
#     s = pattern[pattern.find("L), ") + len("L), "):pattern.find('(S')]
#     # print(s)
#     d = 0
#     if "HIGH" in pattern:
#         d = 1
#
#     if "??Y" not in pattern:
#         existDate = True
#         date = pattern[pattern.find("(?Y, ") + len("(?Y, "):pattern.find(') ->')]
#     else:
#         existDate = False
#
#     pBrother = ""
#     if "(P2)" in pattern:
#         num = pattern.count("contain(L, P")
#         # print(num)
#         for i in range(2, num + 1):
#             pBrother += "?Location :contain ?Product" + str(i) + " . ?Product" + str(i) + " rdf:type :" + pattern[pattern.find("contain(L, P), ") + len("contain(L, P), "):pattern.find('(P' + str(i) + '),')] + " . "
#         # print(pBrother)
#
#     lBrother = ""
#     if "(L2)" in pattern:
#         numl = pattern.count("has_location(S, L")
#         # print(numl)
#         for i in range(2, numl + 1):
#             lBrother += "?Structure :has_location ?Location" + str(i) + " . ?Location" + str(i) + " rdf:type :" + pattern[pattern.find("has_location(S, L), ") + len("has_location(S, L), "):pattern.find('(L' + str(i) + '),')] + " . "
#         # print(lBrother)
#
#     if l != 'Location':
#         if s != 'Structure':
#             if existDate:
#                 q = 'SELECT ?Structure ?Location ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s. ?Location rdf:type ?l . ?Product rdf:type ?p . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year <= ?y) . }'
#                 qres = k.query(q, initBindings={'s': rdflib.term.URIRef(k_onto.base_iri + s),
#                                                 'l': rdflib.term.URIRef(k_onto.base_iri + l),
#                                                 'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                                 'd': rdflib.term.Literal(d),
#                                                 'y': rdflib.term.Literal(date + '-01-01T00:00:00',
#                                                                          datatype=rdflib.term.URIRef(
#                                                                              'http://www.w3.org/2001/XMLSchema#dateTime'))})
#             else:
#                 q = 'SELECT ?Structure ?Location ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s. ?Location rdf:type ?l . ?Product rdf:type ?p . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . }'
#                 qres = k.query(q, initBindings={'s': rdflib.term.URIRef(k_onto.base_iri + s),
#                                                 'l': rdflib.term.URIRef(k_onto.base_iri + l),
#                                                 'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                                 'd': rdflib.term.Literal(d)})
#         else:
#             if existDate:
#                 q = 'SELECT ?Location ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Location rdf:type ?l . ?Product rdf:type ?p . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year <= ?y) . }'
#                 qres = k.query(q, initBindings={'l': rdflib.term.URIRef(k_onto.base_iri + l),
#                                                 'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                                 'd': rdflib.term.Literal(d),
#                                                 'y': rdflib.term.Literal(date + '-01-01T00:00:00',
#                                                                          datatype=rdflib.term.URIRef(
#                                                                              'http://www.w3.org/2001/XMLSchema#dateTime'))})
#             else:
#                 q = 'SELECT ?Location ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Location rdf:type ?l . ?Product rdf:type ?p . ?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . }'
#                 qres = k.query(q, initBindings={'l': rdflib.term.URIRef(k_onto.base_iri + l),
#                                                 'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                                 'd': rdflib.term.Literal(d)})
#     else:
#         if existDate:
#             q = 'SELECT ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ?Product rdf:type ?p . ' + pBrother + '?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year <= ?y) . }'
#             # print('****'+q)
#             qres = k.query(q, initBindings={'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                             'd': rdflib.term.Literal(d),
#                                             'y': rdflib.term.Literal(date + '-01-01T00:00:00',
#                                                                      datatype=rdflib.term.URIRef(
#                                                                          'http://www.w3.org/2001/XMLSchema#dateTime'))})
#
#         else:
#             q = 'SELECT ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ?Product rdf:type ?p . ' + pBrother + '?Product :has_diagnostic_characteristic ?Diagnostic . ?Diagnostic :has_diagnostic ?d . }'
#             qres = k.query(q, initBindings={'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                             'd': rdflib.term.Literal(d)})
#
#
#     for row in qres:
#         # print(row)
#         supp = int(row[len(row) - 1])
#
#     return supp
#
#
# def confCalculate(k, k_onto, pattern, supp):
#     occ = 0
#     p = pattern[:pattern.find('(')]
#     # print(p)
#     l = pattern[pattern.find("P), ") + len("P), "):pattern.find('(L')]
#     # print(l)
#     s = pattern[pattern.find("L), ") + len("L), "):pattern.find('(S')]
#     # print(s)
#
#     if "greaterThan" in pattern:
#         d = False
#     else:
#         d = True
#
#     if "??Y" not in pattern:
#         existDate = True
#         date = pattern[pattern.find("(?Y, ") + len("(?Y, "):pattern.find(') ->')]
#     else:
#         existDate = False
#
#     pBrother = ""
#     if "(P2)" in pattern:
#         num = pattern.count("contain(L, P")
#         # print(num)
#         for i in range(2, num + 1):
#             pBrother += "?Location :contain ?Product" + str(i) + " . ?Product" + str(i) + " rdf:type :" + pattern[pattern.find("contain(L, P), ") + len("contain(L, P), "):pattern.find('(P' + str(i) + '),')] + " . "
#         # print(pBrother)
#
#     lBrother = ""
#     if "(L2)" in pattern:
#         numl = pattern.count("has_location(S, L")
#         # print(numl)
#         for i in range(2, numl + 1):
#             lBrother += "?Structure :has_location ?Location" + str(i) + " . ?Location" + str(
#                 i) + " rdf:type :" + pattern[
#                                      pattern.find("has_location(S, L), ") + len("has_location(S, L), "):pattern.find(
#                                          '(L' + str(i) + '),')] + " . "
#         # print(lBrother)
#
#     if l != 'Location':
#         if s != 'Structure':
#             if existDate:
#                 q = 'SELECT ?Structure ?Location ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s. ?Location rdf:type ?l . ?Product rdf:type ?p . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year <= ?y) . }'
#                 qres = k.query(q, initBindings={'s': rdflib.term.URIRef(k_onto.base_iri + s),
#                                                 'l': rdflib.term.URIRef(k_onto.base_iri + l),
#                                                 'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                                 'y': rdflib.term.Literal(date + '-01-01T00:00:00',
#                                                                          datatype=rdflib.term.URIRef(
#                                                                              'http://www.w3.org/2001/XMLSchema#dateTime'))})
#             else:
#                 q = 'SELECT ?Structure ?Location ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Structure rdf:type ?s. ?Location rdf:type ?l . ?Product rdf:type ?p . }'
#                 qres = k.query(q, initBindings={'s': rdflib.term.URIRef(k_onto.base_iri + s),
#                                                 'l': rdflib.term.URIRef(k_onto.base_iri + l),
#                                                 'p': rdflib.term.URIRef(k_onto.base_iri + p)})
#         else:
#             if existDate:
#                 q = 'SELECT ?Location ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Location rdf:type ?l . ?Product rdf:type ?p . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year <= ?y) . }'
#                 qres = k.query(q, initBindings={'l': rdflib.term.URIRef(k_onto.base_iri + l),
#                                                 'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                                 'y': rdflib.term.Literal(date + '-01-01T00:00:00',
#                                                                          datatype=rdflib.term.URIRef(
#                                                                              'http://www.w3.org/2001/XMLSchema#dateTime'))})
#             else:
#                 q = 'SELECT ?Location ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Location rdf:type ?l . ?Product rdf:type ?p . }'
#                 qres = k.query(q, initBindings={'l': rdflib.term.URIRef(k_onto.base_iri + l),
#                                                 'p': rdflib.term.URIRef(k_onto.base_iri + p)})
#     else:
#         if existDate:
#             q = 'SELECT ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Product rdf:type ?p . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year <= ?y) . }'
#             # print('//' + q)
#             qres = k.query(q, initBindings={'p': rdflib.term.URIRef(k_onto.base_iri + p),
#                                             'y': rdflib.term.Literal(date + '-01-01T00:00:00',
#                                                                      datatype=rdflib.term.URIRef(
#                                                                          'http://www.w3.org/2001/XMLSchema#dateTime'))})
#         else:
#             q = 'SELECT ?Product (count(?Product) as ?count) WHERE { ?Structure :has_location ?Location . ' + lBrother + '?Location :contain ?Product . ' + pBrother + '?Product rdf:type ?p . }'
#             # print(q)
#             qres = k.query(q, initBindings={'p': rdflib.term.URIRef(k_onto.base_iri + p)})
#
#     for row in qres:
#         # print(row)
#         occ = int(row[len(row) - 1])
#         # print(occ)
#
#     if occ > 0:
#         return (supp / occ)
#     else:
#         return 0
#
#
# def InstantiateDate(k, k_onto, pattern, minConf, minSupp, maxConf, startDate, continu):
#     date = startDate
#     # print(date)
#     s = 0
#     c = 0
#     d = startDate
#     pattern_d = pattern.replace("??Y", str(date))
#     # print("-"+pattern_d)
#     supp = suppCalculate(k, k_onto, pattern_d)
#     # print(supp)
#     if supp >= minSupp:
#         conf = confCalculate(k, k_onto, pattern_d, supp)
#         # print(conf)
#         if conf >= maxConf:
#             while conf >= maxConf and supp >= minSupp and date >= 1946:
#                 d = date
#                 s = supp
#                 c = conf
#                 date -= 1
#                 supp = suppCalculate(k ,k_onto, pattern.replace("??Y", str(date)))
#                 conf = confCalculate(k, k_onto, pattern.replace("??Y", str(date)), supp)
#             pattern = pattern.replace("??Y", str(d))
#         else:
#             if conf >= minConf:
#                 maxConf = conf
#                 while conf >= maxConf and supp >= minSupp and date >= 1946:
#                     d = date
#                     s = supp
#                     c = conf
#                     date -= 1
#                     supp = suppCalculate(k, k_onto, pattern.replace("??Y", str(date)))
#                     conf = confCalculate(k, k_onto, pattern.replace("??Y", str(date)), supp)
#                 pattern = pattern.replace("??Y", str(d))
#             else:
#                 continu = False
#     else:
#         continu = False
#
#     return pattern, continu, s, c, d
#
#
#
#
# def Instantiate(k, k_onto, pattern, p, lSet, sSet, minConf, minSupp, maxConf):
#     startDate = 1996
#     patternSet = set()
#     pattern_p = pattern.replace("Product", p)
#     for proba in ['LOW', 'HIGH']:
#         pattern_c = pattern_p.replace('class', proba)
#         if proba == 'LOW':
#             pattern_c = pattern_c.replace('->', ', greaterThanOrEqual(?Y, ??Y) ->')
#         else:
#             pattern_c = pattern_c.replace('->', ', lessThanOrEqual(?Y, ??Y) ->')
#         # print("-"+pattern_c)
#         supp = suppCalculate(k, k_onto, pattern_c)
#         # print(supp)
#         conf = confCalculate(k, k_onto, pattern_c, supp)
#         # print(conf)
#         if supp >= minSupp or conf >= minConf:
#             continu = True
#             InstantiateDateResult = InstantiateDate(k, k_onto, pattern_c, minConf, minSupp, maxConf, startDate, continu)
#             # print("++")
#             # print(InstantiateDateResult)
#             pattern_pd = InstantiateDateResult[0]
#             continu = InstantiateDateResult[1]
#             supp = InstantiateDateResult[2]
#             conf = InstantiateDateResult[3]
#
#             if continu:
#                 startDate = InstantiateDateResult[4] #--------------------------------------------------------------------------------------- must be: InstantiateDateResult[4] - 1
#                 patternSet_l = set()
#                 lAdd = False
#                 # lSet = SelectLocation(k, k_onto, p)
#                 # print(lSet)
#                 # if 'NamedIndividual' in lSet:
#                 #     lSet.remove('NamedIndividual')
#                 # pattern_lpd = pattern_pd
#                 for l in lSet:
#                     pattern_l = pattern_pd.replace("Location", l)
#                     su = suppCalculate(k, k_onto, pattern_l)
#                     if su >= minSupp:
#                         c = confCalculate(k, k_onto, pattern_l, su)
#                         if c > conf:
#                             # print("1- c="+str(c)+" ... conf="+str(conf))
#                             conf = c
#                             lAdd = True
#                             patternSet_l.add(tuple([pattern_l, su, c]))
#                             # pattern_lpd = pattern_l
#                 if not lAdd:
#                     patternSet_l.add(tuple([pattern_pd, supp, conf]))
#                 # pattern_slpd = pattern_lpd
#
#
#                 # sSet = SelectStructure(k, k_onto, p)
#                 # print(sSet)
#                 # if 'NamedIndividual' in sSet:
#                 #     sSet.remove('NamedIndividual')
#                 for pattern_i in patternSet_l:
#                     sAdd = False
#                     for s in sSet:
#                         pattern_s = pattern_i[0].replace("Structure", s)
#                         su = suppCalculate(k, k_onto, pattern_s)
#                         if su >= minSupp:
#                             c = confCalculate(k, k_onto, pattern_s, su)
#                             if c > pattern_i[2]:
#                                 # print("2- c=" + str(c) + " ... conf=" + str(conf))
#                                 # conf = c
#                                 sAdd = True
#                                 patternSet.add(tuple([pattern_s, su, c]))
#                                 # pattern_slpd = pattern_s
#                         if not sAdd:
#                             patternSet.add(pattern_i)
#
#     # print("END")
#     # print(patternSet)
#     return patternSet
#
#
# def SelectProductBrother(k, k_onto, lSet, p):
#     brothersList = []
#     for l in lSet:
#         q = 'SELECT DISTINCT ?x WHERE { ?Location :contain ?Product . ?Location rdf:type ?l . ?l rdfs:subClassOf* :Location . ?Product rdf:type ?x . ?x rdfs:subClassOf* :Product . }'
#         qres = k.query(q, initBindings={'l': rdflib.term.URIRef(k_onto.base_iri + l)})
#
#         productList = []
#         for row in qres:
#             brothersList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
#     brothersList.remove(p)
#
#     return brothersList
#
#
# def SelectLocationBrother(k, k_onto, lSet):
#     brothersList = []
#     for l in lSet:
#         q = 'SELECT DISTINCT ?x WHERE { ?Structure :has_location ?Location . ?Structure :has_location ?Location2 . ?Location rdf:type ?l . ?l rdfs:subClassOf* :Location . ?Location2 rdf:type ?x . ?x rdfs:subClassOf* :Location .}'
#         qres = k.query(q, initBindings={'l': rdflib.term.URIRef(k_onto.base_iri + l)})
#
#         productList = []
#         for row in qres:
#             brothersList.append(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
#         brothersList.remove(l)
#
#     return brothersList
#
#
# def Combine(k, k_onto, R_initial, pBrotherSet, lBrotherSet, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL):
#     patternSet = set()
#
#     for ri in R_initial:
#         numP = 2
#         r = ri[0]
#         su = ri[1]
#         c = ri[2]
#         if c < maxConf:
#             pBrotherNum = 0
#             for b in pBrotherSet:
#                 rf = r.replace("contain(L, P), ", "contain(L, P), " + b + "(P" + str(numP) + "), contain(L, P" + str(numP) + "), ")
#                 # print("**"+rf)
#                 supp = suppCalculate(k, k_onto, rf)
#                 # print(supp)
#                 conf = confCalculate(k, k_onto, rf, supp)
#                 # print(conf)
#                 if supp >= minSupp and conf > c:
#                     numP += 1
#                     r = rf
#                     su = supp
#                     c = conf
#                     pBrotherNum += 1
#                     if pBrotherNum == maxBrotherP:
#                         break
#             numL = 2
#             lBrotherNum = 0
#             for lb in lBrotherSet:
#                 rf = r.replace("has_location(S, L), ", "has_location(S, L), " + lb + "(L" + str(numL) + "), has_location(S, L" + str(numL) + "), ")
#                 # print("--"+rf)
#                 supp = suppCalculate(k, k_onto, rf)
#                 # print(supp)
#                 conf = confCalculate(k, k_onto, rf, supp)
#                 # print(conf)
#                 if supp >= minSupp and conf > c:
#                     numL += 1
#                     r = rf
#                     su = supp
#                     c = conf
#                     lBrotherNum += 1
#                     if lBrotherNum == maxBrotherL:
#                         break
#
#         patternSet.add(tuple([r, su, c]))
#
#     return patternSet
#
#
#
#
#
#
#
# def ALGO(k, k_onto, pattern, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL):
#     ruleSet = set()
#     pSet = SelectProduct(k)
#     # print(pSet)
#     for p in pSet:
#         lSet = SelectLocation(k, k_onto, p)
#         sSet = SelectStructure(k, k_onto, p)
#         R_initial = Instantiate(k, k_onto, pattern, p, lSet, sSet, minConf, minSupp, maxConf)
#         # print(R_initial)
#         if R_initial:
#             pBrotherSet = SelectProductBrother(k, k_onto, lSet, p)
#             # print(pBrotherSet)
#             lBrotherSet = SelectLocationBrother(k, k_onto, lSet)
#             # print(lBrotherSet)
#
#             R_f = Combine(k, k_onto, R_initial, pBrotherSet, lBrotherSet, minConf, minSupp, maxConf, maxBrotherP, maxBrotherL)
#             ruleSet.update(R_f)
#
#     print("END")
#     print(ruleSet)
#
#
#
#         # lSet = SelectLocation(k, k_onto, p)
#         # if 'NamedIndividual' in lSet:
#         #     lSet.remove('NamedIndividual')
#         # # print(lSet)
#         # for l in lSet:
#         #     sSet = SelectStructure(k, k_onto, l)
#         #     if 'NamedIndividual' in sSet:
#         #         sSet.remove('NamedIndividual')
#         #     # print(sSet)
#         #     continu = True
#         #     for s in sSet:
#         #         R_initial = Instantiate(k, k_onto, pattern, p, l, s, minConf, minSupp, maxConf, continu)
#
#
# ALGO(k, k_onto, pattern, 0, 1, 2, 3, 3)
# ###----------------------------------- ALGORITHM -----------------------------------###







# import owlready2
# owlready2.JAVA_EXE = "C:\\Program Files\\Java\\jdk-13.0.1\\bin\\java.exe"
#
# # # Load the ontology -----------------------------------------
# # ontoTest = get_ontology("file://t\\t.owl").load()
# # ontoTest.save(file="t\\tIn.owl")
#
# ontoIn = get_ontology("file://t\\tIn.owl").load()
# # rule = Imp()
# # rule.set_as_rule("""has_calculated_characteristic(?PR1, ?C1), has_calculated_characteristic(?PR2, ?C2), has_calculation_year(?C1, ?Y1), has_calculation_year(?C2, ?Y2), greaterThanOrEqual(?Y2, ?Y1), Enduit(?PR1), Enduit(?PR2), has_product_class(?C1, "Low") -> has_product_class(?C2, "Low")""")
#
# with ontoIn:
#     # sync_reasoner_pellet()
#     sync_reasoner_pellet(infer_data_property_values=True)
#
# ontoIn.save(file="t\\tontologyResult.owl", format="rdfxml")


# global annee
# global numbB


# # Load the ontology -----------------------------------------
# onto = get_ontology("file://AsbestosOntology.owl").load()
# onto.load()
# print(list(onto.classes()))
# print(list(onto.object_properties()))
# print(list(onto.data_properties()))
# print(list(onto.properties()))


# # Load the 'Projet type homologué' --------------------------
# with open('DATA\ph1.csv') as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=';')
#     line_count = 0
#     for row in csv_reader:
#         if line_count == 0:
#
#             print(f'++{row[1]}')
#         else:
#             print(f'\t{row[0]} => {row[1]}')
#         line_count += 1


# Settlement ---------------------------------------------------
# batiment_1 = onto.Building("Bat_73")
# structure_1 = onto.Structure("Plancher-sols")
# localisation_1 = onto.Location("Dalle")
# famiile_de_produit_1 = onto.ProductFamily("Beton_armé")
#
# batiment_1.has_structure.append(structure_1)
# structure_1.has_location.append(localisation_1)
# localisation_1.contain.append(famiile_de_produit_1)
#
# batiment_1.has_type.append("F4")
# batiment_1.has_address.append("11_AVENUE_ALBERT")
# batiment_1.has_year.append(1957)

# Enrechissement
# with onto:
#     class Equipment(Thing):
#         pass
#
#     class has_type_of_use(DataProperty):
#         range = [str]
#
#     class has_for_ingredient(ObjectProperty):
#         domain = [onto.ProductFamily]
#         range = [Equipment]

# # Save le peuplement
# onto.save(file = "peuplement.owl", format = "rdfxml")
# ---------------------------------------------------------------

BTN_L_BG = "#7b68ee"
BTN_E_BG = "#4169e1"

FONT_1 = ("Constantia", 18)
FONT_2 = ("Constantia", 16)
FONT_3 = ("Constantia", 14)
FONT_4 = ("Constantia", 12)
FONT_5 = ('consolas', 10)
FONT_BTN = ("Constantia", 12, "bold")

MAINAPP_WIDTH = 1100
MAINAPP_HEIGHT = 600

# SIDEBARE_BG = "#3e4c54"
SIDEBARE_BG = "#212f3c"
SIDEBARE_WIDTH = 250
SIDEBARE_HEIGHT = 600
SIDEBARE_ELEMENT_WIDTH = 28
SIDEBARE_ELEMENT_HEIGHT = 2
SIDEBARE_ELEMENT_NBG = "#212f3c"
SIDEBARE_ELEMENT_NFG = "#6ba4c3"
SIDEBARE_ELEMENT_HBG = "#2e4053"
SIDEBARE_ELEMENT_HFG = "#78b8db"
SIDEBARE_ELEMENT_SBG = "#34495e"
SIDEBARE_ELEMENT_SFG = "#78b8db"

TITEL_CELL_BG = "#2e4053"
CELL_BG = "#212f3c"

WORKSPACE_WIDTH = 850
WORKSPACE_HEIGHT = 600

# BOARD_BG = "#495a62"
BOARD_BG = "#1b2631"
BOARD_WIDTH = 850
BOARD_HEIGHT = 580

TITLE_FG = "#78b8db"
LABEL_FG = "white"
BUTTON_FG = "#78b8db"
BUTTON_WIDTH = 28
PATH_BG = "#6a828e"
PATH_FG = "#cccccc"
PATH_WIDTH = 70
PATH_PADDING = "10 0 0 0"

# STATUSBAR_BG = "#778e9a"
STATUSBAR_BG = "#283747"

VIEWER_BG = "#7f7f7f"

CONTAINER_WIDTH = 700

ICON_WIDTH = 10
ICON_HEIGHT = 10

projetFilesNames = []
diagnosticFilesNames = []
dtuFilesNames = None
inrsFileName = None
andevaFileName = None
wordTokens = None
sentTokens = None
termsList = []

buildingID = 0
structID = 0
locID = 0
prodID = 0


def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("Erreur")
    container = tk.Frame(popup, bg=BOARD_BG, width=300, height=150)
    container.pack()
    container.pack_propagate(0)
    label = ttk.Label(container, background=BOARD_BG, foreground="white", text=msg, anchor="n", font=FONT_4)
    label.pack(side="top", fill="x", pady=10)
    b1 = ttk.Button(container, text="OK", command=popup.destroy)
    b1.pack(side="bottom", pady=10)
    positionRight = int(popup.winfo_screenwidth() / 2 - popup.winfo_reqwidth() / 2)
    positionDown = int(popup.winfo_screenheight() / 2 - popup.winfo_reqheight() / 2)
    popup.geometry("+{}+{}".format(positionRight, positionDown))
    popup.resizable(0, 0)
    popup.mainloop()


def deleteFiles(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def filesChooser(filePath):
    fileN = askopenfilenames(parent=app, title="Choisir vos fichiers")
    lst = list(fileN)
    filePath.config(text=lst)
    return lst


def projetFilesChooser(filePath):
    global projetFilesNames
    projetFilesNames = filesChooser(filePath)


def diagnosticFilesChooser(filePath):
    global diagnosticFilesNames
    diagnosticFilesNames = filesChooser(filePath)


def dtuFilesChooser(filePath):
    global dtuFilesNames
    dtuFilesNames = filesChooser(filePath)


def getProjectsContenent(num):
    global projetFilesNames

    building = []
    with open(projetFilesNames[num]) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        buildingConponents = []
        for row in csv_reader:
            if line_count == 0:
                buildingInfo = [f'{row[0]}', f'{row[1]}', f'{row[2]}', f'{row[3]}', f'{row[4]}', f'{row[5]}',
                                f'{row[6]}']
            else:
                if f'{row[2]}' != '':
                    structureDiscription = [f'{row[0]}', f'{row[1]}' + ' contient ' + f'{row[2]}']
                else:
                    structureDiscription = [f'{row[0]}', f'{row[1]}']
                buildingConponents.append(structureDiscription)
            line_count += 1
        building = [buildingInfo, buildingConponents]

    return building


def getProjectsResults(fileName):
    result = []
    with open('RESULTS\\' + fileName + '.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            line = [f'{row[1]}', f'{row[2]}', f'{row[3]}', f'{row[4]}', f'{row[5]}']
            result.append(line)

    return result


# Similarity between two termes
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def terminologyExtraction(data):
    # global projetFilesNames
    # data = ""
    # for i in projetFilesNames:
        ## f = open(i, "r")
        # f = open(i, encoding='utf-8', mode="r").read()
        # text_filtered = re.sub(r'<(.*?)>', '', f)
        # data += text_filtered.strip()
    ## print(data)
    # global sentTokens
    ## sentTokens = sent_tokenize(f.read(), language='french')
    sentTokens = sent_tokenize(data, language='french')
    ## global word_tokens
    ## word_tokens = word_tokenize(data)
    ## print(sentTokens)
    ## print(word_tokens)
    ## f.close()
    global termsList
    for i in sentTokens:
        # 1) build a TreeTagger wrapper:
        tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr')
        # 2) tag the text.
        tags = tagger.tag_text(i)
        # 3) use the tags list... (list of string output from TreeTagger).
        findNoun = False
        findPrp = False
        count = 0
        term = ''
        prop = ''
        for j in tags:
            count += 1
            # print(j)
            if j[j.find('\t') + len('\t'):j.rfind('\t')] in ['NOM', 'VER:pper', 'VER:infi', 'ADJ']:# Verifier l'expression reguliere avec toutes les possibilités
                term += prop + j[:j.find('\t')] + ' '
                findNoun = True
                findPrp = False
                prop = ''
                # print('findNoun')
            elif findNoun and j[j.find('\t') + len('\t'):j.rfind('\t')] in ['PRP'] and j[:j.find('\t')] != 'avec':
                prop += j[:j.find('\t')] + ' '
                findNoun = False
                findPrp = True
                # print('findPRP')
            elif term != '':
                termsList.append(term[:-1])
                term = ''
                prop = ''
                findNoun = False
                findPrp = False
                # print('add')
            if count == len(tags) and term != '':
                termsList.append(term[:-1])
                # print('end')

            #     term += j[:j.find('\t')] + ' '
            # else:
            #     if term != '':
            #         termsList.append(term[:-1])
            #     term = ''

        # print(termsList)

    ## abestosTermSearch()


def dataOntologySettlement():
    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # Load Data Constraint --------------------------
    with open('DATA\DataConstraint.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if f'{row[1]}' == '1' or f'{row[1]}' == '2' or f'{row[1]}' == '3':
                structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_'))
                location_i = onto.Location(f'{row[2]}'.lower().replace(' ', '_'))
                structure_i.has_location.append(location_i)
            else:
                location_i = onto.Location(f'{row[0]}'.lower().replace(' ', '_'))
                product_i = onto.Product(f'{row[2]}'.lower().replace(' ', '_'))
                location_i.contain.append(product_i)
            line_count += 1
        # Save data settlement
        onto.save(file="ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")

        # Delete old individuals
        for individual in list(onto.individuals()):
            destroy_entity(individual)


dataOntologySettlement()

def str2date(date):
    if len(date) == 7:
        return dt.strptime(date, "%m/%Y")
    else:
        return dt.strptime(date, "%Y")

def compareDates(date_1, date_2):
    if len(date_1) == 7 and len(date_2) == 7:
        return dt.strptime(date_1, "%m/%Y") <= dt.strptime(date_2, "%m/%Y")
    elif len(date_1) == 4 and len(date_2) == 4:
        return int(date_1) <= int(date_2)
    elif len(date_1) == 4 and len(date_2) == 7:
        return int(date_1) <= int(date_2[date_2.find('/') + len('/'):])
    elif len(date_1) == 7 and len(date_2) == 4:
        return int(date_1[date_1.find('/') + len('/'):]) <= int(date_2)


def paCalculation(prodactFamilyName, date):
    probaSum = 0
    cardinal = 0

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")

    #Select Products in this family
    q = 'SELECT ?x WHERE { ?x rdf:type ?type .}'
    qres = g.query(q, initBindings={'type': rdflib.term.URIRef(onto.base_iri + prodactFamilyName)})

    for rowProd in qres:
        # Select merged characteristics
        qp = 'SELECT ?sd ?ed ?pr WHERE { ?p :has_extracted_characteristic ?c . ?c :has_source ?s . ?c :has_start_date ?sd . ?c :has_end_date ?ed . ?c :has_extracted_probability ?pr .}'
        qresp = g.query(qp, initBindings={'p': rowProd[0], 's': rdflib.term.Literal('merged', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string'))})
        for row in qresp:
            # print(row[0] + '-' + row[1] + '-' + row[2])
            if len(row[0]) <= 7:
                startDate = row[0]
            else:
                startDate = row[0][row[0].find(' ') + len(' '):row[0].rfind('\'')]
            if len(row[1]) <= 7:
                endDate = row[1]
            else:
                endDate = row[1][row[1].find(' ') + len(' '):row[1].rfind('\'')]
            if compareDates(startDate, date) and compareDates(date, endDate):
                probaSum += float(row[2])
                cardinal += 1
    if cardinal > 0:
        # print('-')
        # print(probaSum)
        # print(cardinal)
        #
        # print((probaSum + cardinal*0.0366*0.00021) / (cardinal + cardinal*0.0366))
        # print((probaSum + cardinal * 0.0366 * 0.00021) / (cardinal - cardinal * 0.0366))

        return probaSum / cardinal
    else:
        return -1


def wCalculation(k, iri, prodactFamilyName, da, productType):
    print(prodactFamilyName)
    # da = 1989
    # prodactFamilyName = 'plaquessouplesantivibratiles'
    date = str(da) + '-01-01T00:00:00'
    # print(date)

    positiveD = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Product rdf:type ?p . ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year = ?y) . }'
    positiveDqres = k.query(positiveD, initBindings={'p': rdflib.term.URIRef(iri + productType),
                                                     'd': rdflib.term.Literal(1),
                                                     'y': rdflib.term.Literal(date,
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))
                                                     })
    pDiagA = len(positiveDqres)

    # negativeD = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Product rdf:type ?p . ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year = ?y) . }'
    # negativeDqres = k.query(negativeD, initBindings={'p': rdflib.term.URIRef(iri + productType),
    #                                                  'd': rdflib.term.Literal(0),
    #                                                  'y': rdflib.term.Literal(date,
    #                                                                           datatype=rdflib.term.URIRef(
    #                                                                               'http://www.w3.org/2001/XMLSchema#dateTime'))
    #                                                  })
    negativeD = 'SELECT DISTINCT ?Product WHERE { ?Product rdf:type ?p . ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year = ?y) . }'
    negativeDqres = k.query(negativeD, initBindings={'p': rdflib.term.URIRef(iri + productType),
                                                     'y': rdflib.term.Literal(date,
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))
                                                     })
    pDiag = len(negativeDqres) + pDiagA

    pa = paCalculation(prodactFamilyName, da)

    # positiveP = 'SELECT DISTINCT ?Product WHERE { ?Product rdf:type ?p . ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year = ?y) . }'
    # positivePqres = k.query(positiveP, initBindings={'p': rdflib.term.URIRef(iri + productType),
    #                                                  'y': rdflib.term.Literal(date,
    #                                                                           datatype=rdflib.term.URIRef(
    #                                                                               'http://www.w3.org/2001/XMLSchema#dateTime'))
    #                                                  })
    # xk = len(positivePqres)

    print('pDiagA: ', str(pDiagA))
    print('pDiag: ', str(pDiag))
    print('pa: ', str(pa))
    # print('xk: ', str(xk))

    if pDiag == 0:#xk == 0 or
        return -1
    else:
        return ((pDiagA / pDiag) - pa)



def alphaCalculation(k, iri, prodactFamilyName, date, productType):
    w = wCalculation(k, iri, prodactFamilyName, date, productType)
    print('w', str(w))
    if w == -1:
        return -1
    else:
        return (0 - w) / (1 + w)


def probabilityCalculation(k, iri, prodactFamilyName, date, productType):
    probaSum = 0
    cardinal = 0

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")

    #Select Products in this family
    q = 'SELECT ?x WHERE { ?x rdf:type ?type .}'
    qres = g.query(q, initBindings={'type': rdflib.term.URIRef(onto.base_iri + prodactFamilyName)})

    for rowProd in qres:
        # Select merged characteristics
        qp = 'SELECT ?sd ?ed ?pr WHERE { ?p :has_extracted_characteristic ?c . ?c :has_source ?s . ?c :has_start_date ?sd . ?c :has_end_date ?ed . ?c :has_extracted_probability ?pr .}'
        qresp = g.query(qp, initBindings={'p': rowProd[0], 's': rdflib.term.Literal('merged', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string'))})
        for row in qresp:
            # print(row[0] + '-' + row[1] + '-' + row[2])
            if len(row[0]) <= 7:
                startDate = row[0]
            else:
                startDate = row[0][row[0].find(' ') + len(' '):row[0].rfind('\'')]
            if len(row[1]) <= 7:
                endDate = row[1]
            else:
                endDate = row[1][row[1].find(' ') + len(' '):row[1].rfind('\'')]
            if compareDates(startDate, date) and compareDates(date, endDate):
                probaSum += float(row[2])
                cardinal += 1
    if cardinal > 0:
        # print('-')
        # print(probaSum)
        # print(cardinal)
        #
        # print((probaSum + cardinal*0.0366*0.00021) / (cardinal + cardinal*0.0366))
        # print((probaSum + cardinal * 0.0366 * 0.00021) / (cardinal - cardinal * 0.0366))

        # return probaSum / (cardinal * (1 + 1.0076)) # with old alpha
        alpha = alphaCalculation(k, iri, prodactFamilyName, date, productType)
        print('alpha', str(alpha))
        if alpha == -1:
            return -1
        else:
            return probaSum / (cardinal * (1 + alpha))  # with new calculated alpha
    else:
        return -1


# print(probabilityCalculation('enduits_de_façade', '1948'))


def probabilityCalculation_Old(prodactFamilyName, date):
    probaSum = 0
    cardinal = 0

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")

    #Select Products in this family
    q = 'SELECT ?x WHERE { ?x rdf:type ?type .}'
    qres = g.query(q, initBindings={'type': rdflib.term.URIRef(onto.base_iri + prodactFamilyName)})

    for rowProd in qres:
        # Select merged characteristics
        qp = 'SELECT ?sd ?ed ?pr WHERE { ?p :has_extracted_characteristic ?c . ?c :has_source ?s . ?c :has_start_date ?sd . ?c :has_end_date ?ed . ?c :has_extracted_probability ?pr .}'
        qresp = g.query(qp, initBindings={'p': rowProd[0], 's': rdflib.term.Literal('merged', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string'))})
        for row in qresp:
            # print(row[0] + '-' + row[1] + '-' + row[2])
            if len(row[0]) <= 7:
                startDate = row[0]
            else:
                startDate = row[0][row[0].find(' ') + len(' '):row[0].rfind('\'')]
            if len(row[1]) <= 7:
                endDate = row[1]
            else:
                endDate = row[1][row[1].find(' ') + len(' '):row[1].rfind('\'')]
            if compareDates(startDate, date) and compareDates(date, endDate):
                probaSum += float(row[2])
                cardinal += 1
    if cardinal > 0:
        # print('-')
        # print(probaSum)
        # print(cardinal)
        #
        # print((probaSum + cardinal*0.0366*0.00021) / (cardinal + cardinal*0.0366))
        # print((probaSum + cardinal * 0.0366 * 0.00021) / (cardinal - cardinal * 0.0366))

        return probaSum / (cardinal * (1 + 1.0076)) # with alpha
    else:
        return -1


def probabilityCalculationByYearByProductFamely():
    productFamilyNameList = ['adhésif', 'amiante_ciment', 'bandes', 'bourrelets', 'cartons', 'chaudières', 'cloisons', 'colles', 'coquilles', 'cordons', 'couvertures', 'dalle', 'enduits', 'enduits_de_façade', 'enduits_plâtre_de_protection_incendie',
                             'faux_plafonds', 'feuilles', 'feutres', 'freins', 'gaine', 'isolant', 'isolant_thermique', 'isolateurs_électriques', 'isolation_thermique', 'joints', 'joint_béton', 'mastics', 'mastic_bitume', 'matelas', 'materiau_pour_joints',
                             'matière_plastique', 'matériaux_composites', 'matériaux_de_friction', 'mortiers_colles', 'mortiers_de_protection_incendie', 'mortiers_réfractaires', 'nez_de_marches', 'panneaux', 'panneau_isolant', 'peintures', 'plan', 'plaques',
                             'plâtre', 'portes', 'portes_d_ascenseur', 'poudre_à_mouler', 'pâte_à_joint', 'radiateurs', 'revêtement', 'revêtements_de_sols_en_dalles_ou_en_rouleaux', 'tissus', 'tresses']

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")

    csvFile = open('testGraphYearProduct.csv', 'a')
    csvFile.write('year')
    for i in productFamilyNameList:
        csvFile.write(';' + i)

    date = 1946
    while date < 1997:
        print(date)
        csvFile.write('\n' + str(date))

        for productFamilyName in productFamilyNameList:

            # Select Products in this family
            q = 'SELECT ?x WHERE { ?x rdf:type ?type .}'
            qres = g.query(q, initBindings={'type': rdflib.term.URIRef(onto.base_iri + productFamilyName)})

            probaSum = 0
            cardinal = 0

            for rowProd in qres:
                # Select merged characteristics
                qp = 'SELECT ?sd ?ed ?pr WHERE { ?p :has_extracted_characteristic ?c . ?c :has_source ?s . ?c :has_start_date ?sd . ?c :has_end_date ?ed . ?c :has_extracted_probability ?pr .}'
                qresp = g.query(qp, initBindings={'p': rowProd[0], 's': rdflib.term.Literal('merged', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string'))})
                for row in qresp:
                    # print(row[0] + '-' + row[1] + '-' + row[2])
                    if len(row[0]) <= 7:
                        startDate = row[0]
                    else:
                        startDate = row[0][row[0].find(' ') + len(' '):row[0].rfind('\'')]
                    if len(row[1]) <= 7:
                        endDate = row[1]
                    else:
                        endDate = row[1][row[1].find(' ') + len(' '):row[1].rfind('\'')]
                    if compareDates(startDate, str(date)) and compareDates(str(date), endDate):
                        probaSum += float(row[2])
                        cardinal += 1
            if cardinal > 0:
                # print('-')
                # print(probaSum)
                # print(cardinal)
                #
                # print((probaSum) / (cardinal + cardinal*1.0077))
                #
                proba = probaSum / cardinal
            else:
                proba = -1
            csvFile.write(';' + str(proba))
        date += 1
    csvFile.close()

# probabilityCalculationByYearByProductFamely()


def probabilityCalculationByYear():

    prodactFamilyName = "Product"

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")

    #Select Products
    q = 'SELECT ?x WHERE { ?x :has_extracted_characteristic ?c .}'
    qres = g.query(q)

    csvFile = open('testGraphYear.csv', 'a')
    csvFile.write('year;proba\n')

    date = 1946
    while date < 1997:
        print(date)
        probaSum = 0
        cardinal = 0

        for rowProd in qres:
            # Select merged characteristics
            qp = 'SELECT ?sd ?ed ?pr WHERE { ?p :has_extracted_characteristic ?c . ?c :has_source ?s . ?c :has_start_date ?sd . ?c :has_end_date ?ed . ?c :has_extracted_probability ?pr .}'
            qresp = g.query(qp, initBindings={'p': rowProd[0], 's': rdflib.term.Literal('merged', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string'))})
            for row in qresp:
                # print(row[0] + '-' + row[1] + '-' + row[2])
                if len(row[0]) <= 7:
                    startDate = row[0]
                else:
                    startDate = row[0][row[0].find(' ') + len(' '):row[0].rfind('\'')]
                if len(row[1]) <= 7:
                    endDate = row[1]
                else:
                    endDate = row[1][row[1].find(' ') + len(' '):row[1].rfind('\'')]
                if compareDates(startDate, str(date)) and compareDates(str(date), endDate):
                    probaSum += float(row[2])
                    cardinal += 1
        if cardinal > 0:
            # print('-')
            # print(probaSum)
            # print(cardinal)
            #
            # print((probaSum) / (cardinal + cardinal*1.0077))
            #
            proba = probaSum / cardinal
        else:
            proba = -1
        csvFile.write(str(date) + ';' + str(proba) + '\n')
        date += 1
    csvFile.close()


def probabilityClassCalculation(probability):
    if probability <= 0.39: # recalculer le seuuil 0.25095 ------------------------------------------------------------------------
        return 0#avant c'etait 1
    else:
        return 1#avant c'etait 2
    # if probability == 0:
    #     return 0
    # elif probability == 1:
    #     return 3
    # elif 0 < probability <= 0.5:
    #     return 1
    # elif 0.5 < probability < 1:
    #     return 2

# def stringIntersection(str1, str2):
#     i = 0
#     while i < len(str1):
#         if str1[i:i+5] in str2:
#             return True
#         i += 1
#     return False


def productOntologySettlement():
    externalResourcesFileName = 'DATA\ExternalResources.csv'

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # Load the external resources --------------------------
    with open(externalResourcesFileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                typeStr = f'{row[0]}'.lower().replace(' ', '_').replace('-', '_').replace('\'', '_') + '/' + f'{row[7]}'.lower().replace(' ', '_').replace('-', '_').replace('\'', '_')
                for className in typeStr.replace('/', ' ').split():
                    featureNbr = 0
                    # className = f'{row[0]}'.lower().replace(' ', '_').replace('-', '_').replace('\'', '_')
                    # Enrichment
                    with onto:
                        if className != 'product':
                            if f'{row[9]}' == '':
                                exec("class %s(onto.Product):\
                                        pass" % (className))
                            else:
                                uperClass = f'{row[9]}'.lower().replace(' ', '_').replace('-', '_').replace('\'', '_')
                                exec("class %s(onto.Product):\
                                        pass" % (uperClass))
                                exec("class %s(onto.%s):\
                                        pass" % (className, uperClass))
                        else:
                            className = 'Product'
                    providerName = f'{row[1]}'.replace(' ', '_')
                    prodName = f'{row[2]}'.replace(' ', '_') + ':' + providerName + ':' + className
                    exec("product_i = onto.%s(prodName)" % (className))
                    exec("product_i.has_provider.append(providerName)")
                    exec("product_i.has_asbestos_type.append(f'{row[6]}'.replace(' ', '_').replace('-', '_'))")

                    # for type in f'{row[7]}'.lower().replace(' ', '_').replace('-', '_').replace('/', ' ').split():
                    #     # Enrichment
                    #     with onto:
                    #         exec("class %s(Thing):\
                    #                 pass" % (type))
                    #     # Settlement
                    #     exec("product_i.is_a.append(onto.%s)" % (type))

                    extractedFeature_i = onto.ExtractedCharacteristic(
                        'extracted_feature_' + str(featureNbr) + ':' + prodName)
                    extractedFeature_i.has_start_date.append('1945')
                    if f'{row[3]}' == '' and f'{row[4]}' == '':
                        extractedFeature_i.has_end_date.append('1997')
                        extractedFeature_i.has_extracted_probability.append(0.5)
                        extractedFeature_i.has_source.append('merged')
                        exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                    else:
                        date = ''
                        if f'{row[3]}' != '' and f'{row[4]}' == '':
                            date = f'{row[3]}'
                            # extractedFeature_i.has_source.append('andeva')
                        elif f'{row[3]}' != '' and f'{row[4]}' != '' and compareDates(f'{row[4]}', f'{row[3]}'):
                            date = f'{row[3]}'
                        elif f'{row[3]}' == '' and f'{row[4]}' != '':
                            date = f'{row[4]}'
                            # extractedFeature_i.has_source.append('inrs')
                        elif f'{row[3]}' != '' and f'{row[4]}' != '' and compareDates(f'{row[3]}', f'{row[4]}'):
                            date = f'{row[4]}'
                        elif f'{row[3]}' == f'{row[4]}':
                            date = f'{row[3]}'

                        extractedFeature_i.has_end_date.append(date)
                        extractedFeature_i.has_extracted_probability.append(1)
                        extractedFeature_i.has_source.append('merged')
                        exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                        featureNbr += 1

                        if f'{row[5]}' in ['3', '6']:
                            extractedFeature_i = onto.ExtractedCharacteristic(
                                'extracted_feature_' + str(featureNbr) + ':' + prodName)
                            extractedFeature_i.has_start_date.append(date)
                            extractedFeature_i.has_end_date.append('1997')
                            extractedFeature_i.has_extracted_probability.append(0.5)
                            extractedFeature_i.has_source.append('merged')
                            exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                            featureNbr += 1
                        elif f'{row[5]}' in ['', '1', '2', '4']:
                            extractedFeature_i = onto.ExtractedCharacteristic(
                                'extracted_feature_' + str(featureNbr) + ':' + prodName)
                            extractedFeature_i.has_start_date.append(date)
                            extractedFeature_i.has_end_date.append('1997')
                            extractedFeature_i.has_extracted_probability.append(0)
                            extractedFeature_i.has_source.append('merged')
                            exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                            featureNbr += 1
                        elif f'{row[5]}' in ['8']:
                            extractedFeature_i = onto.ExtractedCharacteristic(
                                'extracted_feature_' + str(featureNbr) + ':' + prodName)
                            extractedFeature_i.has_start_date.append(date)
                            extractedFeature_i.has_end_date.append('1997')
                            extractedFeature_i.has_extracted_probability.append(0)
                            extractedFeature_i.has_source.append('merged')
                            exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                            featureNbr += 1
                            exec(
                                "product_i.has_newName.append(f'{row[8]}' + ':' + str(featureNbr))")  # apply the new name from this feature
                        if f'{row[3]}' != '':
                            extractedFeature_i = onto.ExtractedCharacteristic(
                                'extracted_feature_' + str(featureNbr) + ':' + prodName)
                            extractedFeature_i.has_start_date.append('1945')
                            extractedFeature_i.has_end_date.append(f'{row[3]}')
                            extractedFeature_i.has_extracted_probability.append(1)
                            extractedFeature_i.has_source.append('andeva')
                            exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                            featureNbr += 1
                            if f'{row[5]}' in ['3', '6']:
                                extractedFeature_i = onto.ExtractedCharacteristic(
                                    'extracted_feature_' + str(featureNbr) + ':' + prodName)
                                extractedFeature_i.has_start_date.append(f'{row[3]}')
                                extractedFeature_i.has_end_date.append('1997')
                                extractedFeature_i.has_extracted_probability.append(0.5)
                                extractedFeature_i.has_source.append('andeva')
                                exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                                featureNbr += 1
                            elif f'{row[5]}' in ['', '1', '2', '4']:
                                extractedFeature_i = onto.ExtractedCharacteristic(
                                    'extracted_feature_' + str(featureNbr) + ':' + prodName)
                                extractedFeature_i.has_start_date.append(f'{row[3]}')
                                extractedFeature_i.has_end_date.append('1997')
                                extractedFeature_i.has_extracted_probability.append(0)
                                extractedFeature_i.has_source.append('andeva')
                                exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                                featureNbr += 1
                            elif f'{row[5]}' in ['8']:
                                extractedFeature_i = onto.ExtractedCharacteristic(
                                    'extracted_feature_' + str(featureNbr) + ':' + prodName)
                                extractedFeature_i.has_start_date.append(f'{row[3]}')
                                extractedFeature_i.has_end_date.append('1997')
                                extractedFeature_i.has_extracted_probability.append(0)
                                extractedFeature_i.has_source.append('andeva')
                                exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                                featureNbr += 1
                                exec(
                                    "product_i.has_newName.append(f'{row[8]}' + ':' + str(featureNbr))")
                        if f'{row[4]}' != '':
                            extractedFeature_i = onto.ExtractedCharacteristic(
                                'extracted_feature_' + str(featureNbr) + ':' + prodName)
                            extractedFeature_i.has_start_date.append('1945')
                            extractedFeature_i.has_end_date.append(f'{row[4]}')
                            extractedFeature_i.has_extracted_probability.append(1)
                            extractedFeature_i.has_source.append('inrs')
                            exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                            featureNbr += 1
                            if f'{row[5]}' in ['3', '6']:
                                extractedFeature_i = onto.ExtractedCharacteristic(
                                    'extracted_feature_' + str(featureNbr) + ':' + prodName)
                                extractedFeature_i.has_start_date.append(f'{row[4]}')
                                extractedFeature_i.has_end_date.append('1997')
                                extractedFeature_i.has_extracted_probability.append(0.5)
                                extractedFeature_i.has_source.append('inrs')
                                exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                                featureNbr += 1
                            elif f'{row[5]}' in ['', '1', '2', '4']:
                                extractedFeature_i = onto.ExtractedCharacteristic(
                                    'extracted_feature_' + str(featureNbr) + ':' + prodName)
                                extractedFeature_i.has_start_date.append(f'{row[4]}')
                                extractedFeature_i.has_end_date.append('1997')
                                extractedFeature_i.has_extracted_probability.append(0)
                                extractedFeature_i.has_source.append('inrs')
                                exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                                featureNbr += 1
                            elif f'{row[5]}' in ['8']:
                                extractedFeature_i = onto.ExtractedCharacteristic(
                                    'extracted_feature_' + str(featureNbr) + ':' + prodName)
                                extractedFeature_i.has_start_date.append(f'{row[4]}')
                                extractedFeature_i.has_end_date.append('1997')
                                extractedFeature_i.has_extracted_probability.append(0)
                                extractedFeature_i.has_source.append('inrs')
                                exec("product_i.has_extracted_characteristic.append(extractedFeature_i)")
                                featureNbr += 1
                                exec(
                                    "product_i.has_newName.append(f'{row[8]}' + ':' + str(featureNbr))")

            line_count += 1

        # Save the products ontology settlement
        onto.save(file="ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")

        # Delete old individuals
        for individual in list(onto.individuals()):
            destroy_entity(individual)

productOntologySettlement()


def AsbestosOntologySettlement_newRAT(projectFileName, path):#the new format of the diagnostic
    global termsList
    locationsList = []
    # productsList = []
    productFamilyList = []
    global buildingID
    global structID
    global locID
    global prodID

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # # Delete old individuals
    # if 'testingSet' in path:
    #     for individual in list(onto.individuals()):
    #         destroy_entity(individual)
    #
    # if dell:
    #     for individual in list(onto.individuals()):
    #         destroy_entity(individual)

    # Extract locations list from data graph --------------
    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

    q = 'SELECT DISTINCT ?Location WHERE { ?Structure :has_location ?Location .}'
    qresLoc = g.query(q)
    for rowLoc in qresLoc:
        locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')].replace('_', ' '))
    # print(locationsList)

    # # Extract products list from data graph --------------
    # q = 'SELECT DISTINCT ?Product WHERE { ?Location :contain ?Product .}'
    # qresProd = g.query(q)
    # for rowProd in qresProd:
    #     productsList.append(f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')].replace('_', ' '))
    # print('++++++++')
    # print(productsList)

    # Extract product families from product graph --------------
    gProd = rdflib.Graph()
    gProd.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")
    # qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Product . }'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Product' in productFamilyList:
        productFamilyList.remove('Product')
    # print(productFamilyList)

    qTypeL = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    qresTypeL = g.query(qTypeL)
    locationFamilyList = []
    for rowType in qresTypeL:
        locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in locationFamilyList:
        locationFamilyList.remove('Location')

    qTypeS = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    qresTypeS = g.query(qTypeS)
    structureFamilyList = []
    for rowType in qresTypeS:
        structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in structureFamilyList:
        structureFamilyList.remove('Structure')

    # locationFamilyList =[]
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Location' in locationFamilyList:
    #     locationFamilyList.remove('Location')
    #
    # structureFamilyList = []
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Structure' in structureFamilyList:
    #     structureFamilyList.remove('Structure')

    # Load the 'Diagnostic' --------------------------
    with open(projectFileName) as csv_file:
        sourceDocument_i = onto.SourceDocument(projectFileName[projectFileName.find('\\') + len('\\'):].replace(' ', '_'))
        sourceDocument_i.has_category.append('RAT')
        csv_reader = csv.reader(csv_file, delimiter=';')
        # line_count = 0
        batInfo = next(csv_reader)
        # buildingID += 1
        # codeBuilding = batInfo[0].replace(' ', '_') + '-' + batInfo[1].replace(' ', '_').replace('.', '_').replace('/', '_')
        # date = batInfo[9]
        # csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
        # # lineResult = ''
        # building_i = onto.Building('Bat_' + codeBuilding + '*' + str(buildingID))
        # building_i.extract_from.append(sourceDocument_i)
        # building_i.has_type.append(batInfo[8].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        # building_i.has_region.append(batInfo[17].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        # building_i.has_department_number.append(batInfo[18].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        # building_i.has_registration_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        # building_i.has_owner.append(batInfo[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        # building_i.has_address.append(batInfo[16].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        # if date != '':
        #     building_i.has_year.append(str2date(date))
        # # location_i = ontology.Location()
        # batInfo = next(csv_reader)
        # locProba = -1
        # structProba = -1
        # thisStructure = ''
        # structID += 1
        oldBuildingCode = ''
        for row in csv_reader:
            codeBuilding = row[0].replace(' ', '_') + '-' + row[1].replace(' ', '_').replace('.', '_').replace(
                '/', '_')
            date = row[9]
            csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
            # lineResult = ''
            if codeBuilding != oldBuildingCode:
                buildingID += 1
            building_i = onto.Building('Bat_' + codeBuilding + '*' + str(buildingID))
            if codeBuilding != oldBuildingCode:
                building_i.extract_from.append(sourceDocument_i)
                building_i.has_type.append(
                    row[8].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',',
                                                                                                               '_').replace(
                        '(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«',
                                                                                                                   '').replace(
                        '»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â',
                                                                                                                 'a').replace(
                        'ù', 'u').replace('û', 'u').replace('ô', 'o'))
                building_i.has_region.append(
                    row[17].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',',
                                                                                                                '_').replace(
                        '(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«',
                                                                                                                   '').replace(
                        '»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â',
                                                                                                                 'a').replace(
                        'ù', 'u').replace('û', 'u').replace('ô', 'o'))
                building_i.has_department_number.append(
                    row[18].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',',
                                                                                                                '_').replace(
                        '(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«',
                                                                                                                   '').replace(
                        '»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â',
                                                                                                                 'a').replace(
                        'ù', 'u').replace('û', 'u').replace('ô', 'o'))
                building_i.has_registration_number.append(
                    row[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',',
                                                                                                               '_').replace(
                        '(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«',
                                                                                                                   '').replace(
                        '»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â',
                                                                                                                 'a').replace(
                        'ù', 'u').replace('û', 'u').replace('ô', 'o'))
                building_i.has_owner.append(
                    row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',',
                                                                                                               '_').replace(
                        '(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«',
                                                                                                                   '').replace(
                        '»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â',
                                                                                                                 'a').replace(
                        'ù', 'u').replace('û', 'u').replace('ô', 'o'))
                building_i.has_address.append(
                    row[16].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',',
                                                                                                                '_').replace(
                        '(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«',
                                                                                                                   '').replace(
                        '»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â',
                                                                                                                 'a').replace(
                        'ù', 'u').replace('û', 'u').replace('ô', 'o'))
                if date != '':
                    building_i.has_year.append(str2date(date))
                # location_i = ontology.Location()
                # batInfo = next(csv_reader)
                locProba = -1
                structProba = -1
                thisStructure = ''
                structID += 1
            oldBuildingCode = codeBuilding
            # if line_count == 0:
            #     print(f'{row[0]}')
            #     building_i.has_type.append(f'{row[0]}')
            #     building_i.has_address.append(f'{row[5]}')
            #     building_i.has_year.append(date)
            # else:
            # foundLoc = False # if ther is an unknown problem decoment this - just try :)

            # structureType = onto.StructureType(f'{row[0]}'.lower().replace(' ', '_'))
            structureTypeName = f'{row[5]}'.lower().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('\"', '_')
            # structureType = re.sub('\d', '', f'{row[5]}'.lower().replace(' ', '').replace('-', '').replace('.', '')).replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            structureType = f'{row[5]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',',
                                                                                                          '').replace(
                '(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace(
                '»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â',
                                                                                                         'a').replace(
                'ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a').replace('\"', '_')
            # building_i.has_structure.append(structureType)
            # print(similar('colle', 'colle'))
            if structureType == '':
                structureType = 'Structure'
            else:
                upperStructure = 'Structure'
                similarStructure = []
                for f in structureFamilyList:
                    if f in structureType and f != structureType:
                        similarStructure.append(f)
                if similarStructure:
                    upperStructure = max(similarStructure, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (structureType, upperStructure))
            # Settlement
            if structProba != -1:
                exec("structure_i.has_structure_diagnostic.append(structProba)")
                # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")
            exec("structure_i = onto.%s(structureTypeName + '*' + str(structID))" % (structureType))
            print('-' + structureType)
            # structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_') + '*' + str(structID))
            # structID += 1
            if thisStructure != structureType:
                locID += 1
                thisStructure = structureType
            exec("building_i.has_structure.append(structure_i)")
            structProba = -1
            # structure_i.is_a.append(structureType)

            locationType = f'{row[6]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a').replace('\"', '_')
            if locationType == '':
                locationType = 'Location'
            else:
                upperLocation = 'Location'
                similarLocation = []
                for f in locationFamilyList:
                    if f in locationType and f != locationType:
                        similarLocation.append(f)
                if similarLocation:
                    upperLocation = max(similarLocation, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (locationType, upperLocation))
            # Settlement
            if locProba != -1:
                exec("location_i.has_location_diagnostic.append(locProba)")
                # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
            exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
            print('--' + locationType)
            # locID += 1
            prodID += 1
            csvProductVerif = []
            # location_i = onto.Location(foundLocName.replace(' ', '_') + '*' + str(locID))
            exec("structure_i.has_location.append(location_i)")
            locProba = -1
            noProduct = False

            productType = f'{row[4]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a').replace('\"', '_')
            if productType == '':
                productType = 'Product'
            else:
                upperProduct = 'Product'
                similarProduct = []
                for f in productFamilyList:
                    if f in productType and f != productType:
                        similarProduct.append(f)
                if similarProduct:
                    upperProduct = max(similarProduct, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (productType, upperProduct))
            # Settlement
            exec("product_i = onto.%s(productType + '_X*' + str(prodID))" % (productType))
            print('---' + productType)
            if structureType == 'Structure':
                strType = ''
            else:
                strType = structureType
            if locationType == 'Location':
                locType = ''
            else:
                locType = locationType
            if productType == 'Product':
                prodType = ''
            else:
                prodType = productType
            lineResult = codeBuilding + ';' + strType.replace('_', ' ') + ';' + locType.replace('_', ' ') + ';' + prodType.replace('_', ' ')
            # prodID += 1
            # product_i = onto.Product(foundProdName.replace(' ', '_'))
            # print('---------------------------------------------------------')

            # print(productType)

            # Diagnosis extraction
            diagnosis = -1
            foundFamily = False
            foundFamilyList = []
            foundFamilySim = 0
            foundFamilyName = ''

            # for f in productFamilyList:
            #     # print('ff::'+f)
            #     if f in productType or productType in f:
            #         # print('f:'+f)
            #         foundFamily = True
            #         foundFamilyList.append(f)

            # print(foundFamilyList)
            # if foundFamily:
            #     for fam in foundFamilyList:
            #         if similar(fam, productType) > foundFamilySim:
            #             foundFamilyName = fam
            #             foundFamilySim = similar(fam, productType)
                # print('+'+foundFamilyName)

            predictionFeatureID = 1
            predictionFeature = onto.PredictedCharacteristic(
                'predictedFeature*' + str(predictionFeatureID) + ':' + productType + '*' + str(prodID))
            exec('product_i.has_predicted_characteristic.append(predictionFeature)')

            calculatedFeatureID = 1
            calculatedFeature = onto.CalculatedCharacteristic(
                'calculatedFeature*' + str(calculatedFeatureID) + ':' + productType + '*' + str(prodID))
            exec('product_i.has_calculated_characteristic.append(calculatedFeature)')

            diagnosticFeatureID = 1
            diagnosticFeature = onto.DiagnosticCharacteristic(
                'diagnosticFeature*' + str(diagnosticFeatureID) + ':' + productType + '*' + str(prodID))
            diagnosis = int(f'{row[28]}')
                # print('proba : ' + str(probability))
                # print(productType + '--')
            if diagnosis != -1:
                # probabilityClass = probabilityClassCalculation(probability)
                # print('class : ' + str(probabilityClass))
                diagnosticFeature.has_diagnostic.append(diagnosis)
                # calculatedFeature.has_class.append(probabilityClass)

            exec('product_i.has_diagnostic_characteristic.append(diagnosticFeature)')
            diagnosticFeatureID += 1
            if locProba < diagnosis:
                locProba = diagnosis
                if structProba < locProba:
                    structProba = locProba

            exec("location_i.contain.append(product_i)")
            if not productType in csvProductVerif:
                # print(productType)
                # print(diagnosis)
                csvProductVerif.append(productType)
                if diagnosis != -1:
                    lineResult += ';' + str(diagnosis) + '\n'
                    csvFileResult.write(lineResult)
                else:
                    lineResult += ';Le diagnostic n\'est pas fait pour ce produit\n'
                    csvFileResult.write(lineResult)
            # if foundLoc:
            #     locID += 1
            # line_count += 1
        csvFileResult.close()


        if locProba != -1:
            exec("location_i.has_location_diagnostic.append(locProba)")
            # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
        if structProba != -1:
            exec("structure_i.has_structure_diagnostic.append(structProba)")
            # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")

        # prodID += 1

        # Save ontology settlement
        # onto.save(file="ONTOLOGY_SETTLEMENT\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")
        onto.save(file="ONTOLOGY_SETTLEMENT\\" + path + "\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")


        # # Delete old individuals
        # if 'testingSet' in path:
        #     for individual in list(onto.individuals()):
        #         destroy_entity(individual)


# AsbestosOntologySettlement_newRAT('RAT/RAT_decoded_test10000.csv', '')#*****************************************
# AsbestosOntologySettlement3('APPROVED_PROJECT_TYPE\ph2t.csv')
# AsbestosOntologySettlement_newRAT('RAT/RAT_decoded_test3000.csv', '')



def decodeRAT(ratFileName):
    refFileName = 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/RAT/Table_Ref_ORIGAMI.csv'
    with open(ratFileName) as csv_file:
        csvFileResult = open('RAT/RAT_decoded.csv', 'w')
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        # batInfo = next(csv_reader)
        for row in csv_reader:
            if line_count == 0:
                csvFileResult.write(f'{row[0]}' + ';' + f'{row[1]}' + ';' + f'{row[2]}' + ';' + f'{row[3]}' + ';' + f'{row[4]}' + ';' + f'{row[5]}' + ';' + f'{row[6]}' + ';' + f'{row[7]}' + ';' + f'{row[8]}' + ';' + f'{row[9]}' + ';' + f'{row[10]}' + ';' + f'{row[11]}' + ';' + f'{row[12]}' + ';' + f'{row[13]}' + ';' + f'{row[14]}' + ';' + f'{row[15]}' + ';' + f'{row[16]}' + ';' + f'{row[17]}' + ';' + f'{row[18]}' + ';' + f'{row[19]}' + ';' + f'{row[20]}' + ';' + f'{row[21]}' + ';' + f'{row[22]}' + ';' + f'{row[23]}' + ';' + f'{row[24]}' + ';' + f'{row[25]}' + ';' + f'{row[26]}' + ';' + f'{row[27]}' + ';' + f'{row[28]}' + '\n')
            else:
                lineResult = f'{row[0]}' + ';' f'{row[1]}' + ';' f'{row[2]}' + ';' f'{row[3]}'
                with open(refFileName) as ref_csv_file:
                    ref_csv_reader = csv.reader(ref_csv_file, delimiter=';')
                    for ref_row in ref_csv_reader:
                        if f'{row[4]}' == f'{ref_row[0]}':
                            lineResult += ';' + f'{ref_row[5]}' ';' + f'{ref_row[7]}' ';' + f'{ref_row[6]}' + ';' + f'{row[7]}' + ';' + f'{row[8]}' + ';' + f'{row[9]}' + ';' + f'{row[10]}' + ';' + f'{row[11]}' + ';' + f'{row[12]}' + ';' + f'{row[13]}' + ';' + f'{row[14]}' + ';' + f'{row[15]}' + ';' + f'{row[16]}' + ';' + f'{row[17]}' + ';' + f'{row[18]}' + ';' + f'{row[19]}' + ';' + f'{row[20]}' + ';' + f'{row[21]}' + ';' + f'{row[22]}' + ';' + f'{row[23]}' + ';' + f'{row[24]}' + ';' + f'{row[25]}' + ';' + f'{row[26]}' + ';' + f'{row[27]}' + ';' + f'{row[28]}' + '\n'
                            csvFileResult.write(lineResult)
                            break
            line_count += 1


# decodeRAT('C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/RAT/trainingSet.csv')


def AsbestosOntologySettlement(projectFileName):
    global termsList
    locationsList = []
    productsList = []
    productFamilyList = []
    global structID
    global locID
    global prodID

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # Extract locations list from data graph --------------
    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

    q = 'SELECT DISTINCT ?Location WHERE { ?Structure :has_location ?Location .}'
    qresLoc = g.query(q)
    for rowLoc in qresLoc:
        locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')].replace('_', ' '))
    # print(locationsList)

    # Extract products list from data graph --------------
    q = 'SELECT DISTINCT ?Product WHERE { ?Location :contain ?Product .}'
    qresProd = g.query(q)
    for rowProd in qresProd:
        productsList.append(f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')].replace('_', ' '))
    # print('++++++++')
    # print(productsList)

    # Extract product families from product graph --------------
    gProd = rdflib.Graph()
    gProd.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")
    qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # print(productFamilyList)

    # Load the 'Projet type homologué' --------------------------
    with open(projectFileName) as csv_file:
        sourceDocument_i = onto.SourceDocument(projectFileName[projectFileName.find('\\') + len('\\'):].replace(' ', '_'))
        sourceDocument_i.has_category.append('Projet_type_homologué')
        csv_reader = csv.reader(csv_file, delimiter=';')
        # line_count = 0
        batInfo = next(csv_reader)
        codeBuilding = batInfo[0] + '-' + batInfo[1].replace(' ', '_') + '-' + batInfo[2] + '-' + batInfo[3]
        date = batInfo[6]
        csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
        # lineResult = ''
        building_i = onto.Building('Bat_' + codeBuilding)
        building_i.extract_from.append(sourceDocument_i)
        building_i.has_type.append(batInfo[0])
        building_i.has_region.append(batInfo[1].replace(' ', '_'))
        building_i.has_department_number.append(batInfo[2])
        building_i.has_registration_number.append(batInfo[3])
        building_i.has_owner.append(batInfo[4])
        building_i.has_address.append(batInfo[5].replace(' ', '_'))
        building_i.has_year.append(str2date(date))
        # location_i = ontology.Location()
        locProba = -1
        structProba = -1
        for row in csv_reader:
            # if line_count == 0:
            #     print(f'{row[0]}')
            #     building_i.has_type.append(f'{row[0]}')
            #     building_i.has_address.append(f'{row[5]}')
            #     building_i.has_year.append(date)
            # else:
            # foundLoc = False # if ther is an unknown problem decoment this - just try :)

            # structureType = onto.StructureType(f'{row[0]}'.lower().replace(' ', '_'))
            structureType = f'{row[0]}'.lower().replace(' ', '_').replace('-', '_')
            # building_i.has_structure.append(structureType)

            # Enrichment
            with onto:
                exec("class %s(onto.Structure):\
                    pass" % (structureType))
            # Settlement
            if structProba != -1:
                exec("structure_i.has_structure_probability.append(structProba)")
                exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")
            exec("structure_i = onto.%s(structureType + '*' + str(structID))" % (structureType))
            # structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_') + '*' + str(structID))
            structID += 1
            locID += 1
            exec("building_i.has_structure.append(structure_i)")
            structProba = -1
            # structure_i.is_a.append(structureType)

            # Extract locations and products ----------------------------
            termsList = []
            terminologyExtraction(f'{row[1]}'.lower())
            noProduct = False
            for t in termsList:
                # print(termsList)
                # print(t)
                word_tokens = word_tokenize(t)
                for word in word_tokens:
                    if len(word) > 2:
                        if (word in ['sans', 'sauf']):
                            noProduct = True
                        foundLoc = False
                        foundLocList = []
                        foundLocSim = 0
                        foundLocName = ''
                        foundProd = False
                        foundProdList = []
                        foundProdSim = 0
                        foundProdName = ''
                        for l in locationsList:
                            if l in word or word in l:
                                foundLoc = True
                                foundLocList.append(l)
                        if foundLoc:
                            # print('loc')
                            for loc in foundLocList:
                                if loc in t:
                                    foundLocName = loc
                                    foundLocSim = 1
                                elif similar(loc, word) > foundLocSim:
                                    foundLocName = loc
                                    foundLocSim = similar(loc, word)
                            if foundLocName != 'néant':
                                # Enrichment
                                with onto:
                                    locationType = foundLocName.lower().replace(' ', '_').replace('-', '_')
                                    exec("class %s(onto.Location):\
                                        pass" % (locationType))
                                # Settlement
                                if locProba != -1:
                                    exec("location_i.has_location_probability.append(locProba)")
                                    exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
                                exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
                                print('---'+locationType)
                                # locID += 1
                                prodID += 1
                                csvProductVerif = []
                                # location_i = onto.Location(foundLocName.replace(' ', '_') + '*' + str(locID))
                                exec("structure_i.has_location.append(location_i)")
                                locProba = -1
                                noProduct = False
                        if not foundLoc and not noProduct:
                            # print(productsList)
                            for p in productFamilyList:
                            # for p in productsList:
                            #     print('*'+p)
                            #     print('**'+word)
                                if p in word or word in p:
                                    foundProd = True
                                    foundProdList.append(p)
                            if foundProd:
                                for prod in foundProdList:
                                    if prod in t:
                                        foundProdName = prod
                                        foundProdSim = 1
                                    elif similar(prod, word) > foundProdSim:
                                        foundProdName = prod
                                        foundProdSim = similar(prod, word)
                                productType = foundProdName.lower().replace(' ', '_').replace('-', '_')
                                # Enrichment
                                with onto:
                                    exec("class %s(onto.Product):\
                                        pass" % (productType))
                                # Settlement
                                exec("product_i = onto.%s(productType + '_X*' + str(prodID))" % (productType))
                                lineResult = codeBuilding + ';' + structureType.replace('_', ' ') + ';' + locationType.replace('_', ' ') + ';' + productType.replace('_', ' ')
                                # prodID += 1
                                # product_i = onto.Product(foundProdName.replace(' ', '_'))
                                # print('---------------------------------------------------------')

                                # print(productType)

                                # Probability calculation
                                probability = -1
                                foundFamily = False
                                foundFamilyList = []
                                foundFamilySim = 0
                                foundFamilyName = ''

                                for f in productFamilyList:
                                    # print('ff::'+f)
                                    if f in productType or productType in f:
                                        # print('f:'+f)
                                        foundFamily = True
                                        foundFamilyList.append(f)

                                # print(foundFamilyList)
                                if foundFamily:
                                    for fam in foundFamilyList:
                                        if similar(fam, productType) > foundFamilySim:
                                            foundFamilyName = fam
                                            foundFamilySim = similar(fam, productType)
                                    # print('+'+foundFamilyName)
                                    calculatedFeatureID = 1
                                    calculatedFeature = onto.CalculatedCharacteristic('calculatedFeature*' + str(calculatedFeatureID) + ':' + productType + '*' + str(prodID))
                                    calculatedFeature.has_calculation_year.append(str2date(date))
                                    probability = probabilityCalculation(foundFamilyName, date)
                                    # print('proba : ' + str(probability))
                                    # print(productType + '--')
                                    if probability != -1:
                                        probabilityClass = probabilityClassCalculation(probability)
                                        # print('class : ' + str(probabilityClass))
                                        calculatedFeature.has_probability.append(probability)
                                        calculatedFeature.has_class.append(probabilityClass)

                                    exec('product_i.has_calculated_characteristic.append(calculatedFeature)')
                                    calculatedFeatureID += 1
                                    if locProba < probability:
                                        locProba = probability
                                        if structProba < locProba:
                                            structProba = locProba

                                exec("location_i.contain.append(product_i)")
                                if not productType in csvProductVerif:
                                    print(productType)
                                    csvProductVerif.append(productType)
                                    if probability != -1:
                                        lineResult += ';' + 'Classe ' + str(probabilityClass) + ';' + str(
                                            probability) + '\n'
                                        csvFileResult.write(lineResult)
                                    else:
                                        lineResult += ';Produit non mentioné dans les ressources externes;\n'
                                        csvFileResult.write(lineResult)
                # if foundLoc:
                #     locID += 1
            # line_count += 1
        csvFileResult.close()

        if locProba != -1:
            exec("location_i.has_location_probability.append(locProba)")
            exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
        if structProba != -1:
            exec("structure_i.has_structure_probability.append(structProba)")
            exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")

        # prodID += 1

        # Save ontology settlement
        onto.save(file="ONTOLOGY_SETTLEMENT\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")

        # # Delete old individuals
        # for individual in list(onto.individuals()):
        #     destroy_entity(individual)

    # # query test ---------------------------------------------------------------------------
    # q = 'SELECT ?Building ?Structure WHERE { ?Building :has_structure ?Structure .}'
    #
    # # q = prepareQuery(
    # #     'SELECT ?Building ?Structure WHERE { ?Building rdf:has_structure ?Structure .}',
    # #     initNs={"rdf": RDF})
    # # q = prepareQuery(
    # #     'SELECT ?Building ?Structure WHERE { ?Building foaf:has_structure ?Structure .}',
    # #     initNs={"foaf": FOAF})
    #
    # g = rdflib.Graph()
    # g.load("ASBESTOS_ONTOLOGY_SETTLEMENT.owl")
    #
    # qres = g.query(q)
    # print("+")
    # for row in qres:
    #     print(row)
    # print("-")
    # -------------------------------------------------------------------------------

    # ontolo = get_ontology("file://peuplement.owl").load()
    # ontolo.load()
    # sync_reasoner(ontolo)  # reasoner is started and synchronized here
    # # graph = rdflib.Graph()
    # graph = ontolo.as_rdflib_graph()
    # query = "SELECT ?x"
    # # query is being run
    # resultsList = graph.query(query)
    # # creating json object
    # response = []
    # for item in resultsList:
    #     x = str(item['x'].toPython())
    #     x = re.sub(r'.*#', "", x)
    #
    #     response.append({'x': x})
    #
    # print(response)  # just to show the output



# AsbestosOntologySettlement('APPROVED_PROJECT_TYPE\ph1.csv')


def baseLine1():  # par année
    fileName = "HybridApproachResults\\third1\\LeaveOneThirdOutTestsThird1\\data\\0\\learningSet\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    # Load the KB -----------------------------------------
    k_onto = get_ontology("file://" + fileName).load()
    iri = k_onto.base_iri
    k = rdflib.Graph()
    k.load(fileName)

    print("Année;tp;tn;fp;fn;precisionP;rappelP;FmesureP;precisionN;rappelN;FmesureN;FmesureAvg;accuracy")

    for year in range(1946, 1997):
        y = str(year)
        tp = 0
        tn = 0
        fp = 0
        fn = 0

        tpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year <= ?y) }'
        tpqres = k.query(tpq, initBindings={'d': rdflib.term.Literal(1), 'y': rdflib.term.Literal(y + '-01-01T00:00:00',
                                                                              datatype=rdflib.term.URIRef(
                                                                                  'http://www.w3.org/2001/XMLSchema#dateTime'))})
        tp = len(tpqres)

        tnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year > ?y) }'
        tnqres = k.query(tnq, initBindings={'d': rdflib.term.Literal(0), 'y': rdflib.term.Literal(y + '-01-01T00:00:00',
                                                                                                  datatype=rdflib.term.URIRef(
                                                                                                      'http://www.w3.org/2001/XMLSchema#dateTime'))})
        tn = len(tnqres)

        fpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year <= ?y) }'
        fpqres = k.query(fpq, initBindings={'d': rdflib.term.Literal(0), 'y': rdflib.term.Literal(y + '-01-01T00:00:00',
                                                                                                  datatype=rdflib.term.URIRef(
                                                                                                      'http://www.w3.org/2001/XMLSchema#dateTime'))})
        fp = len(fpqres)

        fnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year . FILTER(?Year > ?y) }'
        fnqres = k.query(fnq, initBindings={'d': rdflib.term.Literal(1), 'y': rdflib.term.Literal(y + '-01-01T00:00:00',
                                                                                                  datatype=rdflib.term.URIRef(
                                                                                                      'http://www.w3.org/2001/XMLSchema#dateTime'))})
        fn = len(fnqres)

        if tp + fp == 0:
            precisionP = 0
        else:
            precisionP = tp / (tp + fp)
        if tp + fn == 0:
            rappelP = 0
        else:
            rappelP = tp / (tp + fn)
        if rappelP == 0 or precisionP == 0:
            FmesureP = 0
        else:
            FmesureP = 2 * (precisionP * rappelP) / (precisionP + rappelP)

        if tn + fn == 0:
            precisionN = 0
        else:
            precisionN = tn / (tn + fn)
        if tn + fp == 0:
            rappelN = 0
        else:
            rappelN = tn / (tn + fp)
        if rappelN == 0 or precisionN == 0:
            FmesureN = 0
        else:
            FmesureN = 2 * (precisionN * rappelN) / (precisionN + rappelN)

        FmesureAvg = (FmesureP + FmesureN) / 2

        accuracy = (tp + tn) / (tp + fp + tn + fn)

        print(y, ";", tp, ";", tn, ";", fp, ";", fn, ";", precisionP, ";", rappelP, ";", FmesureP, ";", precisionN, ";", rappelN, ";", FmesureN, ";", FmesureAvg, ";", accuracy)


# baseLine1()


def baseLine2():  # par classe
    fileNameL = "HybridApproachResults\\third1\\LeaveOneThirdOutTestsThird1\\data\\0\\learningSet\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    # Load the KB -----------------------------------------
    kL = rdflib.Graph()
    kL.load(fileNameL)
    ontoL = get_ontology("file://" + fileNameL).load()
    iriL = ontoL.base_iri

    fileNameT = "HybridApproachResults\\third1\\LeaveOneThirdOutTestsThird1\\data\\0\\testingSet\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    # Load the KB -----------------------------------------
    kT = rdflib.Graph()
    kT.load(fileNameT)
    ontoT = get_ontology("file://" + fileNameT).load()
    iriT = ontoT.base_iri

    # Extract product types from the onto --------------
    productFamilyList = []
    gProd = rdflib.Graph()
    gProd.load("data3000\ASBESTOS_ONTOLOGY_SETTLEMENT.owl")
    # qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Product . }'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Product' in productFamilyList:
        productFamilyList.remove('Product')

    tp = 0
    tn = 0
    fp = 0
    fn = 0
    nbrClassePos = 0
    nbrClasseNeg = 0

    print(len(productFamilyList))

    for p in productFamilyList:
        nbrPq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product rdf:type ?p}'
        nbrPqres = kL.query(nbrPq, initBindings={'p': rdflib.term.URIRef(iriL + p)})
        nbrP = len(nbrPqres)

        if nbrP > 0:
            tpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Product rdf:type ?p}'

            tp0 = 0
            tpqres = kL.query(tpq, initBindings={'d': rdflib.term.Literal(1), 'p': rdflib.term.URIRef(iriL + p)})
            tp1 = len(tpqres)

            tnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Product rdf:type ?p}'
            tnqres = kL.query(tnq, initBindings={'d': rdflib.term.Literal(0), 'p': rdflib.term.URIRef(iriL + p)})
            tn0 = len(tnqres)

            tn1 = 0

            fpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Product rdf:type ?p}'

            fp0 = 0
            fpqres = kL.query(fpq, initBindings={'d': rdflib.term.Literal(0), 'p': rdflib.term.URIRef(iriL + p)})
            fp1 = len(fpqres)

            fnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . ?Product rdf:type ?p}'
            fnqres = kL.query(fnq, initBindings={'d': rdflib.term.Literal(1), 'p': rdflib.term.URIRef(iriL + p)})
            fn0 = len(fnqres)

            fn1 = 0

            accuracy0 = (tp0 + tn0) / (tp0 + fp0 + tn0 + fn0)

            accuracy1 = (tp1 + tn1) / (tp1 + fp1 + tn1 + fn1)

            if accuracy0 > accuracy1:
                nbrClasseNeg += 1

                tp += 0
                tnqres = kT.query(tnq, initBindings={'d': rdflib.term.Literal(0), 'p': rdflib.term.URIRef(iriT + p)})

                tn += len(tnqres)

                fp += 0

                fnqres = kT.query(fnq, initBindings={'d': rdflib.term.Literal(1), 'p': rdflib.term.URIRef(iriT + p)})
                fn += len(fnqres)

            else:
                nbrClassePos += 1

                tpqres = kT.query(tpq, initBindings={'d': rdflib.term.Literal(1), 'p': rdflib.term.URIRef(iriT + p)})
                tp += len(tpqres)

                tn += 0

                fpqres = kT.query(fpq, initBindings={'d': rdflib.term.Literal(0), 'p': rdflib.term.URIRef(iriT + p)})
                fp += len(fpqres)

                fn += 0

    if tp + fp == 0:
        precisionP = 0
    else:
        precisionP = tp / (tp + fp)
    if tp + fn == 0:
        rappelP = 0
    else:
        rappelP = tp / (tp + fn)
    if rappelP == 0 or precisionP == 0:
        FmesureP = 0
    else:
        FmesureP = 2 * (precisionP * rappelP) / (precisionP + rappelP)

    if tn + fn == 0:
        precisionN = 0
    else:
        precisionN = tn / (tn + fn)
    if tn + fp == 0:
        rappelN = 0
    else:
        rappelN = tn / (tn + fp)
    if rappelN == 0 or precisionN == 0:
        FmesureN = 0
    else:
        FmesureN = 2 * (precisionN * rappelN) / (precisionN + rappelN)

    FmesureAvg = (FmesureP + FmesureN) / 2

    accuracy = (tp + tn) / (tp + fp + tn + fn)

    print("nbrClassePos:", nbrClassePos)
    print("nbrClasseNeg:", nbrClasseNeg)

    print("Année;tp;tn;fp;fn;precisionP;rappelP;FmesureP;precisionN;rappelN;FmesureN;FmesureAvg;accuracy")
    print(tp, ";", tn, ";", fp, ";", fn, ";", precisionP, ";", rappelP, ";", FmesureP, ";", precisionN, ";", rappelN, ";", FmesureN, ";", FmesureAvg, ";", accuracy)


# baseLine2()


def HybridApproachApply():
    global termsList
    locationsList = []
    # productsList = []
    productFamilyList = []
    global buildingID
    global structID
    global locID
    global prodID

    # Load the ontology -----------------------------------------
    fileName = "ONTOLOGY_SETTLEMENT\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    onto = get_ontology("file://" + fileName).load()
    k = rdflib.Graph()
    k.load(fileName)
    iri = onto.base_iri

    # Extract locations list from data graph --------------
    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

    q = 'SELECT DISTINCT ?Location WHERE { ?Structure :has_location ?Location .}'
    qresLoc = g.query(q)
    for rowLoc in qresLoc:
        locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')].replace('_', ' '))
    # print(locationsList)

    # # Extract products list from data graph --------------
    # q = 'SELECT DISTINCT ?Product WHERE { ?Location :contain ?Product .}'
    # qresProd = g.query(q)
    # for rowProd in qresProd:
    #     productsList.append(f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')].replace('_', ' '))
    # print('++++++++')
    # print(productsList)

    # Extract product families from product graph --------------
    gProd = rdflib.Graph()
    gProd.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")
    # qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Product . }'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Product' in productFamilyList:
        productFamilyList.remove('Product')
    # print(productFamilyList)

    # # Load the 'Projet type homologué' --------------------------
    # with open(projectFileName) as csv_file:
    #     sourceDocument_i = onto.SourceDocument(projectFileName[projectFileName.find('\\') + len('\\'):].replace(' ', '_'))
    #     sourceDocument_i.has_category.append('Projet_type_homologué')
    #     csv_reader = csv.reader(csv_file, delimiter=';')
    #     # line_count = 0
    #     batInfo = next(csv_reader)
    #     buildingID += 1
    #     codeBuilding = batInfo[0] + '-' + batInfo[1].replace(' ', '_') + '-' + batInfo[2] + '-' + batInfo[3]
    #     date = batInfo[6]
    #     csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
    #     # lineResult = ''
    #     building_i = onto.Building('Bat_' + codeBuilding + '*' + str(buildingID))
    #     building_i.extract_from.append(sourceDocument_i)
    #     building_i.has_type.append(batInfo[0])
    #     building_i.has_region.append(batInfo[1].replace(' ', '_'))
    #     building_i.has_department_number.append(batInfo[2])
    #     building_i.has_registration_number.append(batInfo[3])
    #     building_i.has_owner.append(batInfo[4])
    #     building_i.has_address.append(batInfo[5].replace(' ', '_'))
    #     building_i.has_year.append(str2date(date))
    #     # location_i = ontology.Location()
    #     locProba = -1
    #     structProba = -1
    #     thisStructure = ''
    #     structID += 1
    #     for row in csv_reader:
    #         # if line_count == 0:
    #         #     print(f'{row[0]}')
    #         #     building_i.has_type.append(f'{row[0]}')
    #         #     building_i.has_address.append(f'{row[5]}')
    #         #     building_i.has_year.append(date)
    #         # else:
    #         # foundLoc = False # if ther is an unknown problem decoment this - just try :)
    #
    #         # structureType = onto.StructureType(f'{row[0]}'.lower().replace(' ', '_'))
    #         structureType = f'{row[0]}'.lower().replace(' ', '_').replace('-', '_')
    #         # building_i.has_structure.append(structureType)
    #         # print(similar('colle', 'colle'))
    #         if structureType == '':
    #             structureType = 'Structure'
    #         else:
    #             # Enrichment
    #             with onto:
    #                 exec("class %s(onto.Structure):\
    #                     pass" % (structureType))
    #         # Settlement
    #         if structProba != -1:
    #             exec("structure_i.has_structure_probability.append(structProba)")
    #             exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")
    #         exec("structure_i = onto.%s(structureType + '*' + str(structID))" % (structureType))
    #         print('-' + structureType)
    #         # structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_') + '*' + str(structID))
    #         # structID += 1
    #         # locID += 1
    #         if thisStructure != structureType:
    #             locID += 1
    #             thisStructure = structureType
    #         exec("building_i.has_structure.append(structure_i)")
    #         structProba = -1
    #         # structure_i.is_a.append(structureType)
    #
    #         locationType = f'{row[1]}'.lower().replace(' ', '_').replace('-', '_')
    #         if locationType == '':
    #             locationType = 'Location'
    #         else:
    #             # Enrichment
    #             with onto:
    #                 exec("class %s(onto.Location):\
    #                     pass" % (locationType))
    #         # Settlement
    #         if locProba != -1:
    #             exec("location_i.has_location_probability.append(locProba)")
    #             exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
    #         exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
    #         print('--' + locationType)
    #         # locID += 1
    #         prodID += 1
    #         csvProductVerif = []
    #         # location_i = onto.Location(foundLocName.replace(' ', '_') + '*' + str(locID))
    #         exec("structure_i.has_location.append(location_i)")
    #         locProba = -1
    #         noProduct = False

    # productType = f'{row[2]}'.lower().replace(' ', '_').replace('-', '_')
    # if productType == '':
    #     productType = 'Product'
    # else:
    #     # Enrichment
    #     with onto:
    #         exec("class %s(onto.Product):\
    #             pass" % (productType))
    # # Settlement
    # exec("product_i = onto.%s(productType + '_X*' + str(prodID))" % (productType))
    # print('---' + productType)
    # if structureType == 'Structure':
    #     strType = ''
    # else:
    #     strType = structureType
    # if locationType == 'Location':
    #     locType = ''
    # else:
    #     locType = locationType
    # if productType == 'Product':
    #     prodType = ''
    # else:
    #     prodType = productType
    # lineResult = codeBuilding + ';' + strType.replace('_', ' ') + ';' + locType.replace('_', ' ') + ';' + prodType.replace('_', ' ')
    # prodID += 1
    # product_i = onto.Product(foundProdName.replace(' ', '_'))
    # print('---------------------------------------------------------')

    # print(productType)

    # print(iri)
    for product_i in onto.Product.instances():
        print(product_i.name)
        productName = str(product_i.name)
        productType = product_i.name[:product_i.name.find('_X*')]
        print(productType)
        qDate = 'SELECT ?Year WHERE { ?Location :contain ?Product . ?Structure :has_location ?Location . ?Building :has_structure ?Structure . ?Building :has_year ?Year .}'
        qDateqres = k.query(qDate, initBindings={'Product': rdflib.term.URIRef(iri + productName)})
        for rowDate in qDateqres:
            date = f'{rowDate}'[f'{rowDate}'.find('(\'') + len('(\''):f'{rowDate}'.find('-')]

        # print(qDateqres)
        # date = qDateqres
        print(date)

        cfQ = 'SELECT ?calculatedFeature WHERE { ?Product :has_calculated_characteristic ?calculatedFeature .}'
        cfQqres = k.query(cfQ, initBindings={'Product': rdflib.term.URIRef(iri + productName)})
        for rowcalculatedFeature in cfQqres:
            # print(rowcalculatedFeature)
            calculatedFeatureName = f'{rowcalculatedFeature}'[f'{rowcalculatedFeature}'.find('#') + len('#'):f'{rowcalculatedFeature}'.rfind('\'')]


        # print('/////////', calculatedFeatureName)
        for calFeat in onto.CalculatedCharacteristic.instances():
            # print('-----name:', calFeat.name)
            if calFeat.name == calculatedFeatureName:
                calculatedFeature = calFeat
                # print('*******************************', calculatedFeature.name)



        # Probability calculation
        probability = -1
        foundFamily = False
        foundFamilyList = []
        foundFamilySim = 0
        foundFamilyName = ''

        for f in productFamilyList:
            # print('ff::'+f)
            if f in productType or productType in f:
                # print('f:'+f)
                foundFamily = True
                foundFamilyList.append(f)

        # print(foundFamilyList)
        if foundFamily:
            for fam in foundFamilyList:
                if similar(fam, productType) > foundFamilySim:
                    foundFamilyName = fam
                    foundFamilySim = similar(fam, productType)
            # print('+'+foundFamilyName)

            # calculatedFeatureID = 1
            # calculatedFeature = onto.CalculatedCharacteristic(
            #     'calculatedFeature*' + str(calculatedFeatureID) + ':' + productType + '*' + product_i.name[
            #                                                                                 product_i.name.find(
            #                                                                                     '_X*') + len('_X*'):], namespace = onto)

            # calculatedFeature.has_calculation_year.append(str2date(date))
            probability = probabilityCalculation(k, iri, foundFamilyName, date, productType)
            # probability = 0
            print('proba : ' + str(probability))
            # print(productType + '--')
            if probability != -1:
                probabilityClass = probabilityClassCalculation(probability)#-----------------------------
                print('class : ' + str(probabilityClass))
                exec('calculatedFeature.has_probability.append(probability)')
                exec('calculatedFeature.has_class.append(probabilityClass)')#-----------------------------

            # exec('product_i.has_calculated_characteristic.append(calculatedFeature)')
            # product_i.has_calculated_characteristic.append(calculatedFeature)
            # calculatedFeatureID += 1
        #     if locProba < probability:
        #         locProba = probability
        #         if structProba < locProba:
        #             structProba = locProba
        #
        # exec("location_i.contain.append(product_i)")
        # if not productType in csvProductVerif:
        #     # print(productType)
        #     csvProductVerif.append(productType)
        #     if probability != -1:
        #         lineResult += ';' + 'Classe ' + str(probabilityClass) + ';' + str(
        #             probability) + '\n'
        #         csvFileResult.write(lineResult)
        #     else:
        #         lineResult += ';Produit non mentioné dans les ressources externes;\n'
        #         csvFileResult.write(lineResult)
        # # if foundLoc:
        # #     locID += 1
        # # line_count += 1
        # csvFileResult.close()


        # if locProba != -1:
        #     exec("location_i.has_location_probability.append(locProba)")
        #     exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
        # if structProba != -1:
        #     exec("structure_i.has_structure_probability.append(structProba)")
        #     exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")

        # prodID += 1

        # Save ontology settlement
    # onto.save(file="HybridApproachResults\\third1\\LeaveOneThirdOutTestsThird1\\data\\0\\testingSet\\ASBESTOS_ONTOLOGY_SETTLEMENT_RESULT.owl", format="rdfxml")
    onto.save(file="ONTOLOGY_SETTLEMENT\\HybridApproachResults\\ASBESTOS_ONTOLOGY_SETTLEMENT_RESULT.owl", format="rdfxml")


# HybridApproachApply()#13:17 17:07


def countIndividual():#compter le nombre de positifs loc, struc et bat
    fileName = "data3000/ASBESTOS_ONTOLOGY_SETTLEMENT.owl"
    k_onto_test = get_ontology("file://" + fileName).load()
    iri = k_onto_test.base_iri
    kt = rdflib.Graph()
    kt.load(fileName)

    positiveP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    positivePqres = kt.query(positiveP, initBindings={'d': rdflib.term.Literal(1)})
    positivePro = len(positivePqres)

    negativeP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    negativePqres = kt.query(negativeP, initBindings={'d': rdflib.term.Literal(0)})
    negativePro = len(negativePqres)

    positiveL = 'SELECT DISTINCT ?Location WHERE { ?Location :contain ?Product . ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    positiveLqres = kt.query(positiveL, initBindings={'d': rdflib.term.Literal(1)})
    positiveLoc = len(positiveLqres)

    negativeL = 'SELECT DISTINCT ?Location WHERE { ?Location :contain ?Product . ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    negativeLqres = kt.query(negativeL, initBindings={'d': rdflib.term.Literal(0)})
    negativeLoc = len(negativeLqres)

    positiveS = 'SELECT DISTINCT ?Structure WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    positiveSqres = kt.query(positiveS, initBindings={'d': rdflib.term.Literal(1)})
    positiveStr = len(positiveSqres)

    negativeS = 'SELECT DISTINCT ?Structure WHERE { ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    negativeSqres = kt.query(negativeS, initBindings={'d': rdflib.term.Literal(0)})
    negativeStr = len(negativeSqres)

    positiveB = 'SELECT DISTINCT ?Building WHERE { ?Building :has_structure ?Structure . ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    positiveBqres = kt.query(positiveB, initBindings={'d': rdflib.term.Literal(1)})
    positiveBui = len(positiveBqres)

    negativeB = 'SELECT DISTINCT ?Building WHERE { ?Building :has_structure ?Structure . ?Structure :has_location ?Location . ?Location :contain ?Product . ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    negativeBqres = kt.query(negativeB, initBindings={'d': rdflib.term.Literal(0)})
    negativeBui = len(negativeBqres)

    print("posP:", positivePro)
    print("negP:", negativePro)
    print("posL:", positiveLoc)
    print("negL:", negativeLoc)
    print("posS:", positiveStr)
    print("negS:", negativeStr)
    print("posB:", positiveBui)
    print("negB:", negativeBui)

# countIndividual()


def countPositiveNegativeIndividualHybrid(kt, iri, threshold):
    positiveNegativeP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_calculated_characteristic ?Prediction . ?Prediction :has_probability ?pc . ?Prediction :has_probability ?pc2 . FILTER(?pc >= ?threshold && ?pc2 < ?threshold) . }'
    positiveNegativePqres = kt.query(positiveNegativeP, initBindings={'threshold': rdflib.term.Literal(threshold)})

    positiveNegativePro = len(positiveNegativePqres)

    positiveP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    positivePqres = kt.query(positiveP, initBindings={'d': rdflib.term.Literal(1)})

    positivePro = len(positivePqres)

    negativeP = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Diagnistic :has_diagnostic ?d . }'
    negativePqres = kt.query(negativeP, initBindings={'d': rdflib.term.Literal(0)})

    negativePro = len(negativePqres)

    tpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_probability ?pc . FILTER(?pc >= ?threshold) . }'
    tpqres = kt.query(tpq, initBindings={'d': rdflib.term.Literal(1), 'threshold': rdflib.term.Literal(threshold)})

    # tpnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    # tpnqres = kt.query(tpnq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(0)})

    tp = len(tpqres)
    # tp = len(tpqres) - len(tpnqres)

    tnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_probability ?pc . FILTER(?pc < ?threshold) . }'
    tnqres = kt.query(tnq, initBindings={'d': rdflib.term.Literal(0), 'threshold': rdflib.term.Literal(threshold)})

    # tnpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_probability ?pc . ?Prediction :has_probability ?pc2 . }'
    # tnpqres = kt.query(tnpq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(2)})

    tn = len(tnqres)# - len(tnpqres)

    fpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_probability ?pc . FILTER(?pc >= ?threshold) . }'
    fpqres = kt.query(fpq, initBindings={'d': rdflib.term.Literal(0), 'threshold': rdflib.term.Literal(threshold)})

    # fpnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_predicted_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_predicted_class ?pc . ?Prediction :has_predicted_class ?pc2 . }'
    # fpnqres = kt.query(fpnq, initBindings={'d': rdflib.term.Literal(0), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(0)})

    fp = len(fpqres)
    # fp = len(fpqres) - len(fpnqres)

    fnq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_probability ?pc . FILTER(?pc < ?threshold) . }'
    fnqres = kt.query(fnq, initBindings={'d': rdflib.term.Literal(1), 'threshold': rdflib.term.Literal(threshold)})

    # fnpq = 'SELECT DISTINCT ?Product WHERE { ?Product :has_diagnostic_characteristic ?Diagnistic . ?Product :has_calculated_characteristic ?Prediction . ?Diagnistic :has_diagnostic ?d . ?Prediction :has_class ?pc . ?Prediction :has_class ?pc2 . }'
    # fnpqres = kt.query(fnpq, initBindings={'d': rdflib.term.Literal(1), 'pc': rdflib.term.Literal(1), 'pc2': rdflib.term.Literal(2)})

    fn = len(fnqres)# - len(fnpqres)

    return [tp, tn, fp, fn, positivePro, negativePro, positiveNegativePro, tpqres, tnqres, fpqres, fnqres, positivePqres, negativePqres, positiveNegativePqres]



def testResultHybridBestthreshold():
    print('+++++++-----------------------------------------------------------------------------------')
    # print(i)
    fileName = "HybridApproachResults/third1/LeaveOneThirdOutTestsThird1/data/0/learningSet/ASBESTOS_ONTOLOGY_SETTLEMENT_RESULT.owl"
    # #print(fileName)
    k_onto_test = get_ontology("file://" + fileName).load()
    iri = k_onto_test.base_iri
    # #print('-')
    kt = rdflib.Graph()
    kt.load(fileName)
    # #print('-')
    for threshold in np.arange(0.3, 0.5, 0.01):
        tp = 0
        tn = 0
        fp = 0
        fn = 0
        positivePro = 0
        negativePro = 0
        positiveNegativePro = 0
        print(str(threshold), '******************************')
        result = countPositiveNegativeIndividualHybrid(kt, iri, threshold)
        tp += result[0]
        tn += result[1]
        fp += result[2]
        fn += result[3]
        positivePro += result[4]
        negativePro += result[5]
        positiveNegativePro += result[6]
        # print('PosNeglist product list:')
        PosNeglist = set()
        for row in result[13]:
            # print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
            PosNeglist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        # print(len(PosNeglist))
        # print('TP product list:')
        TPlist = set()
        for row in result[7]:
            # print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
            TPlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        # print(len(TPlist))
        # print(result[7])
        # print('TN product list:')
        TNlist = set()
        for row in result[8]:
            # print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
            TNlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        # print(len(TNlist))
        # print(result[8])
        # print('FP product list:')
        FPlist = set()
        for row in result[9]:
            # print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
            FPlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        # print(len(FPlist))
        # print(result[9])
        # print('FN product list:')
        FNlist = set()
        for row in result[10]:
            # print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
            FNlist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        # print(len(FNlist))
        # print(result[10])
        # print('Positive product list:')
        Positivelist = set()
        for row in result[11]:
            # print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
            Positivelist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        # print(len(Positivelist))
        # print(result[11])
        # print('Negalive product list:')
        Negativelist = set()
        for row in result[12]:
            # print(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
            Negativelist.add(f'{row}'[f'{row}'.find('#') + len('#'):f'{row}'.rfind('\'')])
        # print(len(Negativelist))
        # print(result[12])
        # print('UP product list:')
        UPlist = Positivelist.difference(TPlist.union(FNlist))
        # print(len(TPlist.union(FNlist)))
        # print(UPlist)
        # print(len(UPlist))
        # for row in UPlist:
        #     print(row)
        # print(list(set(result[11]).difference(set(result[7] + result[10]))))
        # print('UN product list:')
        UNlist = Negativelist.difference(TNlist.union(FPlist))
        # print(len(TNlist.union(FPlist)))
        # print(UNlist)
        # print(len(UNlist))
        # for row in UNlist:
        #     print(row)
        # print(list(set(result[12]).difference(set(result[8] + result[9]))))

        # # Delete old individuals
        # for individual in list(k_onto_test.individuals()):
        #     destroy_entity(individual)

        # up = positivePro - (tp + fn)
        # un = negativePro - (tn + fp)
        up = len(UPlist)
        un = len(UNlist)


        print("positveNegative =", positiveNegativePro)
        print("positve =", positivePro)
        print("negative =", negativePro)
        print("tp =", tp)
        print("tn =", tn)
        print("fp =", fp)
        print("fn =", fn)
        print("up =", up)
        print("un =", un)

        if tp + fp == 0:
            precisionP = 0
        else:
            precisionP = tp / (tp + fp)
        if tp + fn + up == 0:
            rappelP = 0
        else:
            rappelP = tp / (tp + fn + up)
        if rappelP == 0 or precisionP == 0:
            FmesureP = 0
        else:
            FmesureP = 2 * (precisionP * rappelP) / (precisionP + rappelP)

        if tn + fn == 0:
            precisionN = 0
        else:
            precisionN = tn / (tn + fn)
        if tn + fp + un == 0:
            rappelN = 0
        else:
            rappelN = tn / (tn + fp + un)
        if rappelN == 0 or precisionN == 0:
            FmesureN = 0
        else:
            FmesureN = 2 * (precisionN * rappelN) / (precisionN + rappelN)

        # accuracy = (tp + tn) / (tp + fp + up + tn + fn + un)
        accuracy = (tp + tn) / (tp + fp + tn + fn)

        FmesureAvrg = (FmesureP + FmesureN) / 2

        Coverage = (tp + fp + up + tn) / (tp + fp + up + tn + fn + un)

        print('precisionP =', precisionP)
        print('rappelP =', rappelP)
        print('FmesureP =', FmesureP)
        print('precisionN =', precisionN)
        print('rappelN =', rappelN)
        print('FmesureN =', FmesureN)
        print('FmesureAvrg =', FmesureAvrg)
        print('accuracy =', accuracy)
        print('Coverage =', Coverage)


# testResultHybridBestthreshold()


def AsbestosOntologySettlement2(projectFileName):#the new format of the APPROVED_PROJECT_TYPE
    global termsList
    locationsList = []
    # productsList = []
    productFamilyList = []
    global buildingID
    global structID
    global locID
    global prodID

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # Extract locations list from data graph --------------
    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

    q = 'SELECT DISTINCT ?Location WHERE { ?Structure :has_location ?Location .}'
    qresLoc = g.query(q)
    for rowLoc in qresLoc:
        locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')].replace('_', ' '))
    # print(locationsList)

    # # Extract products list from data graph --------------
    # q = 'SELECT DISTINCT ?Product WHERE { ?Location :contain ?Product .}'
    # qresProd = g.query(q)
    # for rowProd in qresProd:
    #     productsList.append(f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')].replace('_', ' '))
    # print('++++++++')
    # print(productsList)

    # Extract product families from product graph --------------
    gProd = rdflib.Graph()
    gProd.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")
    # qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Product . }'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Product' in productFamilyList:
        productFamilyList.remove('Product')
    # print(productFamilyList)

    # locationFamilyList =[]
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Location' in locationFamilyList:
    #     locationFamilyList.remove('Location')
    #
    # structureFamilyList = []
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Structure' in structureFamilyList:
    #     structureFamilyList.remove('Structure')

    # Load the 'Projet type homologué' --------------------------
    with open(projectFileName) as csv_file:
        sourceDocument_i = onto.SourceDocument(projectFileName[projectFileName.find('\\') + len('\\'):].replace(' ', '_'))
        sourceDocument_i.has_category.append('Projet_type_homologué')
        csv_reader = csv.reader(csv_file, delimiter=';')
        # line_count = 0
        batInfo = next(csv_reader)
        buildingID += 1
        codeBuilding = batInfo[0] + '-' + batInfo[1].replace(' ', '_') + '-' + batInfo[2] + '-' + batInfo[3]
        date = batInfo[6]
        csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
        # lineResult = ''
        building_i = onto.Building('Bat_' + codeBuilding + '*' + str(buildingID))
        building_i.extract_from.append(sourceDocument_i)
        building_i.has_type.append(batInfo[0])
        building_i.has_region.append(batInfo[1].replace(' ', '_'))
        building_i.has_department_number.append(batInfo[2])
        building_i.has_registration_number.append(batInfo[3])
        building_i.has_owner.append(batInfo[4])
        building_i.has_address.append(batInfo[5].replace(' ', '_'))
        building_i.has_year.append(str2date(date))
        # location_i = ontology.Location()
        locProba = -1
        structProba = -1
        thisStructure = ''
        structID += 1
        for row in csv_reader:
            # if line_count == 0:
            #     print(f'{row[0]}')
            #     building_i.has_type.append(f'{row[0]}')
            #     building_i.has_address.append(f'{row[5]}')
            #     building_i.has_year.append(date)
            # else:
            # foundLoc = False # if ther is an unknown problem decoment this - just try :)

            # structureType = onto.StructureType(f'{row[0]}'.lower().replace(' ', '_'))
            structureType = f'{row[0]}'.lower().replace(' ', '_').replace('-', '_')
            # building_i.has_structure.append(structureType)
            # print(similar('colle', 'colle'))
            if structureType == '':
                structureType = 'Structure'
            else:
                # Enrichment
                with onto:
                    exec("class %s(onto.Structure):\
                        pass" % (structureType))
            # Settlement
            if structProba != -1:
                exec("structure_i.has_structure_probability.append(structProba)")
                exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")
            exec("structure_i = onto.%s(structureType + '*' + str(structID))" % (structureType))
            print('-' + structureType)
            # structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_') + '*' + str(structID))
            # structID += 1
            # locID += 1
            if thisStructure != structureType:
                locID += 1
                thisStructure = structureType
            exec("building_i.has_structure.append(structure_i)")
            structProba = -1
            # structure_i.is_a.append(structureType)

            locationType = f'{row[1]}'.lower().replace(' ', '_').replace('-', '_')
            if locationType == '':
                locationType = 'Location'
            else:
                # Enrichment
                with onto:
                    exec("class %s(onto.Location):\
                        pass" % (locationType))
            # Settlement
            if locProba != -1:
                exec("location_i.has_location_probability.append(locProba)")
                exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
            exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
            print('--' + locationType)
            # locID += 1
            prodID += 1
            csvProductVerif = []
            # location_i = onto.Location(foundLocName.replace(' ', '_') + '*' + str(locID))
            exec("structure_i.has_location.append(location_i)")
            locProba = -1
            noProduct = False

            productType = f'{row[2]}'.lower().replace(' ', '_').replace('-', '_')
            if productType == '':
                productType = 'Product'
            else:
                # Enrichment
                with onto:
                    exec("class %s(onto.Product):\
                        pass" % (productType))
            # Settlement
            exec("product_i = onto.%s(productType + '_X*' + str(prodID))" % (productType))
            print('---' + productType)
            if structureType == 'Structure':
                strType = ''
            else:
                strType = structureType
            if locationType == 'Location':
                locType = ''
            else:
                locType = locationType
            if productType == 'Product':
                prodType = ''
            else:
                prodType = productType
            lineResult = codeBuilding + ';' + strType.replace('_', ' ') + ';' + locType.replace('_', ' ') + ';' + prodType.replace('_', ' ')
            # prodID += 1
            # product_i = onto.Product(foundProdName.replace(' ', '_'))
            # print('---------------------------------------------------------')

            # print(productType)

            # Probability calculation
            probability = -1
            foundFamily = False
            foundFamilyList = []
            foundFamilySim = 0
            foundFamilyName = ''

            for f in productFamilyList:
                # print('ff::'+f)
                if f in productType or productType in f:
                    # print('f:'+f)
                    foundFamily = True
                    foundFamilyList.append(f)

            # print(foundFamilyList)
            if foundFamily:
                for fam in foundFamilyList:
                    if similar(fam, productType) > foundFamilySim:
                        foundFamilyName = fam
                        foundFamilySim = similar(fam, productType)
                # print('+'+foundFamilyName)
                calculatedFeatureID = 1
                calculatedFeature = onto.CalculatedCharacteristic(
                    'calculatedFeature*' + str(calculatedFeatureID) + ':' + productType + '*' + str(prodID))
                calculatedFeature.has_calculation_year.append(str2date(date))
                probability = probabilityCalculation(foundFamilyName, date)
                # print('proba : ' + str(probability))
                # print(productType + '--')
                if probability != -1:
                    probabilityClass = probabilityClassCalculation(probability)
                    # print('class : ' + str(probabilityClass))
                    calculatedFeature.has_probability.append(probability)
                    calculatedFeature.has_class.append(probabilityClass)

                exec('product_i.has_calculated_characteristic.append(calculatedFeature)')
                calculatedFeatureID += 1
                if locProba < probability:
                    locProba = probability
                    if structProba < locProba:
                        structProba = locProba

            exec("location_i.contain.append(product_i)")
            if not productType in csvProductVerif:
                # print(productType)
                csvProductVerif.append(productType)
                if probability != -1:
                    lineResult += ';' + 'Classe ' + str(probabilityClass) + ';' + str(
                        probability) + '\n'
                    csvFileResult.write(lineResult)
                else:
                    lineResult += ';Produit non mentioné dans les ressources externes;\n'
                    csvFileResult.write(lineResult)
            # if foundLoc:
            #     locID += 1
            # line_count += 1
        csvFileResult.close()


        if locProba != -1:
            exec("location_i.has_location_probability.append(locProba)")
            exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
        if structProba != -1:
            exec("structure_i.has_structure_probability.append(structProba)")
            exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")

        # prodID += 1

        # Save ontology settlement
        onto.save(file="ONTOLOGY_SETTLEMENT\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")



# AsbestosOntologySettlement2('APPROVED_PROJECT_TYPE\ph2.csv')



def AsbestosOntologySettlement3(projectFileName, path, dell):#the new format of the diagnostic
    global termsList
    locationsList = []
    # productsList = []
    productFamilyList = []
    global buildingID
    global structID
    global locID
    global prodID

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # Delete old individuals
    if 'testingSet' in path:
        for individual in list(onto.individuals()):
            destroy_entity(individual)

    if dell:
        for individual in list(onto.individuals()):
            destroy_entity(individual)

    # Extract locations list from data graph --------------
    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

    q = 'SELECT DISTINCT ?Location WHERE { ?Structure :has_location ?Location .}'
    qresLoc = g.query(q)
    for rowLoc in qresLoc:
        locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')].replace('_', ' '))
    # print(locationsList)

    # # Extract products list from data graph --------------
    # q = 'SELECT DISTINCT ?Product WHERE { ?Location :contain ?Product .}'
    # qresProd = g.query(q)
    # for rowProd in qresProd:
    #     productsList.append(f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')].replace('_', ' '))
    # print('++++++++')
    # print(productsList)

    # Extract product families from product graph --------------
    gProd = rdflib.Graph()
    gProd.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")
    # qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Product . }'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Product' in productFamilyList:
        productFamilyList.remove('Product')
    # print(productFamilyList)

    qTypeL = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    qresTypeL = g.query(qTypeL)
    locationFamilyList = []
    for rowType in qresTypeL:
        locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in locationFamilyList:
        locationFamilyList.remove('Location')

    qTypeS = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    qresTypeS = g.query(qTypeS)
    structureFamilyList = []
    for rowType in qresTypeS:
        structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in structureFamilyList:
        structureFamilyList.remove('Structure')

    # locationFamilyList =[]
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Location' in locationFamilyList:
    #     locationFamilyList.remove('Location')
    #
    # structureFamilyList = []
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Structure' in structureFamilyList:
    #     structureFamilyList.remove('Structure')

    # Load the 'Diagnostic' --------------------------
    with open(projectFileName) as csv_file:
        sourceDocument_i = onto.SourceDocument(projectFileName[projectFileName.find('\\') + len('\\'):].replace(' ', '_'))
        sourceDocument_i.has_category.append('Diagnostic')
        csv_reader = csv.reader(csv_file, delimiter=';')
        # line_count = 0
        batInfo = next(csv_reader)
        buildingID += 1
        codeBuilding = batInfo[1].replace(' ', '_') + '-' + batInfo[2].replace(' ', '_')
        date = batInfo[4]
        csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
        # lineResult = ''
        building_i = onto.Building('Bat_' + codeBuilding + '*' + str(buildingID))
        building_i.extract_from.append(sourceDocument_i)
        building_i.has_type.append(batInfo[3].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        building_i.has_region.append(batInfo[2].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        building_i.has_department_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        building_i.has_registration_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        building_i.has_owner.append(batInfo[2].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        building_i.has_address.append(batInfo[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
        if date != '':
            building_i.has_year.append(str2date(date))
        # location_i = ontology.Location()
        batInfo = next(csv_reader)
        locProba = -1
        structProba = -1
        thisStructure = ''
        structID += 1
        for row in csv_reader:
            # if line_count == 0:
            #     print(f'{row[0]}')
            #     building_i.has_type.append(f'{row[0]}')
            #     building_i.has_address.append(f'{row[5]}')
            #     building_i.has_year.append(date)
            # else:
            # foundLoc = False # if ther is an unknown problem decoment this - just try :)

            # structureType = onto.StructureType(f'{row[0]}'.lower().replace(' ', '_'))
            structureTypeName = f'{row[0]}'.lower().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o')
            structureType = re.sub('\d', '', f'{row[0]}'.lower().replace(' ', '').replace('-', '').replace('.', '')).replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            # building_i.has_structure.append(structureType)
            # print(similar('colle', 'colle'))
            if structureType == '':
                structureType = 'Structure'
            else:
                upperStructure = 'Structure'
                similarStructure = []
                for f in structureFamilyList:
                    if f in structureType and f != structureType:
                        similarStructure.append(f)
                if similarStructure:
                    upperStructure = max(similarStructure, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (structureType, upperStructure))
            # Settlement
            if structProba != -1:
                exec("structure_i.has_structure_diagnostic.append(structProba)")
                # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")
            exec("structure_i = onto.%s(structureTypeName + '*' + str(structID))" % (structureType))
            print('-' + structureType)
            # structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_') + '*' + str(structID))
            # structID += 1
            if thisStructure != structureType:
                locID += 1
                thisStructure = structureType
            exec("building_i.has_structure.append(structure_i)")
            structProba = -1
            # structure_i.is_a.append(structureType)

            locationType = f'{row[1]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            if locationType == '':
                locationType = 'Location'
            else:
                upperLocation = 'Location'
                similarLocation = []
                for f in locationFamilyList:
                    if f in locationType and f != locationType:
                        similarLocation.append(f)
                if similarLocation:
                    upperLocation = max(similarLocation, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (locationType, upperLocation))
            # Settlement
            if locProba != -1:
                exec("location_i.has_location_diagnostic.append(locProba)")
                # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
            exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
            print('--' + locationType)
            # locID += 1
            prodID += 1
            csvProductVerif = []
            # location_i = onto.Location(foundLocName.replace(' ', '_') + '*' + str(locID))
            exec("structure_i.has_location.append(location_i)")
            locProba = -1
            noProduct = False

            productType = f'{row[2]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            if productType == '':
                productType = 'Product'
            else:
                upperProduct = 'Product'
                similarProduct = []
                for f in productFamilyList:
                    if f in productType and f != productType:
                        similarProduct.append(f)
                if similarProduct:
                    upperProduct = max(similarProduct, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (productType, upperProduct))
            # Settlement
            exec("product_i = onto.%s(productType + '_X*' + str(prodID))" % (productType))
            print('---' + productType)
            if structureType == 'Structure':
                strType = ''
            else:
                strType = structureType
            if locationType == 'Location':
                locType = ''
            else:
                locType = locationType
            if productType == 'Product':
                prodType = ''
            else:
                prodType = productType
            lineResult = codeBuilding + ';' + strType.replace('_', ' ') + ';' + locType.replace('_', ' ') + ';' + prodType.replace('_', ' ')
            # prodID += 1
            # product_i = onto.Product(foundProdName.replace(' ', '_'))
            # print('---------------------------------------------------------')

            # print(productType)

            # Diagnosis extraction
            diagnosis = -1
            foundFamily = False
            foundFamilyList = []
            foundFamilySim = 0
            foundFamilyName = ''

            # for f in productFamilyList:
            #     # print('ff::'+f)
            #     if f in productType or productType in f:
            #         # print('f:'+f)
            #         foundFamily = True
            #         foundFamilyList.append(f)

            # print(foundFamilyList)
            # if foundFamily:
            #     for fam in foundFamilyList:
            #         if similar(fam, productType) > foundFamilySim:
            #             foundFamilyName = fam
            #             foundFamilySim = similar(fam, productType)
                # print('+'+foundFamilyName)

            predictionFeatureID = 1
            predictionFeature = onto.PredictedCharacteristic(
                'predictedFeature*' + str(predictionFeatureID) + ':' + productType + '*' + str(prodID))
            exec('product_i.has_predicted_characteristic.append(predictionFeature)')

            diagnosticFeatureID = 1
            diagnosticFeature = onto.DiagnosticCharacteristic(
                'diagnosticFeature*' + str(diagnosticFeatureID) + ':' + productType + '*' + str(prodID))
            diagnosis = int(f'{row[3]}')
                # print('proba : ' + str(probability))
                # print(productType + '--')
            if diagnosis != -1:
                # probabilityClass = probabilityClassCalculation(probability)
                # print('class : ' + str(probabilityClass))
                diagnosticFeature.has_diagnostic.append(diagnosis)
                # calculatedFeature.has_class.append(probabilityClass)

            exec('product_i.has_diagnostic_characteristic.append(diagnosticFeature)')
            diagnosticFeatureID += 1
            if locProba < diagnosis:
                locProba = diagnosis
                if structProba < locProba:
                    structProba = locProba

            exec("location_i.contain.append(product_i)")
            if not productType in csvProductVerif:
                # print(productType)
                # print(diagnosis)
                csvProductVerif.append(productType)
                if diagnosis != -1:
                    lineResult += ';' + str(diagnosis) + '\n'
                    csvFileResult.write(lineResult)
                else:
                    lineResult += ';Le diagnostic n\'est pas fait pour ce produit\n'
                    csvFileResult.write(lineResult)
            # if foundLoc:
            #     locID += 1
            # line_count += 1
        csvFileResult.close()


        if locProba != -1:
            exec("location_i.has_location_diagnostic.append(locProba)")
            # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
        if structProba != -1:
            exec("structure_i.has_structure_diagnostic.append(structProba)")
            # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")

        # prodID += 1

        # Save ontology settlement
        # onto.save(file="ONTOLOGY_SETTLEMENT\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")
        onto.save(file="ONTOLOGY_SETTLEMENT\\" + path + "\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")


        # Delete old individuals
        if 'testingSet' in path:
            for individual in list(onto.individuals()):
                destroy_entity(individual)


# AsbestosOntologySettlement3('C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/APPROVED_PROJECT_TYPE/amiante_1.csv', '', False)
# AsbestosOntologySettlement3('APPROVED_PROJECT_TYPE\ph2t.csv')


def AsbestosOntologySettlement4(projectFileName, path, dell):#DTU
    global termsList
    locationsList = []
    # productsList = []
    productFamilyList = []
    global buildingID
    global structID
    global locID
    global prodID

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # Delete old individuals
    if 'testingSet' in path:
        for individual in list(onto.individuals()):
            destroy_entity(individual)

    if dell:
        for individual in list(onto.individuals()):
            destroy_entity(individual)

    # Extract locations list from data graph --------------
    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

    q = 'SELECT DISTINCT ?Location WHERE { ?Structure :has_location ?Location .}'
    qresLoc = g.query(q)
    for rowLoc in qresLoc:
        locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')].replace('_', ' '))
    # print(locationsList)

    # # Extract products list from data graph --------------
    # q = 'SELECT DISTINCT ?Product WHERE { ?Location :contain ?Product .}'
    # qresProd = g.query(q)
    # for rowProd in qresProd:
    #     productsList.append(f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')].replace('_', ' '))
    # print('++++++++')
    # print(productsList)

    # Extract product families from product graph --------------
    gProd = rdflib.Graph()
    gProd.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")
    # qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Product . }'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Product' in productFamilyList:
        productFamilyList.remove('Product')
    # print(productFamilyList)

    qTypeL = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    qresTypeL = g.query(qTypeL)
    locationFamilyList = []
    for rowType in qresTypeL:
        locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in locationFamilyList:
        locationFamilyList.remove('Location')

    qTypeS = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    qresTypeS = g.query(qTypeS)
    structureFamilyList = []
    for rowType in qresTypeS:
        structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in structureFamilyList:
        structureFamilyList.remove('Structure')

    # locationFamilyList =[]
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Location' in locationFamilyList:
    #     locationFamilyList.remove('Location')
    #
    # structureFamilyList = []
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Structure' in structureFamilyList:
    #     structureFamilyList.remove('Structure')

    # Load the 'DTU' --------------------------
    fileID = ''
    with open(projectFileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        # line_count = 0
        batInfo = next(csv_reader)
        for row in csv_reader:
            if row[0] != fileID:
                fileID = row[0]
                # fileID = row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
                sourceDocument_i = onto.SourceDocument(row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
                sourceDocument_i.has_category.append('DTU')
                buildingID += 1
                codeBuilding = 'BAT_' + row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o')
                date = row[1]
                csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
                # lineResult = ''
                building_i = onto.Building('Bat_' + codeBuilding + '*' + str(buildingID))
                building_i.extract_from.append(sourceDocument_i)
            # building_i.has_type.append(batInfo[3].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_region.append(batInfo[2].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_department_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_registration_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_owner.append(batInfo[2].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_address.append(batInfo[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            if date != '':
                building_i.has_year.append(str2date(date))
            # location_i = ontology.Location()
            # batInfo = next(csv_reader)
            locProba = -1
            structProba = -1
            thisStructure = ''
            structID += 1
            # for row in csv_reader:
            # if line_count == 0:
            #     print(f'{row[0]}')
            #     building_i.has_type.append(f'{row[0]}')
            #     building_i.has_address.append(f'{row[5]}')
            #     building_i.has_year.append(date)
            # else:
            # foundLoc = False # if ther is an unknown problem decoment this - just try :)

            # structureType = onto.StructureType(f'{row[0]}'.lower().replace(' ', '_'))
            structureTypeName = f'{row[2]}'.lower().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o')
            structureType = re.sub('\d', '', f'{row[2]}'.lower().replace(' ', '').replace('-', '').replace('.', '')).replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            # building_i.has_structure.append(structureType)
            # print(similar('colle', 'colle'))
            if structureType == '':
                structureType = 'Structure'
            else:
                upperStructure = 'Structure'
                similarStructure = []
                for f in structureFamilyList:
                    if f in structureType and f != structureType:
                        similarStructure.append(f)
                if similarStructure:
                    upperStructure = max(similarStructure, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (structureType, upperStructure))
            # Settlement
            if structProba != -1:
                exec("structure_i.has_structure_diagnostic.append(structProba)")
                # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")
            exec("structure_i = onto.%s(structureTypeName + '*' + str(structID))" % (structureType))
            print('-' + structureType)
            # structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_') + '*' + str(structID))
            # structID += 1
            if thisStructure != structureType:
                locID += 1
                thisStructure = structureType
            exec("building_i.has_structure.append(structure_i)")
            structProba = -1
            # structure_i.is_a.append(structureType)

            locationType = f'{row[3]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            if locationType == '':
                locationType = 'Location'
            else:
                upperLocation = 'Location'
                similarLocation = []
                for f in locationFamilyList:
                    if f in locationType and f != locationType:
                        similarLocation.append(f)
                if similarLocation:
                    upperLocation = max(similarLocation, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (locationType, upperLocation))
            # Settlement
            if locProba != -1:
                exec("location_i.has_location_diagnostic.append(locProba)")
                # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
            exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
            print('--' + locationType)
            # locID += 1
            prodID += 1
            csvProductVerif = []
            # location_i = onto.Location(foundLocName.replace(' ', '_') + '*' + str(locID))
            exec("structure_i.has_location.append(location_i)")
            locProba = -1
            noProduct = False

            productType = f'{row[4]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            if productType == '':
                productType = 'Product'
            else:
                upperProduct = 'Product'
                similarProduct = []
                for f in productFamilyList:
                    if f in productType and f != productType:
                        similarProduct.append(f)
                if similarProduct:
                    upperProduct = max(similarProduct, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (productType, upperProduct))
            # Settlement
            exec("product_i = onto.%s(productType + '_X*' + str(prodID))" % (productType))
            print('---' + productType)
            if structureType == 'Structure':
                strType = ''
            else:
                strType = structureType
            if locationType == 'Location':
                locType = ''
            else:
                locType = locationType
            if productType == 'Product':
                prodType = ''
            else:
                prodType = productType
            lineResult = codeBuilding + ';' + strType.replace('_', ' ') + ';' + locType.replace('_', ' ') + ';' + prodType.replace('_', ' ')
            # prodID += 1
            # product_i = onto.Product(foundProdName.replace(' ', '_'))
            # print('---------------------------------------------------------')

            # print(productType)

            # Diagnosis extraction
            diagnosis = -1
            foundFamily = False
            foundFamilyList = []
            foundFamilySim = 0
            foundFamilyName = ''

            # for f in productFamilyList:
            #     # print('ff::'+f)
            #     if f in productType or productType in f:
            #         # print('f:'+f)
            #         foundFamily = True
            #         foundFamilyList.append(f)

            # print(foundFamilyList)
            # if foundFamily:
            #     for fam in foundFamilyList:
            #         if similar(fam, productType) > foundFamilySim:
            #             foundFamilyName = fam
            #             foundFamilySim = similar(fam, productType)
                # print('+'+foundFamilyName)

            predictionFeatureID = 1
            predictionFeature = onto.PredictedCharacteristic(
                'predictedFeature*' + str(predictionFeatureID) + ':' + productType + '*' + str(prodID))
            exec('product_i.has_predicted_characteristic.append(predictionFeature)')

            diagnosticFeatureID = 1
            diagnosticFeature = onto.DiagnosticCharacteristic(
                'diagnosticFeature*' + str(diagnosticFeatureID) + ':' + productType + '*' + str(prodID))
            diagnosis = int(f'{row[5]}')
                # print('proba : ' + str(probability))
                # print(productType + '--')
            if diagnosis != -1:
                # probabilityClass = probabilityClassCalculation(probability)
                # print('class : ' + str(probabilityClass))
                diagnosticFeature.has_diagnostic.append(diagnosis)
                # calculatedFeature.has_class.append(probabilityClass)

            exec('product_i.has_diagnostic_characteristic.append(diagnosticFeature)')
            diagnosticFeatureID += 1
            if locProba < diagnosis:
                locProba = diagnosis
                if structProba < locProba:
                    structProba = locProba

            exec("location_i.contain.append(product_i)")
            if not productType in csvProductVerif:
                # print(productType)
                # print(diagnosis)
                csvProductVerif.append(productType)
                if diagnosis != -1:
                    lineResult += ';' + str(diagnosis) + '\n'
                    csvFileResult.write(lineResult)
                else:
                    lineResult += ';Le diagnostic n\'est pas fait pour ce produit\n'
                    csvFileResult.write(lineResult)
            # if foundLoc:
            #     locID += 1
            # line_count += 1
        csvFileResult.close()


        if locProba != -1:
            exec("location_i.has_location_diagnostic.append(locProba)")
            # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
        if structProba != -1:
            exec("structure_i.has_structure_diagnostic.append(structProba)")
            # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")

        # prodID += 1

        # Save ontology settlement
        # onto.save(file="ONTOLOGY_SETTLEMENT\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")
        onto.save(file="ONTOLOGY_SETTLEMENT\\" + path + "\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")


        # Delete old individuals
        if 'testingSet' in path:
            for individual in list(onto.individuals()):
                destroy_entity(individual)


def AsbestosOntologySettlement5(projectFileName, path, dell):#ATEC
    global termsList
    locationsList = []
    # productsList = []
    productFamilyList = []
    global buildingID
    global structID
    global locID
    global prodID

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # Delete old individuals
    if 'testingSet' in path:
        for individual in list(onto.individuals()):
            destroy_entity(individual)

    if dell:
        for individual in list(onto.individuals()):
            destroy_entity(individual)

    # Extract locations list from data graph --------------
    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

    q = 'SELECT DISTINCT ?Location WHERE { ?Structure :has_location ?Location .}'
    qresLoc = g.query(q)
    for rowLoc in qresLoc:
        locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')].replace('_', ' '))
    # print(locationsList)

    # # Extract products list from data graph --------------
    # q = 'SELECT DISTINCT ?Product WHERE { ?Location :contain ?Product .}'
    # qresProd = g.query(q)
    # for rowProd in qresProd:
    #     productsList.append(f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')].replace('_', ' '))
    # print('++++++++')
    # print(productsList)

    # Extract product families from product graph --------------
    gProd = rdflib.Graph()
    gProd.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")
    # qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Product . }'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Product' in productFamilyList:
        productFamilyList.remove('Product')
    # print(productFamilyList)

    qTypeL = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    qresTypeL = g.query(qTypeL)
    locationFamilyList = []
    for rowType in qresTypeL:
        locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in locationFamilyList:
        locationFamilyList.remove('Location')

    qTypeS = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    qresTypeS = g.query(qTypeS)
    structureFamilyList = []
    for rowType in qresTypeS:
        structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in structureFamilyList:
        structureFamilyList.remove('Structure')

    # locationFamilyList =[]
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Location' in locationFamilyList:
    #     locationFamilyList.remove('Location')
    #
    # structureFamilyList = []
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Structure' in structureFamilyList:
    #     structureFamilyList.remove('Structure')

    # Load the 'ATEC' --------------------------
    fileID = ''
    with open(projectFileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        # line_count = 0
        batInfo = next(csv_reader)
        for row in csv_reader:
            if row[0] != fileID:
                fileID = row[0]
                # fileID = row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
                sourceDocument_i = onto.SourceDocument(row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
                sourceDocument_i.has_category.append('ATEC')
                buildingID += 1
                codeBuilding = 'BAT_' + row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o')
                date = row[1]
                csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
                # lineResult = ''
                building_i = onto.Building('Bat_' + codeBuilding + '*' + str(buildingID))
                building_i.extract_from.append(sourceDocument_i)
            # building_i.has_type.append(batInfo[3].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_region.append(batInfo[2].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_department_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_registration_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_owner.append(batInfo[2].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_address.append(batInfo[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            if date != '':
                building_i.has_year.append(str2date(date))
            # location_i = ontology.Location()
            # batInfo = next(csv_reader)
            locProba = -1
            structProba = -1
            thisStructure = ''
            structID += 1
            # for row in csv_reader:
            # if line_count == 0:
            #     print(f'{row[0]}')
            #     building_i.has_type.append(f'{row[0]}')
            #     building_i.has_address.append(f'{row[5]}')
            #     building_i.has_year.append(date)
            # else:
            # foundLoc = False # if ther is an unknown problem decoment this - just try :)

            # structureType = onto.StructureType(f'{row[0]}'.lower().replace(' ', '_'))
            structureTypeName = f'{row[2]}'.lower().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o')
            structureType = re.sub('\d', '', f'{row[2]}'.lower().replace(' ', '').replace('-', '').replace('.', '')).replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            # building_i.has_structure.append(structureType)
            # print(similar('colle', 'colle'))
            if structureType == '':
                structureType = 'Structure'
            else:
                upperStructure = 'Structure'
                similarStructure = []
                for f in structureFamilyList:
                    if f in structureType and f != structureType:
                        similarStructure.append(f)
                if similarStructure:
                    upperStructure = max(similarStructure, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (structureType, upperStructure))
            # Settlement
            if structProba != -1:
                exec("structure_i.has_structure_diagnostic.append(structProba)")
                # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")
            exec("structure_i = onto.%s(structureTypeName + '*' + str(structID))" % (structureType))
            print('-' + structureType)
            # structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_') + '*' + str(structID))
            # structID += 1
            if thisStructure != structureType:
                locID += 1
                thisStructure = structureType
            exec("building_i.has_structure.append(structure_i)")
            structProba = -1
            # structure_i.is_a.append(structureType)

            locationType = f'{row[3]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            if locationType == '':
                locationType = 'Location'
            else:
                upperLocation = 'Location'
                similarLocation = []
                for f in locationFamilyList:
                    if f in locationType and f != locationType:
                        similarLocation.append(f)
                if similarLocation:
                    upperLocation = max(similarLocation, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (locationType, upperLocation))
            # Settlement
            if locProba != -1:
                exec("location_i.has_location_diagnostic.append(locProba)")
                # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
            exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
            print('--' + locationType)
            # locID += 1
            prodID += 1
            csvProductVerif = []
            # location_i = onto.Location(foundLocName.replace(' ', '_') + '*' + str(locID))
            exec("structure_i.has_location.append(location_i)")
            locProba = -1
            noProduct = False

            productType = f'{row[4]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            if productType == '':
                productType = 'Product'
            else:
                upperProduct = 'Product'
                similarProduct = []
                for f in productFamilyList:
                    if f in productType and f != productType:
                        similarProduct.append(f)
                if similarProduct:
                    upperProduct = max(similarProduct, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (productType, upperProduct))
            # Settlement
            exec("product_i = onto.%s(productType + '_X*' + str(prodID))" % (productType))
            print('---' + productType)
            if structureType == 'Structure':
                strType = ''
            else:
                strType = structureType
            if locationType == 'Location':
                locType = ''
            else:
                locType = locationType
            if productType == 'Product':
                prodType = ''
            else:
                prodType = productType
            lineResult = codeBuilding + ';' + strType.replace('_', ' ') + ';' + locType.replace('_', ' ') + ';' + prodType.replace('_', ' ')
            # prodID += 1
            # product_i = onto.Product(foundProdName.replace(' ', '_'))
            # print('---------------------------------------------------------')

            # print(productType)

            # Diagnosis extraction
            diagnosis = -1
            foundFamily = False
            foundFamilyList = []
            foundFamilySim = 0
            foundFamilyName = ''

            # for f in productFamilyList:
            #     # print('ff::'+f)
            #     if f in productType or productType in f:
            #         # print('f:'+f)
            #         foundFamily = True
            #         foundFamilyList.append(f)

            # print(foundFamilyList)
            # if foundFamily:
            #     for fam in foundFamilyList:
            #         if similar(fam, productType) > foundFamilySim:
            #             foundFamilyName = fam
            #             foundFamilySim = similar(fam, productType)
                # print('+'+foundFamilyName)

            predictionFeatureID = 1
            predictionFeature = onto.PredictedCharacteristic(
                'predictedFeature*' + str(predictionFeatureID) + ':' + productType + '*' + str(prodID))
            exec('product_i.has_predicted_characteristic.append(predictionFeature)')

            diagnosticFeatureID = 1
            diagnosticFeature = onto.DiagnosticCharacteristic(
                'diagnosticFeature*' + str(diagnosticFeatureID) + ':' + productType + '*' + str(prodID))
            diagnosis = int(f'{row[5]}')
                # print('proba : ' + str(probability))
                # print(productType + '--')
            if diagnosis != -1:
                # probabilityClass = probabilityClassCalculation(probability)
                # print('class : ' + str(probabilityClass))
                diagnosticFeature.has_diagnostic.append(diagnosis)
                # calculatedFeature.has_class.append(probabilityClass)

            exec('product_i.has_diagnostic_characteristic.append(diagnosticFeature)')
            diagnosticFeatureID += 1
            if locProba < diagnosis:
                locProba = diagnosis
                if structProba < locProba:
                    structProba = locProba

            exec("location_i.contain.append(product_i)")
            if not productType in csvProductVerif:
                # print(productType)
                # print(diagnosis)
                csvProductVerif.append(productType)
                if diagnosis != -1:
                    lineResult += ';' + str(diagnosis) + '\n'
                    csvFileResult.write(lineResult)
                else:
                    lineResult += ';Le diagnostic n\'est pas fait pour ce produit\n'
                    csvFileResult.write(lineResult)
            # if foundLoc:
            #     locID += 1
            # line_count += 1
        csvFileResult.close()


        if locProba != -1:
            exec("location_i.has_location_diagnostic.append(locProba)")
            # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
        if structProba != -1:
            exec("structure_i.has_structure_diagnostic.append(structProba)")
            # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")

        # prodID += 1

        # Save ontology settlement
        # onto.save(file="ONTOLOGY_SETTLEMENT\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")
        onto.save(file="ONTOLOGY_SETTLEMENT\\" + path + "\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")


        # Delete old individuals
        if 'testingSet' in path:
            for individual in list(onto.individuals()):
                destroy_entity(individual)


def AsbestosOntologySettlement6(projectFileName, path, dell):#RAT
    global termsList
    locationsList = []
    # productsList = []
    productFamilyList = []
    global buildingID
    global structID
    global locID
    global prodID

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    # Delete old individuals
    if 'testingSet' in path:
        for individual in list(onto.individuals()):
            destroy_entity(individual)

    if dell:
        for individual in list(onto.individuals()):
            destroy_entity(individual)

    # Extract locations list from data graph --------------
    g = rdflib.Graph()
    g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

    q = 'SELECT DISTINCT ?Location WHERE { ?Structure :has_location ?Location .}'
    qresLoc = g.query(q)
    for rowLoc in qresLoc:
        locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')].replace('_', ' '))
    # print(locationsList)

    # # Extract products list from data graph --------------
    # q = 'SELECT DISTINCT ?Product WHERE { ?Location :contain ?Product .}'
    # qresProd = g.query(q)
    # for rowProd in qresProd:
    #     productsList.append(f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')].replace('_', ' '))
    # print('++++++++')
    # print(productsList)

    # Extract product families from product graph --------------
    gProd = rdflib.Graph()
    gProd.load("ONTOLOGY_SETTLEMENT\PRODUCTS_ONTOLOGY_SETTLEMENT.owl")
    # qType = 'SELECT DISTINCT ?type WHERE { ?x rdf:type ?type .}'
    qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Product . }'
    qresType = gProd.query(qType)

    for rowType in qresType:
        productFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Product' in productFamilyList:
        productFamilyList.remove('Product')
    # print(productFamilyList)

    qTypeL = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    qresTypeL = g.query(qTypeL)
    locationFamilyList = []
    for rowType in qresTypeL:
        locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in locationFamilyList:
        locationFamilyList.remove('Location')

    qTypeS = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    qresTypeS = g.query(qTypeS)
    structureFamilyList = []
    for rowType in qresTypeS:
        structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    if 'Location' in structureFamilyList:
        structureFamilyList.remove('Structure')

    # locationFamilyList =[]
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Location . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     locationFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Location' in locationFamilyList:
    #     locationFamilyList.remove('Location')
    #
    # structureFamilyList = []
    # qType = 'SELECT DISTINCT ?x WHERE { ?x rdfs:subClassOf* :Structure . }'
    # qresType = gProd.query(qType)
    # for rowType in qresType:
    #     structureFamilyList.append(f'{rowType}'[f'{rowType}'.find('#') + len('#'):f'{rowType}'.rfind('\'')])
    # if 'Structure' in structureFamilyList:
    #     structureFamilyList.remove('Structure')

    # Load the 'RAT' --------------------------
    fileID = ''
    with open(projectFileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        # line_count = 0
        batInfo = next(csv_reader)
        for row in csv_reader:
            if row[0] != fileID:
                fileID = row[0]
                # fileID = row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
                sourceDocument_i = onto.SourceDocument(row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
                sourceDocument_i.has_category.append('RAT')
                buildingID += 1
                codeBuilding = 'BAT_' + row[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o')
                date = row[2]
                csvFileResult = open('RESULTS\\' + codeBuilding + '.csv', 'w')
                # lineResult = ''
                building_i = onto.Building('Bat_' + codeBuilding + '*' + str(buildingID))
                building_i.extract_from.append(sourceDocument_i)
                building_i.has_type.append(row[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_region.append(batInfo[2].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_department_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_registration_number.append(batInfo[1].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_owner.append(batInfo[2].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            # building_i.has_address.append(batInfo[0].replace(' ', '_').replace('-', '_').replace('@', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o'))
            if date != '':
                building_i.has_year.append(str2date(date))
            # location_i = ontology.Location()
            # batInfo = next(csv_reader)
            locProba = -1
            structProba = -1
            thisStructure = ''
            structID += 1
            # for row in csv_reader:
            # if line_count == 0:
            #     print(f'{row[0]}')
            #     building_i.has_type.append(f'{row[0]}')
            #     building_i.has_address.append(f'{row[5]}')
            #     building_i.has_year.append(date)
            # else:
            # foundLoc = False # if ther is an unknown problem decoment this - just try :)

            # structureType = onto.StructureType(f'{row[0]}'.lower().replace(' ', '_'))
            structureTypeName = f'{row[3]}'.lower().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '_').replace('(', '_').replace(')', '_').replace('\'', '_').replace(':', '_').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o')
            structureType = re.sub('\d', '', f'{row[2]}'.lower().replace(' ', '').replace('-', '').replace('.', '')).replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '_').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            # building_i.has_structure.append(structureType)
            # print(similar('colle', 'colle'))
            if structureType == '':
                structureType = 'Structure'
            else:
                upperStructure = 'Structure'
                similarStructure = []
                for f in structureFamilyList:
                    if f in structureType and f != structureType:
                        similarStructure.append(f)
                if similarStructure:
                    upperStructure = max(similarStructure, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (structureType, upperStructure))
            # Settlement
            if structProba != -1:
                exec("structure_i.has_structure_diagnostic.append(structProba)")
                # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")
            exec("structure_i = onto.%s(structureTypeName + '*' + str(structID))" % (structureType))
            print('-' + structureType)
            # structure_i = onto.Structure(f'{row[0]}'.lower().replace(' ', '_') + '*' + str(structID))
            # structID += 1
            if thisStructure != structureType:
                locID += 1
                thisStructure = structureType
            exec("building_i.has_structure.append(structure_i)")
            structProba = -1
            # structure_i.is_a.append(structureType)

            locationType = f'{row[4]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            if locationType == '':
                locationType = 'Location'
            else:
                upperLocation = 'Location'
                similarLocation = []
                for f in locationFamilyList:
                    if f in locationType and f != locationType:
                        similarLocation.append(f)
                if similarLocation:
                    upperLocation = max(similarLocation, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (locationType, upperLocation))
            # Settlement
            if locProba != -1:
                exec("location_i.has_location_diagnostic.append(locProba)")
                # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
            exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
            print('--' + locationType)
            # locID += 1
            prodID += 1
            csvProductVerif = []
            # location_i = onto.Location(foundLocName.replace(' ', '_') + '*' + str(locID))
            exec("structure_i.has_location.append(location_i)")
            locProba = -1
            noProduct = False

            productType = f'{row[5]}'.lower().replace(' ', '').replace('-', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '').replace('\'', '').replace(':', '').replace('/', '').replace('«', '').replace('»', '').replace('é', 'e').replace('ê', 'e').replace('è', 'e').replace('î', 'i').replace('â', 'a').replace('ù', 'u').replace('û', 'u').replace('ô', 'o').replace('ç', 'c').replace('ï', 'i').replace('à', 'a')
            if productType == '':
                productType = 'Product'
            else:
                upperProduct = 'Product'
                similarProduct = []
                for f in productFamilyList:
                    if f in productType and f != productType:
                        similarProduct.append(f)
                if similarProduct:
                    upperProduct = max(similarProduct, key=len)
                # Enrichment
                with onto:
                    exec("class %s(onto.%s):\
                        pass" % (productType, upperProduct))
            # Settlement
            exec("product_i = onto.%s(productType + '_X*' + str(prodID))" % (productType))
            print('---' + productType)
            if structureType == 'Structure':
                strType = ''
            else:
                strType = structureType
            if locationType == 'Location':
                locType = ''
            else:
                locType = locationType
            if productType == 'Product':
                prodType = ''
            else:
                prodType = productType
            lineResult = codeBuilding + ';' + strType.replace('_', ' ') + ';' + locType.replace('_', ' ') + ';' + prodType.replace('_', ' ')
            # prodID += 1
            # product_i = onto.Product(foundProdName.replace(' ', '_'))
            # print('---------------------------------------------------------')

            # print(productType)

            # Diagnosis extraction
            diagnosis = -1
            foundFamily = False
            foundFamilyList = []
            foundFamilySim = 0
            foundFamilyName = ''

            # for f in productFamilyList:
            #     # print('ff::'+f)
            #     if f in productType or productType in f:
            #         # print('f:'+f)
            #         foundFamily = True
            #         foundFamilyList.append(f)

            # print(foundFamilyList)
            # if foundFamily:
            #     for fam in foundFamilyList:
            #         if similar(fam, productType) > foundFamilySim:
            #             foundFamilyName = fam
            #             foundFamilySim = similar(fam, productType)
                # print('+'+foundFamilyName)

            predictionFeatureID = 1
            predictionFeature = onto.PredictedCharacteristic(
                'predictedFeature*' + str(predictionFeatureID) + ':' + productType + '*' + str(prodID))
            exec('product_i.has_predicted_characteristic.append(predictionFeature)')

            diagnosticFeatureID = 1
            diagnosticFeature = onto.DiagnosticCharacteristic(
                'diagnosticFeature*' + str(diagnosticFeatureID) + ':' + productType + '*' + str(prodID))
            diagnosis = int(f'{row[6]}')
                # print('proba : ' + str(probability))
                # print(productType + '--')
            if diagnosis != -1:
                # probabilityClass = probabilityClassCalculation(probability)
                # print('class : ' + str(probabilityClass))
                diagnosticFeature.has_diagnostic.append(diagnosis)
                # calculatedFeature.has_class.append(probabilityClass)

            exec('product_i.has_diagnostic_characteristic.append(diagnosticFeature)')
            diagnosticFeatureID += 1
            if locProba < diagnosis:
                locProba = diagnosis
                if structProba < locProba:
                    structProba = locProba

            exec("location_i.contain.append(product_i)")
            if not productType in csvProductVerif:
                # print(productType)
                # print(diagnosis)
                csvProductVerif.append(productType)
                if diagnosis != -1:
                    lineResult += ';' + str(diagnosis) + '\n'
                    csvFileResult.write(lineResult)
                else:
                    lineResult += ';Le diagnostic n\'est pas fait pour ce produit\n'
                    csvFileResult.write(lineResult)
            # if foundLoc:
            #     locID += 1
            # line_count += 1
        csvFileResult.close()


        if locProba != -1:
            exec("location_i.has_location_diagnostic.append(locProba)")
            # exec("location_i.has_location_class.append(probabilityClassCalculation(locProba))")
        if structProba != -1:
            exec("structure_i.has_structure_diagnostic.append(structProba)")
            # exec("structure_i.has_structure_class.append(probabilityClassCalculation(structProba))")

        # prodID += 1

        # Save ontology settlement
        # onto.save(file="ONTOLOGY_SETTLEMENT\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")
        onto.save(file="ONTOLOGY_SETTLEMENT\\" + path + "\\ASBESTOS_ONTOLOGY_SETTLEMENT.owl", format="rdfxml")


        # Delete old individuals
        if 'testingSet' in path:
            for individual in list(onto.individuals()):
                destroy_entity(individual)


def ekaw():# leave one out
    fileList = ['C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091_DAT_20180411.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091_DAT_20180411_2.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0037_DAT_20180425.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0103_DAT_20171102.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0121_DAR.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0134_DAT_20171220.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0152_DAT_20170519_F.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0162_DAR.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0187_DAT_20180118.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0202_DAT_20180109.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0240_DAT_20180504.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0254_DAT_20170420_F.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0256_DAT_20180327.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0305_PMR_DAT_20170626.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0325_DAT_20170626.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0371_DAT_20170420_F.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0373_DAT_20170512_F.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/A-AP75120612096SUD-1 17 RUE CRISTINO GARCIA PARIS 20 - LOT N 007091H0346.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/A-AP75180612096SUD 18 RUE CRITINO GARCIA PARIS 20 - LOT 007091H0382.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante  18 rue lamoriciere 75012  paris ex   authier  007091 h 0032.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante  115 rue de lagny  75020 paris   007091 h 0356 ex   henneton.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante 22 avenue lamoricière  75012 paris ex  molouk   007091 h 0054.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante 26 A rue louis de laporte  75020 paris ex  padovani   007091 h 0275.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante_1.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante_14.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante_15.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT  18, avenue lamoriciere  75012 paris ex.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 8 rue Maryse Hilsz 75020 Paris 007091 H 0335.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 8 rue Maryse Hilsz 75020 Paris 007091 H 0340 PMR.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 8, rue maryse hilsz 75020 paris ex.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 18 avenue lamoriciere   75012  paris -  007091 h 0004.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 18, avenue lamoriciere 75012  paris - 007091 h 0046.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 20, rue cristino garcia 75020  paris -  007091 h 0393.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 22 avenue lamoriciere 75012 PARIS 007091 h 0049.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 22 avenue lamoricière 75012 PARIS 007091 h 0080.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 22, avenue lamoriciere  75012  paris  - 007091 h 7052 - sunsja.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 30 avenue lamoriciere 75012  paris - 007091 h 0094 PMR.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 30 avenue lamoriciere 75012 PARIS 007091h 0095.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 007091 h 0044.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 007091 H 0125.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT120, rue de lagny   75020  paris  - 007091 h 0271.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/10326_-_Amiante_Avant_Tvx_Liste_C__27_02_2012__16_27 ECH.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/12018_-_Amiante_Avant_Tvx_Liste_C_2013 final.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU1.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU2.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU3.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU4.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU5.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU6.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU7.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU8.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU9.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU10.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU11.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU12.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC1.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC2.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC3.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC4.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC5.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC6.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC7.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC8.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC9.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC10.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC11.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC12.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC13.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC14.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC15.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT1.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT2.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT3.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT4.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT5.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT6.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT7.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT8.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT9.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT10.csv']
    dell = True
    for test in range(len(fileList)):
        print('level' + str(test))
        print('test')
        count = 0
        for file in fileList:
            if count == test:
                if 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU' in file:
                    AsbestosOntologySettlement4(file, 'ekaw\\' + str(test) + '\\testingSet', dell)
                elif 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC' in file:
                    AsbestosOntologySettlement5(file, 'ekaw\\' + str(test) + '\\testingSet', dell)
                elif 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT' in file:
                    AsbestosOntologySettlement6(file, 'ekaw\\' + str(test) + '\\testingSet', dell)
                else:
                    AsbestosOntologySettlement3(file, 'ekaw\\' + str(test) + '\\testingSet', dell)
            count += 1
            dell = False

        print('learn')
        count = 0
        for file in fileList:
            print(count)
            if count != test:
                if 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU' in file:
                    AsbestosOntologySettlement4(file, 'ekaw\\' + str(test) + '\\learningSet', dell)
                elif 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC' in file:
                    AsbestosOntologySettlement5(file, 'ekaw\\' + str(test) + '\\learningSet', dell)
                elif 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT' in file:
                    AsbestosOntologySettlement6(file, 'ekaw\\' + str(test) + '\\learningSet', dell)
                else:
                    AsbestosOntologySettlement3(file, 'ekaw\\' + str(test) + '\\learningSet', dell)
            count += 1
            dell = False

    print('END++++++++++ekaw')


# ekaw()


def creatOntoTest():# leave one out
    fileList = ['C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091_DAT_20180411.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091_DAT_20180411_2.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0037_DAT_20180425.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0103_DAT_20171102.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0121_DAR.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0134_DAT_20171220.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0152_DAT_20170519_F.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0162_DAR.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0187_DAT_20180118.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0202_DAT_20180109.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0240_DAT_20180504.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0254_DAT_20170420_F.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0256_DAT_20180327.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0305_PMR_DAT_20170626.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0325_DAT_20170626.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0371_DAT_20170420_F.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/007091H0373_DAT_20170512_F.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/A-AP75120612096SUD-1 17 RUE CRISTINO GARCIA PARIS 20 - LOT N 007091H0346.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/A-AP75180612096SUD 18 RUE CRITINO GARCIA PARIS 20 - LOT 007091H0382.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante  18 rue lamoriciere 75012  paris ex   authier  007091 h 0032.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante  115 rue de lagny  75020 paris   007091 h 0356 ex   henneton.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante 22 avenue lamoricière  75012 paris ex  molouk   007091 h 0054.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante 26 A rue louis de laporte  75020 paris ex  padovani   007091 h 0275.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante_1.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante_14.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/amiante_15.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT  18, avenue lamoriciere  75012 paris ex.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 8 rue Maryse Hilsz 75020 Paris 007091 H 0335.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 8 rue Maryse Hilsz 75020 Paris 007091 H 0340 PMR.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 8, rue maryse hilsz 75020 paris ex.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 18 avenue lamoriciere   75012  paris -  007091 h 0004.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 18, avenue lamoriciere 75012  paris - 007091 h 0046.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 20, rue cristino garcia 75020  paris -  007091 h 0393.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 22 avenue lamoriciere 75012 PARIS 007091 h 0049.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 22 avenue lamoricière 75012 PARIS 007091 h 0080.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 22, avenue lamoriciere  75012  paris  - 007091 h 7052 - sunsja.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 30 avenue lamoriciere 75012  paris - 007091 h 0094 PMR.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 30 avenue lamoriciere 75012 PARIS 007091h 0095.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 007091 h 0044.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT 007091 H 0125.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/DAT120, rue de lagny   75020  paris  - 007091 h 0271.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/10326_-_Amiante_Avant_Tvx_Liste_C__27_02_2012__16_27 ECH.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/PDF_Extracter/DATA/DIAGNOSTIC/12018_-_Amiante_Avant_Tvx_Liste_C_2013 final.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU1.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU2.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU3.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU4.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU5.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU6.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU7.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU8.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU9.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU10.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU11.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU12.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC1.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC2.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC3.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC4.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC5.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC6.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC7.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC8.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC9.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC10.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC11.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC12.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC13.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC14.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC15.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT1.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT2.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT3.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT4.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT5.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT6.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT7.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT8.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT9.csv', 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT10.csv']
    dell = False
    for file in fileList:
        # print(count)
        # if count != test:
        if 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/DTU' in file:
            AsbestosOntologySettlement4(file, 'ekaw', dell)
        elif 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/ATEC' in file:
            AsbestosOntologySettlement5(file, 'ekaw', dell)
        elif 'C:/Users/MECHARNIA/Desktop/OntologyThesis/SourceCode/AsbestosOntology/DATA_BASE/RAT' in file:
            AsbestosOntologySettlement6(file, 'ekaw', dell)
        else:
            AsbestosOntologySettlement3(file, 'ekaw', dell)

    print('END++++++++++ontoTest')


# creatOntoTest()


def getFilePathFromDataBase(type, region, departmentNumber, registrationNumber, ownerName, address, year):
    catalogFileName = 'DATA\Catalog.csv'
    paths = []
    with open(catalogFileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                if type != '':
                    if type == f'{row[1]}':
                        paths.append('DATA_BASE\\' + f'{row[0]}')
            if line_count > 0:
                if region != '':
                    if region == f'{row[2]}':
                        paths.append('DATA_BASE\\' + f'{row[0]}')
            if line_count > 0:
                if departmentNumber != '':
                    if departmentNumber == f'{row[3]}':
                        paths.append('DATA_BASE\\' + f'{row[0]}')
            if line_count > 0:
                if registrationNumber != '':
                    if registrationNumber == f'{row[4]}':
                        paths.append('DATA_BASE\\' + f'{row[0]}')
            if line_count > 0:
                if ownerName != '':
                    if ownerName == f'{row[5]}':
                        paths.append('DATA_BASE\\' + f'{row[0]}')
            if line_count > 0:
                if address != '':
                    if address == f'{row[6]}':
                        paths.append('DATA_BASE\\' + f'{row[0]}')
            if line_count > 0:
                if year != '':
                    if year == f'{row[7]}':
                        paths.append('DATA_BASE\\' + f'{row[0]}')

            line_count += 1
    return paths


def projectToOntology(type, region, departmentNumber, registrationNumber, ownerName, address, year):
    global projetFilesNames
    global diagnosticFilesNames
    global dataStatus

    if not projetFilesNames and not diagnosticFilesNames:# and type=="" and region=="" and departmentNumber=="" and registrationNumber=="" and ownerName=="" and address=="" and year=="":
        popupmsg("Vous devez choisir au moins\nun fichier de projet homologué valide\nou un diagnostic valide !")
    else:
        # Delete previous results
        deleteFiles('RESULTS')

        if not projetFilesNames and not diagnosticFilesNames:
            projetFilesNames = getFilePathFromDataBase(type, region, departmentNumber, registrationNumber, ownerName, address, year)
            for project in projetFilesNames:
                # print(project)
                AsbestosOntologySettlement2(project)
        else:
            if projetFilesNames:
                for project in projetFilesNames:
                    AsbestosOntologySettlement2(project)
            if diagnosticFilesNames:
                for diagnostic in diagnosticFilesNames:
                    print(diagnostic)
                    AsbestosOntologySettlement_newRAT(diagnostic, '')

        dataStatus.config(text='Le classement est términé.')


def callHybridApproach():
    global projetFilesNames
    global diagnosticFilesNames
    global dataStatus

    if not projetFilesNames and not diagnosticFilesNames:
        popupmsg("Vous devez choisir au moins\nun diagnostic valide !")
    else:
        # Delete previous results
        deleteFiles('RESULTS')

        if diagnosticFilesNames:
            for diagnostic in diagnosticFilesNames:
                print(diagnostic)
                AsbestosOntologySettlement_newRAT(diagnostic, '')
            HybridApproachApply()

        dataStatus.config(text="L'approche hybride est términée.")


def callCRAMiner():
    global projetFilesNames
    global diagnosticFilesNames
    global dataStatus

    if not projetFilesNames and not diagnosticFilesNames:
        popupmsg("Vous devez choisir au moins\nun diagnostic valide !")
    else:
        # Delete previous results
        deleteFiles('RESULTS')

        if diagnosticFilesNames:
            for diagnostic in diagnosticFilesNames:
                print(diagnostic)
                AsbestosOntologySettlement_newRAT(diagnostic, '')
            # main(0.6, 0.001, 3, 3)
            applyRules9010minConfSeuilTest()
            applyRules9010minConfSeuilTestRunRaisoneur()

        dataStatus.config(text="CRA-Miner est términé.")


def callCRAMinerRulesUpdate():
    global projetFilesNames
    global diagnosticFilesNames
    global dataStatus

    if not projetFilesNames and not diagnosticFilesNames:
        popupmsg("Vous devez choisir au moins\nun diagnostic valide !")
    else:
        # Delete previous results
        deleteFiles('RESULTS')

        if diagnosticFilesNames:
            for diagnostic in diagnosticFilesNames:
                print(diagnostic)
                AsbestosOntologySettlement_newRAT(diagnostic, '')
            main(0.6, 0.001, 3, 3)

        dataStatus.config(text="La mise à jour de règles de CRA-Miner est términé.")


def owlTocsv(fileName, date):
    structuresList=[]

    csvFile = open(fileName + '.csv', 'a')
    csvFile.write(fileName[fileName.find('\\') + len('\\'):] + ';;;;;;' + date)

    # Load the ontology -----------------------------------------
    onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

    g = rdflib.Graph()
    g.load("GENERATED_SYNTHETIC_DATA\GENERATED_SYNTHETIC_DATA_1.owl")

    qs = 'SELECT DISTINCT ?Structure WHERE { ?Structure :has_location ?Location .}'
    qresStruc = g.query(qs)
    for rowStruc in qresStruc:
        structuresList.append(
            f'{rowStruc}'[f'{rowStruc}'.find('#') + len('#'):f'{rowStruc}'.rfind('\'')])

    for structur in structuresList:
        line = '\n' + structur[:structur.find('*')].replace('_', ' ') + ';'
        locationsList = []
        ql = 'SELECT ?Location WHERE { ?Structure :has_location ?Location .}'
        struc = rdflib.term.URIRef(onto.base_iri + structur)
        qresLoc = g.query(ql, initBindings={'Structure': struc})
        for rowLoc in qresLoc:
            locationsList.append(f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')])

        for location in locationsList:
            if location != 'néant':
                line += ' - ' + location[:location.find('*')].replace('_', ' ')
                productsList = []
                qp = 'SELECT ?Product WHERE { ?Location :contain ?Product .}'
                loc = rdflib.term.URIRef(onto.base_iri + location)
                qresProd = g.query(qp, initBindings={'Location': loc})
                for rowProd in qresProd:
                    productsList.append(
                        f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')])

                addProduct = False
                for product in productsList:
                    if product != 'néant':
                        if addProduct:
                            line += ' et ' + product[:product.find('X')-1].replace('_', ' ')
                        else:
                            line += ' contient ' + product[:product.find('X')-1].replace('_', ' ')
                            addProduct = True
        csvFile.write(line)
    csvFile.close()


def generateSyntheticData(st):
    global generationStatus
    error = True

    if st.isdigit():
        if int(st) != 0:
            error = False
            nbr = int(st)
            structuresList = []
            n = 1
            structID = 1
            locID = 1
            prodID = 1

            # Load the ontology -----------------------------------------
            onto = get_ontology("file://ONTOLOGY\AsbestosOntology.owl").load()

            # Delete GENERATED_SYNTHETIC_DATA files
            deleteFiles('GENERATED_SYNTHETIC_DATA')

            g = rdflib.Graph()
            g.load("ONTOLOGY_SETTLEMENT\DATA_ONTOLOGY_SETTLEMENT.owl")

            qs = 'SELECT DISTINCT ?Structure WHERE { ?Structure :has_location ?Location .}'
            qresStruc = g.query(qs)
            for rowStruc in qresStruc:
                structuresList.append(f'{rowStruc}'[f'{rowStruc}'.find('#') + len('#'):f'{rowStruc}'.rfind('\'')])

            while n <= nbr:
                # locID = 1
                date = str(random.randint(1946, 1996))
                building_i = onto.Building('Bat_' + str(n))
                building_i.has_year.append(str2date(date))
                for s in structuresList:
                    locationsList = []
                    productsList = []
                    structureType = s.lower().replace(' ', '_').replace('-', '_')
                    # Enrichment
                    with onto:
                        exec("class %s(onto.Structure):\
                                pass" % (structureType))
                    # Settlement
                    exec("structure_i = onto.%s(structureType + '*' + str(structID))" % (structureType))
                    structID += 1
                    exec("building_i.has_structure.append(structure_i)")

                    # structure_i = onto.Structure(s)
                    # building_i.has_structure.append(structure_i)
                    ql = 'SELECT ?Location WHERE { ?Structure :has_location ?Location .}'
                    struc = rdflib.term.URIRef(onto.base_iri + s)
                    qresLoc = g.query(ql, initBindings={'Structure': struc})
                    for rowLoc in qresLoc:
                        locationsList.append(
                            f'{rowLoc}'[f'{rowLoc}'.find('#') + len('#'):f'{rowLoc}'.rfind('\'')])
                    if locationsList:
                        maxL = min(3, len(locationsList))
                        ranL = random.randint(1, maxL)
                        locations = random.sample(locationsList, k=ranL)
                        for chosenLocation in locations:
                            if chosenLocation != 'néant':
                                # Enrichment
                                with onto:
                                    locationType = chosenLocation.lower().replace(' ', '_').replace('-', '_')
                                    exec("class %s(onto.Location):\
                                            pass" % (locationType))
                                # Settlement
                                exec("location_i = onto.%s(locationType + '*' + str(locID))" % (locationType))
                                locID += 1
                                exec("structure_i.has_location.append(location_i)")

                                # location_i = onto.Location(chosenLocation + '*' + str(locID))
                                # locID += 1
                                # structure_i.has_location.append(location_i)

                                qp = 'SELECT ?Product WHERE { ?Location :contain ?Product .}'
                                loc = rdflib.term.URIRef(onto.base_iri + chosenLocation)
                                qresProd = g.query(qp, initBindings={'Location': loc})
                                for rowProd in qresProd:
                                    productsList.append(
                                        f'{rowProd}'[f'{rowProd}'.find('#') + len('#'):f'{rowProd}'.rfind('\'')])
                                if productsList:
                                    maxP = min(5, len(productsList))
                                    ranP = random.randint(1, maxP)
                                    products = random.sample(productsList, k=ranP)
                                    for iProduct in products:
                                        chosenProduct = iProduct.replace('-', '_')
                                        if chosenProduct != 'néant':
                                            # productType = chosenProduct.lower().replace(' ', '_').replace('-', '_')
                                            # # Enrichment
                                            # with onto:
                                            #     exec("class %s(Thing):\
                                            #             pass" % (productType))
                                            # # Settlement
                                            # exec("product_i = onto.%s(productType + '*' + str(prodID))" % (productType))
                                            # prodID += 1
                                            # exec("location_i.contain.append(product_i)")
                                            # Enrichment
                                            with onto:
                                                exec("class %s(onto.Product):\
                                                        pass" % (chosenProduct))
                                            # Settlement
                                            exec("product_i = onto.%s(chosenProduct + '_X*' + str(prodID))" % (chosenProduct))
                                            # product_i = onto.Product(chosenProduct)
                                            exec("location_i.contain.append(product_i)")
                                            # location_i.contain.append(product_i)

                # Save the new settlement
                onto.save(file="GENERATED_SYNTHETIC_DATA\GENERATED_SYNTHETIC_DATA_" + str(n) + ".owl", format="rdfxml")

                # Save the new settlement as csv file
                global annee
                global numbB
                if numbB < 4:
                    date = str(annee)
                    numbB += 1
                else:
                    annee += 1
                    date = str(annee)
                    numbB = 1
                owlTocsv("GENERATED_SYNTHETIC_DATA\GENERATED_SYNTHETIC_DATA_" + str(n), date)

                n += 1

                # Delete old individuals
                for individual in list(onto.individuals()):
                    destroy_entity(individual)

            generationStatus.config(text='La génération de données synthétiques est términée.')
    if error:
        popupmsg("Entrer un nombre entier non null !")

# generateSyntheticData(10)





def paperTests():

    max = 204
    i=1
    # nbrStruct = 0
    # nbrFort = 0
    # nbrLoc = 0
    # nbrProd = 0

    yearList = []
    batList = []
    batFortList = []
    structList = []
    structFortList = []
    locList = []
    locFortList = []
    prodList = []
    prodFortList = []
    probaList = []
    builduigProbability = []
    structProbaListTotal = []
    locProbaListTotal = []
    j = 1946
    while j < 1997:
        yearList.append(j)
        batList.append(0)
        batFortList.append(0)
        structList.append(0)
        structFortList.append(0)
        locList.append(0)
        locFortList.append(0)
        prodList.append(0)
        prodFortList.append(0)
        probaList.append(0)
        builduigProbability.append(0)
        structProbaListTotal.append(0)
        locProbaListTotal.append(0)
        j +=1

    while i <= max:
        # fileName = 'test\\papertest\\GENERATED_SYNTHETIC_DATA\\GENERATED_SYNTHETIC_DATA_' + str(i) + '.owl'
        csvFileName = 'GENERATED_SYNTHETIC_DATA\\GENERATED_SYNTHETIC_DATA_' + str(i) + '.csv'
        csvName = 'RESULTS\\GENERATED_SYNTHETIC_DATA_' + str(i) + '---.csv'
        # g = rdflib.Graph()
        # g.load(fileName)
        #
        # qs = 'SELECT ?Structure WHERE { ?Structure :has_location ?Location .}'
        # qresStruc = g.query(qs)
        # nbrStruct += len(list(qresStruc))
        #
        # ql = 'SELECT ?Location WHERE { ?Structure :has_location ?Location .}'
        # qresLoc = g.query(ql)
        # nbrLoc += len(list(qresLoc))
        #
        # qp = 'SELECT ?Product WHERE { ?Location :contain ?Product .}'
        # qresProd = g.query(qp)
        # nbrProd += len(list(qresProd))

        nbrFort = 0
        nbrFaibl = 0
        fort = False
        sum = 0
        card = 0
        struct = ''
        structF = ''
        structN = 0
        structNF = 0
        structProba = 0
        structProbaList = []
        structFirst = True
        loc = ''
        locF = ''
        locN = 0
        locNF = 0
        locProba = 0
        locProbaList = []
        locFirst = True
        buildingProba = 0

        with open(csvName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            # line_count = 0
            for row in csv_reader:
                # if line_count >= 0:
                if f'{row[4]}' in ['Classe 1', 'Classe 2']:
                    if struct != f'{row[1]}':
                        structN += 1
                        if structFirst:
                            structFirst = False
                        else:
                            structProbaList.append(structProba)
                            structProba = 0

                    if loc != f'{row[2]}':
                        locN += 1
                        if locFirst:
                            locFirst = False
                        else:
                            locProbaList.append(locProba)
                            locProba = 0

                    card += 1
                    if f'{row[5]}' != '':
                        sum += float(f'{row[5]}')
                        if float(f'{row[5]}') > buildingProba:
                            buildingProba = float(f'{row[5]}')
                        if float(f'{row[5]}') > structProba:
                            structProba = float(f'{row[5]}')
                        if float(f'{row[5]}') > locProba:
                            locProba = float(f'{row[5]}')
                    if f'{row[4]}' in ['Classe 2']:
                        nbrFort += 1
                        if structF != f'{row[1]}':
                            structNF += 1
                            structF = f'{row[1]}'
                        if locF != f'{row[2]}':
                            locNF += 1
                            locF = f'{row[2]}'
                        fort = True
                    else:
                        nbrFaibl += 1
                    struct = f'{row[1]}'
                    loc = f'{row[2]}'
                # line_count += 1

        with open(csvFileName) as csv_fileData:
            csv_readerData = csv.reader(csv_fileData, delimiter=';')
            line = next(csv_readerData)
            batList[int(line[6]) - 1946] += 1
            if fort:
                batFortList[int(line[6]) - 1946] += 1
            prodList[int(line[6]) - 1946] += nbrFort + nbrFaibl
            prodFortList[int(line[6]) - 1946] += nbrFort
            structList[int(line[6]) - 1946] += structN
            structFortList[int(line[6]) - 1946] += structNF
            locList[int(line[6]) - 1946] += locN
            locFortList[int(line[6]) - 1946] += locNF
        if card != 0:
            probaList[int(line[6]) - 1946] += sum / card
            builduigProbability[int(line[6]) - 1946] += buildingProba
            sSum = 0
            for st in structProbaList:
                sSum += st
            structProbaListTotal[int(line[6]) - 1946] += sSum / len(structProbaList)
            lSum = 0
            for lo in locProbaList:
                lSum += lo
            locProbaListTotal[int(line[6]) - 1946] += lSum / len(locProbaList)
        else:
            probaList[int(line[6]) - 1946] += 0
            structProbaListTotal[int(line[6]) - 1946] += 0
            locProbaListTotal[int(line[6]) - 1946] += 0




        i += 1

    csvFileR = open('donneesSynthetiques.csv', 'w')
    csvFileR.write('year;nbr bâtiments total;nbr bâtiments amiantés;probabilité de bâtiment;nbr structures total;nbr structures Amiantées;probabilité de structures;nbr localisations total;nbr localisations amiantées;probabilité de localisations;nbr produits total; nbr produits amiantés; probabilité moyenne des produits')
    j = 1946
    while j < 1997: # Je devise par 4 parce que j'ai 4 batiments par année
        csvFileR.write('\n' + str(yearList[j - 1946]) + ';' + str(batList[j - 1946]) + ';' + str(batFortList[j - 1946]) + ';' + str(builduigProbability[j - 1946] / 4) + ';' + str(structList[j - 1946]) + ';' + str(structFortList[j - 1946]) + ';' + str(structProbaListTotal[j - 1946] / 4) + ';' + str(locList[j - 1946]) + ';' + str(locFortList[j - 1946]) + ';' + str(locProbaListTotal[j - 1946] / 4)  + ';' + str(prodList[j - 1946]) + ';' + str(prodFortList[j - 1946]) + ';' + str(probaList[j - 1946] / 4))
        j += 1
    # print(nbrStruct)
    # print(nbrLoc)
    # print(nbrProd)
    # print(nbrFort)


# paperTests()


def seuilCalcul():
    csvName = 'DIAG.csv'
    seuilList = []
    probabiliteList = []
    diagList = []
    precisionList = []
    rappelList = []
    FmesureList = []
    tpl = []
    tnl = []
    fpl = []
    fnl = []

    with open(csvName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            probabiliteList.append(float(f'{row[0]}'))
            diagList.append(int(f'{row[1]}'))

        i = 0
        while i < len(probabiliteList):
            seuilList.append(probabiliteList[i])
            j = 0
            tp = 0
            tn = 0
            fp = 0
            fn = 0
            while j < len(probabiliteList):
                if probabiliteList[j] >= seuilList[i]:
                    if diagList[j] == 1:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if diagList[j] == 0:
                        tn += 1
                    else:
                        fn += 1
                j += 1
            tpl.append(tp)
            tnl.append(tn)
            fpl.append(fp)
            fnl.append(fn)
            precisionList.append(tp/(tp+fp))
            rappelList.append(tp/(tp+fn))
            FmesureList.append(2 * ((tp/(tp+fp)) * (tp/(tp+fn))) / (tp/(tp+fp) + tp/(tp+fn)))
            i += 1

        print(seuilList)
        print(precisionList)
        print(rappelList)

        print(max(rappelList))

        csvFileThreshold = open('threshold.csv', 'w')
        csvFileThreshold.write('threshold;precision;reminder;F-mesure;TP;TN;FP;FN\n')

        k = 0
        while k < len(seuilList):
            csvFileThreshold.write(str(seuilList[k]) + ';' + str(precisionList[k]) + ';' + str(rappelList[k]) + ';' + str(FmesureList[k]) + ';' + str(tpl[k]) + ';' + str(tnl[k]) + ';' + str(fpl[k]) + ';' + str(fnl[k]) + '\n')
            print(str(seuilList[k]) + '\t--P ' + str(precisionList[k]) + '\t--R '  + str(rappelList[k]) + '\t--TP ' + str(tpl[k]) + '\t--TN ' + str(tnl[k]) + '\t--FP ' + str(fpl[k]) + '\t--FN ' + str(fnl[k]))
            k += 1


# seuilCalcul()


def seuilTest8020():
    csvNamesListe = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    c = 1

    csvFileResult = open('SeuilTest\\TrainningResults\\_Result.csv', 'w')
    csvFileResult.write('Num;threshold;precision;reminder;F-mesure\n')

    csvFileResultTT = open('SeuilTest\\TestingResults\\_Result.csv', 'w')
    csvFileResultTT.write('Num;threshold;precision;reminder;F-mesure\n')

    while c <= 100:
        testingSetNumList = []
        choosenNum = random.choices(csvNamesListe, k=13)
        for numero in csvNamesListe:
            if numero not in choosenNum:
                testingSetNumList.append(numero)
        csvCombinName = 'SeuilTest\\TrainningSet\\DIAG_Combin (' + str(c) + ').csv'
        csvCombin = open(csvCombinName, 'w')
        for num in choosenNum:
            csvNameDiag = 'SeuilTest\\DIAG (' + str(num) + ').csv'
            with open(csvNameDiag) as csv_fileDiag:
                csv_readerDiag = csv.reader(csv_fileDiag, delimiter=';')
                for row in csv_readerDiag:
                    csvCombin.write(f'{row[0]}' + ';' + f'{row[1]}' + '\n')



        seuilList = []
        probabiliteList = []
        diagList = []
        precisionList = []
        rappelList = []
        FmesureList = []
        tpl = []
        tnl = []
        fpl = []
        fnl = []

        csvCombin.close()


        with open(csvCombinName) as csv_fileCombin:
            csv_reader = csv.reader(csv_fileCombin, delimiter=';')
            for row in csv_reader:
                probabiliteList.append(float(f'{row[0]}'))
                diagList.append(int(f'{row[1]}'))

            i = 0
            while i < len(probabiliteList):
                seuilList.append(probabiliteList[i])
                j = 0
                tp = 0
                tn = 0
                fp = 0
                fn = 0
                while j < len(probabiliteList):
                    if probabiliteList[j] >= seuilList[i]:
                        if diagList[j] == 1:
                            tp += 1
                        else:
                            fp += 1
                    else:
                        if diagList[j] == 0:
                            tn += 1
                        else:
                            fn += 1
                    j += 1
                tpl.append(tp)
                tnl.append(tn)
                fpl.append(fp)
                fnl.append(fn)
                if tp + fp != 0:
                    precisionList.append(tp / (tp + fp))
                else:
                    precisionList.append(0)
                if tp + fn != 0:
                    rappelList.append(tp / (tp + fn))
                else:
                    rappelList.append(0)
                FmesureList.append(2 * ((tp / (tp + fp)) * (tp / (tp + fn))) / (tp / (tp + fp) + tp / (tp + fn)))
                i += 1

            # print(seuilList)
            # print(precisionList)
            # print(rappelList)
            #
            # print(max(rappelList))

            maxRappel = max(rappelList)
            choisRappelList = []
            choisPrecesionList = []
            choisSeuilList = []
            r = 0
            for rapp in rappelList:
                if rapp == maxRappel:
                    choisRappelList.append(rapp)
                    choisPrecesionList.append(precisionList[r])
                    choisSeuilList.append(seuilList[r])
                r += 1

            maxPrecesion = max(choisPrecesionList)
            resList = []
            p = 0
            for prec in choisPrecesionList:
                if prec == maxPrecesion:
                    resList.append(choisSeuilList[p])
                    resList.append(prec)
                    resList.append(maxRappel)
                    resList.append(2 * prec * maxRappel / (prec + maxRappel))
                    break
                p += 1

            csvFileResult.write(str(c) + ';' + str(resList[0]) + ';' + str(resList[1]) + ';' + str(resList[2]) + ';' + str(resList[3]) + '\n')

            csvFileThreshold = open('SeuilTest\\TrainningResults\\DIAG_Result (' + str(c) + ').csv', 'w')
            csvFileThreshold.write('threshold;precision;reminder;F-mesure;TP;TN;FP;FN\n')

            k = 0
            while k < len(seuilList):
                csvFileThreshold.write(
                    str(seuilList[k]) + ';' + str(precisionList[k]) + ';' + str(rappelList[k]) + ';' + str(
                        FmesureList[k]) + ';' + str(tpl[k]) + ';' + str(tnl[k]) + ';' + str(fpl[k]) + ';' + str(
                        fnl[k]) + '\n')

                k += 1





        csvTestSetName = 'SeuilTest\\TestingSet\\DIAG_Combin (' + str(c) + ').csv'
        csvCombinT = open(csvTestSetName, 'w')
        for numT in testingSetNumList:
            csvNameDiagT = 'SeuilTest\\DIAG (' + str(numT) + ').csv'
            with open(csvNameDiagT) as csv_fileDiagT:
                csv_readerDiagT = csv.reader(csv_fileDiagT, delimiter=';')
                for rowT in csv_readerDiagT:
                    csvCombinT.write(f'{rowT[0]}' + ';' + f'{rowT[1]}' + '\n')

        csvCombinT.close()

        probabiliteList = []
        diagList = []
        precisionList = []
        rappelList = []
        FmesureList = []
        tpl = []
        tnl = []
        fpl = []
        fnl = []

        with open(csvTestSetName) as csv_fileCombinTT:
            csv_readerTT = csv.reader(csv_fileCombinTT, delimiter=';')
            for rowTT in csv_readerTT:
                probabiliteList.append(float(f'{rowTT[0]}'))
                diagList.append(int(f'{rowTT[1]}'))

            j = 0
            tp = 0
            tn = 0
            fp = 0
            fn = 0
            while j < len(probabiliteList):
                if probabiliteList[j] >= resList[0]:
                    if diagList[j] == 1:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if diagList[j] == 0:
                        tn += 1
                    else:
                        fn += 1
                j += 1
            tpl.append(tp)
            tnl.append(tn)
            fpl.append(fp)
            fnl.append(fn)
            if tp + fp != 0:
                precisionList.append(tp / (tp + fp))
            else:
                precisionList.append(0)
            if tp + fn != 0:
                rappelList.append(tp / (tp + fn))
            else:
                rappelList.append(0)
            FmesureList.append(2 * ((tp / (tp + fp)) * (tp / (tp + fn))) / (tp / (tp + fp) + tp / (tp + fn)))

            # print(seuilList)
            # print(precisionList)
            # print(rappelList)
            #
            # print(max(rappelList))

            maxRappel = max(rappelList)
            choisRappelList = []
            choisPrecesionList = []
            choisSeuilList = []
            r = 0
            for rapp in rappelList:
                if rapp == maxRappel:
                    choisRappelList.append(rapp)
                    choisPrecesionList.append(precisionList[r])
                    choisSeuilList.append(resList[0])
                r += 1

            maxPrecesion = max(choisPrecesionList)
            resList = []
            p = 0
            for prec in choisPrecesionList:
                if prec == maxPrecesion:
                    resList.append(choisSeuilList[p])
                    resList.append(prec)
                    resList.append(maxRappel)
                    resList.append(2 * prec * maxRappel / (prec + maxRappel))
                    break
                p += 1

            csvFileResultTT.write(str(c) + ';' + str(resList[0]) + ';' + str(resList[1]) + ';' + str(resList[2]) + ';' + str(resList[3]) + '\n')

            csvFileThresholdTT = open('SeuilTest\\TestingResults\\DIAG_Result (' + str(c) + ').csv', 'w')
            csvFileThresholdTT.write('threshold;precision;reminder;F-mesure;TP;TN;FP;FN\n')

            k = 0
            while k < 1:
                csvFileThresholdTT.write(
                    str(resList[0]) + ';' + str(precisionList[k]) + ';' + str(rappelList[k]) + ';' + str(
                        FmesureList[k]) + ';' + str(tpl[k]) + ';' + str(tnl[k]) + ';' + str(fpl[k]) + ';' + str(
                        fnl[k]) + '\n')

                k += 1

        c += 1


# seuilTest8020()


def newSeuilTest():
    csvNamesListe = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    c = 1

    csvFileResult = open('SeuilTest\\TrainningResults\\_Result.csv', 'w')
    csvFileResult.write('Num;threshold;precision;reminder;F-mesure\n')

    csvFileResultTT = open('SeuilTest\\TestingResults\\_Result.csv', 'w')
    csvFileResultTT.write('Num;threshold;precision;reminder;F-mesure\n')

    while c <= 50:
        testingSetNumList = csvNamesListe
        choosenNum = csvNamesListe
        # for numero in csvNamesListe:
        #     if numero not in choosenNum:
        #         testingSetNumList.append(numero)
        csvCombinName = 'SeuilTest\\TrainningSet\\DIAG_Combin (' + str(c) + ').csv'
        csvCombin = open(csvCombinName, 'w')
        # for num in choosenNum:
        csvNameDiag = 'SeuilTest\\DIAG.csv'
        line = 1
        with open(csvNameDiag) as csv_fileDiag:
            csv_readerDiag = csv.reader(csv_fileDiag, delimiter=';')
            for row in csv_readerDiag:
                if line != c:
                    csvCombin.write(f'{row[0]}' + ';' + f'{row[1]}' + '\n')
                line += 1



        seuilList = []
        probabiliteList = []
        diagList = []
        precisionList = []
        rappelList = []
        FmesureList = []
        tpl = []
        tnl = []
        fpl = []
        fnl = []

        csvCombin.close()


        with open(csvCombinName) as csv_fileCombin:
            csv_reader = csv.reader(csv_fileCombin, delimiter=';')
            for row in csv_reader:
                probabiliteList.append(float(f'{row[0]}'))
                diagList.append(int(f'{row[1]}'))

            i = 0
            while i < len(probabiliteList):
                seuilList.append(probabiliteList[i])
                j = 0
                tp = 0
                tn = 0
                fp = 0
                fn = 0
                while j < len(probabiliteList):
                    if probabiliteList[j] >= seuilList[i]:
                        if diagList[j] == 1:
                            tp += 1
                        else:
                            fp += 1
                    else:
                        if diagList[j] == 0:
                            tn += 1
                        else:
                            fn += 1
                    j += 1
                tpl.append(tp)
                tnl.append(tn)
                fpl.append(fp)
                fnl.append(fn)
                if tp + fp != 0:
                    precisionList.append(tp / (tp + fp))
                else:
                    precisionList.append(0)
                if tp + fn != 0:
                    rappelList.append(tp / (tp + fn))
                else:
                    rappelList.append(0)
                FmesureList.append(2 * ((tp / (tp + fp)) * (tp / (tp + fn))) / (tp / (tp + fp) + tp / (tp + fn)))
                i += 1

            # print(seuilList)
            # print(precisionList)
            # print(rappelList)
            #
            # print(max(rappelList))

            maxRappel = max(rappelList)
            choisRappelList = []
            choisPrecesionList = []
            choisSeuilList = []
            r = 0
            for rapp in rappelList:
                if rapp == maxRappel:
                    choisRappelList.append(rapp)
                    choisPrecesionList.append(precisionList[r])
                    choisSeuilList.append(seuilList[r])
                r += 1

            maxPrecesion = max(choisPrecesionList)
            resList = []
            p = 0
            for prec in choisPrecesionList:
                if prec == maxPrecesion:
                    resList.append(choisSeuilList[p])
                    resList.append(prec)
                    resList.append(maxRappel)
                    resList.append(2 * prec * maxRappel / (prec + maxRappel))
                    break
                p += 1

            csvFileResult.write(str(c) + ';' + str(resList[0]) + ';' + str(resList[1]) + ';' + str(resList[2]) + ';' + str(resList[3]) + '\n')

            csvFileThreshold = open('SeuilTest\\TrainningResults\\DIAG_Result (' + str(c) + ').csv', 'w')
            csvFileThreshold.write('threshold;precision;reminder;F-mesure;TP;TN;FP;FN\n')

            k = 0
            while k < len(seuilList):
                csvFileThreshold.write(
                    str(seuilList[k]) + ';' + str(precisionList[k]) + ';' + str(rappelList[k]) + ';' + str(
                        FmesureList[k]) + ';' + str(tpl[k]) + ';' + str(tnl[k]) + ';' + str(fpl[k]) + ';' + str(
                        fnl[k]) + '\n')

                k += 1





        csvTestSetName = 'SeuilTest\\TestingSet\\DIAG_Combin (' + str(c) + ').csv'
        csvCombinT = open(csvTestSetName, 'w')
        # for numT in testingSetNumList:
        csvNameDiagT = 'SeuilTest\\DIAG.csv'
        line = 1
        with open(csvNameDiagT) as csv_fileDiagT:
            csv_readerDiagT = csv.reader(csv_fileDiagT, delimiter=';')
            for rowT in csv_readerDiagT:
                if line == c:
                    csvCombinT.write(f'{rowT[0]}' + ';' + f'{rowT[1]}' + '\n')
                line += 1

        csvCombinT.close()

        probabiliteList = []
        diagList = []
        precisionList = []
        rappelList = []
        FmesureList = []
        tpl = []
        tnl = []
        fpl = []
        fnl = []

        with open(csvTestSetName) as csv_fileCombinTT:
            csv_readerTT = csv.reader(csv_fileCombinTT, delimiter=';')
            for rowTT in csv_readerTT:
                probabiliteList.append(float(f'{rowTT[0]}'))
                diagList.append(int(f'{rowTT[1]}'))

            j = 0
            tp = 0
            tn = 0
            fp = 0
            fn = 0
            while j < len(probabiliteList):
                if probabiliteList[j] >= resList[0]:
                    if diagList[j] == 1:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if diagList[j] == 0:
                        tn += 1
                    else:
                        fn += 1
                j += 1
            tpl.append(tp)
            tnl.append(tn)
            fpl.append(fp)
            fnl.append(fn)
            if tp + fp != 0:
                pr = tp / (tp + fp)
                precisionList.append(tp / (tp + fp))
            else:
                pr = 0
                precisionList.append(0)
            if tp + fn != 0:
                ra = tp / (tp + fn)
                rappelList.append(tp / (tp + fn))
            else:
                ra = 0
                rappelList.append(0)
            # print(pr)
            # print(ra)
            if ra + pr != 0:
                FmesureList.append(2 * ((tp / (tp + fp)) * (tp / (tp + fn))) / (tp / (tp + fp) + tp / (tp + fn)))
            else:
                FmesureList.append(0)

            # print(seuilList)
            # print(precisionList)
            # print(rappelList)
            #
            # print(max(rappelList))

            maxRappel = max(rappelList)
            choisRappelList = []
            choisPrecesionList = []
            choisSeuilList = []
            r = 0
            for rapp in rappelList:
                if rapp == maxRappel:
                    choisRappelList.append(rapp)
                    choisPrecesionList.append(precisionList[r])
                    choisSeuilList.append(resList[0])
                r += 1

            maxPrecesion = max(choisPrecesionList)
            resList = []
            p = 0
            for prec in choisPrecesionList:
                if prec == maxPrecesion:
                    resList.append(choisSeuilList[p])
                    resList.append(prec)
                    resList.append(maxRappel)
                    if prec + maxRappel != 0:
                        resList.append(2 * prec * maxRappel / (prec + maxRappel))
                    else:
                        resList.append(0)
                    break
                p += 1

            csvFileResultTT.write(str(c) + ';' + str(resList[0]) + ';' + str(resList[1]) + ';' + str(resList[2]) + ';' + str(resList[3]) + '\n')

            csvFileThresholdTT = open('SeuilTest\\TestingResults\\DIAG_Result (' + str(c) + ').csv', 'w')
            csvFileThresholdTT.write('threshold;precision;reminder;F-mesure;TP;TN;FP;FN\n')

            k = 0
            while k < 1:
                csvFileThresholdTT.write(
                    str(resList[0]) + ';' + str(precisionList[k]) + ';' + str(rappelList[k]) + ';' + str(
                        FmesureList[k]) + ';' + str(tpl[k]) + ';' + str(tnl[k]) + ';' + str(fpl[k]) + ';' + str(
                        fnl[k]) + '\n')

                k += 1


        c += 1


# newSeuilTest()


def abestosTermSearch():
    global termsList
    global results
    abestosTerms = ["amiante", "amiant"] # to put in dictionary
    for i in termsList:
        for term in abestosTerms:
            if term in i:
                # print(i)
                # text = results.cget("text") + i + "\n"
                # results.config(text=text)
                results.insert(1.0, unidecode(i + '\n'))
                break


def FileChooser():
    fileName = askopenfilename(parent=app, title="Choisir votre fichier")
    return fileName


def InrsFileChooser():
    global inrsFileName
    inrsFileName = FileChooser()
    # print(inrsFileName)


def andevaFileChooser():
    global andevaFileName
    andevaFileName = FileChooser()


def showDoc(type, num):
    global docViewer
    if type == 0:
        xmlDoc = open(projetFilesNames[num], encoding='utf-8', mode="r").read()
        text_filtered = re.sub(r'<(.*?)>', '', xmlDoc)
        docViewer.insert(1.0, unidecode(text_filtered))
        # print(projetFilesNames[0])
        # for i in projetFilesNames:
        #     print(i)
    if type == 1:
        xmlDoc = open(dtuFilesNames[num], encoding='utf-8', mode="r").read()
        text_filtered = re.sub(r'<(.*?)>', '', xmlDoc)
        docViewer.insert(1.0, unidecode(text_filtered))
        # print(dtuFilesNames[0])
        # for i in dtuFilesNames:
        #     print(i)


def on_select(event=None):
    if event:  # <-- this works only with bind because `command=` doesn't send event
        if event.widget.get() == "Agrément":
            showDoc(0, 0)
        if event.widget.get() == "DTU":
            showDoc(1, 0)



class MainApp(tk.Tk):

    def __init__(self, *arg, **kwargs):

        tk.Tk.__init__(self, *arg, **kwargs)
        tk.Tk.iconbitmap(self, default="icon.ico")
        tk.Tk.wm_title(self, "AsbestosReveal")
        container = ttk.Frame(self, width=1100, height=600)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # menubar = tk.Menu(container)
        # filemenu = tk.Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Sauvegarder", command=lambda: popupmsg("n'est pas encor implementé :("))
        # filemenu.add_separator()
        # filemenu.add_command(label="Quiter", command=quit)
        # menubar.add_cascade(label="Fichier", menu=filemenu)
        #
        # tk.Tk.config(self, menu=menubar)

        self.frames = {}

        for F in (Intro, GenerationPage, DataPage, ResultsPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Intro)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Intro(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        container = tk.Frame(self, bg="#201e1f", width=MAINAPP_WIDTH, height=MAINAPP_HEIGHT)
        container.grid(row=0, column=0)
        container.pack_propagate(0)

        canvas = tk.Canvas(container, highlightthickness=0, relief="ridge", width=400, height=400)
        canvas.pack()
        sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(Image.open(r'intro.gif'))]
        image = canvas.create_image(200, 200, image=sequence[0])

        def animate(counter):
            canvas.itemconfig(image, image=sequence[counter])
            parent.after(20, lambda: animate((counter + 1) % len(sequence)))

        animate(0)

        startBtn = tk.Button(container, background=BTN_L_BG, activebackground="#6495ed", relief="flat", text="Démarer",
                             font=FONT_BTN, foreground="white", activeforeground="white", width=20, height=2, command=lambda: validation())
        startBtn.pack(pady=(50, 0))

        def on_enter(e):
            startBtn['background'] = BTN_E_BG

        def on_leave(e):
            startBtn['background'] = BTN_L_BG

        startBtn.bind("<Enter>", on_enter)
        startBtn.bind("<Leave>", on_leave)

        def validation():
            # controller.show_frame(GenerationPage)
            controller.show_frame(DataPage)

class GenerationPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # ------------------------------------------------- Sidebar ---------------------------------------------------
        sidebar = tk.Frame(self, bg=SIDEBARE_BG, width=SIDEBARE_WIDTH, height=SIDEBARE_HEIGHT)
        sidebar.grid(row=0, column=0)
        sidebar.pack_propagate(0)

        space_1_sidebar = ttk.Label(sidebar, background=SIDEBARE_BG)
        space_1_sidebar.pack()
        generateFiles = tk.Label(sidebar, text="Génération de données", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
                                  height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_SFG,
                                  background=SIDEBARE_ELEMENT_SBG, font=FONT_3)
        generateFiles.pack()

        importFiles = tk.Button(sidebar, text="Importation de documents", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
                                height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_NFG,
                                activeforeground=SIDEBARE_ELEMENT_SFG, background=SIDEBARE_ELEMENT_NBG,
                                activebackground=SIDEBARE_ELEMENT_SBG, font=FONT_3, command=lambda: ToDataPage())
        importFiles.pack()

        def on_enter(e):
            importFiles['background'] = SIDEBARE_ELEMENT_HBG
            importFiles['foreground'] = SIDEBARE_ELEMENT_HFG

        def on_leave(e):
            importFiles['background'] = SIDEBARE_ELEMENT_NBG
            importFiles['foreground'] = SIDEBARE_ELEMENT_NFG

        importFiles.bind("<Enter>", on_enter)
        importFiles.bind("<Leave>", on_leave)

        def ToDataPage():
            controller.show_frame(DataPage)

        result = tk.Button(sidebar, text="Résultats", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
                           height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_NFG,
                           activeforeground=SIDEBARE_ELEMENT_SFG, background=SIDEBARE_ELEMENT_NBG,
                           activebackground=SIDEBARE_ELEMENT_SBG, font=FONT_3, command=lambda: ToResultsPage())#, state=tk.DISABLED
        result.pack()

        def on_enter(e):
            result['background'] = SIDEBARE_ELEMENT_HBG
            result['foreground'] = SIDEBARE_ELEMENT_HFG

        def on_leave(e):
            result['background'] = SIDEBARE_ELEMENT_NBG
            result['foreground'] = SIDEBARE_ELEMENT_NFG

        result.bind("<Enter>", on_enter)
        result.bind("<Leave>", on_leave)

        def ToResultsPage():
            controller.show_frame(ResultsPage)

        # ------------------------------------------------- WorkSpace -------------------------------------------------
        workspace = tk.Frame(self, width=WORKSPACE_WIDTH, height=WORKSPACE_HEIGHT)
        workspace.grid(row=0, column=1)
        workspace.pack_propagate(0)

        # ---------------------------------------------------- Board --------------------------------------------------
        board = tk.Frame(workspace, bg=BOARD_BG, width=BOARD_WIDTH, height=BOARD_HEIGHT)
        board.pack()
        board.grid_propagate(0)

        title_1_board = ttk.Label(board, text="Génération de données synthétiques", background=BOARD_BG,
                                  foreground=TITLE_FG, font=FONT_1, anchor="w")
        title_1_board.grid(row=1, sticky="w", padx=(10, 0), pady=(10, 0))
        title_2_board = ttk.Label(board, text="Les données synthétiques à générées", background=BOARD_BG, foreground=TITLE_FG,
                                  font=FONT_2, anchor="w")
        title_2_board.grid(row=2, sticky="w", padx=(20, 0), pady=(10, 0))

        dataDescription = ttk.Label(board, text="Les données synthetics sont des projets homologués générés "
                                                "aléatoirement.", background=BOARD_BG, foreground=LABEL_FG, font=FONT_4,
                                    anchor="w")
        dataDescription.grid(row=3, column=0, sticky="w", padx=(30, 0), pady=(10, 0))

        generateProjectPanel = tk.Frame(board, bg=BOARD_BG, width=650, height=50)
        generateProjectPanel.grid(row=4, column=0, sticky="w", padx=(30, 0))
        generateProjectPanel.grid_propagate(0)

        generateProject = ttk.Label(generateProjectPanel, text="Entrer le nombre de projets homologués à générer *",
                                    background=BOARD_BG, foreground=LABEL_FG, font=FONT_4, anchor="w")
        generateProject.grid(row=0, column=0, sticky="w", pady=(10, 0))

        generateProjectNbr = tk.Entry(generateProjectPanel, justify="right", takefocus = True)
        generateProjectNbr.grid(row=0, column=1, padx=(30, 0), pady=(10, 0))

        # generateProjectButton = ttk.Button(generateProjectPanel, text="Générer",
        #                                    command=lambda: generateSyntheticData(int(generateProjectNbr.get())))
        # generateProjectButton.grid(row=0, column=2, sticky="w", padx=(30, 0), pady=(10, 0))

        # def validation():
        #     controller.show_frame(TermExtraction)

        runBtn = tk.Button(board, background=BTN_L_BG, activebackground="#6495ed", relief="flat", text="Générer",
                           font=FONT_BTN, foreground="white", activeforeground="white", width=10, height=1,
                           command=lambda: generateSyntheticData(generateProjectNbr.get()))
        runBtn.grid(row=5, column=1, pady=(70, 0))

        def on_enter(e):
            runBtn['background'] = BTN_E_BG

        def on_leave(e):
            runBtn['background'] = BTN_L_BG

        runBtn.bind("<Enter>", on_enter)
        runBtn.bind("<Leave>", on_leave)

        # ------------------------------------------------- Status Bar ------------------------------------------------
        global generationStatus
        generationStatus = tk.Label(workspace, text="Fonctionnement...", foreground="white", background=STATUSBAR_BG, bd=1,
                          relief="sunken", anchor="w")
        generationStatus.pack(side="bottom", fill="x")

class DataPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # ------------------------------------------------- Sidebar ---------------------------------------------------
        sidebar = tk.Frame(self, bg=SIDEBARE_BG, width=SIDEBARE_WIDTH, height=SIDEBARE_HEIGHT)
        sidebar.grid(row=0, column=0)
        sidebar.pack_propagate(0)

        space_1_sidebar = ttk.Label(sidebar, background=SIDEBARE_BG)
        space_1_sidebar.pack()
        # generateFiles = tk.Button(sidebar, text="Génération de données", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
        #                         height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_NFG,
        #                         activeforeground=SIDEBARE_ELEMENT_SFG, background=SIDEBARE_ELEMENT_NBG,
        #                         activebackground=SIDEBARE_ELEMENT_SBG, font=FONT_3, command=lambda: ToGenerationPage())
        # generateFiles.pack()
        #
        # def on_enter(e):
        #     generateFiles['background'] = SIDEBARE_ELEMENT_HBG
        #     generateFiles['foreground'] = SIDEBARE_ELEMENT_HFG
        #
        # def on_leave(e):
        #     generateFiles['background'] = SIDEBARE_ELEMENT_NBG
        #     generateFiles['foreground'] = SIDEBARE_ELEMENT_NFG
        #
        # generateFiles.bind("<Enter>", on_enter)
        # generateFiles.bind("<Leave>", on_leave)
        #
        # def ToGenerationPage():
        #     controller.show_frame(GenerationPage)

        importFiles = tk.Label(sidebar, text="Importation de documents", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
                                 height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_SFG,
                                 background=SIDEBARE_ELEMENT_SBG, font=FONT_3)
        importFiles.pack()

        # self.result = tk.Button(sidebar, text="Résultats", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
        #                    height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_NFG,
        #                    activeforeground=SIDEBARE_ELEMENT_SFG, background=SIDEBARE_ELEMENT_NBG,
        #                    activebackground=SIDEBARE_ELEMENT_SBG, font=FONT_3, command=lambda: ToResultsPage())#, state=tk.DISABLED
        # self.result.pack()
        #
        # def on_enter(e):
        #     self.result['background'] = SIDEBARE_ELEMENT_HBG
        #     self.result['foreground'] = SIDEBARE_ELEMENT_HFG
        #
        # def on_leave(e):
        #     self.result['background'] = SIDEBARE_ELEMENT_NBG
        #     self.result['foreground'] = SIDEBARE_ELEMENT_NFG
        #
        # self.result.bind("<Enter>", on_enter)
        # self.result.bind("<Leave>", on_leave)
        #
        # def ToResultsPage():
        #     controller.show_frame(ResultsPage)

        # ------------------------------------------------- WorkSpace -------------------------------------------------
        workspace = tk.Frame(self, width=WORKSPACE_WIDTH, height=WORKSPACE_HEIGHT)
        workspace.grid(row=0, column=1)
        workspace.pack_propagate(0)

        # ---------------------------------------------------- Board --------------------------------------------------
        board = tk.Frame(workspace, bg=BOARD_BG, width=BOARD_WIDTH, height=BOARD_HEIGHT)
        board.pack()
        board.pack_propagate(0)

        self.canvas = tk.Canvas(board, scrollregion=(0, 0, 0, 700), bg=BOARD_BG, bd=0, highlightthickness=0,
                                relief='ridge')

        yscroll = tk.Scrollbar(board, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.config(yscrollcommand=yscroll.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        frame = tk.Frame(workspace, bg=BOARD_BG)
        self.canvas.create_window(0, 0, anchor=tk.NW, window=frame)

        def mouse_scroll(event, canvas):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            else:
                if event.num == 5:
                    move = 1
                else:
                    move = -1

                canvas.yview_scroll(move, 'units')

        self.canvas.bind_all('<MouseWheel>', lambda event, canvas=self.canvas: mouse_scroll(event, canvas))

        title_1_board = ttk.Label(frame, text="Selection de données", background=BOARD_BG, foreground=TITLE_FG,
                                  font=FONT_1, anchor="w")
        # title_1_board.grid(row=1, sticky="w", padx=(10, 0), pady=(10, 0))
        title_1_board.pack(side="top", anchor="nw", padx=(10, 0), pady=(10, 0))

        # title_2_board = ttk.Label(frame, text="Les fichiers de projets homologués", background=BOARD_BG, foreground=TITLE_FG,
        #                           font=FONT_2, anchor="w")
        # # title_2_board.grid(row=2, sticky="w", padx=(20, 0), pady=(10, 0))
        # title_2_board.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))
        #
        # projetList = ttk.Label(frame, text="Choisir le/s fichier/s de projets homologués", background=BOARD_BG,
        #                          foreground=LABEL_FG, font=FONT_4, anchor="w")
        # # projetList.grid(row=3, column=0, sticky="w", padx=(30, 0), pady=(10, 0))
        # projetList.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))
        #
        # projetFileContainer = tk.Frame(frame, bg=BOARD_BG, width=CONTAINER_WIDTH)
        # projetFileContainer.pack(side="top", anchor="n", padx=(30, 0))
        #
        # projetFilePath = ttk.Label(projetFileContainer, text="Choisir les noms de fichiers...", background=PATH_BG, width=PATH_WIDTH,
        #                      foreground=PATH_FG, font=FONT_4, anchor="w", padding=PATH_PADDING )
        # projetFilePath.grid(row=0, column=0, sticky="w", padx=(30, 0))
        # projetChooseFile = ttk.Button(projetFileContainer, text="Parcourir", command=lambda: projetFilesChooser(projetFilePath))
        # projetChooseFile.grid(row=0, column=1, sticky="w")

        title_3_board = ttk.Label(frame, text="Les fichiers de diagnostic", background=BOARD_BG,
                                  foreground=TITLE_FG,
                                  font=FONT_2, anchor="w")
        title_3_board.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        diagnosticList = ttk.Label(frame, text="Choisir le/s fichier/s de diagnostic", background=BOARD_BG,
                               foreground=LABEL_FG, font=FONT_4, anchor="w")
        diagnosticList.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))

        diagnosticFileContainer = tk.Frame(frame, bg=BOARD_BG, width=CONTAINER_WIDTH)
        diagnosticFileContainer.pack(side="top", anchor="n", padx=(30, 0))

        diagnosticFilePath = ttk.Label(diagnosticFileContainer, text="Choisir les noms de fichiers...", background=PATH_BG, width=PATH_WIDTH,
                                   foreground=PATH_FG, font=FONT_4, anchor="w", padding=PATH_PADDING)
        diagnosticFilePath.grid(row=0, column=0, sticky="w", padx=(30, 0))
        diagnosticChooseFile = ttk.Button(diagnosticFileContainer, text="Parcourir", command=lambda: diagnosticFilesChooser(diagnosticFilePath))
        diagnosticChooseFile.grid(row=0, column=1, sticky="w")

        # title_4_board = ttk.Label(frame, text="Les informations du projet homologué", background=BOARD_BG,
        #                           foreground=TITLE_FG, font=FONT_2, anchor="w")
        # title_4_board.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))
        #
        # type_info = ttk.Label(frame, text="Le type du bâtiment", background=BOARD_BG, foreground=LABEL_FG,
        #                               font=FONT_4, anchor="w")
        # type_info.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))
        #
        # type = tk.Entry(frame, justify="left", takefocus=True)
        # type.pack(side="top", anchor="nw", padx=(30, 0))
        #
        # region_info = ttk.Label(frame, text="La région", background=BOARD_BG, foreground=LABEL_FG,
        #                               font=FONT_4, anchor="w")
        # region_info.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))
        #
        # region = tk.Entry(frame, justify="left", takefocus=True)
        # region.pack(side="top", anchor="nw", padx=(30, 0))
        #
        # departmentNumber_info = ttk.Label(frame, text="Le numéro de département", background=BOARD_BG, foreground=LABEL_FG,
        #                         font=FONT_4, anchor="w")
        # departmentNumber_info.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))
        #
        # departmentNumber = tk.Entry(frame, justify="left", takefocus=True)
        # departmentNumber.pack(side="top", anchor="nw", padx=(30, 0))
        #
        # registrationNumber_info = ttk.Label(frame, text="Le numéro d'enregistrement", background=BOARD_BG,
        #                                     foreground=LABEL_FG, font=FONT_4, anchor="w")
        # registrationNumber_info.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))
        #
        # registrationNumber = tk.Entry(frame, justify="left", takefocus=True)
        # registrationNumber.pack(side="top", anchor="nw", padx=(30, 0))
        #
        # ownerName_info = ttk.Label(frame, text="Le nom de bénéficiaire", background=BOARD_BG, foreground=LABEL_FG,
        #                         font=FONT_4, anchor="w")
        # ownerName_info.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))
        #
        # ownerName = tk.Entry(frame, justify="left", takefocus=True, width=50)
        # ownerName.pack(side="top", anchor="nw", padx=(30, 0))
        #
        # address_info = ttk.Label(frame, text="L'adresse du bâtiment", background=BOARD_BG, foreground=LABEL_FG,
        #                         font=FONT_4, anchor="w")
        # address_info.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))
        #
        # address = tk.Entry(frame, justify="left", takefocus=True, width=100)
        # address.pack(side="top", anchor="nw", padx=(30, 0))
        #
        # year_info = ttk.Label(frame, text="L'année du bâtiment", background=BOARD_BG, foreground=LABEL_FG,
        #                         font=FONT_4, anchor="w")
        # year_info.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))
        #
        # year = tk.Entry(frame, justify="left", takefocus=True)
        # year.pack(side="top", anchor="nw", padx=(30, 0))



        def validation():
            controller.show_frame(TermExtraction)
            # print("begin")
            # projectToOntology() # ----------------------------------------------------------------
            # print("end")

        # runBtn = ttk.Button(board, text="Valider", command=lambda: validation())
        hybrideBtn = tk.Button(frame, background=BTN_L_BG, activebackground="#6495ed", relief="flat", text="Exécuter l'approche hybride",
                           font=FONT_BTN, foreground="white", activeforeground="white", width=25, height=1,
                           command=lambda: projectsAnalysisHybride())
        hybrideBtn.pack(side="top", anchor="ne", pady=(10, 0))

        craMinerBtn = tk.Button(frame, background=BTN_L_BG, activebackground="#6495ed", relief="flat",
                           text="Exécuter CRA-Miner",
                           font=FONT_BTN, foreground="white", activeforeground="white", width=20, height=1,
                           command=lambda: projectsAnalysisCRA())
        craMinerBtn.pack(side="top", anchor="ne", pady=(10, 0))

        craMinerUpdateRulesBtn = tk.Button(frame, background=BTN_L_BG, activebackground="#6495ed", relief="flat",
                                text="Mise à jour des règles de CRA-Miner *",
                                font=FONT_BTN, foreground="white", activeforeground="white", width=30, height=1,
                                command=lambda: projectsAnalysisCRA_updateRules())
        craMinerUpdateRulesBtn.pack(side="top", anchor="ne", pady=(10, 0))

        btn_info = ttk.Label(frame, text="* Si vous avez des nouveaux diagnostics.", background=BOARD_BG, foreground=LABEL_FG,
                                font=FONT_4, anchor="w")
        btn_info.pack(side="top", anchor="ne", padx=(30, 0), pady=(10, 0))

        def on_enter_hybride(e):
            hybrideBtn['background'] = BTN_E_BG

        def on_leave_hybride(e):
            hybrideBtn['background'] = BTN_L_BG

        hybrideBtn.bind("<Enter>", on_enter_hybride)
        hybrideBtn.bind("<Leave>", on_leave_hybride)

        def on_enter_cra(e):
            craMinerBtn['background'] = BTN_E_BG

        def on_leave_cra(e):
            craMinerBtn['background'] = BTN_L_BG

        craMinerBtn.bind("<Enter>", on_enter_cra)
        craMinerBtn.bind("<Leave>", on_leave_cra)

        def on_enter_cra_update(e):
            craMinerUpdateRulesBtn['background'] = BTN_E_BG

        def on_leave_cra_update(e):
            craMinerUpdateRulesBtn['background'] = BTN_L_BG

        craMinerUpdateRulesBtn.bind("<Enter>", on_enter_cra_update)
        craMinerUpdateRulesBtn.bind("<Leave>", on_leave_cra_update)

        def projectsAnalysisHybride():
            # self.result.config(state=tk.NORMAL)
            # projectToOntology(type.get(), region.get(), departmentNumber.get(), registrationNumber.get(), ownerName.get(), address.get(), year.get())
            callHybridApproach()

        def projectsAnalysisCRA():
            # self.result.config(state=tk.NORMAL)
            # projectToOntology(type.get(), region.get(), departmentNumber.get(), registrationNumber.get(), ownerName.get(), address.get(), year.get())
            callCRAMiner()

        def projectsAnalysisCRA_updateRules():
            # self.result.config(state=tk.NORMAL)
            # projectToOntology(type.get(), region.get(), departmentNumber.get(), registrationNumber.get(), ownerName.get(), address.get(), year.get())
            callCRAMinerRulesUpdate()


        # ------------------------------------------------- Status Bar ------------------------------------------------
        global dataStatus
        dataStatus = tk.Label(workspace, text="Fonctionnement...", foreground="white", background=STATUSBAR_BG, bd=1,
                          relief="sunken", anchor="w")
        dataStatus.pack(side="bottom", fill="x")

        # button1 = ttk.Button(self, text="Visist page 1", command=lambda: controller.show_frame(PageOne))
        # button1.pack()

class ResultsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # ------------------------------------------------- Sidebar ---------------------------------------------------
        sidebar = tk.Frame(self, bg=SIDEBARE_BG, width=SIDEBARE_WIDTH, height=SIDEBARE_HEIGHT)
        sidebar.grid(row=0, column=0)
        sidebar.pack_propagate(0)

        space_1_sidebar = ttk.Label(sidebar, background=SIDEBARE_BG)
        space_1_sidebar.pack()
        generateFiles = tk.Button(sidebar, text="Génération de données", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
                                height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_NFG,
                                activeforeground=SIDEBARE_ELEMENT_SFG, background=SIDEBARE_ELEMENT_NBG,
                                activebackground=SIDEBARE_ELEMENT_SBG, font=FONT_3, command=lambda: ToGenerationPage())
        generateFiles.pack()

        def on_enter(e):
            generateFiles['background'] = SIDEBARE_ELEMENT_HBG
            generateFiles['foreground'] = SIDEBARE_ELEMENT_HFG

        def on_leave(e):
            generateFiles['background'] = SIDEBARE_ELEMENT_NBG
            generateFiles['foreground'] = SIDEBARE_ELEMENT_NFG

        generateFiles.bind("<Enter>", on_enter)
        generateFiles.bind("<Leave>", on_leave)

        def ToGenerationPage():
            controller.show_frame(GenerationPage)

        importFiles = tk.Button(sidebar, text="Importation de documents", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
                                height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_NFG,
                                activeforeground=SIDEBARE_ELEMENT_SFG, background=SIDEBARE_ELEMENT_NBG,
                                activebackground=SIDEBARE_ELEMENT_SBG, font=FONT_3, command=lambda: ToDataPage())
        importFiles.pack()

        def on_enter(e):
            importFiles['background'] = SIDEBARE_ELEMENT_HBG
            importFiles['foreground'] = SIDEBARE_ELEMENT_HFG

        def on_leave(e):
            importFiles['background'] = SIDEBARE_ELEMENT_NBG
            importFiles['foreground'] = SIDEBARE_ELEMENT_NFG

        importFiles.bind("<Enter>", on_enter)
        importFiles.bind("<Leave>", on_leave)

        def ToDataPage():
            controller.show_frame(DataPage)

        result = tk.Label(sidebar, text="Résultats", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
                          height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_SFG,
                          background=SIDEBARE_ELEMENT_SBG, font=FONT_3)
        # result = tk.Button(sidebar, text="Résultats", relief="flat", width=SIDEBARE_ELEMENT_WIDTH,
        #                    height=SIDEBARE_ELEMENT_HEIGHT, foreground=SIDEBARE_ELEMENT_NFG,
        #                    activeforeground=SIDEBARE_ELEMENT_SFG, background=SIDEBARE_ELEMENT_NBG,
        #                    activebackground=SIDEBARE_ELEMENT_SBG, font=FONT_3, command=lambda: ToResultsPage())
        result.pack()

        # ------------------------------------------------- WorkSpace -------------------------------------------------
        workspace = tk.Frame(self, width=WORKSPACE_WIDTH, height=WORKSPACE_HEIGHT)
        workspace.grid(row=0, column=1)
        workspace.pack_propagate(0)

        # ---------------------------------------------------- Board --------------------------------------------------
        self.firstRefresh = True
        self.pageNum = 0

        board = tk.Frame(workspace, bg=BOARD_BG, width=BOARD_WIDTH, height=BOARD_HEIGHT)
        board.pack()
        board.pack_propagate(0)

        self.canvas = tk.Canvas(board, scrollregion=(0, 0, 0, BOARD_HEIGHT), bg=BOARD_BG, bd=0, highlightthickness=0, relief='ridge')

        yscroll = tk.Scrollbar(board, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.config(yscrollcommand=yscroll.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        frame = tk.Frame(workspace, bg=BOARD_BG)
        self.canvas.create_window(0, 0, anchor=tk.NW, window=frame)

        def mouse_scroll(event, canvas):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            else:
                if event.num == 5:
                    move = 1
                else:
                    move = -1

                canvas.yview_scroll(move, 'units')

        self.canvas.bind_all('<MouseWheel>', lambda event, canvas=self.canvas: mouse_scroll(event, canvas))

        title_1_board = ttk.Label(frame, text="Résultats", background=BOARD_BG,
                                  foreground=TITLE_FG, font=FONT_1, anchor="w")
        title_1_board.pack(side="top", anchor="nw", padx=(10, 0), pady=(10, 0))

        self.title_2_board = ttk.Label(frame, text="", background=BOARD_BG, foreground=TITLE_FG,
                                  font=FONT_2, anchor="w")
        self.title_2_board.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.typeLabel = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                  font=FONT_3, anchor="w")
        self.typeLabel.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.yearLabel = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                  font=FONT_3, anchor="w")
        self.yearLabel.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.regionLabel = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                   font=FONT_3, anchor="w")
        self.regionLabel.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.departmentLabel = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                   font=FONT_3, anchor="w")
        self.departmentLabel.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.registrationLabel = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                   font=FONT_3, anchor="w")
        self.registrationLabel.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.ownerLabel = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                   font=FONT_3, anchor="w")
        self.ownerLabel.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.addressLabel = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                   font=FONT_3, anchor="w")
        self.addressLabel.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.projectContainer = tk.Frame(frame, bg=BOARD_BG, width=CONTAINER_WIDTH)
        self.projectContainer.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))

        self.title_3_board = ttk.Label(frame, text="", background=BOARD_BG, foreground=TITLE_FG,
                                  font=FONT_2, anchor="w")
        self.title_3_board.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.resultsContainer = tk.Frame(frame, bg=BOARD_BG, width=CONTAINER_WIDTH)
        self.resultsContainer.pack(side="top", anchor="nw", padx=(30, 0), pady=(10, 0))

        self.buildingProbability = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                             font=FONT_3, anchor="w")
        self.buildingProbability.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.buildingClass = ttk.Label(frame, text="", background=BOARD_BG, foreground="white",
                                       font=FONT_3, anchor="w")
        self.buildingClass.pack(side="top", anchor="nw", padx=(20, 0), pady=(10, 0))

        self.controlerContainer = tk.Frame(frame, bg=BOARD_BG, width=CONTAINER_WIDTH)
        self.controlerContainer.pack(side="top", anchor="n", padx=(30, 0), pady=(10, 0))

        self.previousBut = tk.Button(self.controlerContainer, background=BTN_L_BG, activebackground="#6495ed",
                                relief="flat", text="Précédent", font=FONT_BTN, foreground="white",
                                activeforeground="white", width=10, height=1, command=lambda: self.previousPage())

        def on_enter(e):
            self.previousBut['background'] = BTN_E_BG

        def on_leave(e):
            self.previousBut['background'] = BTN_L_BG

        self.previousBut.bind("<Enter>", on_enter)
        self.previousBut.bind("<Leave>", on_leave)

        self.pageNumLabel = ttk.Label(self.controlerContainer, text="1 / " + str(len(projetFilesNames)),
                                      background=BOARD_BG, foreground=TITLE_FG, font=FONT_1, anchor="w")

        self.nextBut = tk.Button(self.controlerContainer, background=BTN_L_BG, activebackground="#6495ed",
                            relief="flat", text="Suivant", font=FONT_BTN, foreground="white",
                            activeforeground="white", width=10, height=1, command=lambda: self.nextPage())

        def on_enter(e):
            self.nextBut['background'] = BTN_E_BG

        def on_leave(e):
            self.nextBut['background'] = BTN_L_BG

        self.nextBut.bind("<Enter>", on_enter)
        self.nextBut.bind("<Leave>", on_leave)

        refresh = tk.Button(frame, background=BTN_L_BG, activebackground="#6495ed", relief="flat", text="Actualiser",
                           font=FONT_BTN, foreground="white", activeforeground="white", width=10, height=1,
                           command=lambda: self.refreshPage())
        refresh.pack(side="top", anchor="n", padx=(30, 0))

        def on_enter(e):
            refresh['background'] = BTN_E_BG

        def on_leave(e):
            refresh['background'] = BTN_L_BG

        refresh.bind("<Enter>", on_enter)
        refresh.bind("<Leave>", on_leave)

        # ------------------------------------------------- Status Bar ------------------------------------------------
        global ResultsStatus
        ResultsStatus = tk.Label(workspace, text="Fonctionnement...", foreground="white", background=STATUSBAR_BG, bd=1,
                          relief="sunken", anchor="w")
        ResultsStatus.pack(side="bottom", fill="x")

    def showData(self, num):
        global projetFilesNames
        global diagnosticFilesNames

        self.clear()

        self.title_3_board.config(text="Le résultat de l'extraction")

        height = 2

        buildingClassInfo = "Inconnue"
        buildingProbabilityInfo = -1

        structurColumnTitel = tk.Label(self.projectContainer, text="Structures", background=TITEL_CELL_BG, width=18,
                                       relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                                       anchor="n")
        structurColumnTitel.grid(row=0, column=0, sticky="w")
        descriptionColumnTitel = tk.Label(self.projectContainer, text="Description", background=TITEL_CELL_BG, width=50,
                                          relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                                          anchor="n")
        descriptionColumnTitel.grid(row=0, column=1, sticky="w")

        building = getProjectsContenent(num)

        self.title_2_board.config(
            text="Le projet homologué : " + building[0][0] + '-' + building[0][1].replace(' ', '_') + '-' + building[0][
                2] + '-' + building[0][3])
        self.typeLabel.config(text="- Type de bâtiment : " + building[0][0])
        self.yearLabel.config(text="- Année de construction : " + building[0][6])
        self.regionLabel.config(text="- Région : " + building[0][1])
        self.departmentLabel.config(text="- N° du département : " + building[0][2])
        self.registrationLabel.config(text="- N° d'enregistrement : " + building[0][3])
        self.ownerLabel.config(text="- Nom du bénéficiaire : " + building[0][4])
        self.addressLabel.config(text="- Adresse du bénéficiaire : " + building[0][5])

        for i in range(len(building[1])):
            count_1 = 0
            returnCout_1 = 0
            str_1 = ''
            for s1 in building[1][i][0]:
                if count_1 > 16:
                    str_1 += '-\n'
                    count_1 = 0
                    returnCout_1 += 1
                str_1 += s1
                count_1 += 1

            count_2 = 0
            returnCout_2 = 0
            str_2 = ''
            for s2 in building[1][i][1]:
                if count_2 > 60:
                    str_2 += '-\n'
                    count_2 = 0
                    returnCout_2 += 1
                str_2 += s2
                count_2 += 1

            if returnCout_1 < returnCout_2:
                height += returnCout_2
                for k in range(returnCout_2 - returnCout_1):
                    str_1 += '\n'
            elif returnCout_1 > returnCout_2:
                height += returnCout_1
                for k in range(returnCout_1 - returnCout_2):
                    str_2 += '\n'

            cell_1 = tk.Label(self.projectContainer, text=str_1, background=CELL_BG, width=18,
                            relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                            anchor="n")
            cell_1.grid(row=i + 1, column=0)
            cell_2 = tk.Label(self.projectContainer, text=str_2, background=CELL_BG, width=50,
                            relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                            anchor="w")
            cell_2.grid(row=i + 1, column=1)

        structurColumnTitelR = tk.Label(self.resultsContainer, text="Structures", background=TITEL_CELL_BG, width=16,
                                       relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                                       anchor="n")
        structurColumnTitelR.grid(row=0, column=0, sticky="w")
        locationColumnTitel = tk.Label(self.resultsContainer, text="Localisation", background=TITEL_CELL_BG, width=16,
                                          relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                                          anchor="n")
        locationColumnTitel.grid(row=0, column=1, sticky="w")
        productColumnTitel = tk.Label(self.resultsContainer, text="Produit", background=TITEL_CELL_BG, width=16,
                                       relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                                       anchor="n")
        productColumnTitel.grid(row=0, column=2, sticky="w")
        classColumnTitel = tk.Label(self.resultsContainer, text="Classe", background=TITEL_CELL_BG, width=8,
                                      relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                                      anchor="n")
        classColumnTitel.grid(row=0, column=3, sticky="w")
        probabilityColumnTitel = tk.Label(self.resultsContainer, text="Probabilité", background=TITEL_CELL_BG, width=10,
                                      relief="groove", highlightthickness=1, foreground="white", font=FONT_3,
                                      anchor="n")
        probabilityColumnTitel.grid(row=0, column=4, sticky="w")

        result = getProjectsResults(
            building[0][0] + '-' + building[0][1].replace(' ', '_') + '-' + building[0][2] + '-' + building[0][3])

        for i in range(len(result)):
            count_1 = 0
            returnCout_1 = 0
            str_1 = ''
            for s1 in result[i][0]:
                if count_1 > 17:
                    str_1 += '-\n'
                    count_1 = 0
                    returnCout_1 += 1
                str_1 += s1
                count_1 += 1

            count_2 = 0
            returnCout_2 = 0
            str_2 = ''
            for s2 in result[i][1]:
                if count_2 > 17:
                    str_2 += '-\n'
                    count_2 = 0
                    returnCout_2 += 1
                str_2 += s2
                count_2 += 1

            count_3 = 0
            returnCout_3 = 0
            str_3 = ''
            for s3 in result[i][2]:
                if count_3 > 17:
                    str_3 += '-\n'
                    count_3 = 0
                    returnCout_3 += 1
                str_3 += s3
                count_3 += 1

            if returnCout_1 < returnCout_2:
                for k in range(returnCout_2 - returnCout_1):
                    str_1 += '\n'
            elif returnCout_1 > returnCout_2:
                for k in range(returnCout_1 - returnCout_2):
                    str_2 += '\n'

            if returnCout_1 < returnCout_3:
                height += returnCout_3
                for k in range(returnCout_3 - returnCout_1):
                    str_1 += '\n'
                    str_2 += '\n'
            elif returnCout_1 > returnCout_3:
                height += returnCout_1
                for k in range(returnCout_1 - returnCout_3):
                    str_3 += '\n'

            if result[i][4] == '':
                str_4 = 'Inconnue'
                str_5 = '/'
            else:
                str_5 = result[i][4][:6]
                if float(str_5) > buildingProbabilityInfo:
                    buildingProbabilityInfo = float(str_5)

                if result[i][3] == 'Classe 1':
                    str_4 = 'Faible'
                    if buildingClassInfo != 'Forte':
                        buildingClassInfo = 'Faible'
                else:
                    str_4 = 'Forte'
                    buildingClassInfo = 'Forte'

            for k in range(returnCout_1):
                str_4 += '\n'
                str_5 += '\n'

            cell_1_R = tk.Label(self.resultsContainer, text=str_1, background=CELL_BG, width=16, relief="groove",
                                highlightthickness=1, foreground="white", font=FONT_3, anchor="n")
            cell_1_R.grid(row=i + 1, column=0)
            cell_2_R = tk.Label(self.resultsContainer, text=str_2, background=CELL_BG, width=16, relief="groove",
                                highlightthickness=1, foreground="white", font=FONT_3, anchor="n")
            cell_2_R.grid(row=i + 1, column=1)
            cell_3_R = tk.Label(self.resultsContainer, text=str_3, background=CELL_BG, width=16, relief="groove",
                                highlightthickness=1, foreground="white", font=FONT_3, anchor="n")
            cell_3_R.grid(row=i + 1, column=2)

            cell_4_R = tk.Label(self.resultsContainer, text=str_4, background=CELL_BG, width=8, relief="groove",
                                highlightthickness=1, foreground="white", font=FONT_3, anchor="n")
            cell_4_R.grid(row=i + 1, column=3)
            cell_5_R = tk.Label(self.resultsContainer, text=str_5, background=CELL_BG, width=10, relief="groove",
                                highlightthickness=1, foreground="white", font=FONT_3, anchor="n")
            cell_5_R.grid(row=i + 1, column=4)

        self.buildingClass.config(text="La classe du bâtiment est : " + buildingClassInfo)
        if buildingProbabilityInfo != -1:
            self.buildingProbability.config(text="La probabilité du bâtiment est : " + str(buildingProbabilityInfo))
        else:
            self.buildingProbability.config(text="La probabilité du bâtiment est inconnue ")

        if self.firstRefresh:
            self.firstRefresh = False

            self.previousBut.grid(row=0, column=0)

            self.pageNumLabel.grid(row=0, column=1, padx=(32, 32))

            self.nextBut.grid(row=0, column=2)

        if self.pageNum == 0:
            self.previousBut.config(state=tk.DISABLED)
        else:
            self.previousBut.config(state=tk.NORMAL)

        if self.pageNum == len(projetFilesNames) - 1:
            self.nextBut.config(state=tk.DISABLED)
        else:
            self.nextBut.config(state=tk.NORMAL)

        self.pageNumLabel.config(text=str(num + 1) + " / " + str(len(projetFilesNames)))

        self.canvas.config(scrollregion=(0, 0, 0, height*(2*60) + 1000))

    def refreshPage(self):
        if not projetFilesNames and not diagnosticFilesNames:
            popupmsg("Vous devez analyser un/des fichier/s\nde projets homologués \nou de diagnostic d'abord !")
        else:
            self.pageNum = 0
            self.showData(self.pageNum)

    def nextPage(self):
        self.pageNum += 1
        self.showData(self.pageNum)

    def previousPage(self):
        self.pageNum -= 1
        self.showData(self.pageNum)

    def clear(self):
        listP = self.projectContainer.grid_slaves()
        for l in listP:
            l.destroy()

        listR = self.resultsContainer.grid_slaves()
        for l in listR:
            l.destroy()


class TermExtraction(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # ------------------------------------------------- Sidebar ---------------------------------------------------
        sidebar = tk.Frame(self, bg=SIDEBARE_BG, width=SIDEBARE_WIDTH, height=SIDEBARE_HEIGHT)
        sidebar.grid(row=0, column=0)
        sidebar.pack_propagate(0)

        space_1_sidebar = ttk.Label(sidebar, background=SIDEBARE_BG)
        space_1_sidebar.pack()
        importFiles = ttk.Label(sidebar, text="Importation de données", width=SIDEBARE_ELEMENT_WIDTH,
                                foreground=SIDEBARE_ELEMENT_NFG, background=SIDEBARE_ELEMENT_NBG, font=FONT_3)
        importFiles.pack()
        result = ttk.Label(sidebar, text="Extraction de termes", width=SIDEBARE_ELEMENT_WIDTH,
                           foreground=SIDEBARE_ELEMENT_SFG, background=SIDEBARE_ELEMENT_SBG, font=FONT_3)
        result.pack()
        analyze = ttk.Label(sidebar, text="Analyser", width=SIDEBARE_ELEMENT_WIDTH, foreground=SIDEBARE_ELEMENT_NFG,
                            background=SIDEBARE_ELEMENT_NBG, font=FONT_3)
        analyze.pack()

        # ------------------------------------------------- WorkSpace -------------------------------------------------
        workspace = tk.Frame(self, width=WORKSPACE_WIDTH, height=WORKSPACE_HEIGHT)
        workspace.grid(row=0, column=1)
        workspace.pack_propagate(0)

        # ---------------------------------------------------- Board --------------------------------------------------
        board = tk.Frame(workspace, bg=BOARD_BG, width=BOARD_WIDTH, height=BOARD_HEIGHT)
        board.pack()
        board.pack_propagate(0)

        terminologyPanel = tk.Frame(board, bg=BOARD_BG, width=500, height=BOARD_HEIGHT)
        terminologyPanel.pack(side="left")
        terminologyPanel.pack_propagate(0)

        viewPanel = tk.Frame(board, bg=BOARD_BG, width=400, height=BOARD_HEIGHT, bd=1, relief="sunken")
        viewPanel.pack()
        viewPanel.pack_propagate(0)

        docTypeLabel = ttk.Label(viewPanel, text="Choisir le type de document à afficher", background=BOARD_BG,
                                 foreground=LABEL_FG, font=FONT_4)
        docTypeLabel.pack()
        docType = ttk.Combobox(viewPanel, values=("Agrément", "DTU"), state='readonly')
        docType.pack()
        docType.bind('<<ComboboxSelected>>', on_select)

        docViewerContainer = tk.Frame(viewPanel, bg=VIEWER_BG, width=400, height=500)
        docViewerContainer.pack(expand=True)
        docViewerContainer.grid_propagate(0)
        docViewerContainer.grid_rowconfigure(0, weight=1)
        docViewerContainer.grid_columnconfigure(0, weight=1)

        global docViewer
        docViewer = tkscrolled.ScrolledText(docViewerContainer, undo=True, font=FONT_5)
        docViewer.pack(expand=True, fill='both')

        html_text = "<html></html>"
        text_filtered = re.sub(r'<(.*?)>', '', html_text)
        # print(unidecode(text_filtered))
        # print(text_filtered.encode("utf-8"))

        docViewer.insert(1.0, unidecode(text_filtered))

        navLeft = ttk.Button(viewPanel, text=" < Précédent")
        navLeft.pack(side="left")

        navRight = ttk.Button(viewPanel, text="Suivant > ")
        navRight.pack(side="right")

        global results
        results = tkscrolled.ScrolledText(terminologyPanel, undo=True, font=FONT_5)
        # results['font'] = ('consolas', '12')
        results.pack(expand=True, fill='both')



        # projectToOntology()




        # frame = HtmlFrame(docViewer, horizontal_scrollbar="auto")
        #
        # frame.set_content("<html>"+f.read()+"</html>")

        # frame.set_content(clean_text)

        # frame.set_content(urllib.request.urlopen("http://thonny.cs.ut.ee").read().decode())

        # frame.pack()




        # title_1_board = ttk.Label(board, text="Informations des Fichiers", background=BOARD_BG, foreground=TITLE_FG,
        #                           font=FONT_1, anchor="w")
        # title_1_board.grid(row=1, sticky="w", padx=(10, 0), pady=(10, 0))
        # title_2_board = ttk.Label(board, text="Les fiche de données", background=BOARD_BG, foreground=TITLE_FG,
        #                           font=FONT_2, anchor="w")
        # title_2_board.grid(row=2, sticky="w", padx=(20, 0), pady=(10, 0))




        # runBtn = ttk.Button(board, text="Executer", command=lambda: terminologyExtraction())
        # runBtn.grid(row=10, column=1, pady=(20, 0))
        #
        # global results
        # results = ttk.Label(board, background=BOARD_BG, foreground="white", anchor="w")
        # results.grid(row=11, column=0)

        # ------------------------------------------------- Status Bar ------------------------------------------------
        status = tk.Label(workspace, text="Fonctionnement...", background=STATUSBAR_BG, bd=1, relief="sunken",
                          anchor="w")
        status.pack(side="bottom", fill="x")

        # label = tk.Label(self, text="Page One", font=FONT_1)
        # label.pack(pady=10, padx=10)
        #
        # button1 = ttk.Button(self, text="Back to home", command=controller.show_frame(DataPage))
        # button1.pack()



# #1) build a TreeTagger wrapper:
# tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr')
# #2) tag your text.
# tags = tagger.tag_text("Tableau haut.")
# #3) use the tags list... (list of string output from TreeTagger).
# pprint.pprint(tags)
# print(tags)
# print(tags[0][tags[0].find('\t')+len('\t'):tags[0].rfind('\t')])
# # -----------------------------------------------------------------------------------------
# # 1) build a TreeTagger wrapper:
# tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr')
# # 2) tag your text.
# tags = tagger.tag_text('Je suis un dragon noir, le roi des créatures !')
# # 3) use the tags list... (list of string output from TreeTagger).
# term = ''
# for j in tags:
#     print(j)
#     if j[j.find('\t') + len('\t'):j.rfind('\t')] in ['NOM', 'ADJ', 'ADV']:
#         term += j[:j.find('\t')] + ' '
#     else:
#         if term != '':
#             termsList.append(term[:-1])
#         term = ''
#
# print(termsList)

app = MainApp()
# app.style = ttk.Style()
# app.style.theme_use("equilux")
# style = ttk.Style()
# style.configure("SIDEBARE_BG", background="#3e4c54")
# style.configure("SIDEBARE_ELEMENT_NBG", width=28, foreground="#6ba4c3", background="#546771", font=SIDEBAR_FONT)
# style.configure("SIDEBARE_ELEMENT_HBG", width=28, foreground="#78b8db", background="#6a828e", font=SIDEBAR_FONT)
# style.configure("SIDEBARE_ELEMENT_SBG", width=28, foreground="#78b8db", background="#6a828e", font=SIDEBAR_FONT)

app.geometry("1100x600")
app.resizable(0, 0)
app.mainloop()
































# from tkinter import *
# from tkinter.filedialog import askopenfilename
# import tkinter.messagebox
# from nltk.tokenize import sent_tokenize, word_tokenize
#
# # class MainWindow:
# #
# #     def __init__(self, master):
# #         mainFrame = Frame(master)
# #         mainFrame.pack()
# #         mainFrame.pack_propagate(0)
# #
# #         # ------------------------------------------------- Main Menu -------------------------------------------------
# #         menu = Menu(mainFrame)
# #         root.config(menu=menu)
# #
# #         fileMenu = Menu(menu)
# #         menu.add_cascade(label="Fichier", menu=fileMenu)
# #         fileMenu.add_command(label="Nouveau projet", command=doNothing)
# #         fileMenu.add_command(label="Nouveau", command=doNothing)
# #         fileMenu.add_separator()
# #         fileMenu.add_command(label="Quiter", command=mainFrame.quit)
# #
# #         editMenu = Menu(menu)
# #         menu.add_cascade(label="Editer", menu=editMenu)
# #         editMenu.add_command(label="Copier", command=doNothing)
# #
# #         # -------------------------------------------------- Toolbar --------------------------------------------------
# #         # toolbar = Frame(mainFrame, bg="blue")
# #         #
# #         # insertButt = Button(toolbar, text="Inserer une Image", command=doNothing)
# #         # insertButt.pack(side=LEFT, padx=2, pady=2)
# #         # printButt = Button(toolbar, text="Imprimer", command=doNothing)
# #         # printButt.pack(side=LEFT, padx=2, pady=2)
# #         #
# #         # toolbar.pack(side=TOP, fill=X)
# #
# #         # ------------------------------------------------- Sidebar ---------------------------------------------------
# #         sidebar = Frame(mainFrame, bg="#3e4c54", width=200, height=600)
# #         sidebar.grid(row=0, column=0)
# #         sidebar.pack_propagate(0)
# #
# #         space_1_sidebar = Label(sidebar, bg="#3e4c54", height=1)
# #         space_1_sidebar.pack()
# #         importFiles = Label(sidebar, bg="#6a828e", text="Importer", width=28, fg="#78b8db", font=("Constantia", 18))
# #         importFiles.pack()
# #         results = Label(sidebar, bg="#546771", text="Résultats", width=28, fg="#6ba4c3", font=("Constantia", 18))
# #         results.pack()
# #         analyze = Label(sidebar, bg="#546771", text="Analyser", width=28, fg="#6ba4c3", font=("Constantia", 18))
# #         analyze.pack()
# #
# #         # ------------------------------------------------- WorkSpace -------------------------------------------------
# #         workspace = Frame(mainFrame, width=900, height=600)
# #         workspace.grid(row=0, column=1)
# #         workspace.pack_propagate(0)
# #
# #         # ---------------------------------------------------- Board --------------------------------------------------
# #         board = Frame(workspace, bg="#495a62", width=900, height=580)
# #         board.pack()
# #         board.grid_propagate(0)
# #
# #         space_1_board = Frame(board, bg="#495a62", height=10)
# #         space_1_board.grid(row=0)
# #         title_1_board = Label(board, text="Informations des Fichiers", bg="#495a62", width=28, fg="#78b8db",
# #                               font=("Constantia", 18), anchor=W, padx=10)
# #         title_1_board.grid(row=1, sticky=W)
# #         title_2_board = Label(board, text="Les fiche théchniques", bg="#495a62", width=28, fg="#78b8db",
# #                               font=("Constantia", 14), anchor=W, padx=20)
# #         title_2_board.grid(row=2, sticky=W)
# #
# #         container_1_board = Frame(board, bg="#495a62", padx=30, width=900, height=580)
# #         container_1_board.grid(row=3)
# #         container_1_board.grid_propagate(0)
# #
# #         filePath = Label(container_1_board, text="Choisir les noms dus fichiers...", bg="#6a828e", width=80, anchor=W, fg="#cccccc",
# #                          font=("Constantia", 12))
# #         filePath.grid(row=2, column=0, sticky=W)
# #         chooseFile = Button(container_1_board, text="Parcourir", font=("Constantia", 12), command=fileChooser)
# #         chooseFile.grid(row=2, column=1, sticky=W)
# #
# #         # ------------------------------------------------- Status Bar ------------------------------------------------
# #         status = Label(workspace, text="Fonctionnement...", bg="#778e9a", bd=1, relief=SUNKEN, anchor=W)
# #         status.pack(side=BOTTOM, fill=X)
#
# fileName = None
# wordTokens = None
# sentTokens = None
#
# def fileChooser():
#     fileN = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
#     filePath.config(text=fileN)
#     global fileName
#     fileName = fileN
#     return
#
# def terminologyExtraction():
#     global word_tokens
#     global sentTokens
#     print(fileName)
#     f = open(fileName, "r")
#     #print(f.read())
#     data = f.read().strip()
#     print(data)
#     sentTokens = sent_tokenize(data)
#     word_tokens = word_tokenize(data)
#     print(sentTokens)
#     print(word_tokens)
#     f.close()
#     abestosTermSearch()
#     return
#
# def abestosTermSearch():
#     global sentTokens
#     abestosTerms = ["amiante", "amiant"]
#     for i in sentTokens:
#         for term in abestosTerms:
#             if term in i:
#                 print(i)
#                 text = results.cget("text") + i + "\n"
#                 results.config(text=text)
#                 break
#     return
#
# def doNothing():
#     print("OK")
#     return
#
#
# root = Tk()
# root.title('AsbestosOntology')
# root.geometry("1100x600") #You want the size of the app to be 500x500
# root.resizable(0, 0) #Don't allow resizing in the x or y direction
#
# mainFrame = Frame(root)
# mainFrame.pack()
# mainFrame.pack_propagate(0)
#
# # ------------------------------------------------- Main Menu -------------------------------------------------
# menu = Menu(mainFrame)
# root.config(menu=menu)
#
# fileMenu = Menu(menu)
# menu.add_cascade(label="Fichier", menu=fileMenu)
# fileMenu.add_command(label="Nouveau projet", command=doNothing)
# fileMenu.add_command(label="Nouveau", command=doNothing)
# fileMenu.add_separator()
# fileMenu.add_command(label="Quiter", command=mainFrame.quit)
#
# editMenu = Menu(menu)
# menu.add_cascade(label="Editer", menu=editMenu)
# editMenu.add_command(label="Copier", command=doNothing)
#
# # -------------------------------------------------- Toolbar --------------------------------------------------
# # toolbar = Frame(mainFrame, bg="blue")
# #
# # insertButt = Button(toolbar, text="Inserer une Image", command=doNothing)
# # insertButt.pack(side=LEFT, padx=2, pady=2)
# # printButt = Button(toolbar, text="Imprimer", command=doNothing)
# # printButt.pack(side=LEFT, padx=2, pady=2)
# #
# # toolbar.pack(side=TOP, fill=X)
#
# # ------------------------------------------------- Sidebar ---------------------------------------------------
# sidebar = Frame(mainFrame, bg="#3e4c54", width=200, height=600)
# sidebar.grid(row=0, column=0)
# sidebar.pack_propagate(0)
#
# space_1_sidebar = Label(sidebar, bg="#3e4c54", height=1)
# space_1_sidebar.pack()
# importFiles = Label(sidebar, bg="#6a828e", text="Importer", width=28, fg="#78b8db", font=("Constantia", 18))
# importFiles.pack()
# results = Label(sidebar, bg="#546771", text="Résultats", width=28, fg="#6ba4c3", font=("Constantia", 18))
# results.pack()
# analyze = Label(sidebar, bg="#546771", text="Analyser", width=28, fg="#6ba4c3", font=("Constantia", 18))
# analyze.pack()
#
# # ------------------------------------------------- WorkSpace -------------------------------------------------
# workspace = Frame(mainFrame, width=900, height=600)
# workspace.grid(row=0, column=1)
# workspace.pack_propagate(0)
#
# # ---------------------------------------------------- Board --------------------------------------------------
# board = Frame(workspace, bg="#495a62", width=900, height=580)
# board.pack()
# board.grid_propagate(0)
#
# space_1_board = Frame(board, bg="#495a62", height=10)
# space_1_board.grid(row=0)
# title_1_board = Label(board, text="Informations des Fichiers", bg="#495a62", width=28, fg="#78b8db",
#                       font=("Constantia", 18), anchor=W, padx=10)
# title_1_board.grid(row=1, sticky=W)
# title_2_board = Label(board, text="Les fiche théchniques", bg="#495a62", width=28, fg="#78b8db",
#                       font=("Constantia", 14), anchor=W, padx=20)
# title_2_board.grid(row=2, sticky=W)
#
# container_1_board = Frame(board, bg="#495a62", padx=30, width=900, height=580)
# container_1_board.grid(row=3)
# container_1_board.grid_propagate(0)
#
# filePath = Label(container_1_board, text="Choisir les noms dus fichiers...", bg="#6a828e", width=80, anchor=W, fg="#cccccc",
#                  font=("Constantia", 12))
# filePath.grid(row=2, column=0, sticky=W)
# chooseFile = Button(container_1_board, text="Parcourir", font=("Constantia", 12), command=fileChooser)
# chooseFile.grid(row=2, column=1, sticky=W)
#
# space_1_container_1_board = Frame(container_1_board, bg="#495a62", height=10)
# space_1_container_1_board.grid(row=3, column=1)
#
# runBtn = Button(container_1_board, text="Executer", font=("Constantia", 12), command=terminologyExtraction)
# runBtn.grid(row=4, column=1)
#
# results = Label(container_1_board, bg="#495a62",fg="white", font=("Constantia", 12), height=10, anchor=W)
# results.grid(row=5, column=0)
# # ------------------------------------------------- Status Bar ------------------------------------------------
# status = Label(workspace, text="Fonctionnement...", bg="#778e9a", bd=1, relief=SUNKEN, anchor=W)
# status.pack(side=BOTTOM, fill=X)
#
#
#
# # mainApp = MainWindow(root)
# root.mainloop()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # from nltk.tokenize import sent_tokenize, word_tokenize
# # from nltk.corpus import stopwords
# #
# #
# # example_sent = "Bonjour M. Thamer, comment allez-vous aujourd'hui? Il fait beau et Python est génial. Le ciel est gris."
# #
# # print(sent_tokenize(example_sent))
# #
# # print(word_tokenize(example_sent))
# #
# # stop_words = set(stopwords.words('french'))
# #
# # print(stop_words)
# #
# # word_tokens = word_tokenize(example_sent)
# #
# # filtered_sentence = [w for w in word_tokens if not w in stop_words]
# #
# # filtered_sentence = []
# #
# # for w in word_tokens:
# #     if w not in stop_words:
# #         filtered_sentence.append(w)
# #
# # print(word_tokens)
# # print(filtered_sentence)
#
#
# # import nltk
# # from nltk.corpus import state_union
# # from nltk.tokenize import PunktSentenceTokenizer
# #
# # train_text = "frenche"
# # sample_text = "I am a dragon"
# #
# # custom_sent_tokenizer = PunktSentenceTokenizer(train_text)
# #
# # tokenized = custom_sent_tokenizer.tokenize(sample_text)
# #
# # def process_content():
# #     try:
# #         for i in tokenized[:5]:
# #             words = nltk.word_tokenize(i)
# #             tagged = nltk.pos_tag(words)
# #             print(tagged)
# #
# #     except Exception as e:
# #         print(str(e))
# #
# #
# # process_content()
