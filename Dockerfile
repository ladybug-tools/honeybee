FROM antoinedao/ladybug
MAINTAINER Antoine Dao "antoine.dao@burohappold.com"

# copy radiance
COPY ./radiance/bin /usr/local/bin
COPY ./radiance/lib /usr/local/lib/ray

# Change workdir
WORKDIR /usr/local/lib/python2.7/site-packages

# copy honeybee
COPY ./honeybee ./honeybee
