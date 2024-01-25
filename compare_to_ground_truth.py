import json
import os
import sys
import numpy as np

nr_questions = 12
total_ds = 0
total_skipped = 0

def get_accuracy_over_datasets(r_dataset):
    global total_ds, total_skipped
    #calculate average percentage of correctly answered question over all datasets
    idx = 0
    accuracy = 0
    skipped = False
    nr_skipped = 0
    nr_datasets = len(r_dataset)/nr_questions
    while idx < len(r_dataset):
        nr_matching = 0
        single_r_dataset = r_dataset[idx:idx+nr_questions] 

        for el in single_r_dataset:
            for key,val in el.items():
                #print(f"{key} {val}")
                if val == "TOOBIG":
                    skipped = True
                    break
                if key in val:
                    nr_matching = nr_matching + 1
            if skipped:
                skipped = False
                nr_skipped = nr_skipped + 1
                break

        #print(f" Matching in current dataset {nr_matching}")
        accuracy = accuracy + 100*nr_matching/nr_questions
        #print(accuracy)
        
        idx = idx + nr_questions
    
    print(f"#datasets {nr_datasets}")
    print(f"#skipped {nr_skipped}")
    #print(f"#accuracy {accuracy}")
    total_skipped = nr_skipped
    total_ds = nr_datasets
    return accuracy/(nr_datasets-nr_skipped)
    

def get_accuracy_xquestion(r_dataset):
    #calculate average percentage of correct guessing for each question
    questions_accuracy = []
    idx = 0    

    while idx < nr_questions:
        nr_skipped = 0
        nr_matching = 0
        single_r_question = r_dataset[idx::nr_questions] 

        for el in single_r_question:
            for key,val in el.items():
                if val == "TOOBIG":
                    nr_skipped = nr_skipped + 1
                    break
                if key in val:
                    nr_matching = nr_matching + 1
        #print(f"#matching {nr_matching}")
        #print(f"#skipped {nr_skipped}")

        questions_accuracy.append(100*nr_matching/(len(single_r_question)-nr_skipped))
        idx = idx + 1
    
    return questions_accuracy

def get_random_accuracies():
    products_path = "products.json"
    with open(products_path, 'r') as json_file:
        content = json.loads(json_file.read())
    # get first entry in products
    product = content[0]
    options_length = [] # array of nr of alternatives for each question
    for rubric in product['rubric']:
        length = len(rubric["question"]["options"])
        options_length.append(length)

    prob_correctness_xquestion = [100/x for x in options_length] 
    print(f"{prob_correctness_xquestion}")
    #TODO the weight is based on the nr of questions having x alternatives, this is multiplied.
    prob_correctness_over_datasets = np.sum(prob_correctness_xquestion)/len(prob_correctness_xquestion)
    print(f"{prob_correctness_over_datasets}")

    return prob_correctness_over_datasets, prob_correctness_xquestion

total, xquestion = get_random_accuracies()
#Provide filenames with the results
filename_results_list = ["opensource-results-sum", "opensource-results-intact"]
foutput = []
for fname in filename_results_list:
    element = f"{fname}.csv"
    foutput.append(element)
    with open(element, "w+") as f:
        f.write("method, #ds, #skipped, total, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12\n")
        f.write(f"random, {total_ds}, {0}, {total}, ")
        for q in xquestion:
            f.write(f"{q},")
        f.write("\n")

#Iterate over results -- each result file is a product of a single generative AI
for idx, fname in enumerate(filename_results_list):
    with open(f"{fname}.json", "r") as f:
        tos_result = json.load(f)
    total_accuracy = get_accuracy_over_datasets(tos_result)
    print(total_accuracy)
    accuracy_xquestion = get_accuracy_xquestion(tos_result)
    print(accuracy_xquestion)

    #append values to file
    with open(foutput[idx], "a") as f:
        f.write(f"{fname}, {total_ds}, {total_skipped}, {total_accuracy},")
        for q in accuracy_xquestion:
            f.write(f"{q},")
        f.write("\n")


