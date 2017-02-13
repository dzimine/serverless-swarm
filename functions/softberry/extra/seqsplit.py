#!/usr/bin/python
"""
Script to split Fasta formated file with sequences to N parts
by Victor Solovyev 01/22/2017
"""
import sys, collections
def read_fasta(fp):
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith(">"):
            if name: yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line.upper())
    if name: yield (name, ''.join(seq))
try:
 genome_file = sys.argv[1]
 output_file = sys.argv[2]
 nspl= int(sys.argv[3])
except:
  print "USAGE: <genome fasta> <output file> <split num>"
  sys.exit()

F = open(genome_file,'r')
num=0;
for n,seq in read_fasta(F):
  num=num+1
F.close()
npa=int((1.*num)/nspl)
ii=0; ic=1;
F = open(genome_file,'r')
for n,seq in read_fasta(F):
  name_seq = n[1:]
  name_seq = n
  lg = len(seq)
  if(ii==0): 
   Fou = open(output_file+"."+str(ic),'w+')
   ic=ic+1
  Fou.write("%s\n" %(name_seq))
  nn=lg/60
  i1=0; 
  for i in range(nn):
    Fou.write("%s\n" %(seq[i1:i1+60]))
    i1=i1+60
  if(60*nn<lg):Fou.write("%s\n" %(seq[60*nn:lg]))
  ii=ii+1
  if(ii==npa and (num-(ic-1)*npa >= nspl)):
   ii=0; Fou.close() 
if(nspl*npa<num):Fou.close()
F.close()