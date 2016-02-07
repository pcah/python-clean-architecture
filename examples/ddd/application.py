Annotations = None
Spring = None


@Spring.Service
@Spring.Transactional
@Annotations.type
class ApplicationService(object):
    def value(self):
        return ""


@Annotations.generic
class ApplicationEvent(object):
    pass


@Spring.Component
@Spring.Scope(value='session')
@Spring.Transactional
@Annotations.type
class ApplicationStatefullComponent(object):
    pass


class ApplicationEventPublisher(object):
    def publish(application_event):
        pass


@Spring.Component
class SystemUser(object):

    # @Spring.PersistenceContext
    entity_manager = None

    def get_user_id(self):
        clients = self.entity_manager.createQuery("from Client").\
            getResultList()
        return clients.get(0).getEntityId()
