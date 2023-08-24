# start from openfoam:8
FROM openfoam/openfoam8-paraview56:8 as base

# define shell
SHELL ["/bin/bash", "-c", "-l"]

# switch to root in order to install dependencies
USER root

ENV DEBIAN_FRONTEND noninteractive

# install linux-dependencies
RUN apt-get update && apt-get install -y \
    tk git python3.8 python3-pip python3-tk make cmake \
    g++ apt-transport-https ca-certificates gnupg \
    software-properties-common build-essential \
    libboost-all-dev librapidxml-dev libeigen3-dev \
    gfortran nodejs

# retrieve build args
ARG GITHUB_ACCESS_TOKEN
ARG GITLAB_ACCESS_TOKEN
ARG EIGEN_REPO
ARG CATALYTIC_FOAM_REPO


# make code base in homedir read-/write-/executable to USER
RUN chmod -R 0777 /home/openfoam
# update .profile and add .local/bin to PATH
RUN echo "export PATH=$PATH:/home/openfoam/.local/bin" >> /home/openfoam/.profile

# download catalyticFoam solver
WORKDIR /home/openfoam
RUN git clone $CATALYTIC_FOAM_REPO catalyticFoam

# make dynamic link to eigen-library
RUN ln -sf /usr/include/eigen3/Eigen /usr/include/Eigen
RUN ln -sf /usr/include/eigen3/unsupported /usr/include/unsupported

# add env files
WORKDIR /home/openfoam

# compile catalytic foam solver
WORKDIR /home/openfoam/catalyticFoam
COPY .compile mybashrc
RUN source /opt/openfoam8/etc/bashrc && source mybashrc && ./Allwmake

# add code base
WORKDIR /home/openfoam/reaxpro_wrappers
COPY osp osp
COPY tests tests
COPY examples examples
COPY setup.py setup.cfg README.md ./
RUN chmod -R 0777 .

# # make dynamic links to python3
RUN \
   echo 'alias python="/usr/bin/python3"' >> /root/.bashrc && \
   echo 'alias pip="/usr/bin/pip3"' >> /root/.bashrc && \
   echo 'alias python="/usr/bin/python3"' >> /home/openfoam/.bashrc && \
   echo 'alias pip="/usr/bin/pip3"' >> /home/openfoam/.bashrc


################################## target: dev ##################################
from base as develop

WORKDIR /home/openfoam/reaxpro_wrappers

# # install deps for pytests
RUN pip install --upgrade pip
RUN pip install osp-core
RUN pip install .[dev,pre_commit,tests]

# go /app dir
WORKDIR /app
RUN echo "export PATH=$PATH:/home/openfoam/.local/bin" >> /root/.bashrc

RUN chmod -R 0777 /tmp
RUN chown openfoam:openfoam /tmp

################################## target: production ##################################

from base as production

WORKDIR /home/openfoam/reaxpro_wrappers
USER openfoam

# # install wrappers and their python-dependencies
RUN pip install --upgrade pip
RUN pip install osp-core
RUN pip install .
