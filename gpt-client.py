from openai import OpenAI

key = ""
client = OpenAI(api_key=key)

#TODO maybe read these from a file?
alternatives_for_questions = ["Who is the GOAT of male tennis?", "How to make lasagna?", "What is the most sold album in rock history?"]

answers = []

for idx, q in enumerate(alternatives_for_questions):

  completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": q}
      ]
    )

  answers.append(completion.choices[0].message.content)
  print(completion.choices[0].message.content)
  print(f"Progress made {int(100*(idx+1)/float(len(alternatives_for_questions)))}")

#TODO record answers to file
