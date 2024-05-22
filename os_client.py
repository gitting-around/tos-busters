import requests
import json
import sys



def make_requests(input_text):
  return requests.post(
       'URL to server running Chatbot', #TODO User puts url to server
       headers={
           'Content-Type': 'application/json',
       },
       json={
           'inputs': """
        ### Instruction:
        %s
        ### Response:
        """ % input_text,
           'parameters': {
               'max_new_tokens': 50,
           },
       }
   )

def make_single_request(dataset_fname, idx):

  print(f"dataset name {dataset_fname}\n\n")
  print(f"Running single request for question: #{idx+1}")
  nr_questions = 12
  # Load dataset
  with open(dataset_fname, "r") as f:
    dataset = json.load(f)
    index = idx*nr_questions
    single_question = dataset[index]["question"]
    print("\n")
    print(f"Question: {single_question}\n")
    completion = make_requests(single_question)
    print(f"Chatbot answer: {completion.json()}\n")

if __name__ == '__main__':
  if len(sys.argv) == 2:
    method = sys.argv[1]
  else:
      print("Too few/many inputs to the script. Run as $ python os-client-local.py method_name")
      sys.exit()

  nr_questions = 12
  prompt = 'Hi!'  

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
