import json
import os
import sys
import requests

summariseFlag = True # set to true if you want to summarize the tos
min_len_break = 3730


def split_text(input_text, pieces):
    #print(f"Splitting in {pieces}, length of input {len(input_text)}")
    array_of_pieces = []
    r = int(len(input_text)/pieces)

    for x in range(pieces):
        part = input_text[x*r:x*r+r+1]
        array_of_pieces.append(part)

    return array_of_pieces

def summarise(input_text):
    #print("summarising")
    nr_splits = 2
    successful_split = False
    summarized = ""

    while not successful_split:
        if nr_splits > 30:
            return input_text
        array_of_pieces = split_text(input_text, nr_splits)
        count = 0
        nr_chars = int(min_len_break/(nr_splits+1))

        for piece in array_of_pieces:
            piece_summary = requests.post(
            'http://titan.maleci.ece.au.dk:8181/generate',
            headers={
                'Content-Type': 'application/json',
            },
            json={
                'inputs': """
                ### Instruction: Please summarize the following text with maximum %d characters
                %s
                ### Response:
                """ % (nr_chars, piece),
                'parameters': {
                    'max_new_tokens': 50,
                },
            }
            ) 

            if 'error_type' in piece_summary.json():
                nr_splits = nr_splits + 1
                summarized = ""
                count = 0
                break
            else:
                count = count + 1
                summarized = summarized + piece_summary.json()['generated_text'] + " " 
                if count == nr_splits:
                    test = requests.post(
                    'http://titan.maleci.ece.au.dk:8181/generate',
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json={
                        'inputs': """
                        ### Instruction: Please summarize the following text with maximum %d characters
                        %s
                        ### Response:
                        """ % (nr_chars, summarized),
                        'parameters': {
                            'max_new_tokens': 50,
                        },
                    }
                    ) 
                    if 'error_type' in test.json():
                        nr_splits = nr_splits + 1
                        summarized = ""
                        print("split not enough after joining")
                        count = 0
                    else:
                        successful_split = True

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
    question += 'Additionally provide the part of the text that contains the answer.\n'
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
            if summariseFlag and len(tos_text) > min_len_break: #this value has been evaluated empirically
                tos_text = summarise(tos_text)
                for rubric in product['rubric']:
                    entry, question = prepare_entry(product, tos_text, rubric)
                    dataset.append(entry)
                    pairs += 1
                    words += len(question.split())
            else:
                for rubric in product['rubric']:
                    entry, question = prepare_entry(product, tos_text, rubric)
                    dataset.append(entry)
                    pairs += 1
                    words += len(question.split())
        else:
            doesnt_exist = doesnt_exist + 1
            #print(f"Skipped {i+1}")

    with open(dataset_path, 'w') as dataset_file:
        dataset_file.write(json.dumps(dataset))
    #print(f"Dataset length {len(dataset)}")
    #print(f"Doesn't exist {doesnt_exist}")
    print(pairs, 'pairs,', words, 'words,', words * 1000 / 750, 'tokens')