FROM centos:5.11
RUN yum install -y perl
ADD FgenesB /sb/FgenesB
ADD blast-2.2.26 /sb/blast-2.2.26
ADD tRNAscan-SE /sb/tRNAscan-SE
ADD path.list /sb
ADD test.seq  /sb

WORKDIR /sb

ENTRYPOINT ["FgenesB/run_annot.pl", "path.list"]