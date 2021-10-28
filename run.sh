#!/bin/bash

if [ "$1" = "" ]; then
echo "Please enter the mode(train, train_valid, submission)."

else 
mode=$1
python run.py --mode "$mode" run

fi