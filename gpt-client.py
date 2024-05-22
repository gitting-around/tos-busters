from openai import OpenAI
import openai
import json
import sys
import time

if len(sys.argv) == 2:
    method = sys.argv[1]
else:
    print("Too few/many inputs to the script. Run as $ python gpt-client-local.py model_name")
    sys.exit()

client = OpenAI(api_key="PUT your own API key here.")
gpt_model = method
# Load dataset
fname = "dataset-" + method + ".json"
with open(fname) as f:
  dataset = json.load(f)
datasize = len(dataset)

answers = []
skipped = 0
sleep_count = 1

try:
  for idx, q in enumerate(dataset):
    if idx == sleep_count*30:
       #putting a sleep once in a while so the requests don't get rejected 
       time.sleep(30)
       sleep_count = sleep_count + 1
    completion = client.chat.completions.create(
        model=gpt_model,
        messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": q["question"]}
        ]
      )

    print(f"Progress: {int(100*(idx+1)/float(datasize))}%")
    print(f"IDX: {idx}")

    #save pair GT/GPT answers
    pair = {
      q["answer"] : completion.choices[0].message.content
    }
    answers.append(pair)
    
except Exception as e:
    #Handle timeout error, e.g. retry or log
    print(f"API error: {e}")
    pair = {
        q["answer"] : 'TOOBIG'
    }
    skipped = skipped + 1
    answers.append(pair)

    #save to file
    fname = "except-gpt-results-" + method + ".json"
    with open(fname, 'w+') as f:
        json.dump(answers, f)

finally:
  #save to file
  fname = "gpt-results-" + method + ".json"
  with open(fname, 'w+') as f:
      json.dump(answers, f)