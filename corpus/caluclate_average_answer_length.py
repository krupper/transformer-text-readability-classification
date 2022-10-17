import json
import re
from spacy_langdetect import LanguageDetector
from spacy.language import Language
import spacy


#
# Calculates the average length of a chatbot answer based in the KMI chatbot.
# Median answer length [sentences]: 2.23728813559322
#

TAG_RE = re.compile(r'<[^>]+>')


def count_words(sent):
    list_of_non_word_pos = ["PUNCT", "NUM", "SYM", "SPACE"]
    count = 0

    for token in sent:
        if token.pos_ not in list_of_non_word_pos:
            count += 1
    return count

@Language.factory("language_detector")
def create_language_detector(nlp, name):
    return LanguageDetector(language_detection_function=None)


def remove_tags(text):
    return TAG_RE.sub('', text)


if __name__ == '__main__':


    # Propagate spacy globally to reduce the time per task
    nlp = spacy.load("de_dep_news_trf")

    # Add language detection
    nlp.add_pipe("language_detector")

    f = open("../skill-KIMI_DE(6).json")

    data = json.load(f)



    number_of_answers = 0
    number_of_words = 0
    number_of_sentences = 0

    for i in data["dialog_nodes"]:
        try:
            for j in i["output"]["generic"]:
                for k in j["values"]:
                    text = remove_tags(k["text"])

                    if text == "":
                        continue

                    doc = nlp(text)

                    if doc._.language["language"] != "de":
                        continue

                    sentences = [sent for sent in doc.sents]
                    number_of_sentences += len(sentences)
                    number_of_words += count_words(doc)
                    number_of_answers += 1

                    print(text, len(sentences))
        except:
            a = False

    print("Average number of words per answer:", number_of_words / number_of_answers)
    print("Average number of sentences per answer:", number_of_sentences / number_of_answers)
    print("Number of answers:", number_of_answers)

    f.close()
