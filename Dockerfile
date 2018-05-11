FROM ladybugtools/ladybug
MAINTAINER Ladybug Tools "info@ladybug.tools"

WORKDIR /usr/local/lib/python2.7/site-packages

# copy radiance
COPY ./radiance/bin /usr/local/bin
COPY ./radiance/lib /usr/local/lib/ray

# copy honeybee
COPY ./honeybee ./honeybee
