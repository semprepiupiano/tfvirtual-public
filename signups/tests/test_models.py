from django.test import TestCase
import datetime
from django.utils import timezone
from signups.models import Event, SignUp
import pytz
from.test_helpers import *
from django.core.exceptions import ValidationError


class EventModelTests(TestCase):
    
    def test_signups_remaining_default(self):
        """signups_remaining() returns 3 after 5 signups have been created for a default signup_limit of 8"""
        event = create_event(5, 0, 0, 0)
        for i in range(5):
            create_signup(event)
        self.assertEqual(event.signups_remaining(), 3)
    
    def test_signups_remaining_limit(self):
        """signups_remaining() returns 5 after 5 signups have been created for a signup_limit of 10"""
        event=create_event_limit(5, 0, 0, 0, 10)
        for i in range(5):
            create_signup(event)
        self.assertEqual(event.signups_remaining(), 5)
    
    def test_signups_remaining_one(self):
        """signups_remaining() returns 0 after 1 signup has been created for a signup_limit of 1"""
        event=create_event_limit(5, 0, 0, 0, 1)
        create_signup(event)
        self.assertEqual(event.signups_remaining(), 0)
    
    def test_spots_open_empty(self):
        """spots_open returns True for an event with no signups"""
        event = create_event(5, 0, 0, 0)
        self.assertEqual(event.spots_open(), True)
    
    def test_spots_open_some(self):
        """spots_open returns True for an event with some signups"""
        event=create_event(5, 0, 0, 0)
        for i in range(7):
            create_signup(event)
        self.assertEqual(event.spots_open(), True)
    
    def test_spots_open_full(self):
        """spots_open returns False for an event with signups equal to the signup_limit"""
        event = create_event(5, 0, 0, 0)
        for i in range(8):
            create_signup(event)
        self.assertEqual(event.spots_open(), False)
    
    def test_spots_open_greater(self):
        """spots_open returns False for an event with more signups than its signup_limit"""
        event = create_event(5, 0, 0, 0)
        for i in range(9):
            create_signup(event)
        self.assertEqual(event.spots_open(), False)
    
    def test_signups_closed_gt_10_days(self):
        """signups_closed returns True for an event that is more than 10 days in the future"""
        event = create_event(10, 0, 0, 1)
        self.assertEqual(event.signups_closed(), True)
    
    def test_signups_closed_lt_10_days(self):
        """signups_closed returns False for an event that is closer than 10 days but more than 1 day 
        in the future"""
        event = create_event(9, 23, 59, 59)
        self.assertEqual(event.signups_closed(), False)
    
    def test_signups_closed_gt_1_day(self):
        """signups_closed returns False for an event that is more than 1 day but closer than 10 days
        in the future"""
        event = create_event(1, 0, 0, 1)
        self.assertEqual(event.signups_closed(), False)
    
    def test_signups_closed_lt_1_day(self):
        """signups_closed returns True for an event that is less than 1 day in the future"""
        event = create_event(0, 23, 59, 59)
        self.assertEqual(event.signups_closed(), True)
    
    def test_get_date(self):
        """get_date returns the date in the proper format for an event"""
        time = timezone.now() + datetime.timedelta(days=10)
        event = create_event(10, 0, 0, 0)
        self.assertEqual(event.get_date(), time.strftime("%m/%d/%Y"))
    
    def test_is_future_event_past(self):
        """is_future_event returns False for an event in the past"""
        event = create_event(0, 0, 0, -1)
        self.assertEqual(event.is_future_event(), False)

    def test_is_future_event_future(self):
        """is_future_event returns True for an event in the future"""
        event = create_event(0, 0, 0, 1)
        self.assertEqual(event.is_future_event(), True)
    
    def test_program_length_empty(self):
        """program_length returns 0:00 for an empty program"""
        event = create_event(10, 0, 0, 0)
        self.assertEqual(event.program_length(), "0:00")
    
    def test_program_length_lt_one_hour_one_signup(self):
        """program_length returns the correct length for a program less than one hour with one signup"""
        event = create_event(10, 0, 0, 0)
        signup1 = create_signup_piece_length(event, datetime.timedelta(minutes=2, seconds=30))
        self.assertEqual(event.program_length(), "2:30")
    
    def test_program_length_lt_one_hour_multiple_signups(self):
        """program_length returns the correct length for a program less than one hour with multiple signups"""
        event = create_event(10, 0, 0, 0)
        signup1 = create_signup_piece_length(event, datetime.timedelta(minutes=2, seconds=30))
        signup2 = create_signup_piece_length(event, datetime.timedelta(minutes=5, seconds=45))
        signup3 = create_signup_piece_length(event, datetime.timedelta(minutes=8, seconds=45))
        signup4 = create_signup_piece_length(event, datetime.timedelta(minutes=3, seconds=3))
        self.assertEqual(event.program_length(), "20:03")
    
    def test_program_length_gt_one_hour(self):
        """program_length returns the correct length for a program greater than one hour"""
        event = create_event(10, 0, 0, 0)
        signup1 = create_signup_piece_length(event, datetime.timedelta(hours=1))
        signup2 = create_signup_piece_length(event, datetime.timedelta(minutes=5, seconds=3))
        self.assertEqual(event.program_length(), "1:05:03")
    
    def test_program_length_gt_one_day(self):
        """program_length returns the correct length for a program greater than one day"""
        event = create_event(10, 0, 0, 0)
        signup1 = create_signup_piece_length(event, datetime.timedelta(days=1, seconds=1))
        signup2 = create_signup_piece_length(event, datetime.timedelta(hours=3, minutes=3, seconds=30))
        self.assertEqual(event.program_length(), "1 day, 3:03:31")

    def test_performance_order_active_open_signup_order_finalized(self):
        """performance_order_active returns False if signups are still open but the event's order is finalized"""
        event = create_event(1, 0, 0, 1)
        event.order_finalized = True
        self.assertEqual(event.performance_order_active(), False)
    
    def test_performance_order_active_closed_signups_order_not_finalized(self):
        """performance_order_active returns False if the event's order is not finalized but signups are closed"""
        event = create_event(0, 23, 59, 59)
        event.order_finalized = False
        self.assertEqual(event.performance_order_active(), False)
    
    def test_performance_order_active_open_signups_order_not_finalized(self):
        """performance_order_active returns False if the event's order is not finalized and the signups are open"""
        event = create_event(1, 0, 0, 1)
        event.order_finalized = False
        self.assertEqual(event.performance_order_active(), False)

    def test_performance_order_active_closed_signups_order_finalized(self):
        """performance_order_active returns True if the event's order is finalized and the signups are closed"""
        event = create_event(0, 23, 59, 59)
        event.order_finalized = True
        self.assertEqual(event.performance_order_active(), True)

    def test_performance_order_active_signups_closed_10_days_order_finalized(self):
        """performance_order_active returns False if the event's signups are closed more than 10 days before
        and the order is not finalized"""
        event = create_event(10, 0, 0, 1)
        event.order_finalized = True
        self.assertEqual(event.performance_order_active(), False)
    
    def test_performance_order_active_signups_closed_10_days_order_not_finalized(self):
        """performance_order_active returns False if the event's signups are closed more than 10 days before"""
        event = create_event(10, 0, 0, 1)
        event.order_finalized = False
        self.assertEqual(event.performance_order_active(), False)
        
    def test_str(self):
        """__str__ returns the correct string representation for an event"""
        eastern = pytz.timezone('US/Eastern')
        date = eastern.localize(datetime.datetime(2021, 5, 18, 15, 0, 0, 0))
        event =  Event.objects.create(date=date, streamyard_link="streamyard.com", youtube_link="youtube.com")
        self.assertEqual(str(event), "May 18, 2021, 3:00 PM")
    
    def test_default_name(self):
        """name returns the correct default name for an event"""
        event = create_event(10, 0, 0, 0)
        self.assertEqual(event.name, "Tacy Foundation Virtual Live Performance")

    def test_default_signup_limit(self):
        """signup_lmit returns the correct default signup limit for an event"""
        event = create_event(10, 0, 0, 0)
        self.assertEqual(event.signup_limit, 8)

class SignUpModelTests(TestCase):

    def test_str(self):
        """__str__ returns the correct string representation for a signup"""
        event = create_event(10, 0, 0, 0)
        signup = create_signup(event)
        self.assertEqual(str(signup), "Sasha Suh")

    #TODO: Create signup tests!
    # def test_empty_performer_email(self):
    #     """