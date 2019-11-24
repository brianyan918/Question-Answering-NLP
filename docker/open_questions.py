#!/usr/bin/env python3

import spacy
import textacy.extract
import re

# Load the large English NLP model
nlp = spacy.load('en_core_web_sm')

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)


class QuestionGenerator(object):
    def __init__(self, article):
        self.questions = []

        self.entity_to_pronoun = {'PERSON': 'Who', 'NORP': 'Who', 'FAC': 'Where', 'ORG': 'Which organization',
                             'GPE': 'Where', 'LOC': 'Where', 'PRODUCT': 'What', 'EVENT': 'What event',
                             'WORK_OF_ART': 'What', 'LAW': 'What', 'LANGUAGE': 'What language', 'DATE': 'When',
                             'TIME': 'When', 'PERCENT': 'What percent', 'MONEY': 'How much', 'QUANTITY': 'How much',
                            'ORDINAL':'When', 'CARDINAL': 'How many'}

        # Parse the document with spaCy
        doc = nlp(article)
        doc = nlp(doc._.coref_resolved)
        self.ner = {}
        for ent in doc.ents:
            self.ner.update({ent.text : ent.label_})
            #print(ent.text, ent.start_char, ent.end_char, ent.label_)

        # Extract semi-structured statements
        svos = textacy.extract.subject_verb_object_triples(doc)

        # open questions generated from relative clauses
        for token in doc:
            # if token.pos_ == 'VERB':
            #     # Extract semi-structured statements

            #     # TODO: find all verbs first - may be redundant (put in a set)
            #     statements = textacy.extract.semistructured_statements(doc, "London", cue=token.lemma_, ignore_entity_case=True)
            #     for statement in statements:
            #         entity, verb, fact = statement
            #         #print(f" - " + token.text + " " + str(fact))

            #         if token.text == "was": # TODO: LEMMA COMPARISON
            #             # open-ended question: X is Y -> What is Y? X.
            #             # TODO: replace "What" based on type of NER
            #             what_is_y = "What " + token.text + " London?"
            #             self.add_question(what_is_y, str(fact))
        
            if token.dep_ == "relcl": # relative clause
                # close ended question: X, who/which verb -> Who verb? X

                if token.left_edge.dep_ == "aux": # exclude infinitve clauses
                    continue

                # the relative pronoun is guaranteed to be the left child
                # right child is direct object
                """verb_phrase = doc[token.left_edge.i + 1 : token.right_edge.i + 1].text # https://spacy.io/usage/examples#subtrees
                verb_phrase = ' '.join(verb_phrase.split())
                interrogative_pronoun = token.left_edge.text
                if token.left_edge.text == "which":
                    interrogative_pronoun = "What"
                elif token.left_edge.text == "that":
                    interrogative_pronoun = "What"
                    # TODO: handle test_4 and test_5
                elif token.left_edge.text == "when":
                    interrogative_pronoun = "When did" # TODO: tense agreement with rest of verb
                elif token.left_edge.text == "where":
                    interrogative_pronoun = "Where does" # TODO: verb subject agreement (plurality) / where was
                elif token.left_edge.dep_ == "nsubj": # clause is already a sentence
                    interrogative_pronoun = "What"
                    verb_phrase = doc[token.i : token.right_edge.i + 1].text # replace the full subject of clause
                x_who_question = interrogative_pronoun.capitalize() + " " + verb_phrase + "?"
                # answer = token.head.text # the token that the relative clause refers to
                # TODO - coreference for appositives (e.g. "Jacobo, the advisor who retired - replace advisor with Jacobo")

                self.questions.append(x_who_question)
"""
                test_1 = "Colonel Sanders, who founded KFC, is my hero."
                test_2 = "Water, which is the source of all life, is made of hydrogen."
                test_3 = "Jacobo, the advisor who retired, used to teach 15-121."
                test_4 = "nlp, the course that I took, uses gradescope."
                test_5 = "Hello Kitty, the cat that cannot smile, is old."

        # SVOs to generate closed questions and open ended X verbs Y -> What does X verb?
        self.treated_verbs = []
        self.closed_questions = []
        for token_verb in doc:
            if token_verb.dep_ == 'ROOT':
                for token_subj in token_verb.lefts:
                    if token_subj.dep_ == 'nsubj':
                        if token_subj.lefts:
                            subj_left = ' '.join([t.text for t in token_subj.lefts])+' '
                        else:
                            subj_left = ''
                        if token_subj.rights:
                            subj_right = ' ' + ' '.join([t.text for t in token_subj.rights])
                        else:
                            subj_right = ''
                        token_subj_txt = (subj_left + token_subj.text + subj_right).strip()
                        if token_verb.lemma_ not in self.treated_verbs:
                            # TODO - don't rely on statements?? this will miss many sentences and is unnecessary work
                            # X verbs Y (nsubj ROOT rest -> What/why/who/when does/do/did lemma(ROOT) rest)
                            self.treated_verbs.append(token_verb.lemma_)
                            statements = textacy.extract.semistructured_statements(doc, token_subj_txt, cue=token_verb.lemma_,
                                                               ignore_entity_case=True)
                            
                            for statement in statements:
                                entity, verb, fact = statement
                                q = self.generate_open_question(entity, verb, fact, token_verb.lemma_)
                                if q:
                                    self.questions.append(q)
                                self.closed_questions.append(self.generate_closed_question(entity, verb, fact, token_verb.lemma_))

    
    def generate_open_question(self, entity, verb, fact, lemma):
        if entity.text not in self.ner and entity.text != "I":
            entity_txt = entity.text.lower()
            entity_txt = ' '.join(entity_txt.split()).strip()
        else:
            entity_txt = ' '.join(entity.text.split()).strip()
        fact_txt = ' '.join(fact.text.split()).strip()
        verb_txt = ' '.join(verb.text.split()).strip()
        if (fact_txt[-1] == '.'):
            fact_txt = fact_txt[:-1]
        # print(entity.text, entity_txt, verb.text, fact.text)
        if entity.label_ in self.entity_to_pronoun:
            w_word = self.entity_to_pronoun[entity.label_]
        elif entity_txt in self.ner:
            w_word = self.entity_to_pronoun[self.ner[entity_txt]]
        else:
            return
        if (' ' in verb.text):
            verb = verb.text.split()
            question = w_word + ' ' + verb[0] + ' ' + entity_txt + ' ' + verb[1] + '?'
        elif lemma == "be":
            # TODO: tense / agreement
            #question = "What is " + fact.text.strip() + '?'
            if verb.tag_ == "VBD":
                question = w_word + "was " + fact_txt + '?'
            else:
                question = w_word + " is " + fact_txt + '?'
            # TODO: if entity is a named entity (who) / time (when) / location (where) - what/why/who/when
        else: # X verbs Y
            #question = "What does " + entity.text + ' ' + verb.text + '?'
            """if verb.tag_ == "VBD":
                question = w_word + " did "
            elif verb.tag_ == "VBZ":
                question = w_word + " does "
            elif verb.tag_ == "VBP":
                question = w_word + " do "
            else:
                question = w_word + " did "
            if entity[0].dep_ != 'nsubjpass' and entity[0].dep_ != 'auxpass':
                question += entity_txt
            question += ' ' + lemma + " " + fact_txt + '?'"""
            if verb_txt == "are ":
                verb_txt = "is"
            #elif verb_txt.split()[0] == "have":
                #verb_txt = "has" + ' '.join(verb_txt.split()[1:])
            verb_txt = verb_txt.replace("have ", "has ")
            question = w_word + ' ' + verb_txt + ' ' + fact_txt

        # Capitalize first letter of string
        #print(question)
        return question

    def generate_closed_question(self, entity, verb, fact, lemma):
        if entity.text not in self.ner and entity.text != "I":
            entity_txt = entity.text.lower()
            entity_txt = ' '.join(entity_txt.split()).strip()
        else:
            entity_txt = ' '.join(entity.text.split()).strip()
        fact_txt = ' '.join(fact.text.split()).strip()
        verb_txt = ' '.join(verb.text.split()).strip()
        if (fact_txt[-1] == '.'):
            fact_txt = fact_txt[:-1]
        if (' ' in verb_txt): # auxiliary verbs
            verb_txt = verb_txt.split()
            question = verb_txt[0] + ' ' + entity_txt + ' ' + verb_txt[1] + ' ' + fact_txt + '?'
        elif lemma == "be":
            question = verb_txt + ' ' + entity_txt + ' ' + fact_txt + '?'
        else: # X verbs Y
            # TODO - tense matching, verb agreement
            if verb.tag_ == "VBD":
                question = "Did " + entity_txt + ' ' + lemma + " " + fact_txt + '?'
            elif verb.tag_ == "VBZ":
                question = "Does " + entity_txt + ' ' + lemma + " " + fact_txt + '?'
            elif verb.tag_ == "VBP":
                question = "Do " + entity_txt + ' ' + lemma + " " + fact_txt + '?'
            else:
                question = "Did " + entity_txt + ' ' + lemma + " " + fact_txt + '?'

        # Capitalize first letter of string
        question = re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), question, 1)
        return question

    def post_process(self, question):
        # TODO: fix plural agreement between subject and verb
        return question

    def get_questions(self):
        questions = self.questions + self.closed_questions
        # postprocess the questions
        return questions