FROM sb/sb_base

WORKDIR /sb

ENTRYPOINT ["FgenesB/run_annot.pl", "path.list"]
