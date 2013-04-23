difficulty = 0

print "Welcome to SNAEL, version 1.0"

from time import gmtime, strftime
print strftime("%X", gmtime())

available_texts = ['../text/' + i for i in \
                   ['simple.txt', # BBC 2009 national
                    'highwayman.txt', # http://fiction.homepageofthedead.com/forum.pl?readfiction=1047H
                    '135.txt']] # Les Miserables

FILE_NAME = available_texts[difficulty]

class Entity:
    def __init__(self, name):
        self.names = set([name])
        self.occurances = set()

    def find_occurances(self, text):
        for sentence in text:
            for name in self.names:
                if name in sentence:
                    self.occurances.add(text.index(sentence))
        try:
            self.common_name = sorted(list(self.occurances))[0]
        except:
            self.common_name = 'Error:NoOccurance'

    def same(self, entity, threshold=.6):
        """Absorbs `entity` into self if `entity` and self are sufficiently
 similar.
        
        Arguments:
        - `self`:
        - `entity`:
        """
        
        similarity = 0.0

        for my_name in self.names:
            for your_name in entity.names:
                if same(my_name, your_name):
                    similarity += 1

        similarity_ratio = similarity / (len(self.names)*len(entity.names))

        return similarity_ratio >= threshold

    def absorb(self, entity):
        """Absorbs another entity
        
        Arguments:
        - `self`:
        - `entity`:
        """
        self.names |= entity.names
        self.occurances |= entity.occurances

    def __str__(self):
        r = "{!"
        for name in self.names:
            r += "{%s}" % name
        r += "}"
        return r

## {{{ http://code.activestate.com/recipes/578228/ (r5)
import sys

class ProgressBar:
    def __init__(self, minValue = 0, maxValue = 100, totalWidth=75):
        """ Initializes the progress bar. """
        self.progBar = ""   # This holds the progress bar string
        self.oldprogBar = ""
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done 
        self.updateAmount(0)  # Build progress bar string
        
    def appendAmount(self, append):
        """ Increases the current amount of the value of append and 
        updates the progress bar to new ammount. """
        self.updateAmount(self.amount + append)
    
    def step(self):
        self.appendAmount(1)
    
    def updatePercentage(self, newPercentage):
        """ Updates the progress bar to the new percentage. """
        self.updateAmount((newPercentage * float(self.max)) / 100.0)

    def updateAmount(self, newAmount = 0):
        """ Update the progress bar with the new amount (with min and max
        values set at initialization; if it is over or under, it takes the
        min or max value as a default. """
        if newAmount < self.min: newAmount = self.min
        if newAmount > self.max: newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self.amount - self.min)
        percentDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = int(round(percentDone))

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        # Build a progress bar with an arrow of equal signs; special cases for
        # empty and full
        if numHashes == 0:
            self.progBar = "[>%s]" % (' '*(allFull-1))
        elif numHashes == allFull:
            self.progBar = "[%s]" % ('='*allFull)
        else:
            self.progBar = "[%s>%s]" % ('='*(numHashes-1), ' '*(allFull-numHashes))

        # figure out where to put the percentage, roughly centered
        percentPlace = (len(self.progBar) / 2) - len(str(percentDone))
        percentString = str(percentDone) + "%"

        # slice the percentage into the bar
        self.progBar = ' '.join([self.progBar, percentString])
    
    def draw(self):
        """ Draws the progress bar if it has changed from it's previous value.  """
        if self.progBar != self.oldprogBar:
            self.oldprogBar = self.progBar
            sys.stdout.write('\b'*len(self.progBar)+self.progBar)
#            sys.stdout.write(self.progBar + '\r')
            sys.stdout.flush()      # force updating of screen

    def __str__(self):
        """ Returns the current progress bar. """
        return str(self.progBar)
## end of http://code.activestate.com/recipes/578228/ }}}

if __name__ == '__main__':
    with open(FILE_NAME, 'r') as f:
        print '>reading file: ' + FILE_NAME
        raw = ''.join(f.readlines())
        print '>file read'

    print '>importing nltk'
    import nltk
    print '>tokenizing'
    tokens = nltk.sent_tokenize(raw)
    tokens = [t.replace('\n',' ').replace('  ',' ') \
              for t in tokens if t is not '.']

    print '>converting to nltk.Text'
    text = nltk.Text(tokens)


    grammer = r'NAME: {<NNP>+(<DT>?<NNP>+)?}'
    ne_chunker = nltk.RegexpParser(grammer)
    entities = lambda text: \
               ne_chunker.parse( \
                                 nltk.pos_tag( \
                                               nltk.word_tokenize(text)))

    print '>tagging entire text'
    
    tag_bar = ProgressBar(maxValue=len(text))

    tagged_sentences = list()

    for sentence in text:
        tagged_sentences.append(entities(sentence))
        tag_bar.step()
        tag_bar.draw()

    def get_names_from_sentence(sentence):
        """Extracts the names from a single sentence and returns them in a
        list.

        """

        names = list()

        production_names = sentence.productions()[1:]

        names_tagged = [tag.rhs() for tag in production_names]
    
        for name in names_tagged:
            this_name = [tag[0] for tag in name]
            names.append(' '.join(this_name))

        return names

    def get_names_from_text(text):
        """Extracts all names from a text.
        """
        print '>getting names from text'
        
        name_bar = ProgressBar(maxValue=len(text))

        names = set()
        
        for sentence in text:
            names = names.union(get_names_from_sentence(sentence))
            name_bar.step()
            name_bar.draw()

        return list(names)

    names = get_names_from_text(tagged_sentences)


    print '>finding occurances of each person'
    people = [Entity(name) for name in names]
    occur_bar = ProgressBar(maxValue=len(people))
    for person in people:
        person.find_occurances(text)
        occur_bar.step()
        occur_bar.draw()

    def same(name1, name2, treshold=.5):
        """Compares two names and determines if they refer to the same person.
    
        Arguments:
        - `name1`: A name
        - `name2`: A name
        """
        if name1 is name2:
            #    print 'Identical'
            return True
        if name1 in name2 or name2 in name1:
            #    print 'Contained'
            return True

        import ngram
 
        s = ngram.NGram.compare(name1, name2)
 
        if s > treshold:
            print '{} is {} (confidence {})'.format(name1, name2, s)
            return True
        return False

    people = sorted(people,
                    key=lambda entity: len(entity.occurances),
                    reverse=True)

    from itertools import combinations

    for entity1, entity2 in combinations(people, 2):
        if entity1.same(entity2):
            again = True
            entity1.absorb(entity2)
            people.remove(entity2)
            break

    import networkx as nx
    network = nx.Graph()

    node_bar = ProgressBar(maxValue=len(people))


    print '>Add nodes to graph'
    for person in people:
        network.add_node(person, label=person.common_name, weight=len(person.occurances))
        node_bar.step()
        node_bar.draw()

    from itertools import combinations

    pairs = list(combinations(people, 2))

    print 'Finding co-occurences'
    edge_bar = ProgressBar(maxValue=len(pairs))


    radius = 5
    for A, B in pairs:
        i = 0
        a = sorted(list(A.occurances))
        b = sorted(list(B.occurances))
        if len(a) is 0 or len(b) is 0:
            edge_bar.step()
            edge_bar.draw()
            continue
        maxi = len(B.occurances) - 1
        for oA in a:
            lo = oA - radius
            hi = oA + radius
            while (b[i] > lo) and (i > 0):     # while we're above the low end of the range
                i = i - 1                      #   go towards the low end of the range
            while (b[i] < lo) and (i < maxi):  # while we're below the low end of the range
                i = i + 1                      #   go towards the low end of the range
            if b[i] >= lo:
                while (b[i] <= hi):            # while we're below the high end of the range
                    try:                       #   increase edge weight
                        network.edge[A.common_name][B.common_name]['weight'] += 1
                    except:
                        network.add_edge(A.common_name, B.common_name, weight=1)

                    if i < maxi:               #   and go towards the high end of the range
                        i = i + 1
                    else:
                        break
        edge_bar.step()
        edge_bar.draw()
    # radius = 5
    # for A, B in pairs:
    #     for oA in A.occurances:
    #         for oB in B.occurances:
    #             if oB > oA + radius + 1:
    #                 break
    #             if oB in range(oA-radius, oA+radius):
    #                 try:
    #                     network.edge[A.common_name][B.common_name]['weight'] += 1
    #                 except:
    #                     network.add_edge(A.common_name, B.common_name, weight=1)
    #             edge_bar.step()
    #     edge_bar.draw()

    

    print 'Writing output...',

    def getname(filepath):
        b = filepath.rfind('/') + 1
        e = filepath.rfind('.')
        return filepath[b:e]

    nx.write_gexf(network, 'network-{}.gexf'.format(getname(FILE_NAME)))
    print 'Done.  Program complete.'

    from time import gmtime, strftime
    print strftime("%X", gmtime())

