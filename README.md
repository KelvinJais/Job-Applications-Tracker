# A Job Applications Tracker app.

Works by reading through your email and using nlp to extract company names and job

## Notes

The text "Thank you for applying to Kelvin Corp."
returned this {'apply': 1, 'thank you for applying to company': 1}, Even though I specified greedy as longest.

## To do

->Gotta move the matcher declarion to a function and pass as argument to function. instead of creating one for every feature extraction. Slows down the code
