from openai import OpenAI
import json

key = ""
client = OpenAI(api_key=key)

# Load dataset
with open("dataset.json") as f:
  dataset = json.load(f)
datasize = len(dataset)

answers = []

for idx, q in enumerate(dataset):

  
  completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": q["question"]}
      ]
    )

  print(f"Progress: {int(100*(idx+1)/float(datasize))}%")

  #save pair GT/GPT answers
  pair = {
    q["answer"] : completion.choices[0].message.content
  }
  answers.append(pair)

#save to file
with open('results.json', 'w') as f:
    json.dump(answers, f)

