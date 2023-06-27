import json
import random
import pandas as pd
import gzip


num_objects = 15000
random_indices = random.sample(range(num_objects), num_objects)


table_data = []
with gzip.open("metadata.json.gz", "rt") as file:
    for i, line in enumerate(file):
        if i in random_indices:
            json_object = json.loads(line)

            extracted_data = {
                "asin": json_object["asin"],
                "title": json_object["title"],
                "salesRank": json_object["salesRank"],
                "categories": json_object["categories"],

            }
            table_data.append(extracted_data)

df = pd.DataFrame(table_data)

print(df)