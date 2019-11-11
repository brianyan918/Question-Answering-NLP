import spacy
import textacy.extract
import re

# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)

# List of verbs we have already generated closed questions with
treated_verbs = []

def generate_closed_question(doc, subject, verb_token):
    questions = []
    statements = textacy.extract.semistructured_statements(doc, subject, cue = verb_token.lemma_, ignore_entity_case=True)
    treated_verbs.append(verb_token.lemma_)
    for statement in statements:
        entity, verb, fact = statement
        if (' ' in verb.text):
            verb = verb.text.split()
            question = verb[0]+' '+entity.text+' '+verb[1]+' '+fact.text.strip()[:-1]+'?'
        else:
            question = verb.text+' '+entity.text+' '+fact.text.strip()[:-1]+'?'
        # Capitalize first letter of string
        question = re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), question, 1)
        questions.append(question)
    return(questions)


text = """London is the capital and most populous city of England and the United Kingdom.  
Standing on the River Thames in the south east of the island of Great Britain, 
London has been a major settlement for two millennia. It was founded by the Romans, 
who named it Londinium.
"""

# Parse the document with SpaCy
def main(text):
    doc = nlp(text)

    questions = []

    for token_verb in doc:
        if token_verb.dep_ == 'ROOT':
            for token_subj in token_verb.lefts:
                if token_subj.dep_ == 'nsubj':
                    if token_verb.lemma_ not in treated_verbs:
                        questions += generate_closed_question(doc, token_subj.text, token_verb)

    # for question in questions:
    #     print(question)
    return questions
