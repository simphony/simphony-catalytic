# SimPhoNy-Catalytic

SimPhoNy-Catalytic is a Python package developed by Fraunhofer IWM that provides a convenient interface for running [catalyticFOAM simulations](https://github.com/multiscale-catalysis-polimi/catalyticFoam) using OpenFOAM.

The wrappers of this repository are the driver for running the catalyticFOAM solver, which was developed by Polimi and which is *NOT* included into the code here.

The SimPhoNy-Cataltic interface hosts the code and resources required to set up and run simulations of catalytic reactions in fluid flow systems.

The package is a plugin for [osp-core](https://github.com/simphony/simphony-osp) and hence is a semantic framework based on the [EMMO-ontology](https://github.com/emmo-repo).

## Authors

[Matthias Büschelberger](mailto:matthias.bueschelberger@iwm.fraunhofer.de) (Fraunhofer Institute for Mechanics of Materials IWM)

## Features

* Simulate laminar or turbulent flow with catalytic reactions.
* Define chemical species and their composition within the mixture.
* Specify boundary conditions for velocity, pressure, and temperature.
* Choose from a range of diffusivity and turbulence models.
* Set up and control simulation parameters such as maximum simulation time, time step length, and more.

## Installation

### Simulation engine

Make sure you have OpenFOAM installed on your system. Refer to the OpenFOAM documentation for installation instructions.

More important, make sure that you have the catalyticFOAM-solver installed on your machine. For the installation procedure, please refer to the [README from polimi](https://github.com/multiscale-catalysis-polimi/catalyticFoam/blob/master/README.md).

### Python dependencies

First of all, you will need to install OSP-core, plams, AdaptiveDesignProcedure and pyZacros (all except osp-core are not on PyPI yet unfortunately):

```shell
(env) user@computer:~/reaxpro-wrappers$ pip install osp-core https://github.com/SCM-NV/pyZacros/archive/refs/tags/v.1.2.zip https://github.com/mbracconi/adaptiveDesignProcedure/archive/refs/tags/v1.4.0.zip git+https://github.com/SCM-NV/PLAMS@7661960a9db53249a0b77935dacc8a7668c2489b
```

Then, install the wrapper. Simply type:

```shell
(env) user@computer:~/reaxpro-wrappers$ pip install simphony-catalytic
```

... or if you are installing from source (cloning of the repository needed before):


```shell
(env) user@computer:~/reaxpro-wrappers$ pip install .
```

## Usage

For detailed examples and usage instructions, refer to the [documentation](https://reaxpro.pages.fraunhofer.de/docs/usecases.html#co-catalyticfoam-use-case-laminar-2d-flow-through-a-pipe-with-catalytic-wall) and example files in the examples directory of this repository.

## License

This project is licensed under the GPL-3 License. See the LICENSE file for more information.

## Disclaimer

Copyright (c) 2014-2023, Fraunhofer-Gesellschaft zur Förderung der angewandten Forschung e.V. acting on behalf of its Fraunhofer IWM.

This offering is not approved or endorsed by OpenCFD Limited, producer and distributor of the OpenFOAM software via www.openfoam.com, and owner of the OPENFOAM® and OpenCFD® trade marks.

The catalyticFoam solver itself has been developed in the Multiscale Catalysis Group of the [Laboratory of Catalysis and Catalytic Processes of Politecnico di Milano](https://www.lccp.polimi.it/) and hence is not authored by Fraunhofer IWM.

Contact: [SimPhoNy](mailto:simphony@iwm.fraunhofer.de)
