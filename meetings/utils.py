from re import fullmatch
from django.utils import timezone
from datetime import datetime, timedelta

from graphql import GraphQLError

from .models import Meeting
from .constants import EMAIL_REGEX


def calculate_meeting_end_time(start_time, duration_in_minutes):
    """
    calculate & return end time after adding given duration minutes in it
    """

    return start_time + timedelta(minutes=duration_in_minutes)


def str_to_datetime(str_time):
    """
    converts given time in str format to datetime
    """

    return datetime.fromisoformat(str_time)


def _next_free_slot(reserved_meetings, start_time):
    """
    calculate the time when user will be free by comparing two timestamps

    :param reserved_meetings: (Queryset) meeting object
    :param start_time: (datetime)

    :returns: (str) Minutes in str format i.e 10.0 Minutes
    """

    wait_message = ""
    first_meeting = reserved_meetings.first()
    if first_meeting:
        wait_message = f'{(first_meeting.end_time - start_time).total_seconds() / 60.0} minutes'

    return wait_message


def _validate_user_availability(user, meeting_time, meeting_to_update=None):
    """
    validate user isn't already booked
    """

    user_meetings = Meeting.objects.filter(start_time__lte=meeting_time,
                                           end_time__gte=meeting_time, created_by=user)
    if meeting_to_update:
        user_meetings = user_meetings.exclude(id=meeting_to_update.id)

    wait_message = _next_free_slot(user_meetings, meeting_time)

    if user_meetings:
        raise GraphQLError(f"You already have a slot booked for this time: {meeting_time},"
                           f" try again in {wait_message}")


def _validate_past_dates(meeting_time):
    """
    validate user isn't already booked
    """

    if meeting_time <= timezone.now():
        raise GraphQLError(f"Given date has already passed, try a future date: {meeting_time}")


def _create_meeting(title, start_time, end_time, duration, user):
    """
    create a meeting with given info
    """

    _validate_past_dates(start_time)
    _validate_user_availability(user, start_time)
    return Meeting.objects.create(created_by=user, title=title,
                                  start_time=start_time, end_time=end_time,
                                  slot_duration_in_minutes=duration)


def _validate_meeting_owner(meeting_owner, current_user):
    """
    validate current user matches the given meeting owner
    """

    if meeting_owner != current_user:
        raise GraphQLError("Invalid meeting, you don't have the rights to update or delete this meeting")


def _update_meeting(title, start_time, end_time, duration, meeting_id, current_user):
    """
    update meeting matching given meeting ID
    """

    meeting = Meeting.objects.filter(id=meeting_id).first()
    _validate_meeting_owner(meeting.created_by, current_user)
    _validate_past_dates(start_time)
    _validate_user_availability(current_user, start_time, meeting)

    if meeting:
        Meeting.objects.filter(id=meeting_id).update(
            title=title, start_time=start_time, end_time=end_time,
            slot_duration_in_minutes=duration
        )
        return meeting
    return None


def _validate_meeting_duration(duration):
    """
    validate meeting duration lies within the valid range i.e 15, 30 or 45 minutes
    """

    valid_durations = [15, 30, 45]
    if duration not in valid_durations:
        raise GraphQLError(f'Invalid Meeting duration, expected values are :{valid_durations}')


def create_or_update_meeting(title, start_time, duration, user, meeting_id):
    """
    Create and Meeting and associate with given User
    :param title: (str)
    :param start_time: (Datetime)
    :param duration: (Int)
    :param user: (UserModel)
    :param meeting_id: (int) Meeting ID to update

    :returns: (Meeting) Create or updated Meeting object
    """

    _validate_meeting_duration(duration)
    start_time = str_to_datetime(start_time)
    end_time = calculate_meeting_end_time(start_time, duration)
    meeting = _create_meeting(title, start_time, end_time, duration, user) if \
        meeting_id is None else _update_meeting(title, start_time, end_time, duration, meeting_id, user)
    return meeting


def _validate_email(email):
    """
    validate given Email is valid
    """

    if not fullmatch(EMAIL_REGEX, email):
        raise GraphQLError("Invalid Email, please provide a correct Email")


def _validate_user_data(name, email):
    """
    validate user name and emails are valid
    """

    if name.strip() == '' or email.strip() == '':
        raise GraphQLError("Name & emails shouldn't be empty strings")
    return _validate_email(email.strip())


def reserve_meeting(meeting_id, reserver_name, reserver_email):
    """
    reserve meeting matching given ID for guest users with details

    :returns: (Bool) True if meeting is reserved, False if already reserved or passed
    """

    if Meeting.objects.filter(id=meeting_id).exists():
        meeting = Meeting.objects.filter(id=meeting_id).first()
        if meeting.is_reserved:
            raise GraphQLError("Meeting already reserved by another candidate")
        if meeting.is_meeting_over:
            raise GraphQLError("Meeting is over, please reserve a new meeting with Future date")
        _validate_user_data(reserver_name, reserver_email)
        meeting.reserver_name = reserver_name
        meeting.reserver_email = reserver_email
        meeting.save()
        return True, meeting
    return False, None


def delete_meeting(meeting_id, user):
    """
    Delete the meeting matching given meeting ID & User
    """

    meeting = Meeting.objects.filter(id=meeting_id).first()

    if meeting is None:
        raise GraphQLError(f'No Meeting found matching the given ID: {meeting_id}')
    _validate_meeting_owner(meeting.created_by, user)
    print(f'Deleting meeting with ID:{meeting_id}')
    return meeting.delete()
