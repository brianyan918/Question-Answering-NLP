#!/usr/bin/env python3
import spacy
import textacy.extract
import re
import numpy as np
from functools import reduce

# Load the large English NLP model
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe(nlp.create_pipe('sentencizer'))

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)

class AnswerGenerator():
    def __init__(self, text):
        self.answer = ''
        self.text = text
        self.doc_original = nlp(self.text)
        self.doc = nlp(self.doc_original._.coref_resolved)

        self.pronoun_to_entity = {'Who':{'PERSON', 'NORP'}, 
                    'Where':{'FAC', 'ORG', 'GPE', 'LOC'},
                    'How many':{'CARDINAL', 'DATE'},
                    'How much':{'QUANTITY', 'PERCENT', 'MONEY'},
                    'What percent':{'PERCENT'},
                    'When':{'TIME', 'ORDINAL', 'EVENT', 'DATE'},
                    'What':{'PRODUCT', 'WORK_OF_ART', 'LAW', 'LANGUAGE', 'NORP', 'ORG'}}

        self.closed_question_lemmas = {'be', 'has', 'do'}

    def add_answer(self, question, doc_a, doc_a_original):
        # Remove named entity repetitions cause by Neural Coref.
        potential_NE_answers = set()
        #doc_a = nlp(answer)
        doc_q = nlp(question)
        doc_q_set = [ner.text for ner in doc_q.ents]

        # wh word may not be the first word(s)
        question_word = None
        for wh_word in self.pronoun_to_entity.keys():
            if wh_word.lower() in question.lower():
                question_word = wh_word
                
        for ner in doc_a.ents:
            # If w_word of the question is a real w_word and ner is not in the question
            if question_word and ner.text.strip() not in doc_q_set:
                if ner.label_ in self.pronoun_to_entity[question_word]:
                    potential_NE_answers.add(ner)
        if len(potential_NE_answers) == 1:
            self.answer = potential_NE_answers.pop().text
        # elif len(potential_NE_answers) > 1:
        #     # rank the answers
        else:
            # Remove named entity repetitions cause by Neural Coref.
            found = False
            start_token = ''
            answer = []
            for token in doc_a:
                if token._.in_coref and not found:
                    found = True
                if not token._.in_coref and found:
                    start_token = token.text
                    break

                answer.append(token.text)

            original_found = False
            for token in doc_a_original:
                if token.text == start_token and not original_found:
                    original_found = True
                if original_found:
                    answer.append(token.text)
        # print(answer)

            stripped_answer = ''
            for word in answer:
                if word not in [',', '.', '!', '?', "'s"]:
                    stripped_answer+=' '+word
                else:
                    stripped_answer+=word


            self.answer = ' '.join(stripped_answer.strip().split())

            # closed (yes / no) questions
            if doc_q[0].lemma_ in self.closed_question_lemmas:
                # check if question is contained in the proposed answer
                #print(doc_q)
                #print(doc_a)
                for word in doc_q[1:]: # exclude the question phrase
                    if word.text == "?" or re.match(r'\s', word.text) or word.text == '\'s':
                        continue
                    if word.text.lower() not in self.answer.lower():
                        # Has the verb changed
                        if (word.pos_ == 'VERB'):
                            lemma_in_answer = False
                            for word_a in doc_a_original:
                                if word.lemma_ == word_a.lemma_:
                                    lemma_in_answer = True
                            if not lemma_in_answer:
                                self.answer = 'No'
                                return
                        
                        # Have the other important words of the sentence been changed
                        elif (word.pos_ not in ['ADP', 'AUX', 'DET', 'SCONJ', 'PUNCT']):
                            word_in_answer = False
                            for word_a in doc_a:
                                if word.text == word_a.text and word.dep_ == word_a.dep_:
                                    word_in_answer = True

                            if not word_in_answer:
                                self.answer = 'No'
                                return
                
                self.answer = 'Yes'


    def answer_generator(self, question):
        #generate set of words in current question
        question_set = set()
        question_words = re.split("\W+", question)
        for word in question_words:
            if len(word) != 0:
                question_set.add(word)

        #transform text to list of sentences
        sentences = [' '.join((sent.string.strip()).split()) for sent in self.doc.sents]
        sentence_difference = []

        #check all the sentences for the similarity with the question set
        for sentence in sentences:
            curr_sentence_set = set()
            sentence = re.split("\W+", sentence)
            for word in sentence:
                if len(word) != 0:
                    curr_sentence_set.add(word)
            sentence_difference.append(len(curr_sentence_set.intersection(question_set)))

        #add the sentence most similar to the question to the answer set.
        token_sentences_original = [sent for sent in self.doc_original.sents]
        token_sentences_corefered = [sent for sent in self.doc.sents]
        sentence_position_in_text = np.argmax(sentence_difference)

        self.add_answer(question, token_sentences_corefered[sentence_position_in_text],
                                  token_sentences_original[sentence_position_in_text])

        # print(self.answers[question])

        #return sentences[np.argmax(sentence_difference)]
        return ' '.join(self.answer.split())
