ptmotif
==============
### Version: 1.0.0
ptmotif is used for genome pt modification and methylation modification analysis

Building Requirements
-----------
* 3.5+ (with setuptools package installed)
* [bax2bam](https://github.com/PacificBiosciences/bax2bam)  #网页打不开可以用[conda](https://anaconda.org/bioconda/bax2bam)安装
* [pbalign](https://github.com/PacificBiosciences/pbalign)  #网页打不开可以用[conda](https://anaconda.org/bioconda/pbalign)安装
* [pbcore](https://github.com/PacificBiosciences/pbbioconda) #[pbcore](https://github.com/PacificBiosciences/pbcore/releases/download/2.1.2/pbcore-2.1.2.tar.gz)使用pip或者conda安装只有python2的版本，需要下载原包安装
* [kineticsTools](https://github.com/PacificBiosciences/kineticsTools)  #修复bug的[kineticsTools](https://github.com/zxgsy520/kineticsTools)  #只支持python3

## Installation
```
conda create --prefix=/Work/software/pbtools/v1.0.0 -c bioconda bax2bam=0.0.9 pbalign=0.3.2    #注意检测里面的samtools有没有问题
cd /Work/software/
mkdir kineticsTools
cd kineticsTools
conda create --prefix=/Work/software/kineticsTools/v1.0.0 -c bioconda pbcore python
wget -c https://github.com/zxgsy520/kineticsTools/archive/refs/tags/v1.0.0.tar.gz
tar -zxvf kineticsTools-1.0.0
/Work/software/kineticsTools/v1.0.0/bin/python setup.py install
```

## Instructions
### bax2bam
<pre><code>
bax2bam bax.h5 -o out --subread --pulsefeatures=DeletionQV,DeletionTag,InsertionQV,IPD,MergeQV,SubstitutionQV,PulseWidth,SubstitutionTag
split_bam.py subreads.bam -p name -n 9100
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

Publications
------------
Jian H, Xu G, Yi Y, Hao Y, Wang Y, Xiong L, Wang S, Liu S, Meng C, Wang J, Zhang Y, Chen C, Feng X, Luo H, Zhang H, Zhang X, Wang L, Wang Z, Deng Z, Xiao X. The origin and impeded dissemination of the DNA phosphorothioation system in prokaryotes. Nat Commun. 2021 Nov 4;12(1):6382. doi: [10.1038/s41467-021-26636-7](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8569181/). PMID: 34737280; PMCID: PMC8569181.
