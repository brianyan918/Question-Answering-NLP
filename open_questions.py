## X verbs Y -> What does X verb? Y

import spacy
import textacy.extract

# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)


questions = {}
def add_question(question, answer):
    if question in questions:
        questions[question].append(answer)
    else:
        questions[question] = [answer]


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

for token in doc:
    if token.pos_ == 'VERB':
        # Extract semi-structured statements

        # TODO: find all verbs first - may be redundant (put in a set)
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
    
    if token.dep_ == "relcl": # relative clause
        # close ended question: X, who/which verb -> Who verb? X

        # the relative pronoun is guaranteed to be the left child
        # right child is direct object
        verb_phrase = doc[token.left_edge.i + 1 : token.right_edge.i + 1].text # https://spacy.io/usage/examples#subtrees
        interrogative_pronoun = token.left_edge.text
        if token.left_edge.text == "which":
            interrogative_pronoun = "what"
        elif token.left_edge.text == "that":
            interrogative_pronoun = "which"
            # TODO: handle test_4 and test_5
        x_who_question = interrogative_pronoun + " " + verb_phrase + "?"
        answer = token.head.text # the token that the relative clause refers to
        # TODO - coreference for appositives (e.g. "Jacobo, the advisor who retired - replace advisor with Jacobo")

        add_question(x_who_question, answer)

        test_1 = "Colonel Sanders, who founded KFC, is my hero."
        test_2 = "Water, which is the source of all life, is made of hydrogen."
        test_3 = "Jacobo, the advisor who retired, used to teach 15-121."
        test_4 = "nlp, the course that I took, uses gradescope."
        test_5 = "Hello Kitty, the cat that cannot smile, is old."

print("Questions generated")
print(questions)