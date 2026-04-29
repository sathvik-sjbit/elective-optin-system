"""
Django signals for the elective opt-in system.

Signals:
- post_delete on Allocation: Automatically promotes next waitlisted student
  when an allocation is removed (waitlist auto-promotion feature).
"""

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Allocation


@receiver(post_delete, sender=Allocation)
def promote_waitlist_on_cancellation(sender, instance, **kwargs):
    """
    When an allocation is deleted (cancelled), restore the seat and
    promote the next student from the waitlist automatically.
    """
    course = instance.course

    # Restore the seat
    course.available_seats += 1
    course.save()

    # Import here to avoid circular import
    from .utils import promote_waitlist
    promote_waitlist(course)
