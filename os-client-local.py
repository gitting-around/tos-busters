import requests
import json
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
os.environ["TOKENIZERS_PARALLELISM"] = "true"

if len(sys.argv) == 2:
    method = sys.argv[1]
else:
    print("Too few/many inputs to the script. Run as $ python os-client-local.py method_name")
    sys.exit()

prompt = 'Hi!'  

def make_requests(input_text):
  tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
  
  chat = [
    {"role": "system", "content": "You're a helpful chatbot"},
    {"role": "user", "content": input_text}
  ]

  tokenized_chat = tokenizer.apply_chat_template(chat, tokenize=True, add_generation_prompt=True, return_tensors="pt")
  print(type(tokenized_chat))
  return requests.post(
       'http://titan.maleci.ece.au.dk:8181/generate',
       headers={
           'Content-Type': 'application/json',
       },
       json={
           'inputs': """
            %s
            """ % tokenizer.decode(tokenized_chat[0]),
           'parameters': {
               'max_new_tokens': 50,
           },
       }
   )

# Load dataset
fname = "dataset-" + method + ".json"
#print(fname)
with open(fname, "r") as f:
  dataset = json.load(f)
datasize = len(dataset)
#print(f"Length of dataset: {datasize}")

answers = []

skipped = 0

no_requests = 1

min_len_breaking_it = 50000

for idx, q in enumerate(dataset):
  completion = make_requests(q["question"])

  sys.stdout.write('\rProgress: %d, Request #: %d' % (int(100*(idx+1)/float(datasize)), no_requests))
  sys.stdout.flush()
  no_requests = no_requests + 1
  print(completion)
  if completion.json():
    print(completion.json())
  
  if 'error_type' in completion.json() and completion.json()['error_type'] == 'validation':

    question_length = len(q["question"])

    if question_length < min_len_breaking_it:
      min_len_breaking_it = question_length

    #print(completion.json())
    #print("TOOBIG")

    pair = {
        q["answer"] : 'TOOBIG'
    }
    skipped = skipped + 1
    #print(skipped)
  
  else:
    #save pair GT/GPT answers
    pair = {
        q["answer"] : completion.json()['generated_text']
    }
  
  answers.append(pair)
  
#save to file

fname = "opensource-results-" + method + ".json"
with open(fname, 'w') as f:
    json.dump(answers, f)

print(f"Min length breaking it {min_len_breaking_it}")
