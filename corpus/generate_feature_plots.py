import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def add_text_label(row):
    labels = ['leichte\nSprache', 'einfache\nSprache', 'Alltags-\nsprache', 'Fach-\nsprache']
    return labels[int(row["label"])]


def add_color_label(row):
    labels = ['#4D96FF', '#6BCB77', '#FFD93D', '#FF6B6B']
    return labels[int(row["label"])]


def save_scatter(column_name, name, df, colors):
    plt.figure()
    plt.clf()

    x1 = df.loc[df.label == 0, column_name]
    x2 = df.loc[df.label == 1, column_name]
    x3 = df.loc[df.label == 2, column_name]
    x4 = df.loc[df.label == 3, column_name]

    # kwargs = dict(alpha=0.5, bins=100, density=True, stacked=True)
    kwargs = dict(density=True, stacked=True, histtype="step")

    plt.hist(x1, **kwargs, color='#4D96FF', label='Leicht')
    plt.hist(x2, **kwargs, color='#6BCB77', label='Einfach')
    plt.hist(x3, **kwargs, color='#FFD93D', label='Alltag')
    plt.hist(x4, **kwargs, color='#FF6B6B', label='Fach')
    plt.gca().set(title='Probability Histogram of Diamond Depths', ylabel='Probability')
    # plt.xlim(50, 75)
    plt.legend();

    # df.hist(column=column_name, by=df["label_text"])
    # df.plot.hist(column=[column_name, "label_text"], alpha=0.5)

    ax = df.plot.scatter(x='label_text', y=column_name, s=20, alpha=0.01, color=colors)
    plt.tight_layout()

    ax.yaxis.set_label_text(name)

    # disable x axis
    ax.xaxis.get_label().set_visible(False)

    plt.savefig(
        output_path + column_name + '.pdf',
        bbox_inches='tight')

    plt.savefig(
        output_path + column_name + '.jpg',
        bbox_inches='tight', dpi=700)

    plt.show()
    plt.close()


if __name__ == '__main__':
    output_path = "/Users/rubenklepp/git/yak/corpus/reports/"

    df = pd.read_csv("/Users/rubenklepp/git/yak/corpus/multi-feature_new .csv")
    df.drop('text', axis=1, inplace=True)
    df['label_text'] = df.apply(lambda row: add_text_label(row), axis=1)
    df['label_color'] = df.apply(lambda row: add_color_label(row), axis=1)

    colors = df['label_color'].to_numpy()

    # print(df.head())
    # print(df.columns)

    save_scatter("number_of_words", "Wortanzahl", df, colors)
    save_scatter("number_of_sentences", "Satzanzahl", df, colors)
    save_scatter("lix_score", "LIX Index", df, colors)
    save_scatter("wstf_4_score", "4. Wiener Sachtextformel", df, colors)
    save_scatter("wstf_3_score", "3. Wiener Sachtextformel", df, colors)
    save_scatter("wstf_2_score", "2. Wiener Sachtextformel", df, colors)
    save_scatter("wstf_1_score", "1. Wiener Sachtextformel", df, colors)
    save_scatter("flesch_score", "Flesch Index", df, colors)
    save_scatter("gsmog_score", "gSmog Index", df, colors)
    save_scatter("passive_voice", "Verwendung des Passiv", df, colors)
    save_scatter("subjunctive", "Verwendung des Konjunktiv", df, colors)
    save_scatter("negations", "Verwendung von Verneinungen", df, colors)
    save_scatter("subclauses", "Verwendung von Nebensätzen", df, colors)
    save_scatter("genitive", "Verwendung des Genitivs", df, colors)
    save_scatter("metaphor", "Verwendung von Metaphern", df, colors)
    save_scatter("abstract_words", "Verwendung von abstrakten Worten", df, colors)
    save_scatter("long_words", "Verwendung von langen Worten", df, colors)
    save_scatter("complicated_words", "Verwendung komplizierten Worten", df, colors)
    save_scatter("relative_clause", "Verwendung von Relativsätzen", df, colors)
    save_scatter("indirect_speech", "Verwendung von indirekter Rede", df, colors)
    save_scatter("two_information_units", "Verwendung zwei Informationseinheiten je Satz", df, colors)
    save_scatter("past_tense", "Verwendung des Präteritums", df, colors)
    save_scatter("abbreviations", "Verwendung von Abkürzungen", df, colors)
    save_scatter("questions", "Verwendung von Fragen", df, colors)
    save_scatter("specialist_terms", "Verwendung von Fachausdrücken", df, colors)
    save_scatter("complicated_idioms", "Verwendung von komplizierten Redewendungen", df, colors)
    save_scatter("anglicism", "Verwendung von Anglizismen", df, colors)
    save_scatter("references", "Verwendung von Querverweisen", df, colors)
    save_scatter("roman_numbers", "Verwendung von römischen Zahlen", df, colors)
    save_scatter("numbers", "Verwendung von Zahlen", df, colors)
    save_scatter("from_to", "Verwendung von 'von ... bis'", df, colors)
    save_scatter("numberals", "Verwendung von Zahlworten", df, colors)
    save_scatter("dates", "Verwendung von Datumsangaben", df, colors)
    save_scatter("special_characters", "Verwendung von Sonderzeichen", df, colors)
    save_scatter("footnotes", "Verwendung von Fußnoten", df, colors)
