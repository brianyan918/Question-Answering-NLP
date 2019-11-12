import spacy
import textacy.extract
import re
import numpy as np

# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)

class AnswerGenerator():
    def __init__(self, text):
        self.answers = {}
        self.text = text

    def add_answer(self, question, answer):
        if question in self.answers:
            self.answers[question].append(answer)
        else:
            self.answers[question] = [answer]

    def answer_generator(self, question):
        #generate set of words in current question
        question_set = set()
        question_words = re.split("\W+", question)
        for word in question_words:
            if len(word) != 0:
                question_set.add(word)

        #transform text to list of sentences
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
        doc = nlp(self.text)
        sentences = [sent.string.strip() for sent in doc.sents]
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
        self.add_answer(question, sentences[np.argmax(sentence_difference)])

        # print(self.answers[question])

        return sentences[np.argmax(sentence_difference)]
