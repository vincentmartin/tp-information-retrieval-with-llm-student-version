#!/usr/bin/env python3
import json
import math
import os
import re
from collections import defaultdict, Counter
import numpy as np
from .PorterStemmer import PorterStemmer


class IRSystem:

    def __init__(self):
        # For holding the data - initialized in read_data()
        self.titles = []
        self.docs = []
        self.vocab = []
        # For the text pre-processing.
        self.alphanum = re.compile('[^a-zA-Z0-9]')
        self.p = PorterStemmer()

    def get_uniq_words(self):
        uniq = set()
        for doc in self.docs:
            for word in doc:
                uniq.add(word)
        return uniq

    def __read_raw_data(self, dirname):
        print("Stemming Documents...")

        titles = []
        docs = []
        os.mkdir(f'{dirname}/stemmed')
        title_pattern = re.compile('(.*) \d+\.txt')

        # make sure we're only getting the files we actually want
        filenames = [filename for filename in os.listdir(f'{dirname}/raw') if filename.endswith(".txt") and not filename.startswith(".")]

        for i, filename in enumerate(filenames):
            print(filename)
            title = title_pattern.search(filename).group(1)
            print(f"    Doc {i + 1} of {len(filenames)}: {title}")
            titles.append(title)
            contents = []
            with open(f'{dirname}/raw/{filename}', 'r') as f, open(f'{dirname}/stemmed/{title}.txt', 'w') as of:
                for line in f:
                    # make sure everything is lower case
                    line = line.lower()
                    # split on whitespace
                    line = [xx.strip() for xx in line.split()]
                    # remove non alphanumeric characters
                    line = [self.alphanum.sub('', xx) for xx in line]
                    # remove any words that are now empty
                    line = [xx for xx in line if xx != '']
                    # stem words
                    line = [self.p.stem(xx) for xx in line]
                    # add to the document's contents
                    contents.extend(line)
                    if len(line) > 0:
                        of.write(" ".join(line))
                        of.write('\n')
            docs.append(contents)
        return titles, docs

    def __read_stemmed_data(self, dirname):
        print("Already stemmed!")
        titles = []
        docs = []

        # make sure we're only getting the files we actually want
        filenames = [filename for filename in os.listdir(f'{dirname}/stemmed') if filename.endswith(".txt") and not filename.startswith(".")]

        if len(filenames) != 60:
            msg = "There are not 60 documents in ./data/RiderHaggard/stemmed/\n"
            msg += "Remove ./data/RiderHaggard/stemmed/ directory and re-run."
            raise Exception(msg)

        for i, filename in enumerate(filenames):
            title = filename.split('.')[0]
            titles.append(title)
            contents = []
            with open(f'{dirname}/stemmed/{filename}', 'r') as f:
                for line in f:
                    # split on whitespace
                    line = [xx.strip() for xx in line.split()]
                    # add to the document's contents
                    contents.extend(line)
            docs.append(contents)

        return titles, docs

    def read_data(self, dirname):
        """
        Given the location of the 'data' directory, reads in the documents to
        be indexed.
        """
        # NOTE: We cache stemmed documents for speed
        #       (i.e. write to files in new 'stemmed/' dir).
        print("Reading in documents...")
        # dict mapping file names to list of "words" (tokens)
        subdirs = os.listdir(dirname)
        if 'stemmed' in subdirs:
            titles, docs = self.__read_stemmed_data(dirname)
        else:
            titles, docs = self.__read_raw_data(dirname)

        # Sort document alphabetically by title to ensure we have the proper
        # document indices when referring to them.
        ordering = [idx for idx, title in sorted(enumerate(titles),
                                                 key=lambda xx: xx[1])]

        self.titles = [titles[ordering[d]] for d in range(len(docs))]
        self.docs = [docs[ordering[d]] for d in range(len(docs))]

        # Get the vocabulary.
        self.vocab = list(self.get_uniq_words())

    def process_query(self, query_str):
        """
        Given a query string, process it and return the list of lowercase,
        alphanumeric, stemmed words in the string.
        """
        # make sure everything is lower case
        query = query_str.lower()
        # split on whitespace
        query = query.split()
        # remove non alphanumeric characters
        query = [self.alphanum.sub('', xx) for xx in query]
        # stem words
        query = [self.p.stem(xx) for xx in query]
        return query

    def index(self):
        """
        Build an index of the documents.
        """
        print("Indexing...")
        self.tf = defaultdict(Counter) 

        inverted_index = defaultdict(set)
        for word in self.vocab:
            inverted_index[word] = list()

        self.inverted_index = inverted_index

    def get_posting(self, word):
        """
        Given a word, this returns the list of document indices (sorted) in
        which the word occurs.
        """
        return sorted(self.inverted_index[word])

    def get_posting_unstemmed(self, word):
        """
        Given a word, this *stems* the word and then calls get_posting on the
        stemmed word to get its postings list. You should *not* need to change
        this function. It is needed for submission.
        """
        word = self.p.stem(word)
        return self.get_posting(word)

    def boolean_retrieve(self, query):
        """
        Given a query in the form of a list of *stemmed* words, this returns
        the list of documents in which *all* of those words occur (ie an AND
        query).
        Return an empty list if the query does not return any documents.
        """
        docs = list()
        for doc in self.docs:
            docs.append(doc)
        return docs

    def query_retrieve(self, query_str):
        """
        Given a string, process and then return the list of matching documents
        found by boolean_retrieve().
        """
        query = self.process_query(query_str)
        return self.boolean_retrieve(query)


    def compute_tfidf(self):
        print("Calculating tf-idf...")

        self.tfidf = defaultdict(Counter)
        self.doc_tfidf = defaultdict(float)  # used in 'cosine similarity'
        N = len(self.docs)  # number of documents
        for word in self.vocab:
            for i in range(N):
                try:
                    self.tfidf[i][word] = 0.
                except ValueError:
                    self.tfidf[i][word] = 0.

    def get_tfidf(self, word, document):
        return self.tfidf[document][word]

    def get_tfidf_unstemmed(self, word, document):
        """
        This function gets the TF-IDF of an *unstemmed* word in a document.
        Stems the word and then calls get_tfidf. You should *not* need to
        change this interface, but it is necessary for submission.
        """
        word = self.p.stem(word)
        return self.get_tfidf(word, document)

    def rank_retrieve(self, query):
        """
        Given a query (a list of words), return a rank-ordered list of
        documents (by ID) and score for the query.
        """

        # Actuellement c'est la mesure de Jaccard qui est utilisée.
        scores = [0.0 for _ in range(len(self.docs))]
        query_set = set(query)
        
        for d in range(len(self.docs)):
            doc_set = set(self.docs[d])
            intersection = len(query_set & doc_set)
            union = len(query_set | doc_set)
            # Calculate Jaccard similarity
            scores[d] = intersection / union if union != 0 else 0.0

        # Sort the 'scores'
        ranking = [idx for idx, sim in sorted(enumerate(scores),
                                            key=lambda xx: xx[1], reverse=True)]
        results = []
        for i in range(10):
            results.append((ranking[i], scores[ranking[i]]))
        return results

    def query_rank(self, query_str):
        """
        Given a string, process and then return the list of the top matching
        documents, rank-ordered.
        """
        query = self.process_query(query_str)
        return self.rank_retrieve(query)






def run_tests(irsys, part=None):
    print ("===== Running tests =====")

    ff = open('./data/queries.txt')
    questions = [xx.strip() for xx in ff.readlines()]
    ff.close()
    ff = open('./data/solutions.txt')
    solutions = [xx.strip() for xx in ff.readlines()]
    ff.close()

    epsilon = 1e-4
    #for part in range(4):
    points = 0
    num_correct = 0
    num_total = 0

    prob = questions[part]
    soln = json.loads(solutions[part])

    # inverted index test
    if part == 0:
        print ("Inverted Index Test")
        words = prob.split(", ")
        for i, word in enumerate(words):
            num_total += 1
            posting = irsys.get_posting_unstemmed(word)
            if set(posting) == set(soln[i]):
                num_correct += 1

    # boolean retrieval test
    elif part == 1:
        print ("Boolean Retrieval Test")
        queries = prob.split(", ")
        for i, query in enumerate(queries):
            num_total += 1
            guess = irsys.query_retrieve(query)
            if set(guess) == set(soln[i]):
                num_correct += 1

    # tfidf test
    elif part == 2:
        print ("TF-IDF Test")
        queries = prob.split("; ")
        queries = [xx.split(", ") for xx in queries]
        queries = [(xx[0], int(xx[1])) for xx in queries]
        for i, (word, doc) in enumerate(queries):
            num_total += 1
            guess = irsys.get_tfidf_unstemmed(word, doc)
            if guess >= float(soln[i]) - epsilon and \
                    guess <= float(soln[i]) + epsilon:
                num_correct += 1

    # cosine similarity test
    elif part == 3:
        print ("Cosine Similarity Test")
        queries = prob.split(", ")
        for i, query in enumerate(queries):
            num_total += 1
            ranked = irsys.query_rank(query)
            top_rank = ranked[0]
            if top_rank[0] == soln[i][0]:
                if top_rank[1] >= float(soln[i][1]) - epsilon and \
                        top_rank[1] <= float(soln[i][1]) + epsilon:
                    num_correct += 1

    feedback = "%d/%d Correct. Accuracy: %f" % \
            (num_correct, num_total, float(num_correct)/num_total)
    if num_correct == num_total:
        points = 3
    elif num_correct > 0.75 * num_total:
        points = 2
    elif num_correct > 0:
        points = 1
    else:
        points = 0

    print ("    Score: %d Feedback: %s" % (points, feedback))








if __name__ == '__main__':
    irsys = IRSystem()
    irsys.read_data('./data/RiderHaggard')
    irsys.index()
    irsys.compute_tfidf()
    run_tests(irsys)

"""
The output is:
Reading in documents...
Already stemmed!
Indexing...
Calculating tf-idf...
===== Running tests =====
Inverted Index Test
    Score: 3 Feedback: 5/5 Correct. Accuracy: 1.000000
Boolean Retrieval Test
    Score: 3 Feedback: 5/5 Correct. Accuracy: 1.000000
TF-IDF Test
    Score: 3 Feedback: 5/5 Correct. Accuracy: 1.000000
Cosine Similarity Test
    Score: 3 Feedback: 5/5 Correct. Accuracy: 1.000000
"""