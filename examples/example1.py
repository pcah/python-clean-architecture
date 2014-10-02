class User(Entity):
    user_type = Choice()


class Document(Entity):
    status = Choice()
    author = Instance(User)

    is_visible_to = Predicate(E.author.X('user') | E.status.(status.PUBLISHED))