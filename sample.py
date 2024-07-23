import spacy

nlp = spacy.load('en_core_web_sm')

def active_to_passive(sentence):
    # Parse the sentence using spaCy
    doc = nlp(sentence)
    
    # Identify subject, object, and verb
    subject = None
    passive_subject = None
    verb = None
    object_phrase = None
    
    for token in doc:
        if token.dep_ == 'nsubj':
            subject = token.text
        elif token.dep_ == 'aux' and token.head.pos_ == 'VERB':
            verb = token.head.text
        elif token.dep_ == 'nsubjpass':
            passive_subject = token.text
        elif token.dep_ == 'ROOT' and token.pos_ == 'VERB':
            verb = token.text
        elif token.dep_ == 'dobj' or token.dep_ == 'attr':
            object_phrase = token.text
            
    if subject and verb and object_phrase:
        # Build passive voice sentence
        passive_sentence = f"{object_phrase} {verb} {passive_subject} by {subject}"
        return passive_sentence.capitalize()
    else:
        return "Unable to convert to passive voice"

# Example usage:
active_sentence = "They are building a new bridge"
passive_sentence = active_to_passive(active_sentence)
print(f"Active voice: {active_sentence}")
print(f"Passive voice: {passive_sentence}")
