#This function returns the aggregate number of tokens given a dataset
import tiktoken
import sys
import json

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    print(f"Number of tokens: {num_tokens}")
    return num_tokens

if __name__ == '__main__':
    if len(sys.argv) == 2:
        suffix = sys.argv[1]
    else:
        print("Too few/many inputs to the script. Run as $ python openai-tokenizer.py dataset-suffix")
        sys.exit()

    encoding = "cl100k_base"

    # Load dataset
    fname = "dataset-" + suffix + ".json"
    with open(fname, "r") as f:
        dataset = json.load(f)

    total_tokens = 0
    datasize = len(dataset)

    # Get number of tokens for each question in the dataset and add up
    for idx, q in enumerate(dataset):
        sys.stdout.write('\rProgress: %d' % (int(100*(idx+1)/float(datasize))))
        sys.stdout.flush()
        total_tokens = total_tokens + num_tokens_from_string(q["question"], encoding)

    print(f"\nTotal number of tokens {total_tokens}")
    

