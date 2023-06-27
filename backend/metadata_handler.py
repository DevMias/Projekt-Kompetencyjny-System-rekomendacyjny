import json
import gzip

input_filename = 'metadata.json.gz'
output_filename = 'modified_metadata.json'
max_lines = 200000
max_size = (1024 * 1024 * 1024)
current_size = 0
chunk_size = 1024 * 1024  # 1MB

modified_data = []  


with gzip.open(input_filename, 'rt', encoding='utf-8') as f_in:
    for line in f_in:
        data = json.loads(line)
        
        data.pop('imUrl', None)
        data.pop('salesRank', None)
        
        modified_data.append(data)
        
        current_size += len(line.encode('utf-8'))
        
        if len(modified_data) == max_lines or current_size >= max_size:
            break

with open(output_filename, 'w') as f_out:
    json.dump(modified_data, f_out)

print("DONE!")
