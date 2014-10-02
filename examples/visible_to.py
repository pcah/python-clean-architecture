from datetime import datetime

from django.db.models import Q

from .models import User, Category, Group, EventInvitation, Document, UserRole


def visible_to_q(user):
    """Return only documents that are visible to given user.

    This should be the same logic as in Document.can_see

    >> user = User.objects.get(slug='kk')
    >> filtered = (d for d in Document.objects.all() if d.can_see(user))
    >> set(filtered) == set(Document.objects.visible_to(user))
    True
    """

    user = User.coerce(user)
    invs = _events_user_is_invited_to(user)

    if user is None:
        return _is_public_q()

    visible_to_me = Q(
        visible_to__isnull=False,
        visible_to__in=user.on_userslist_set.all()
    ) | Q(visible_to__isnull=True)

    if user.is_moderator or user.is_superuser:
        visible_to_me |= Q(
            visible_to__isnull=False,
            visible_to__private=False)

    # published documents are visible if they are not group documents
    visible_to_not_invited = Q(category__owner__group__isnull=True)

    # if document is published on site:
    visible_to_not_invited |= Q(category__owner__group__isnull=False) & (
        # show documents to their moderators
        # show published, ACCEPTED, non-private documents
        # on sites visible to this user
        Q(
            site_status=Document.SITE_STATUS_CHOICES.ACCEPTED,
            category__owner__group__in=_groups_visible_to_user(user)
        )
    )
    # events are always visible to invited users
    visible_to_not_invited |= Q(pk__in=invs)

    visible_to_not_invited &= Q(visible_to_invited=False)
    visible_to_not_invited &= visible_to_me

    # if document is visible_to_invited
    visible_to_invited = Q(visible_to_invited=True)
    visible_to_invited &= Q(pk__in=invs)

    visible = visible_to_not_invited | visible_to_invited

    # documents waiting for admin moderation are only visible to author
    # (document is always visible to author, see later, so we only filter
    # by admin_moderation_status here)
    visible &= ~Q(admin_moderation_status=Document.
                  ADMIN_MODERATION_STATUS_CHOICES.WAITING)
    visible &= published_q()
    # no matter what, it's visible to its author
    visible |= Q(user_author=user.userlike_ptr)
    visible |= can_see_as_moderator_q(user)

    return (
        visible_q() & visible
        | _is_public_q())


def can_see_as_moderator_q(user):
    return Q(category__owner__group__in=_groups_user_can_moderate(user),
             publication_date__isnull=False)


def _is_public_q():
    """Return all public Documents"""
    # get all publicly visible sites documents
    public_filter = Q(
        category__owner__group__group_visibility=Group
        .VISIBILITY_OPTIONS.ALL,
        site_status=Document.SITE_STATUS_CHOICES.ACCEPTED)
    # and all non-sites documents
    public_filter |= Q(category__owner__group__isnull=True)

    public_filter &= Q(
        # only take those categories - ignore archive, collections etc.
        category__model_type__in=(Category.TYPE_CHOICES.MAIN_BOARD,
                                  Category.TYPE_CHOICES.TOPIC),
        visible_to=None,
    ) & accepted_by_admin_q()
    public_filter &= Q(visible_to_invited=False)
    return published_q() & public_filter


def published_q():
    return visible_q() & Q(publication_date__lt=datetime.now)


def visible_q():
    """Is this document visible at all"""
    return ~Q(category__model_type=Category.TYPE_CHOICES.ARCHIVE)


def accepted_by_admin_q():
    return Q(admin_moderation_status__in=(
        ADMIN_MODERATION_STATUS_CHOICES.NONE,
        ADMIN_MODERATION_STATUS_CHOICES.ACCEPTED))


def _events_user_is_invited_to(user):
    return EventInvitation.objects.filter(
        invited_user=user, cancelled=False).values_list('event', flat=True)


def _groups_visible_to_user(user):
    return Group.objects.filter(_groups_visible_to_user(user))


def _groups_visible_to_user_q(user):
    """Return only groups visible to `user`"""
    user = User.coerce(user)

    # group is either public, or visible only to some roles
    visible = Q(group_visibility=Group.VISIBILITY_OPTIONS.ALL)
    if user:
        group_pks = UserRole.objects.filter(
            user=user,
            role__in=(
                UserRole.ROLE_CHOICES.ADMINISTRATOR,
                UserRole.ROLE_CHOICES.AUTHOR,
                UserRole.ROLE_CHOICES.MODERATOR)) \
            .values_list('group_id', flat=True)
        visible |= Q(pk__in=group_pks)

    return visible


def _groups_user_can_moderate(user):
    return Group.objects.filter(_groups_user_can_moderate_q(user))


def _groups_user_can_moderate_q(user):
    return Q(userrole__user=User.coerce(user),
             userrole__role=UserRole.ROLE_CHOICES.MODERATOR)
