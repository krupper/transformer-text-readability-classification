import os
import re
import spacy
import hashlib
import sqlite3
import csv
import time
import glob
from multiprocessing import Process, Queue, JoinableQueue
from spacy_langdetect import LanguageDetector
from spacy.language import Language


class Consumer(Process):

    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                print('{}: Exiting'.format(proc_name))
                self.task_queue.task_done()
                break
            # print('{}: {}'.format(proc_name, next_task))
            answer = next_task()

            self.task_queue.task_done()
            self.result_queue.put(answer)


class Task:

    def __init__(self, config):
        self.file_path = config["file_path"]
        self.source_name = config["source_name"]

    def __call__(self):
        with open(self.file_path, 'r') as f:
            try:
                content = f.read()
                f.close()

                # return preprocess_easy_to_read(content, self.source_name)
                # return preprocess_everyday(content, self.source_name)
                # return preprocess_deu_news_2021(content, self.source_name)
                return preprocess_springer_link(content, self.source_name)

            except UnicodeDecodeError:
                print("UTF-8 Error: ", self.file_path)

    def __str__(self):
        return '{self.file_path}'.format(self=self)

@Language.factory("language_detector")
def create_language_detector(nlp, name):
    return LanguageDetector(language_detection_function=None)


# Propagate spacy globally to reduce the time per task
nlp = spacy.load("de_dep_news_trf")

# Add language detection
nlp.add_pipe("language_detector")

def count_words(sent):
    list_of_non_word_pos = ["PUNCT", "NUM", "SYM", "SPACE"]
    count = 0

    for token in sent:
        if token.pos_ not in list_of_non_word_pos:
            count += 1
    return count


def remove_non_alpha_chars_from_start(text):
    if len(text) == 0:
        return ""

    output = ""

    start = False
    for char in list(text):
        if start:
            output += char

        if not start and char.isalpha():
            start = True
            output += char

    return output


def find_sentence_start(lines, index):
    if index == 0:
        return False

    sentence_start = ""

    for i in range(index - 1, 0, -1):
        p = lines[i].strip()

        if p == "":
            continue

        if not p[-1] in ['.', '!', '?']:
            sentence_start = p + " " + sentence_start

            # Break after a enumeration
            if p[-1] == ":" and p[0].isupper():
                break

    if len(sentence_start) > 0 and sentence_start[0].isupper():
        return sentence_start

    return False


def calculate_cleanup_rate(original_text, processed_text):
    original_chars = list(original_text)
    processed_chars = list(processed_text)

    original_count = 0
    for token in original_chars:
        if token not in [' ', '\n']:
            original_count += 1

    processed_count = 0
    for token in processed_chars:
        if token not in [' ', '\n']:
            processed_count += 1

    if original_count == 0:
        return -1

    return 1 - (processed_count / original_count)


def preprocess_springer_link(content, source):
    content = content.replace(u'\xa0', u' ')

    # remove brackets
    content = re.sub(r"\((.*?)\)", "", content)
    content = re.sub(r"\[(.*?)\]", "", content)
    content = re.sub(r"\{(.*?)\}", "", content)

    # remove single brackets
    content = content.replace("(", "")
    content = content.replace(")", "")
    content = content.replace("[", "")
    content = content.replace("]", "")
    content = content.replace("{", "")
    content = content.replace("}", "")

    output = ""

    # Expect every paragraph on a line level to remove headings etc.
    lines = content.splitlines()

    for index, line in enumerate(lines):
        # remove leading and tailing whitespaces
        line = line.strip()
        line = line.replace(" ,", ",")
        line = line.replace(" :", ":")
        line = line.replace(" .", ".")
        line = line.replace(" ?", "?")
        line = line.replace(" !", "!")

        if line == "":
            continue

        if not line[0].isalnum():
            continue

        output += line + "\n"

    # Do some general cleanup
    output = re.sub(r'\s+', ' ', output)

    # Detect sentences in paragraphs
    doc = nlp(output)

    sentences = []
    processed_text = ""

    for sent in doc.sents:
        sentence = str(sent)

        sentence = sentence.replace(" ,", ",")
        sentence = sentence.replace(" :", ":")
        sentence = sentence.replace(" .", ".")
        sentence = sentence.replace(" ?", "?")
        sentence = sentence.replace(" !", "!")

        # skip non german sentences
        if sent._.language["language"] != "de" or sent._.language["score"] < 0.95:
            continue

        if sentence[-1] not in ['.', '!', '?']:
            continue

        if sentence == ".":
            continue

        if not sentence[0].isupper() and not sentence[0].isnumeric():
            continue

        numer_of_words = count_words(sent)
        if numer_of_words < 3:
            continue

        processed_text += sentence + "\n"
        print(sentence)

        entry = {
            "text": sentence,
            "number_of_words": numer_of_words,
            "hash": hashlib.sha256(str.encode(sentence)).hexdigest()
        }

        sentences.append(entry)

    f = open('../corpus/old_data/cleanup_rate-easy_language.csv', 'a')
    writer = csv.writer(f)
    cleanup_rate = calculate_cleanup_rate(content, processed_text, )
    writer.writerow([cleanup_rate, source])
    f.close()

    print()
    print("# Cleanup rate: ", cleanup_rate)
    return sentences


def preprocess_deu_news_2021(content, source):
    content = content.replace(u'\xa0', u' ')

    # remove brackets
    content = re.sub(r"\((.*?)\)", "", content)
    content = re.sub(r"\[(.*?)\]", "", content)
    content = re.sub(r"\{(.*?)\}", "", content)

    # remove single brackets
    content = content.replace("(", "")
    content = content.replace(")", "")
    content = content.replace("[", "")
    content = content.replace("]", "")
    content = content.replace("{", "")
    content = content.replace("}", "")

    output = ""

    # Expect every paragraph on a line level to remove headings etc.
    lines = content.splitlines()

    for index, line in enumerate(lines):
        # remove leading and tailing whitespaces
        line = line.strip()
        line = line.replace(" ,", ",")
        line = line.replace(" :", ":")
        line = line.replace(" .", ".")
        line = line.replace(" ?", "?")
        line = line.replace(" !", "!")

        if line == "":
            continue

        if not line[0].isalnum():
            continue

        output += line + "\n"

    # Do some general cleanup
    output = re.sub(r'\s+', ' ', output)

    # Detect sentences in paragraphs
    doc = nlp(output)

    sentences = []
    processed_text = ""

    for sent in doc.sents:
        sentence = str(sent)

        sentence = sentence.replace(" ,", ",")
        sentence = sentence.replace(" :", ":")
        sentence = sentence.replace(" .", ".")
        sentence = sentence.replace(" ?", "?")
        sentence = sentence.replace(" !", "!")

        if sentence[-1] not in ['.', '!', '?']:
            continue

        if sentence == ".":
            continue

        if not sentence[0].isupper() and not sentence[0].isnumeric():
            continue

        numer_of_words = count_words(sent)
        if numer_of_words < 3:
            continue

        processed_text += sentence + "\n"
        print(sentence)

        entry = {
            "text": sentence,
            "number_of_words": numer_of_words,
            "hash": hashlib.sha256(str.encode(sentence)).hexdigest()
        }

        sentences.append(entry)

    f = open('../corpus/old_data/cleanup_rate-easy_language.csv', 'a')
    writer = csv.writer(f)
    cleanup_rate = calculate_cleanup_rate(content, processed_text, )
    writer.writerow([cleanup_rate, source])
    f.close()

    print()
    print("# Cleanup rate: ", cleanup_rate)
    return sentences


def preprocess_everyday(content, source):
    content = content.replace(u'\xa0', u' ')

    # remove brackets
    content = re.sub(r"\((.*?)\)", "", content)
    content = re.sub(r"\[(.*?)\]", "", content)
    content = re.sub(r"\{(.*?)\}", "", content)

    # remove single brackets
    content = content.replace("(", "")
    content = content.replace(")", "")
    content = content.replace("[", "")
    content = content.replace("]", "")
    content = content.replace("{", "")
    content = content.replace("}", "")

    output = ""

    # Expect every paragraph on a line level to remove headings etc.
    lines = content.splitlines()

    for index, line in enumerate(lines):
        # remove leading and tailing whitespaces
        line = line.strip()
        line = line.replace(" ,", ",")
        line = line.replace(" :", ":")
        line = line.replace(" .", ".")
        line = line.replace(" ?", "?")
        line = line.replace(" !", "!")

        lines[index] = line = remove_non_alpha_chars_from_start(line)

        if line == "":
            continue

        # skip the current line if it does not end with .?! and the enclosing lines are empty
        if not (line[-1] not in ['.', '?', '!'] and 0 < index < (len(lines) + 1) and lines[index - 1] == "" and lines[
            index + 1] == ""):
            output += line + " "

    # Do some general cleanup
    output = output.replace("\n", " ")
    output = re.sub(r'\s+', ' ', output)

    # Detect sentences in paragraphs
    doc = nlp(output)

    sentences = []
    processed_text = ""

    for sent in doc.sents:
        sentence = str(sent)

        sentence = sentence.replace(" ,", ",")
        sentence = sentence.replace(" :", ":")
        sentence = sentence.replace(" .", ".")
        sentence = sentence.replace(" ?", "?")
        sentence = sentence.replace(" !", "!")

        if sentence[-1] not in ['.', '!', '?']:
            continue

        if sentence == ".":
            continue

        if not sentence[0].isupper() and not sentence[0].isnumeric():
            continue

        numer_of_words = count_words(sent)
        if numer_of_words < 3:
            continue

        processed_text += sentence + "\n"
        print(sentence)

        entry = {
            "text": sentence,
            "number_of_words": numer_of_words,
            "hash": hashlib.sha256(str.encode(sentence)).hexdigest()
        }

        sentences.append(entry)

    f = open('../corpus/old_data/cleanup_rate-easy_language.csv', 'a')
    writer = csv.writer(f)
    cleanup_rate = calculate_cleanup_rate(content, processed_text, )
    writer.writerow([cleanup_rate, source])
    f.close()

    print()
    print("# Cleanup rate: ", cleanup_rate)
    return sentences


def preprocess_easy_to_read(content, source):
    content = content.replace(u'\xa0', u' ')

    # remove brackets
    content = re.sub(r"\((.*?)\)", "", content)
    content = re.sub(r"\[(.*?)\]", "", content)
    content = re.sub(r"\{(.*?)\}", "", content)

    # remove single brackets
    content = content.replace("(", "")
    content = content.replace(")", "")
    content = content.replace("[", "")
    content = content.replace("]", "")
    content = content.replace("{", "")
    content = content.replace("}", "")

    paragraphs = content.split("#P#")

    output = ""

    for i, paragraph in enumerate(paragraphs):
        paragraphs[i] = paragraph.strip()

        paragraph = remove_non_alpha_chars_from_start(paragraph)

        if len(paragraph) == 0:
            continue

        # Combine two paragraphs is the current paragraphs does not stop with a punctuation and the next
        # Paragraph starts with a lower character
        if not paragraph[-1] in ['.', '!', '?']:

            # A next paragraph exists
            if i < (len(paragraphs) - 1):
                next_paragraph = paragraphs[i + 1].strip()

                # The next paragraph starts with a lower character
                if next_paragraph != "" and next_paragraph[0].islower():
                    # combine the current with the next paragraph
                    paragraphs[i] += " " + next_paragraph
                    paragraphs[i + 1] = ""

        # Remove paragraphs that start with a lower character
        if paragraph[0].islower():
            paragraphs[i] = ""

        # Expect every paragraph on a line level to remove headings etc.
        temp = ""
        lines = paragraph.splitlines()

        for index, line in enumerate(lines):
            # remove leading and tailing whitespaces
            line = line.strip()
            line = line.replace(" ,", ",")
            line = line.replace(" :", ":")
            line = line.replace(" .", ".")
            line = line.replace(" ?", "?")
            line = line.replace(" !", "!")

            lines[index] = line = remove_non_alpha_chars_from_start(line)

            if line == "":
                continue

            # If a paragraphs ends with a punctuation mark then add the paragraph to the chunks list
            if line[-1] in ['.', '!', '?']:

                # check if a sentence is incomplete
                if (line[0].islower() or len(line.split(" ")) == 1) and index > 0:

                    # Try to fin the sentence start
                    sentence_start = find_sentence_start(lines, index)

                    if sentence_start:
                        temp += sentence_start + " "
                    else:
                        # Cannot find a sentence start
                        continue

                # add the previous line, if the current line is a valid sentence and the previous line ends with a colon
                # if (line[0].isupper() or line[0].isnumeric()) and index > 0:
                #
                #     previous_line = lines[index - 1].strip()
                #     if len(previous_line) > 0 and (previous_line[0].isupper() or previous_line[0].isnumeric()) and previous_line[-1] == ":":
                #         temp += previous_line + " "
                #         # print(previous_line)

                temp += line

                output += temp + "\n"
                temp = ""

    # Do some general cleanup
    output = output.replace("\n", " ")
    output = re.sub(r'\s+', ' ', output)

    # Detect sentences in paragraphs
    doc = nlp(output)

    sentences = []
    processed_text = ""

    for sent in doc.sents:
        sentence = str(sent)

        sentence = sentence.replace(" ,", ",")
        sentence = sentence.replace(" :", ":")
        sentence = sentence.replace(" .", ".")
        sentence = sentence.replace(" ?", "?")
        sentence = sentence.replace(" !", "!")

        if sentence[-1] not in ['.', '!', '?']:
            continue

        if sentence == ".":
            continue

        if not sentence[0].isupper() and not sentence[0].isnumeric():
            continue

        print(sentence)

        processed_text += sentence + "\n"
        numer_of_words = count_words(sent)
        entry = {
            "text": sentence,
            "number_of_words": numer_of_words,
            "hash": hashlib.sha256(str.encode(sentence)).hexdigest()
        }

        sentences.append(entry)

    f = open('../corpus/old_data/cleanup_rate-easy_language.csv', 'a')
    writer = csv.writer(f)
    cleanup_rate = calculate_cleanup_rate(content, processed_text, )
    writer.writerow([cleanup_rate, source])
    f.close()

    print()
    print("# Cleanup rate: ", cleanup_rate)
    return sentences


def add_sentence(sentence, language_type, source, cursor):
    language_type_code = 0

    if language_type == "plain":
        language_type_code = 1

    if language_type == "everyday":
        language_type_code = 2

    if language_type == "special":
        language_type_code = 3

    try:
        cursor.execute("INSERT INTO sentences VALUES (" + str(
            language_type_code) + "," + str(source) + ", '" + sentence["text"] + "'," + str(
            sentence["number_of_words"]) + ",'" + sentence["hash"] + "')")
    except:
        # duplicate entry
        return False
        # print("ERROR: Cannot add ", sentence)


if __name__ == '__main__':
    path = "../corpus/everyday/deu_news_2021/"
    source_name = "deu_news_2021"
    source_id = 17
    language_type = "everyday"

    file_path = path + '979.txt'
    with open(file_path, 'r') as f:
        try:
            content = f.read()
            f.close()

            # print(preprocess_everyday(content, source_name))
            print(preprocess_deu_news_2021(content, source_name))
            # print(preprocess_springer_link(content, source_name))

        except UnicodeDecodeError:
            print("UTF-8 Error: ", file_path)

    #######################################

    # tasks = JoinableQueue()
    # results = Queue()
    #
    # # create consumers
    # num_consumers = round(os.cpu_count() / 2)
    # num_consumers = 6
    # print('Creating {} consumers'.format(num_consumers))
    # consumers = [
    #     Consumer(tasks, results)
    #     for i in range(num_consumers)
    # ]
    #
    # for w in consumers:
    #     w.start()
    #
    # # Enqueue jobs
    # files = glob.glob(f'{path}/*.txt')
    # print("Number of files:", len(files))
    #
    # for i, file in enumerate(files):
    #     # Check whether file is in text format or not
    #     if file.endswith(".txt"):
    #
    #         # Protect the queue from overflowing
    #         if tasks.full():
    #             print()
    #             print("----- Overflow Protection -----")
    #             print()
    #             time.sleep(10)
    #
    #         file_path = file
    #         tasks.put(Task({"file_path": file_path, "source_name": source_name}))
    #
    # # Add a poison pill for each consumer
    # for i in range(num_consumers):
    #     tasks.put(None)
    #
    # # write the resulting sentences to the database
    # connection = sqlite3.connect("../corpus/text_classification_corpus.sqlite")
    # cursor = connection.cursor()
    #
    # number_of_files = len(files)
    #
    # while number_of_files:
    #     result = results.get()
    #
    #     for sentence in result:
    #         add_sentence(sentence, language_type, source_id, cursor)
    #         connection.commit()
    #
    #     number_of_files -= 1
    #     progress = (len(files) - number_of_files) / len(files) * 100
    #     print()
    #     print("-------- Progress:", progress, '% --------')
    #     print()
    #
    # connection.close()
    #
    # # Wait for all the tasks to finish
    # tasks.join()
