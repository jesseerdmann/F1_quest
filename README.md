# F1_Quest

A tool to process entries in the F1 Guessathon and report results.

## Important links

* [Questionnaire and response view](https://docs.google.com/forms/d/e/1FAIpQLScVSQzdRhG6OcdGcjhrt45V7NRMC0pswoKMMpIZ04k23Ys-GQ/viewform?usp=sf_link)
* [Spreadsheet of responses](https://docs.google.com/spreadsheets/d/1UEA9vYsKeAGy86FhEWCcvjqifqjSZ3yj0iqTcUTP5UQ/edit?usp=sharing)
* [Spreadsheet for race results](https://docs.google.com/spreadsheets/d/1_-pQEPdSTRHe8AWTl9mobXlFGweGFntpCpIMI31lgJ8/edit?usp=sharing)

The spreadsheets are exported to the data directory as CSVs for processing


## Design Goals

This project will be visited infrequently, it should be easily read and rely on
simple tools without a lot of unneccessary libraries. This means long, specfic 
variable names and docstrings. The reasons for keeping it simple are that the
developer will lose familiarity with any non-standard components and the data 
is so tiny anything beyond simple CSV reading and for loops are overkill.

## Basic Structure

### Read the real world data

Using Teams, Drivers and Races read the CSVs representing the on track results.
These classes will accumulate race results so that, for instance, the points 
attribute of a driver will reflect the total points accumulated through 
completed races thus far this season. They also provide methods to do things 
like display a text table where it makes sense for things like "What are the 
current driver standings for points scored across the season?"

### Convert the results to an answer key

Using AnswerKey, produce dictionaries that will allow entries answers to be 
mapped directly to the point value those answers are worth where applicable,
or the value to compare against to sort the entries by proximity to the 
correct answer in most other cases.


### Score the entries

Using Entries, read the user entries and score them based on the real world 
results as completed thus far. As suggested by the answer key above, in many
cases this will mean adding the value of the given answer to the entries point
total. In others entries will need to be ranked using various means like 
proximity to the true value. Once ranked, entries will be scored for the 
question based on F1 scoring, 25 for first, 18 for second, etc.