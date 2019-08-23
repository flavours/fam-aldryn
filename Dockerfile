FROM flavour/fam-flavour:0.1

# Version of the addon manager
ARG VERSION=0.1

ENV FAM_IDENTIFIER flavour/fam-diviocloud-addon:$VERSION

RUN mkdir -p /app

RUN mkdir -p /flavour/fam-diviocloud-addon/
COPY requirements.txt /flavour/fam-diviocloud-addon/requirements.txt
RUN pip install -r /flavour/fam-diviocloud-addon/requirements.txt

WORKDIR /app 

# move fam-flavour binaries to a save place
RUN mkdir /bin/fam-flavour
RUN mv /bin/add /bin/fam-flavour/add
RUN mv /bin/remove /bin/fam-flavour/remove
RUN mv /bin/check /bin/fam-flavour/check


# This needs a better way...
RUN mkdir /usr/lib/fam_diviocloud_addon
COPY lib/*.py /usr/lib/fam_diviocloud_addon/

# copy policies
RUN mkdir -p /flavour/fam-divicloud-addon/policy
COPY policy/*.rego /flavour/fam-diviocloud-addon/policy/



# copy the new stuff
COPY bin/add.py /bin/add
COPY bin/remove.py /bin/remove
COPY bin/check.py /bin/check
