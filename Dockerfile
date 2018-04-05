FROM antoinedao/ladybug
MAINTAINER Antoine Dao "antoine.dao@burohappold.com"

# copy radiance
COPY ./radiance/bin /usr/local/bin
COPY ./radiance/lib /usr/local/lib/ray

# Install Radiance from source
# Avoids issue you had here with missing lib file(?)
RUN cd /tmp \
    && wget https://github.com/NREL/Radiance/releases/download/5.1.0/radiance-5.1.0-Linux.tar.gz \
    && tar -xzvf radiance-5.1.0-Linux.tar.gz \
    && cp -a radiance-5.1.0-Linux/usr/local/radiance/bin/. /usr/local/bin \
    && cp -a radiance-5.1.0-Linux/usr/local/radiance/lib/. /usr/local/lib/ray

# Change workdir
WORKDIR /usr/local/lib/python2.7/site-packages

# copy honeybee
COPY ./honeybee /usr/local/lib/python2.7/site-packages/honeybee
