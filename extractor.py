import spacy
import textacy.extract
<<<<<<< HEAD
import question_generator as qg

=======
import sys

article_txt = sys.argv[1]
with open(article_txt, 'r', encoding='utf8') as f:
    article_txt = f.read()
>>>>>>> 6b5ec5dc945d4b3a587d5121340b14a67915b65f

# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)

# Parse the document with spaCy
doc = nlp(article_txt)
print(doc._.has_coref)
print(doc._.coref_clusters)
doc = nlp(doc._.coref_resolved)
print("Coreference Resolution:")
print(doc)

#for token in doc:
#    print(token, token.tag_, token.pos_)

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
for token in doc:
    if token.pos_ == 'VERB':
        # Extract semi-structured statements
        statements = textacy.extract.semistructured_statements(doc, "London", cue=token.lemma_, ignore_entity_case=True)
        for statement in statements:
            entity, verb, fact = statement
<<<<<<< HEAD
            print(f" - " + token.text + " " + str(fact))
        qg.generate_closed_question(doc, "London", token)
=======
            print(f" - " + str(fact))
>>>>>>> 6b5ec5dc945d4b3a587d5121340b14a67915b65f
