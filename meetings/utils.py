from datetime import datetime, timedelta

from .models import Meeting


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


def _create_meeting(title, start_time, end_time, duration, user):
    """
    create a meeting with given info
    """

    return Meeting.objects.create(created_by=user, title=title,
                                  start_time=start_time, end_time=end_time)


def _update_meeting(title, start_time, end_time, duration, meeting_id):
    """
    update meeting matching given meeting ID
    """

    Meeting.objects.filter(id=meeting_id).update(
        title=title, start_time=start_time, end_time=end_time,
        slot_duration_in_minutes=duration
    )
    return Meeting.objects.filter(id=meeting_id).first()


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

    start_time = str_to_datetime(start_time)
    end_time = calculate_meeting_end_time(start_time, duration)
    meeting = _create_meeting(title, start_time, end_time, duration, user) if \
        meeting_id is None else _update_meeting(title, start_time, end_time, duration, meeting_id)
    return meeting


def reserve_meeting(meeting_id, reserver_name, reserver_email):
    """
    reserve meeting matching given ID for guest users with details

    :returns: (Bool) True if meeting is reserved, False if already reserved or passed
    """

    if Meeting.objects.filter(id=meeting_id).exists():
        meeting = Meeting.objects.filter(id=meeting_id).first()
        if meeting.is_reserved or meeting.is_meeting_over:
            return False, None
        meeting.reserver_name = reserver_name
        meeting.reserver_email = reserver_email
        meeting.save()
        return True, meeting
    return False, None
