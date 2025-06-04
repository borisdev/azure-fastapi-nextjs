"""
poetry add https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz
"""

import time

import scispacy
import spacy

nlp = spacy.load("en_core_web_md")
start_time = time.time()
text = "My Oura ring says my REM is low. What can I do to improve it?"
text = "What is the relationship between REM and deep sleep and Dreaming?"
doc = nlp(text)

for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
print("Spacy MD:  %s seconds ---" % (time.time() - start_time))


nlp = spacy.load("en_core_sci_sm")
start_time = time.time()
doc = nlp(text)
for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
print("Scispacy SM:  %s seconds ---" % (time.time() - start_time))
