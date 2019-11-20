#!/usr/bin/env python3
## X verbs Y -> What does X verb? Y

import spacy
import textacy.extract
import re

# Load the large English NLP model
nlp = spacy.load('en_core_web_sm')

# Add neural coref to SpaCy's pipe
#import neuralcoref
#neuralcoref.add_to_pipe(nlp)


class QuestionGenerator(object):
    def __init__(self, article):
        self.questions = {}

        # Parse the document with spaCy
        doc = nlp(article)
        #doc = nlp(doc._.coref_resolved)

        # Extract semi-structured statements
        svos = textacy.extract.subject_verb_object_triples(doc)

        # open questions
        for token in doc:
            print(token.text, token.dep_)
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
                verb_phrase = doc[token.left_edge.i + 1 : token.right_edge.i + 1].text # https://spacy.io/usage/examples#subtrees
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
                answer = token.head.text # the token that the relative clause refers to
                # TODO - coreference for appositives (e.g. "Jacobo, the advisor who retired - replace advisor with Jacobo")

                self.add_question(x_who_question, answer)

                test_1 = "Colonel Sanders, who founded KFC, is my hero."
                test_2 = "Water, which is the source of all life, is made of hydrogen."
                test_3 = "Jacobo, the advisor who retired, used to teach 15-121."
                test_4 = "nlp, the course that I took, uses gradescope."
                test_5 = "Hello Kitty, the cat that cannot smile, is old."

        # Closed Questions
        self.treated_verbs = []
        questions = []
        for token_verb in doc:
            if token_verb.dep_ == 'ROOT':
                for token_subj in token_verb.lefts:
                    if token_subj.dep_ == 'nsubj':
                        if token_verb.lemma_ not in self.treated_verbs:
                            questions += self.generate_closed_question(doc, token_subj.text, token_verb)
        self.closed_questions = questions

    def generate_closed_question(self, doc, subject, verb_token):
        questions = []
        statements = textacy.extract.semistructured_statements(doc, subject, cue=verb_token.lemma_,
                                                               ignore_entity_case=True)
        self.treated_verbs.append(verb_token.lemma_)
        for statement in statements:
            entity, verb, fact = statement
            if (' ' in verb.text):
                verb = verb.text.split()
                question = verb[0] + ' ' + entity.text + ' ' + verb[1] + ' ' + fact.text.strip() + '?'
            else:
                question = verb.text + ' ' + entity.text + ' ' + fact.text.strip() + '?'
            # Capitalize first letter of string
            question = re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), question, 1)
            questions.append(question)
        return (questions)

    def add_question(self, question, answer):
        if question in self.questions:
            self.questions[question].append(answer)
        else:
            self.questions[question] = [answer]

    def questions_only(self):
        return list(self.questions.keys())