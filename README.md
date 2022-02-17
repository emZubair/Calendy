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

   `pip install -e requirements.txt`
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
5. Access the GraphiQL at `http://127.0.0.1:8000/graphql` in any browser of your choice.

### Explore the APIs

#### List Meetings
#### 1. All created Meeting
```shell
query{
  allMeetings{
    id
    owner
    startTime
    endTime
    title
    isReserved
  }
}
```
##### 2. Logged in user's Meetings
```shell
query{
  myMeetings{
    id
    startTime
    endTime
    slotDurationInMinutes
    isReserved
    reserverName
    reserverEmail
  }
}
```
##### 3. meetings by given user ID
```shell
query{
  meetingsByOwner(userId: 3){
    id
    startTime
    endTime
    slotDurationInMinutes
    isReserved
    owner
  }
}
```
##### 4. Bookable Meetings
```shell
query{
  bookableMeetings{
    id
    owner
    title
    startTime
    endTime
    slotDurationInMinutes
  }
}
```
##### Create a Meeting
```shell
mutation{
  createUpdateMeeting: createUpdateMeeting(
    title: "Automation for QA Team",
    startTime: "2022-06-20T18:15:14+00:00", 
    slotDurationInMinutes:30) {
    meeting {
      title,
      owner,
      startTime,
      endTime,
    }
  }
}
```

##### Update a Meeting
```shell
mutation{
  createUpdateMeeting: createUpdateMeeting(
    title: "The created Via Web",
    startTime: "2022-04-20T18:15:14+00:00", 
    slotDurationInMinutes:45, 
    meetingId:3) 
  {
    meeting {
      title
      owner
      startTime
      endTime
    }
  }
}
```

##### Delete A Meeting
```shell
mutation{
  deleteMeeting: deleteMeeting(
    meetingId: 2
  ) 
  {
    meeting {
      message
    }
  }
}
```

##### Reserve a Meeting
```shell
mutation{
  reserveMeeting: reserveMeeting(
    meetingId: 4, 
    reserverName: "Dave", 
    reserverEmail: "dave@example.om") {
    meeting{
      id
      title
      reserverName
      isReserved
      startTime
      endTime
      reserverEmail
      owner
    }
  }
}
```