from django.utils import timezone
from django.db.models import Q

from graphql import GraphQLError
from graphene import (String, Int, Boolean, ObjectType, List, Mutation,
                      Field, Schema)
from graphene_django import DjangoObjectType

from .models import Meeting
from .utils import (reserve_meeting, create_or_update_meeting, delete_meeting)


class MeetingType(DjangoObjectType):
    class Meta:
        model = Meeting
        fields = (
            'id',
            'title',
            'start_time',
            'end_time',
            'reserver_name',
            'reserver_email',
            'slot_duration_in_minutes'
        )
    owner = String()
    is_reserved = Boolean()

    def resolve_owner(self, info):
        return self.created_by.username

    def resolve_is_reserved(self, info):
        return self.is_reserved


class MeetingCreateUpdateType(DjangoObjectType):
    class Meta:
        model = Meeting
        fields = (
            'id',
            'title',
            'start_time',
            'slot_duration_in_minutes',
            'end_time'
        )
    owner = String()

    def resolve_owner(self, info):
        return self.created_by.username


class MeetingDeleteType(ObjectType):
    message = String()

    def resolve_message(self):
        return "Meeting deleted successfully"


class PrivateView:
    @classmethod
    def validate_user(cls, info, error_message="Private view"):
        """
        validate user is logged in
        """

        if info.context.user.is_anonymous:
            raise GraphQLError(error_message)


class CreateUpdateMeeting(Mutation, PrivateView):
    class Arguments:
        meeting_id = Int()
        title = String()
        start_time = String()
        slot_duration_in_minutes = Int()

    ok = Boolean()
    meeting = Field(MeetingCreateUpdateType)

    @classmethod
    def mutate(cls, root, info, title, start_time, slot_duration_in_minutes, meeting_id=None):
        ok = False
        cls.validate_user(info, "You must be logged in to create a meeting")
        meeting = create_or_update_meeting(title, start_time, slot_duration_in_minutes, info.context.user,
                                           meeting_id)

        if meeting:
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
    class Arguments:
        meeting_id = Int()

    ok = Boolean()
    meeting = Field(MeetingDeleteType)

    @classmethod
    def mutate(cls, root, info, meeting_id):
        cls.validate_user(info, "You must be logged in to Delete a meeting")
        delete_meeting(meeting_id, info.context.user)
        ok = True
        return DeleteMeeting(ok=ok)


class Mutation(ObjectType):
    reserve_meeting = ReserveMeeting.Field()
    delete_meeting = DeleteMeeting.Field()
    create_update_meeting = CreateUpdateMeeting.Field()


class Query(ObjectType):
    """
    A list of qeries to get list of meetings
    : all_meetings: get list of all meetings
    """

    my_meetings = List(MeetingType)
    all_meetings = List(MeetingType)
    bookable_meetings = List(MeetingType)
    meetings_by_owner = List(MeetingType, user_id=Int())

    def resolve_bookable_meetings(self, info, **kwargs):
        """
        Get all available meetings
        """

        return Meeting.objects.filter(Q(Q(reserver_name=None) & Q(start_time__gte=timezone.now())))

    def resolve_all_meetings(self, info, **kwargs):
        """
        Get all available meetings
        """

        return Meeting.objects.all()

    def resolve_meetings_by_owner(self, info, user_id):

        """
        Get list of meetings created by a particular User
        """
        return Meeting.objects.filter(created_by=user_id)

    def resolve_my_meetings(self, info):
        """
        Get list of meetings for logged In User
        """
        return Meeting.objects.filter(created_by=info.context.user)


schema = Schema(query=Query, mutation=Mutation)
