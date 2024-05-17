# tos-busters

# Running the whole pipe

```$ ./run.sh chatbot-name```

This will create the dataset, get the result to the questions, compute the statistics and produce a ```statistics.csv``` file.

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