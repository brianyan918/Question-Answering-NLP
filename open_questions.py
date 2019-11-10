## X verbs Y -> What does X verb? Y

import spacy
import textacy.extract

# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)

# The text we want to examine
text = """London is the capital and most populous city of England and  the United Kingdom.  
Standing on the River Thames in the south east of the island of Great Britain, 
London has been a major settlement for two millennia.  It was founded by the Romans, 
who named it Londinium.
"""

# Parse the document with spaCy
doc = nlp(text)
print(doc._.has_coref)
print(doc._.coref_clusters)
doc = nlp(doc._.coref_resolved)
print("Coreference Resolution:")
print(doc)


#https://stackoverflow.com/questions/47856247/extract-verb-phrases-using-spacy
"""print("Verbs:")
verb_clause_pattern = r'<VERB>*<ADV>*<PART>*<VERB>+<PART>*'
verbs = list(textacy.extract.pos_regex_matches(doc, verb_clause_pattern))
for verb in verbs:
    print(f" - {verb.text}")"""

print("Named Entities")
for entity in doc.ents:
    print(f" - {entity.text} ({entity.label_})")

# Extract semi-structured statements
svos = textacy.extract.subject_verb_object_triples(doc)

# Print the results
print("Subject, verb, object tuples:")

for svo in svos:
    subject, verb, object = svo
    print(f" - {svo}")

# Print the results
print("Here are the things I know about London:")

questions = {}
for token in doc:
    if token.pos_ == 'VERB':
        # Extract semi-structured statements
        statements = textacy.extract.semistructured_statements(doc, "London", cue=token.lemma_, ignore_entity_case=True)
        for statement in statements:
            entity, verb, fact = statement
            print(f" - " + token.text + " " + str(fact))

            if token.text == "was": # TODO: LEMMA COMPARISON
                # open-ended question: X is Y -> What is Y? X.
                # TODO: replace "What" based on type of NER
                what_is_y = "What " + token.text + " London?"
                if what_is_y in questions:
                    questions[what_is_y].append(str(fact))
                else:
                    questions[what_is_y] = [str(fact)]

print("Questions generated")
print(questions)