### Calendy
Allows users to 

- Users can create a schedule of available dates and times and select their desired meeting intervals 
(15 min / 30 min / 45 min) 
- allow the user to do CRUD operations ( create / read / update / delete ) on his available schedule
- Non-users can view all available timings for a specific user
- Non-users can reserve a specific time by providing their full name and email for the meeting
- Non-user can’t reserve a time that has been already reserved 


### Testing

List all Meetings
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

Create
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

Update 
```shell
mutation{
  createUpdateMeeting: createUpdateMeeting(
    title: "The created Via Web",
    startTime: "2022-04-20T18:15:14+00:00", 
    slotDurationInMinutes:45, 
    meetingId:4) 
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

Delete
```shell
mutation{
  deleteMeeting: deleteMeeting(id: 2) {
    meeting {
      id
      title
    }
  }
}
```

Reserve
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