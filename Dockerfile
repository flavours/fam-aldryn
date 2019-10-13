FROM flavour/fam-flavour:0.1

# Version of the addon manager
ARG VERSION=0.1.1

ENV FAM_IDENTIFIER flavour/fam-aldryn:$VERSION

RUN mkdir -p /app

RUN mkdir -p /flavour/fam-aldryn/
COPY requirements.txt /flavour/fam-aldryn/requirements.txt
RUN pip install -r /flavour/fam-aldryn/requirements.txt

WORKDIR /app 

# This needs a better way...
RUN mkdir /usr/lib/fam_aldryn
COPY lib/*.py /usr/lib/fam_aldryn/

# copy policies
RUN mkdir -p /flavour/fam-aldryn/policy
COPY policy/*.rego /flavour/fam-aldryn/policy/



# copy the new stuff
COPY bin/add.py /bin/fam-aldryn/add
COPY bin/remove.py /bin/fam-aldryn/remove
COPY bin/check.py /bin/fam-aldryn/check

RUN rm /bin/add && ln -s /bin/fam-aldryn/add /bin/add
RUN rm /bin/check && ln -s /bin/fam-aldryn/check /bin/check
RUN rm /bin/remove && ln -s /bin/fam-aldryn/remove /bin/remove
