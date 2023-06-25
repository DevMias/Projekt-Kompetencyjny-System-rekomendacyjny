import json
import gzip

input_filename = 'kcore_5.json.gz'
output_filename = 'kcore_5.json'
max_lines = 2000000
max_size = (1024 * 1024 * 1024)/8
current_size = 0
chunk_size = 1024 * 1024 # 1MB

with gzip.open(input_filename, 'rb') as f_in, open(output_filename, 'w') as f_out:
    lines = []
    for line in f_in:
        lines.append(line.decode('utf-8'))
        if len(lines) == max_lines:
            for line in lines:
                data = json.loads(line)
                
                data.pop('reviewText', None)
                data.pop('unixReviewTime', None)
                data.pop('reviewerName', None)
                data.pop('helpful', None)
                data.pop('verified', None)
                data.pop('image', None)
                
                modified_line = json.dumps(data) + ','+'\n'
               
                f_out.write(modified_line)
                current_size += len(modified_line.encode('utf-8'))
            lines = []
        if current_size >= max_size:
            break

    if lines:
        for line in lines:
            data = json.loads(line)
           
            data.pop('reviewText', None)
            data.pop('unixReviewTime', None)
            data.pop('reviewerName', None)
            data.pop('helpful', None)
            data.pop('verified', None)
            data.pop('image', None)
            
            modified_line = json.dumps(data) + ','+'\n'

            f_out.write(modified_line)
            current_size += len(modified_line.encode('utf-8'))
print("DONE !")