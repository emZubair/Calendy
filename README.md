### Calendy ![Pylint Workflow](https://github.com/emzubair/Calendy/actions/workflows/pylint.yml/badge.svg)
Allows users to 

- Users can create a schedule of available dates and times and select their desired meeting intervals 
(15 min / 30 min / 45 min) 
- allow the user to do CRUD operations ( create / read / update / delete ) on his available schedule
- Non-users can view all available timings for a specific user
- Non-users can reserve a specific time by providing their full name and email for the meeting
- Non-user can’t reserve a time that has been already reserved 


### Setup
To setup the project locally create & activate a virtual environment using python >= 3.8.0

1. clone the project using following command.

   `git clone git@github.com:emzubair/Calendy.git`

2. After clone, type `cd calendy` & project install the requirements using 

   `pip install -r requirements.txt`
3. Run the migrations using, `python manage.py migrate`
This will populate the database with 4 users & some meetings.
User's details is given below

| Username      | Email | Password     | Superuser     |
| :---        |    :----:   |          :--- | :---|
| edx      | edx@example.com       | edx   |✅
|  wick  | wick@example.com        | admin12345      |❌
|  doe  | john@example.com        | admin12345      |❌
|  hales  | hales@example.com        | admin12345      |❌

4. Run the server using `python manage.py runserver`

### Explore the APIs
Explore APIs instructions are mentioned in [ALTAIR.md](/zee_utils/assets/altair/ALTAIR.md) or follow the path 
`zee_utils/assets/altair/ALTAIR.md`
