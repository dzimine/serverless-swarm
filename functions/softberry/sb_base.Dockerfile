FROM sb/blast_base

RUN yum install -y perl

COPY FgenesB /sb/FgenesB
COPY tRNAscan-SE /sb/tRNAscan-SE
COPY blast_scripts /sb/blast_scripts

COPY path.list /sb
COPY test.seq  /sb
COPY extra /sb/extra

WORKDIR /sb

CMD ["/bin/bash"]
