import json
import os
import sys


if __name__ == '__main__':
    dataset_path = 'dataset.json'
    tos_dir = 'tos'
    dataset = []
    words = 0
    pairs = 0
    products_path = "products.json"
    with open(products_path, 'r') as json_file:
        content = json.loads(json_file.read())

    for i, product in enumerate(content):
        sys.stdout.write('\r[%d/%d]' % (i + 1, len(content)))
        sys.stdout.flush()
        product_tos_path = os.path.join(tos_dir, product['slug'])
        if os.path.exists(product_tos_path):
            with open(product_tos_path, 'r') as tos_file:
                tos_text = tos_file.read()
            for rubric in product['rubric']:
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
                entry['question'] = question
                for option_index, option_id, _ in options:
                    if option_id == rubric['option']['id']:
                        answer = option_index
                entry['answer'] = answer
                dataset.append(entry)
                pairs += 1
                words += len(question.split())
    with open(dataset_path, 'w') as dataset_file:
        dataset_file.write(json.dumps(dataset))
    print(pairs, 'pairs,', words, 'words,', words * 1000 / 750, 'tokens')
