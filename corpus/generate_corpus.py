import csv
import sqlite3
from sklearn.model_selection import train_test_split
import random
import pandas as pd
from sklearn.utils import shuffle

meta_data = []


def log_meta_data(language_type, number_of_words, source, hash):
    meta_data.append({
        "language_type": language_type,
        "number_of_words": number_of_words,
        "source": source,
        "hash": hash
    })


def generate_sub_corpus(language_type, cursor, limiter=[], oversampling=0):
    print("Load sentences from the database")
    cursor.execute("SELECT * FROM sentences WHERE language_type IS " + str(language_type) + " ORDER BY RANDOM();")
    rows = cursor.fetchall()
    entries = []
    number_of_words_threshold = 40

    # Convert db results into a dataframe
    df = pd.DataFrame(rows, columns=['language_type', 'source', 'text', 'number_of_words', 'hash'])
    # print("Number of sentences", len(df))
    # full_17 = len(df[df["source"] == 17])
    # print("Number of sentences [17]", full_17)

    # If a reducer is given reduce the results for one source
    if len(limiter) > 0:
        df = shuffle(df)

        for source in limiter:
            id = source["id"]
            percentage = source["percentage"]

            source_indices = df.index[df['source'] == id]
            df.drop(source_indices[:int(len(source_indices) * percentage)], inplace=True)

    # Drop sentences with a number of words above the threshold
    df.drop(df[df["number_of_words"] > number_of_words_threshold].index, inplace=True)

    # print("Reduced number of sentences:", number_of_rows)
    # reduced_17 = len(df[df["source"] == 17])
    # print("Reduced number of sentences [17]", reduced_17)
    # print(reduced_17 / full_17)

    max_words = 28
    number_of_words = 0
    entry = ""
    i = 0

    long_length_count = 0

    print("Start generating the sub corpus for", language_type)
    stop = False
    while not stop:
        for index, row in df.iterrows():
            # Skip the row if the text column does not include a string
            if not isinstance(row["text"], str):
                print("Skip row")
                continue

            if oversampling != 0 and len(entries) > oversampling:
                break

            if number_of_words + row["number_of_words"] < max_words:
                entry += " " + row["text"]
                number_of_words += row["number_of_words"]
                log_meta_data(language_type, row["number_of_words"], row["source"], row["hash"])

                if number_of_words > number_of_words_threshold:
                    long_length_count += 1
            else:
                if number_of_words > number_of_words_threshold:
                    long_length_count += 1

                entries.append({"label": language_type, "text": entry.strip(), "number_of_words": number_of_words})
                log_meta_data(language_type, row["number_of_words"], row["source"], row["hash"])
                entry = " " + row["text"]
                number_of_words = row["number_of_words"]

            i += 1


        # Shuffel dataframe to repeat the text generation with new sentence combination (oversampling)
        if len(entries) < oversampling:
            df = shuffle(df)
            print("again")
        else:
            stop = True

    print("Number of documents", len(entries))
    print("Long documents", long_length_count)

    return entries


if __name__ == '__main__':
    connection = sqlite3.connect("../corpus/text_classification_corpus.sqlite")
    cursor = connection.cursor()

    training_output = []
    test_output = []

    # Easy to read
    train, test = train_test_split(generate_sub_corpus(0, cursor, oversampling=37783), test_size=0.20, random_state=42)
    # train, test = train_test_split(generate_sub_corpus(0, cursor, oversampling=0), test_size=0.20, random_state=42)
    training_output += train
    test_output += test

    # Plain
    train, test = train_test_split(generate_sub_corpus(1, cursor, oversampling=0), test_size=0.20, random_state=42)
    training_output += train
    test_output += test

    # Everyday
    train, test = train_test_split(generate_sub_corpus(2, cursor, limiter=[
        {"id": 17, "percentage": 0.9},
        {"id": 19, "percentage": 0.55}
    ]), test_size=0.20, random_state=42)
    # train, test = train_test_split(generate_sub_corpus(2, cursor), test_size=0.20, random_state=42)
    training_output += train
    test_output += test

    # Special
    train, test = train_test_split(generate_sub_corpus(3, cursor), test_size=0.20, random_state=42)
    training_output += train
    test_output += test

    header = ["label", "text", "number_of_words"]

    with open('../corpus/training_new.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        # write the header
        writer.writerow(header)

        # write multiple rows
        for line in training_output:
            writer.writerow([line["label"], line["text"], line["number_of_words"]])

    with open('../corpus/test_new.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        # write the header
        writer.writerow(header)

        # write multiple rows
        for line in test_output:
            writer.writerow([line["label"], line["text"], line["number_of_words"]])

    header = ["language_type", "number_of_words", "source", "hash"]
    with open('../corpus/meta_info.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        for line in meta_data:
            writer.writerow([line["language_type"], line["number_of_words"], line["source"], line["hash"]])

    connection.close()


