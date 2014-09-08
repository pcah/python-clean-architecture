from dharma import Entity
from dharma.traits import Str, Int, Float

trait_type_list = [Str, Int, Float,]


@pytest.fixture(scope='session', params=trait_type_list)
def trait_entities(request):
   return build_entity_with_trait(request.param)
