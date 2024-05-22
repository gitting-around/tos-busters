from openai import OpenAI
import openai
import sys, os
import json
from openai_tokenizer import num_tokens_from_string

client = OpenAI(api_key="PUT YOUR API KEY HERE")

############################
##### CHAT DEPENDENT #######
encoding = "cl100k_base"
max_tokens = 128000
gpt_model = "gpt-4-turbo"
############################
############################

def split_text(input_text, pieces):
    #print(f"Splitting in {pieces}, length of input {len(input_text)}")
    array_of_pieces = []
    r = int(len(input_text)/pieces)

    for x in range(pieces):
        part = input_text[x*r:x*r+r+1]
        array_of_pieces.append(part)

    return array_of_pieces

def find_num_splits(num_tokens, nominator):

    div = num_tokens/nominator
    if div < max_tokens:
        return nominator
    else:
        nominator = nominator + 1
        return find_num_splits(num_tokens, nominator)

def summarise(input_text, num_tokens):
    nr_splits = find_num_splits(num_tokens, 2)
    nr_splits = nr_splits + 2
    print(f"Num splits: {nr_splits}")
    successful_split = False
    summarized = ""

    while not successful_split:
        if nr_splits > 30:
            return input_text
        array_of_pieces = split_text(input_text, nr_splits)
        max_chars = len(input_text)/nr_splits #TODO this makes no sense

        for piece in array_of_pieces:
            try:
                content = f"Please summarise with less than {max_chars} characters the following text: {piece}"
                completion = client.chat.completions.create(
                model=gpt_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": content}
                ]
                )
                summarized = summarized + completion.choices[0].message.content
            except openai.error.Timeout as e:
                #Handle timeout error, e.g. retry or log
                print(f"OpenAI API request timed out: {e}")
                return f"Error: {e}"
            except openai.error.APIError as e:
                #Handle API error, e.g. retry or log
                print(f"OpenAI API returned an API Error: {e}")
                return f"Error: {e}"
            except openai.error.APIConnectionError as e:
                #Handle connection error, e.g. check network or log
                print(f"OpenAI API request failed to connect: {e}")
                return f"Error: {e}"
            except openai.error.InvalidRequestError as e:
                #Handle invalid request error, e.g. validate parameters or log
                print(f"OpenAI API request was invalid: {e}")
                return f"Error: {e}"
            except openai.error.AuthenticationError as e:
                #Handle authentication error, e.g. check credentials or log
                print(f"OpenAI API request was not authorized: {e}")
                return f"Error: {e}"
            except openai.error.PermissionError as e:
                #Handle permission error, e.g. check scope or log
                print(f"OpenAI API request was not permitted: {e}")
                return f"Error: {e}"
            except openai.error.RateLimitError as e:
                #Handle rate limit error, e.g. wait or log
                print(f"OpenAI API request exceeded rate limit: {e}")
                return f"Error: {e}"

        num_tokens_summarized = num_tokens_from_string(summarized, encoding)
        if num_tokens_summarized < max_tokens:
            successful_split = True
        else:
            return "ERROR - summarization failed."

    #print(f"Length of summary {len(summarized)}")
    return summarized

def prepare_entry(product, tos_text, rubric):
    entry = {
        'tos': product['slug']
    }
    question = 'In the following privacy policy: "%s", %s' % (
        tos_text,
        rubric['question']['text']
    )
    options = [
        (i + 1, item['id'], item['text']) for i, item in enumerate(rubric['question']['options'])
    ]
    question += ' Answer only with a single number chosen from the following options:\n%s.' % (
        '\n'.join(
            ['%d- %s' % (option_index, option_text) for option_index, _, option_text in options]
        )
    )
    #question += 'Additionally provide the part of the text that contains the answer.\n'
    entry['question'] = question
    for option_index, option_id, _ in options:
        if option_id == rubric['option']['id']:
            answer = option_index
    entry['answer'] = answer

    return entry, question

if __name__ == '__main__':
    if len(sys.argv) == 2:
        method = sys.argv[1]
    else:
        print("Too few/many inputs to the script. Run as $ python create_dataset.py chat_name")
        sys.exit()
    dataset_path = f'dataset-{method}.json'
    tos_dir = 'tos'
    dataset = []
    words = 0
    pairs = 0
    products_path = "products.json"
    with open(products_path, 'r') as json_file:
        content = json.loads(json_file.read())

    #print(f"Length of content {len(content)}")

    doesnt_exist = 0
    for i, product in enumerate(content):
        sys.stdout.write('\r[%d/%d]' % (i + 1, len(content)))
        sys.stdout.flush()
        product_tos_path = os.path.join(tos_dir, product['slug'])

        if os.path.exists(product_tos_path):
            with open(product_tos_path, 'r') as tos_file:
                tos_text = tos_file.read()
            num_tokens = num_tokens_from_string(tos_text, encoding)
            # If more tokens then max, summarise text.
            if num_tokens > max_tokens:
                tos_text = summarise(tos_text, num_tokens)

            for rubric in product['rubric']:
                entry, question = prepare_entry(product, tos_text, rubric)
                dataset.append(entry)
                pairs += 1
                words += len(question.split())
        else:
            doesnt_exist = doesnt_exist + 1
            print(f"Skipped {i+1}")

    with open(dataset_path, 'w') as dataset_file:
        dataset_file.write(json.dumps(dataset))
    #print(f"Dataset length {len(dataset)}")
    #print(f"Doesn't exist {doesnt_exist}")
    print(pairs, 'pairs,', words, 'words,', words * 1000 / 750, 'tokens')