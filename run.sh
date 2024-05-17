#!/bin/bash
if [ $# -eq 0 ]; then
 echo "[ERROR] Provide name of chatbot used"
 exit 1
fi

method=$1

echo Running for $method

echo Prepare environment
source venv/bin/activate
    
echo Create dataset, summarising text that''s too big, with method
time -p python create_dataset.py $method 

echo Ask questions with method and collect results
time -p python os_client_local.py $method 

echo Calculate statistics for method
time -p python compare_to_ground_truth.py $method 

echo Plot results - Not implemented!