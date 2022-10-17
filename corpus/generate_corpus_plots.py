import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def source_distribution(language_type, language_name):

    connection = sqlite3.connect("../corpus/text_classification_corpus.sqlite")
    cursor = connection.cursor()

    # cursor.execute("SELECT sources.name, count(source) FROM sentences INNER JOIN sources ON "
    #                "sources.id=sentences.source WHERE language_type IS " + str(language_type) + " GROUP BY source;")
    # rows = cursor.fetchall()

    cursor.execute("SELECT * FROM sources")
    rows = cursor.fetchall()

    sources_names = {}
    for source in rows:
        sources_names[source[0]] = source[1]

    data = pd.read_csv("../corpus/meta_info.csv")
    data = data[data['language_type'] == language_type]

    sum = len(data)

    # cursor.execute("SELECT count(source) FROM sentences WHERE language_type IS " + str(language_type) + ";")
    # result = cursor.fetchall()

    # difference between word-wise and document-wise counting
    # this is sentences wise

    # sources = [source for source in sources]
    sources = data["source"].unique()
    values = [round(len(data[data["source"] == source]) / sum * 100) for source in sources]

    if language_type == 2:
        sources = data["source"].unique()
        sources = np.delete(sources, 0)

        data.drop(data[data.source == 13].index, inplace=True)
        sum = len(data)
        print(sources)
        values = [round(len(data[data["source"] == source]) / sum * 100) for source in sources]
        print(values)

    fig = plt.figure(figsize=(10, 6))

    # creating the bar plot
    # plt.bar(courses, values, color="#b4b4b4b4", width=0.4)
    plt.bar(sources, values)
    ax = plt.gca()
    ax.axes.xaxis.set_ticks([])

    x0, xmax = plt.xlim()
    y0, ymax = plt.ylim()
    data_width = xmax - x0
    data_height = ymax - y0

    for i in sources:
        plt.text(i, y0 + data_height * 0.05, sources_names[i], ha='center', rotation=90, bbox=dict(facecolor='white', linewidth="0", pad=7.0))

    plt.xticks(rotation=90)
    plt.xlabel("Quellen")
    plt.ylabel("Anteil [%]")
    # plt.title("Quellenverteilung der Sätze in " + language_name)
    plt.savefig('../corpus/plots/source_distribution_for_' + str(language_type) + '.pdf')
    plt.show()

def source_distribution_by_words(language_type, language_name):

    connection = sqlite3.connect("../corpus/text_classification_corpus.sqlite")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM sources")
    rows = cursor.fetchall()

    sources_names = {}
    for source in rows:
        sources_names[source[0]] = source[1]

    data = pd.read_csv("../corpus/meta_info.csv")
    data = data[data['language_type'] == language_type]
    sum = data["number_of_words"].sum()

    # difference between word-wise and document-wise counting
    # this is sentences wise

    # sources = [source for source in sources]
    sources = data["source"].unique()
    values = [round(data[data["source"] == source]["number_of_words"].sum() / sum * 100) for source in sources]

    fig = plt.figure(figsize=(10, 6))

    plt.bar(sources, values)
    ax = plt.gca()
    ax.axes.xaxis.set_ticks([])

    x0, xmax = plt.xlim()
    y0, ymax = plt.ylim()
    data_width = xmax - x0
    data_height = ymax - y0

    for i in sources:
        plt.text(i, y0 + data_height * 0.05, sources_names[i], ha='center', rotation=90, bbox=dict(facecolor='white', linewidth="0", pad=7.0))

    plt.xticks(rotation=90)
    plt.xlabel("Quellen")
    plt.ylabel("Anteil [%]")
    plt.savefig('../corpus/plots/source_distribution_for_' + str(language_type) + '_by_words.pdf')
    plt.show()


def number_of_words_per_document():
    training_data = pd.read_csv("../corpus/training_new.csv")
    evaluation_data = pd.read_csv("../corpus/test_new.csv")
    all_data = pd.concat([training_data, evaluation_data])

    print("Number of documents [Training]:", len(training_data))
    print("Number of documents [Evaluation]:", len(evaluation_data))
    print("Number of documents [All]:", len(all_data))
    print(all_data.loc[all_data['number_of_words'].idxmax()]["text"])

    number_of_words = all_data["number_of_words"].to_numpy()

    plt.figure(figsize=(12, 5))
    n, bins, patches = plt.hist(number_of_words, density=False, bins=36, range=[4, 40])
    # n, bins, patches = plt.hist(number_of_words, density=False, bins=56, range=[4, 60])
    plt.xticks(bins)
    plt.ylabel('Anzahl der Texte')
    plt.xlabel('Anzahl der Worte je Text')

    #plt.title("Verteilung der Textlängen des Korpus", )
    plt.savefig('../corpus/plots/number_of_words_per_document.pdf')
    plt.show()


def number_of_documents_per_languagetype():
    training_data = pd.read_csv("../corpus/training_new.csv")
    evaluation_data = pd.read_csv("../corpus/test_new.csv")
    all_data = pd.concat([training_data, evaluation_data])

    count_easy = len(all_data[(all_data['label'] == 0)])
    count_plain = len(all_data[(all_data['label'] == 1)])
    count_everyday = len(all_data[(all_data['label'] == 2)])
    count_special = len(all_data[(all_data['label'] == 3)])

    fig = plt.figure(figsize=(7, 5))
    x = ['Leichte Sprache', 'Einfache Sprache', 'Alltagssprache', 'Fachsprache']
    count = [count_easy, count_plain, count_everyday, count_special]
    plt.bar(x, count)

    for i in range(len(x)):
        margin = max(count) * 0.01
        
        plt.text(i, (count[i] + margin), count[i], ha='center')

    plt.ylabel('Anzahl der Texte')
    plt.savefig('../corpus/plots/number_of_documents_per_source.pdf')
    plt.show()

    # plt.figure(figsize=(12, 5))
    # n, bins, patches = plt.hist(number_of_documents, density=False, bins=4, range=[0, 4])
    # plt.xticks(bins)
    # plt.ylabel('Anzahl der Dokumente')
    # plt.xlabel('Sprachkategorie')
    #
    # plt.title("Verteilung der Dokumenten über die Sprachkategorien", )
    # plt.savefig('../corpus/plots/number_of_documents_per_source.pdf')
    # plt.show()


if __name__ == '__main__':
    #source_distribution(0, "Leiche Sprache")
    # source_distribution_by_words(1, "Leiche Sprache")
    #source_distribution(1, "Einfache Sprache")
    source_distribution(2, "Alltagssprache")
    #source_distribution(3, "Fachsprache")

    #number_of_words_per_document()
    #number_of_documents_per_languagetype()




    
