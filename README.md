# tos-busters

# Open-source vs. Commercial Chatbots
For experiments with open-source use the scripts ```create_dataset.py``` and ```os_client.py```.
For experiments with ChatGPT use the scripts ```create_dataset_gpt.py``` and ```gpt_client.py```.

Note that you need to supply the URL to a server running any of the open-source chatbots (in both scripts), whereas for ChatGPT, you need to pay and get an API key that you need to add in both scripts.
The ```create_dataset.py``` script can be run with the summarize flag set to ```True```, if so a proper URL should be provided, or with the flag set to ```False```. In the latter case, chatbots are not involved in the creation of the dataset.
For ChatGPT, depending on the model the max number of tokens supported needs to be provided, thereafter a dedicated function estimates each time whether summarization is needed.

# Running the whole pipe

```$ ./run.sh chatbot-name```

This will create the dataset, get the result to the questions, compute the statistics and produce a ```statistics.csv``` file.
Update the scripts in the file depending on which you want to run.

# Running separately

## To crawl the terms of service run:

```$ python crawl_tos_list.py```

## To create the dataset for the experiments run:

```$ python create_dataset.py chatbot-name```

If text is too big it will be split recursively until an adequate nr of splits is made, i.e., the combined final text can be fed successfully to the bot.

## To get the statistics run: 

```$ python compare_to_ground_truth.py chatbot-name```

If ```statistics.csv``` does not exist, it will be created, a header and the values for random will be added, and thereafter the statistics for the chatbot used.
If the file already exists, only one line (corresponding to the results for the chatbot used) will be added.

### List of methods
uncut-nousHermes
Nous-Hermes-Llama2-13b
Mixtral-8x7B-v0.1-Instruct
Smaug-34B-v0.1
gpt-3.5-turbo-0125
gpt-4-turbo

### Prompts
The list of prompts for each chatbot is included in ```prompts.txt```.