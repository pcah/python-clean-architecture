from datetime import datetime
from django.db.models import Q
from typing import (
    Iterable,
    List
)

from dharma.data.formulae import var, Var, Predicate
from .models import User, Category, Group, EventInvitation, Document, UserRole


def visible_to_q(user, event_invitations, event_inv_repo):
    """Return only documents that are visible to given user.

    This should be the same logic as in Document.can_see

    >> user = User.objects.get(slug='kk')
    >> filtered = (d for d in Document.objects.all() if d.can_see(user))
    >> set(filtered) == set(Document.objects.visible_to(user))
    True
    """

    user = Var('user')

    # def _events_user_is_invited_to(user):
    #     return EventInvitation.objects.filter(
    #         invited_user=user, cancelled=False).values_list('event', flat=True)


    invs = [inv.event for inv in event_inv_repo.filter(var('invited_user') == user & var('cancelled').false())]

    if user is None:
        return _is_public_q()

    visible_to = Var('document').visible_to
    user = Var('user')
    visible_to_me = (visible_to.exists() & visible_to.any(user.on_userslist_set)) | ~ visible_to.exists()

    if user.is_moderator.truth() | user.is_superuser.truth():
        visible_to_me |= (visible_to.exists() & visible_to.private.truth())

    # published documents are visible if they are not group documents
    visible_to_not_invited = ~ var('category.owner.group').exists()  # Q(category__owner__group__isnull=True)

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


def _is_public_q():
    """Return all public Documents"""
    # get all publicly visible sites documents
    # public_filter = Q(
    #     category__owner__group__group_visibility=Group
    #     .VISIBILITY_OPTIONS.ALL,
    #     site_status=Document.SITE_STATUS_CHOICES.ACCEPTED)
    # and all non-sites documents
    # public_filter |= Q(category__owner__group__isnull=True)
    # only take those categories - ignore archive, collections etc.
    # public_filter &= Q(
    #     category__model_type__in=(Category.TYPE_CHOICES.MAIN_BOARD,
    #                               Category.TYPE_CHOICES.TOPIC),
    #     visible_to=None,
    # ) & accepted_by_admin_q()

    # get all publicly visible sites documents
    public_filter = (
        Var('category.owner.group.group_visibility') == Group.VISIBILITY_OPTIONS.ALL
        & var('site_status') == Document.SITE_STATUS_CHOICES.ACCEPTED
    )
    # and all non-sites documents
    public_filter |= ~ var('category.owner.group').exists()

    # only take those categories - ignore archive, collections etc.
    public_filter &= (
        var('category.model_type').any([Category.TYPE_CHOICES.MAIN_BOARD, Category.TYPE_CHOICES.TOPIC])
        & ~ visible_to.exists()
    ) & accepted_by_admin_q()

    public_filter &= Q(visible_to_invited=False)

    return published_q() & public_filter



published = Predicate(d=Document) << (visible(d), d.publication_date() < datetime.now)
visible = Predicate(d=Document) << ( d.category(_.C), ~_.C.model_type(Category.TYPE_CHOICES.ARCHIVE))
documents_group = Predicate(d=Document, g=Group) << (EI.d.category(c=Category), EI.c.owner(o=Owner), EI.o.group(g))  # Owner?
group_visible_to_all = Predicate(g=Group) << g.group_visibility(Group.VISIBILITY_OPTIONS.ALL)


accepted_by_admin = predicate(o=None) << (
    O.admin_moderation_status(ADMIN_MODERATION_STATUS_CHOICES.NONE)
    | O.admin_moderation_status(ADMIN_MODERATION_STATUS_CHOICES.ACCEPTED)
)


class ADMIN_MODERATION_STATUS_CHOICES:
    pass  # Dummy, powinno być enumem z NONE, ACCEPTED, i czymś jeszcze


def groups_visible_to_user(user: User) -> List[Group]:
    return Group.objects.filter(_groups_visible_to_user(user))


def _groups_visible_to_user(user: User, user_roles: Iterable[UserRole]) -> Predicate:
    """Return only groups visible to `user`"""
    # group is either public, or visible only to some roles
    # visible = Q(group_visibility=Group.VISIBILITY_OPTIONS.ALL)
    # if user:
    #     group_pks = UserRole.objects.filter(
    #         user=user,
    #         role__in=(
    #             UserRole.ROLE_CHOICES.ADMINISTRATOR,
    #             UserRole.ROLE_CHOICES.AUTHOR,
    #             UserRole.ROLE_CHOICES.MODERATOR)) \
    #         .values_list('group_id', flat=True)
    #     visible |= Q(pk__in=group_pks)
    #
    # return visible
    visible = var('group_visibility') == Group.VISIBILITY_OPTIONS.ALL
    if user:
        visible |= var('id').in_(var('user') == user & var('role').in_([
            UserRole.ROLE_CHOICES.ADMINISTRATOR,
            UserRole.ROLE_CHOICES.AUTHOR,
            UserRole.ROLE_CHOICES.MODERATOR
        ])(user_roles))
    return visible


def groups_user_can_moderate(user: User) -> List[Group]:
    # return Group.objects.filter(_groups_user_can_moderate_q(user))
    return Group.repo.filter(_groups_user_can_moderate(user))


def _groups_user_can_moderate(user: User) -> Predicate:
    # return Q(userrole__user=User.coerce(user),
    #          userrole__role=UserRole.ROLE_CHOICES.MODERATOR)
    return var('userrole.user') == user & var('userrole.role') == UserRole.ROLE_CHOICES.MODERATOR
