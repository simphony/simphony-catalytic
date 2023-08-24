import json
import os

os.environ["REAXPRO_MINIO_USER"] = "rootname"
os.environ["REAXPRO_MINIO_PASSWORD"] = "rootname123"
os.environ["REAXPRO_MINIO_ENDPOINT"] = "172.17.0.3:9000"


from osp.core.namespaces import cuba
from osp.core.utils import pretty_print
from osp.models.catalytic.co_catalyticfoam import COCatalyticFOAMModel
from osp.wrappers.simcatalyticfoam.simcatalyticfoam import SimCatalyticFoamSession

path = os.path.join(os.path.dirname(__file__), "example_co_model.json")
with open(path, mode="r+") as file:
    content = json.loads(file.read())


model = COCatalyticFOAMModel(**content)

pretty_print(model.cuds)


session = SimCatalyticFoamSession()
wrapper = cuba.Wrapper(session=session)
wrapper.add(model.cuds, rel=cuba.relationship)
session.run()

print(session._engine._config)
