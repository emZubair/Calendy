import graphene
from graphene import String, Int, Boolean, ObjectType

from graphene_django import DjangoObjectType
from .models import Meeting
from .utils import reserve_meeting, create_or_update_meeting


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


class CreateUpdateMeeting(graphene.Mutation):
    class Arguments:
        meeting_id = Int()
        title = String()
        start_time = String()
        slot_duration_in_minutes = Int()

    ok = Boolean()
    meeting = graphene.Field(MeetingCreateUpdateType)

    def mutate(self, info, title, start_time, slot_duration_in_minutes, meeting_id=None):
        # if meeting_id:
        ok = False
        meeting = create_or_update_meeting(title, start_time, slot_duration_in_minutes, info.context.user,
                                           meeting_id)

        if meeting:
            ok = True
        return CreateUpdateMeeting(meeting=meeting, ok=ok)


class ReserveMeeting(graphene.Mutation):
    """
    Allows guest users to reserve a meeting added by Registered Users
    """
    class Arguments:
        meeting_id = Int()
        reserver_name = String()
        reserver_email = String()

    ok = Boolean()
    meeting = graphene.Field(MeetingType)

    def mutate(self, info, meeting_id, reserver_name, reserver_email):
        """
        :param meeting_id: (int) ID of the the meeting to reserve
        :param reserver_name: (Str) name of the reserver
        :param reserver_email: (Str) Valid Email ID of the reserver
        """
        print(f'{id} reserved by {reserver_name} @: {reserver_email}')
        ok, meeting = reserve_meeting(meeting_id, reserver_name, reserver_email)
        return ReserveMeeting(meeting=meeting, ok=ok)


class DeleteMeeting(graphene.Mutation):
    class Arguments:
        id = Int()

    ok = Boolean()
    meeting = graphene.Field(MeetingDeleteType)

    def mutate(self, info, id):
        Meeting.objects.get(id=id).delete()
        print(f'Deleting meeting with ID:{id}')
        ok = True
        return DeleteMeeting(ok=ok)


class Mutation(graphene.ObjectType):
    reserve_meeting = ReserveMeeting.Field()
    delete_meeting = DeleteMeeting.Field()
    create_update_meeting = CreateUpdateMeeting.Field()


class Query(graphene.ObjectType):
    """
    A list of qeries to get list of meetings
    : all_meetings: get list of all meetings
    """
    all_meetings = graphene.List(MeetingType)
    meetings_by_owner = graphene.Field(MeetingType, user_id=graphene.Int())

    def resolve_all_meetings(self, info, **kwargs):
        """
        Get all available meetings
        """
        if not info.context.user.is_authenticated:
            print("User is not authenticated")
        else:
            print("User is authenticated")
        return Meeting.objects.all()

    def resolve_meetings_by_owner(self, info, user_id):
        return Meeting.objects.filter(created_by=user_id)


class MeetingInput(graphene.InputObjectType):
    created_by = graphene.ID()
    title = graphene.String()
    start_time = graphene.String()
    year_published = graphene.String()
    review = graphene.Int()


schema = graphene.Schema(query=Query, mutation=Mutation)
# schema = graphene.Schema(query=Query)
