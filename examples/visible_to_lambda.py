from datetime import datetime

from predicates import predicate

from .models import User, Category, Document, Group


visible_to = predicate(U=User, D=Document)

# _is_public_q
visible_to << (lambda _, U, D: (
    # get all publicly visible sites documents
    (documents_group(D, _.G),
     group_visible_to_all(_.G),
     D.site_status(Document.SITE_STATUS_CHOICES.ACCEPTED))
    | (documents_group(D, None)),  # ..and non-site documents

    # only take those categories - ignore archive, collections etc.
    # TODO: __in
    (_.C.model_type(Category.TYPE_CHOICES.MAIN_BOARD)
     | _.C.model_type(Category.TYPE_CHOICES.TOPIC)),
    D.category(_.C),

    D.visible_to(None),
    accepted_by_admin(D),

    ~D.visible_to_invited(),
    published(D)))


# TODO: visible_to dla konkretnych użytkowników


published = predicate(D=Document)
published << (lambda D: (
    visible(D),
    D.publication_date() < datetime.now))


visible = predicate(D=Document)
visible << (lambda _, D: (
    D.category(_.C),
    ~_.C.model_type(Category.TYPE_CHOICES.ARCHIVE)))


documents_group = predicate(D=Document, G=Group)
documents_group << (lambda _, D, G: (
    D.category(_.C), _.C.owner(_.O), _.O.group(G)))


group_visible_to_all = predicate(G=Group)
group_visible_to_all << (lambda _, G: (
    G.group_visibility(Group.VISIBILITY_OPTIONS.ALL)))


accepted_by_admin = predicate(O=None)
accepted_by_admin << (lambda O: (
    O.admin_moderation_status(ADMIN_MODERATION_STATUS_CHOICES.NONE)
    | O.admin_moderation_status(ADMIN_MODERATION_STATUS_CHOICES.ACCEPTED)))


class ADMIN_MODERATION_STATUS_CHOICES:
    pass  # Dummy, powinno być enumem z NONE, ACCEPTED, i czymś jeszcze
