import json
import os

from osp.core.namespaces import crystallography, cuba, emmo
from osp.models.multiscale.co_pt111_full import COPt111FullscaleModel
from osp.wrappers.simams.simams_session import SimamsSession
from osp.wrappers.simcatalyticfoam.simcatalyticfoam import SimCatalyticFoamSession
from osp.wrappers.simzacros.simzacros_session import SimzacrosSession

path = os.path.join(os.path.dirname(__file__), "co_pt111_full.json")
with open(path, mode="r+") as file:
    content = json.loads(file.read())


PATH = os.path.dirname(__file__)
molecule = os.path.join(PATH, "CO_ads+Pt111.xyz")
lattice = os.path.join(PATH, "CO_ads+Pt111.xyz")

content["pes_exploration"]["molecule"] = molecule
content["pes_exploration"]["lattice"] = lattice

model = COPt111FullscaleModel(**content)

# PES Exploration + Binding Site calculation

with SimamsSession() as sess:
    reaxpro_wrapper1 = cuba.Wrapper(session=sess)
    reaxpro_wrapper1.add(model.cuds, rel=cuba.relationship)
    reaxpro_wrapper1.session.run()


# map output from previous calculation to next calculation

workflow = reaxpro_wrapper1.get(rel=cuba.relationship).pop()

process_search = workflow.get(oclass=emmo.ProcessSearch).pop()

binding_sites = workflow.get(oclass=emmo.BindingSites).pop()

mesocopic = workflow.get(oclass=emmo.MesoscopicCalculation).pop()

search_mechanism = process_search.get(
    oclass=emmo.ChemicalReactionMechanism, rel=emmo.hasOutput
)

search_clusters = process_search.get(oclass=emmo.ClusterExpansion, rel=emmo.hasOutput)

search_lattice = binding_sites.get(oclass=crystallography.UnitCell, rel=emmo.hasOutput)

mesocopic.add(*search_mechanism, *search_lattice, *search_clusters, rel=emmo.hasInput)

# Mesoscopic calculation

with SimzacrosSession() as sess:
    reaxpro_wrapper2 = cuba.Wrapper(session=sess)
    reaxpro_wrapper2.add(workflow, rel=cuba.relationship)
    reaxpro_wrapper2.session.run()

workflow = reaxpro_wrapper2.get(rel=cuba.relationship).pop()
apd = workflow.get(oclass=emmo.AdaptiveDesignProcedure).pop()
output = apd.get(rel=emmo.hasOutput)
continuum = workflow.get(oclass=emmo.ContinuumCalculation).pop()
continuum.add(**output, rel=emmo.hasInput)

with SimCatalyticFoamSession() as session:
    reaxpro_wrapper3 = cuba.Wrapper(session=sess)
    reaxpro_wrapper3.add(workflow, rel=cuba.relationship)
    reaxpro_wrapper3.session.run()
