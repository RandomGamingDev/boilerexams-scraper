<img width="700" height="auto" alt="BoilerexamsScraper" src="https://github.com/user-attachments/assets/be548c88-11d3-41a4-906a-fad983ee6f78" alt="BoilerexamsScraper" />

#### A Python script that gets the `Subjects` ▶ `Courses` ▶ `Exams` & `Topics` ▶ `Questions` from Boilerexams

<br/>

## Purpose
#### Provides Boilerexams data in an offline easy to access format, primarily for projects based off of Boilerexams.
##### You're free to use it for anything else though, like offline access :D

<br/>

## Structure
#### The data's provided in directories following the `<subject>`/`<course>`/`<exams/topics>`/`<assessment>`/`question` format.
##### e.g. exam question `"Aero & Astro Engineering/AAE20300/exams/#0-SPRING,2007/question-1.json"`
##### or topic question `"Aero & Astro Engineering/AAE20300/topics/Basic Kinematic Equation (BKE)/question-1.json"`
#### Each and every directory contains the result from the API which includes additional data except for `<assessment>` since it isn't its own query.

Note: Each exam's formatting (directories under `exams`) is its test order within its course (i.e. `Midterm 1 -> 0`, `Midterm 2 -> 1`, `Final -> 2`) followed by season (including year).

<br/>

## Parameters (ENV) & Default Value
#### `JSON_INDENT=2`: JSON spacing. Use an integer for spacing in human readable format, and "None" for none.
#### `QUESTIONS_OUT="./boilerexam-questions"`: Scraped results output directory.

<br/>

## Partial Boilerexams API Documentation
#### (Not meant to be a full explanation, just give you enough to understand the code and maybe even use the API yourself)
- Returns subjects: `https://api.boilerexams.com/courses/subjects`
- Returns specific type of study resources for a course: `https://api.boilerexams.com/courses/<course id>/<study resource type>`
- Returns question (including answers): `https://api.boilerexams.com/questions/<question id>`
