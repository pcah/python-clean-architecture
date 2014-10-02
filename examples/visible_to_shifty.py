from datetime import datetime
from predicates import predicate

from .models import User, Category, Document, Group

class EI(object):
    "Exists instance"


visible_to = predicate(u=User, d=Document) << (
    # get all publicly visible sites documents
    (documents_group(d, _.G), group_visible_to_all(_.G), d.site_status(Document.SITE_STATUS_CHOICES.ACCEPTED)) | (documents_group(d, None)),
    # only take those categories - ignore archive, collections etc.
    _.C.model_type(in=[Category.TYPE_CHOICES.MAIN_BOARD, Category.TYPE_CHOICES.TOPIC]),
    d.category(_.C),
    d.visible_to(None),
    accepted_by_admin(d),
    ~d.visible_to_invited(),
    published(d)
)

# TODO: visible_to dla konkretnych użytkowników

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
