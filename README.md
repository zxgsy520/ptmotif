ptmotif
==============
### Version: 1.0.0
ptmotif is used for genome pt modification and methylation modification analysis

Building Requirements
-----------
* Python 2.7 or 3.5+ (with setuptools package installed)

## Instructions
### bax2bam
<pre><code>
bax2bam bax.h5 -o out --subread --pulsefeatures=DeletionQV,DeletionTag,InsertionQV,IPD,MergeQV,SubstitutionQV,PulseWidth,SubstitutionTag
</code></pre>

### motif
<pre><code>
pbalign subread.bam sample.fasta align.bam --tmpDir tmp --nproc 4 --concordant
samtools faidx sample.fasta
ipdSummary align.bam --reference sample.fasta \
    -v -W contig_ids.txt --methylFraction --gff modifications.gff --csv modifications.csv \
    --identify m6A,m4C  --numWorkers 8
</code></pre>

### motifs2pt
Get a specific modification
example
<pre><code>
motifs2pt ./bin/Drad.motifs.gff.gz --ptbase CCGCGG  --ptsite 2 >Drad.CCGCGG_motifs.gff    #linux system
python ./bin/motifs2pt.pyc Drad.motifs.gff.gz --ptbase CCGCGG --ptsite 2 >Drad.CCGCGG_motifs.gff #Other systems
</code></pre>
<pre><code>
./motifs2pt -h
usage: motifs2pt [-h] -ptb SRT [-pts INT] [--coverage INT] [-ipd FLOAT] gff

name:
     motifs2pt.py Extraction of PT modifications from base modification results

attention:
     motifs2pt.py motif.gff --ptbase GATC --ptsite 1 --coverage 5 --ipdratio 0.5 >pt.gff

version: v1.2.0
contact:  Xingguo Zhang <113178210@qq.com>    

positional arguments:
  gff                   Input the methylation modification result file (gff).

optional arguments:
  -h, --help            show this help message and exit
  -ptb SRT, --ptbase SRT
                        Input PT modified base type.
  -pts INT, --ptsite INT
                        Input the position of the PT modification on the modified
                        base (starting from 1); default=2.
  --coverage INT        Modified base coverage; default=10.
  -ipd FLOAT, --ipdratio FLOAT
                        Modified base IPDRatio; default=1.
</code></pre>
