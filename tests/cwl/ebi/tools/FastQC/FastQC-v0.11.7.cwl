class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
  
baseCommand:  [fastqc, --outdir, .]
  
inputs:
  - id: n_threads
    type: int?
    inputBinding:
      position: 2
      prefix: '--threads'
    label: 'Number of threads'
    doc: >
      Specifies the number of files which can be processed
      simultaneously. Each thread will be allocated 250MB of
      memory so you shouldn't run more threads than your
      available memory will cope with, and not more than
      6 threads on a 32 bit machine.
  - id: in_fastq
    format: 'edam:format_1930'
    type: File[]
    inputBinding:
      position: 3
    label: 'Input FASTQ file(s)'
    doc: >
      Input FASTQ file(s). If multiple files are provided then use space separated

outputs:
  - id: zipped_report
    label: 'Zipped output report'
    type: File[]
    outputBinding:
      glob: '*_fastqc.zip'
  - id: html_report
    label: 'HTML output report'
    type: File[]
    outputBinding:
      glob: '*_fastqc.html'

doc: >
  FastQC reads a set of sequence files and produces from each one a quality
  control report consisting of a number of different modules, each one of
  which will help to identify a different potential type of problem in your
  data.

  If no files to process are specified on the command line then the program
  will start as an interactive graphical application.  If files are provided
  on the command line then the program will run with no user interaction
  required.  In this mode it is suitable for inclusion into a standardised
  analysis pipeline.
    
  Please visit https://www.bioinformatics.babraham.ac.uk/projects/fastqc/ for full documentation.
    
label: FastQC - A high throughtput sequence analyses QC.

hints:
  - class: DockerRequirement
# TODOs: From looking into the result files
# received from the container tag as latest (22/08/2018) we deal with version 0.11.5 here
    dockerPull: 'quay.io/biocontainers/fastqc:0.11.7--4'
$schemas:
  - 'http://edamontology.org/EDAM_1.20.owl'
  - 'https://schema.org/docs/schema_org_rdfa.html'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Arnaud Meng, Maxim Scheremetjew"