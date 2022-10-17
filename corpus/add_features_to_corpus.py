import csv
from concurrent.futures import as_completed
from src.TextAnalyser import TextAnalyser
import os
import time
import psutil
import pandas as pd
import numpy  as np
import concurrent.futures
import random

def do_something(df):
    # pid = int(str(os.getpid())[-1])
    # ppid = os.getppid()

    server = [
        "http://192.168.188.40:8010",
        "http://192.168.188.40:8011",
        "http://192.168.188.40:8012",
        "http://192.168.188.40:8013",
        "http://192.168.188.40:8014",
        "http://192.168.188.40:8015",
        "http://192.168.188.40:8016",
        # "http://localhost:8010",
        # "http://localhost:8011",
    ]

    server_location = random.choice(server)

    analysis = TextAnalyser(df["text"], server_location=server_location)
    report = analysis.report()

    for j, metric in enumerate(report):
        df[metric] = report[metric]

    df = pd.DataFrame([df])
    return(df)


if __name__ == '__main__':
    training_data_path = "/Users/rubenklepp/git/yak/corpus/training_new.csv"
    test_data_path = "/Users/rubenklepp/git/yak/corpus/test_new.csv"
    output_path = "/Users/rubenklepp/git/yak/corpus/multi-feature_new.csv"

    print("- Start generation -")

    train_df = pd.read_csv(training_data_path)
    test_df = pd.read_csv(test_data_path)
    df = pd.concat([train_df, test_df])

    ####### Test
    #df = df.head(10)

    print("Number of items:", len(df))
    number_of_items = len(df)
    number_of_processed_items = 0

    logical = False
    df_results = []
    num_procs = psutil.cpu_count(logical=logical)
    num_procs = 6

    last_progress = 0
    first_write = True

    splitted_df = np.array_split(df, num_procs)
    start = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_procs) as executor:
        # results = [executor.submit(do_something, df=df) for df in splitted_df]

        items_df = df.reset_index()
        results = [executor.submit(do_something, df=df) for index, df in items_df.iterrows()]

        for _ in as_completed(results):
            number_of_processed_items = number_of_items - len(executor._pending_work_items)
            progress = round(number_of_processed_items / number_of_items * 100, 0)

            if progress > last_progress:
                print(progress, "%")
                last_progress = progress

            if number_of_processed_items % 10 == 0:
                elapsed_time = round(time.time() - start, 2)
                remaining_time = round(((100 / progress) * elapsed_time) - elapsed_time, 2)
                print("Remaining time:", remaining_time)
                print("Index:", number_of_processed_items)


        for result in concurrent.futures.as_completed(results):
            try:
                df_results.append(result.result())
            except Exception as ex:
                print(str(ex))
                pass
    end = time.time()
    print()
    print("-------------------------------------------")
    print("PPID %s Completed in %s" % (os.getpid(), round(end - start, 2)))
    df_results = pd.concat(df_results)
    df_results.to_csv(output_path, encoding='utf-8', index=False, quoting=csv.QUOTE_NONNUMERIC)