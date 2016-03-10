#!/bin/bash 

SOURCEIP=$1
REALTIMEUR=$2


cp breach_initial.jsx breach.jsx
sed -i "s/\!replace\!/${REALTIMEUR}/" breach.jsx

gulp browserify

./runner.sh ${SOURCEIP}
