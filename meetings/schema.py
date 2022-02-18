from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import authenticate

from graphql import GraphQLError
from graphene import (String, Int, Boolean, ObjectType, List, Mutation,
                      Field, Schema)
from graphene_django import DjangoObjectType

from .models import Meeting
from .utils import (reserve_meeting, create_or_update_meeting, delete_meeting)


def resolve_meeting_duration(obj):
    return f'{obj.slot_duration_in_minutes} minutes'


class MeetingType(DjangoObjectType):
    """
    Meeting type to map Django Model
    """
    class Meta:
        model = Meeting
        fields = (
            'id',
            'title',
            'start_time',
            'end_time',
            'reserver_name',
            'reserver_email'
        )
        description = "Meeting type to map Django Model"
    owner = String()
    meeting_duration = String()
    is_reserved = Boolean()

    def resolve_owner(self, info):
        return self.created_by.username

    def resolve_meeting_duration(self, info):
        return resolve_meeting_duration(self)

    def resolve_is_reserved(self, info):
        return self.is_reserved


class MeetingCreateUpdateType(DjangoObjectType):
    """
    Create or Update meeting
    """
    class Meta:
        model = Meeting
        fields = (
            'id',
            'title',
            'start_time',
            'end_time'
        )
    owner = String()
    meeting_duration = String()

    def resolve_owner(self, info):
        return self.created_by.username

    def resolve_meeting_duration(self, info):
        return resolve_meeting_duration(self)


class PrivateView:
    """
    Base view to validate User is logged In
    """

    @classmethod
    def validate_user(cls, info, error_message="Private view"):
        """
        validate user is logged in
        """

        username = info.context.headers.get("username")
        password = info.context.headers.get("password")

        user = authenticate(**{"username": username,
                               "password": password}
                            )
        if user:
            info.context.user = user
        if info.context.user.is_anonymous:
            raise GraphQLError(error_message)


class CreateUpdateMeeting(Mutation, PrivateView):
    """
    Create or update an existing Meeting, Meeting start time shouldn't be in the past
    In order to update provide a meeting ID and logged in user should be the one who created the meeting
    """
    class Arguments:
        meeting_id = Int()
        title = String()
        start_time = String()
        slot_duration_in_minutes = Int()

    ok = Boolean()
    meeting = Field(MeetingCreateUpdateType)

    @classmethod
    def mutate(cls, root, info, title, start_time, slot_duration_in_minutes, meeting_id=None):
        """
        User should be logged in
        if meeting_id is not none, fetch the matching Meeting & update that otherwise create a new one when its None

        :param title: (Str) title of the meeting
        :param start_time: (str) start time of the meeting
        :param slot_duration_in_minutes: (Int) duration of meeting in minutes
        :param meeting_id: (int) meeting ID for cases where update is required
        """

        cls.validate_user(info, "You must be logged in to create a meeting")
        meeting = create_or_update_meeting(title, start_time, slot_duration_in_minutes, info.context.user,
                                           meeting_id)

        ok = True
        return CreateUpdateMeeting(meeting=meeting, ok=ok)


class ReserveMeeting(Mutation):
    """
    Allows guest users to reserve a meeting added by Registered Users
    """
    class Arguments:
        meeting_id = Int()
        reserver_name = String()
        reserver_email = String()

    ok = Boolean()
    meeting = Field(MeetingType)

    def mutate(self, info, meeting_id, reserver_name, reserver_email):
        """
        Meeting is reserved when it is not reserved by anyone else and its start time is in future

        :param meeting_id: (int) ID of the the meeting to reserve
        :param reserver_name: (Str) name of the reserver
        :param reserver_email: (Str) Valid Email ID of the reserver
        """

        print(f'{id} reserved by {reserver_name} @: {reserver_email}')
        ok, meeting = reserve_meeting(meeting_id, reserver_name, reserver_email)
        return ReserveMeeting(meeting=meeting, ok=ok)


class DeleteMeeting(Mutation, PrivateView):
    """
    Delete the meeting matching given ID
    """

    message = String()

    class Arguments:
        meeting_id = Int()

    @classmethod
    def mutate(cls, root, info, meeting_id):
        """
        Meeting is deleted if user is logged In, and logged in user has created the meeting
        """

        # cls.validate_user(info, "You must be logged in to Delete a meeting")
        # meeting = delete_meeting(meeting_id, info.context.user)
        message = {"message": "Meeting Delete Successfully"}
        return message


class Mutation(ObjectType):
    """
    Mutation Object Type Definition
    """
    reserve_meeting = ReserveMeeting.Field()
    delete_meeting = DeleteMeeting.Field()
    create_update_meeting = CreateUpdateMeeting.Field()


class Query(ObjectType):
    """
    A list of queries to get list of meetings

    """

    my_meetings = List(MeetingType, description="List all meeting created by LoggedIn user, irrespective of status")
    all_meetings = List(MeetingType, description="List all meeting created by all users, irrespective of status")
    bookable_meetings = List(MeetingType, description="List bookable meetings, having date in future "
                                                      "and not reserved by anyone")
    meetings_by_owner = List(MeetingType, user_name=String(), description="Query meetings by user's username, "
                                                                          "first or last name")

    def resolve_bookable_meetings(self, info, **kwargs):
        """
        Get all bookable meetings i.e not reserved by anyone and start time is in the future
        """

        return Meeting.objects.filter(Q(Q(reserver_name=None) & Q(start_time__gte=timezone.now())))

    def resolve_all_meetings(self, info, **kwargs):
        """
        Get all available meetings, including reserved and past meetings
        """

        return Meeting.objects.all()

    def resolve_meetings_by_owner(self, info, user_name):

        """
        Get list of meetings created by a particular User using user's first, last or username
        """

        return Meeting.objects.filter(Q(Q(created_by__username__iexact=user_name) |
                                        Q(created_by__first_name__iexact=user_name) |
                                        Q(created_by__last_name__iexact=user_name)))

    def resolve_my_meetings(self, info):
        """
        Get list of meetings for logged In User
        """

        return Meeting.objects.filter(created_by=info.context.user)


schema = Schema(query=Query, mutation=Mutation)
