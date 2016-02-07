from . import enum, GenericAnnotation

persistence = GenericAnnotation


@persistence.MappedSuperclass
class BaseEntity(object):

    # ALWAYS ADD NEW STATUS AT THE END - because the entityStatus field is
    # annotated as ordinal in sake of performance
    EntityStatus = enum('ACTIVE', 'ARCHIVE')

    # entityId because ID can mean something (some domain concept) in some
    # Bounded Context
    # @persistence.Id
    # @persistence.GeneratedValue
    entity_id = None

    # @persistence.Version
    # private Long version

    # @persistence.Enumerated(persistence.EnumType.ORDINAL)
    entity_status = EntityStatus.ACTIVE

    def markAsRemoved(self):
        self.entity_status = self.EntityStatus.ARCHIVE

    def getEntityId(self):
        return self.entity_id

    def getEntityStatus(self):
        return self.entity_status


@persistence.MappedSuperclass
class BaseAggregateRoot(BaseEntity):
    """
    * Sample of Domain Event usage
    * Event Publisher is injected by Factory/Repo
    """

    # @persistence.Transient
    domain_event_publisher = None

    def set_event_publisher(self, domain_event_publisher):
        """
        Sample technique of injecting Event Publisher into the Aggregate.
        Can be called only once by Factory/Repository
        Visible for package (Factory/Repository)
        """
        assert not self.domain_event_publisher, \
            "Publisher is already set! Probably You have logical error in code"
        self.domain_event_publisher = domain_event_publisher
