# use base-image for debian (since we are going to load python from berryconda)
# see more about dockerfile templates here:http://docs.resin.io/pages/deployment/docker-templates
FROM resin/raspberrypi3-debian:jessie

# Set our working directory
WORKDIR /usr/src/app

#Set up basic packages. Note build essentials needed for installing gcc
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y tcl8.6 \
                        bzip2 \
                        vim \
                        sudo \
                        build-essential && \
    rm -rf /var/lib/apt/lists/* 

# Copy base requirements first for better caching
# Add should automatically extract the tar file
COPY pkgs/Berryconda3-2.0.0-Linux-armv7l.sh Berryconda3-2.0.0-Linux-armv7l.sh
COPY pkgs/RPi.GPIO-0.6.3.tar.gz . 

#Install berry conda 3 and install necessary packages. 
#Need to run in bash for conda
SHELL ["/bin/bash","-c"]
RUN [ "cross-build-start" ]
RUN chmod +x Berryconda3-2.0.0-Linux-armv7l.sh && \
    ./Berryconda3-2.0.0-Linux-armv7l.sh -ub
ENV PATH="/root/berryconda3/bin:${PATH}"
RUN pip install --upgrade pip && \
    tar -xvf RPi.GPIO-0.6.3.tar.gz && \
    cd RPi.GPIO-0.6.3 && python setup.py install && \
    cd ../ && rm -rf RPi.GPIO-0.* && \
    conda install pyserial -y && \
    pip install zaber.serial --no-cache-dir && \ 
    pip install minimalmodbus --no-cache-dir && \
    pip install AWSIoTPythonSDK --no-cache-dir && \
    pip install filelock --no-cache-dir && \
    conda install -c poehlmann python-seabreeze -y && \
    conda install -c conda-forge arrow -y && \
    conda install -c rpi numpy pandas -y

COPY chemiosbrain/ chemiosbrain/
COPY prototype/ prototype/
COPY tests/ tests/
COPY setup.py setup.py
COPY run.sh run.sh
RUN pip install -e . -q && \
    chmod +x run.sh

RUN [ "cross-build-end" ]
ENV INITSYSTEM on
#Prototype one  will run when container starts up on the device
CMD [ "sh", "-c", "./run.sh" ]
