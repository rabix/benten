class: Workflow
cwlVersion: v1.0
id: admin/sbg-public-data/salmon-workflow-0-9-1-cwl-1-0/18
label: Salmon Workflow CWL 1.0
$namespaces:
  sbg: 'https://sevenbridges.com'
inputs:
  - id: transcriptome_fasta_or_salmon_index_archive
    'sbg:fileTypes': 'FASTA, FA, TAR, FASTA.GZ, FA.GZ'
    type: File
    label: Transcriptome FASTA or Salmon index archive
    doc: 'Transcriptome FASTA file, or an already generated Salmon index archive.'
    description: 'Transcriptome FASTA file, or an already generated Salmon index archive.'
    format: 'FASTA,FA,TAR,FASTA.GZ,FA.GZ'
    'sbg:includeInPorts': true
    'sbg:suggestedValue':
      class: File
      name: gencode.v27.transcripts.salmon-0.9.1-index-archive.tar
      path: 5a6ba7c84f0c278a3ba2d1e2
    'sbg:x': -353
    'sbg:y': 160.9386444091797
  - id: reads
    'sbg:fileTypes': 'FASTQ, FQ, FASTQ.GZ, FQ.GZ'
    type: 'File[]'
    label: FASTQ Read Files
    doc: Input FASTQ read files.
    description: Input FASTQ read files.
    format: 'FASTQ, FQ, FASTQ.GZ, FQ.GZ'
    'sbg:includeInPorts': true
    'sbg:x': -347.4034423828125
    'sbg:y': 371.9826965332031
  - id: gtf
    'sbg:fileTypes': 'GTF, GFF, GFF3'
    type: File?
    label: Gene map or GTF file
    doc: >-
      File containing a mapping of transcripts to genes.  If this file is
      provided Salmon will output both quant.sf and quant.genes.sf files, where
      the latter contains aggregated gene-level abundance estimates.  The
      transcript to gene mapping should be provided as either a GTF file, or a
      in a simple tab-delimited format where each line contains the name of a
      transcript and the gene to which it belongs separated by a tab.  The
      extension of the file is used to determine how the file should be parsed. 
      Files ending in '.gtf’, ‘.gff’ or '.gff3’ are assumed to be in GTF format;
      files with any other extension are assumed to be in the simple format. In
      GTF/GFF format, the ‘transcript_id’ is assumed to contain the transcript
      identifier and the ‘gene_id’ is assumed to contain the corresponding gene
      identifier.
    description: >-
      File containing a mapping of transcripts to genes.  If this file is
      provided Salmon will output both quant.sf and quant.genes.sf files, where
      the latter contains aggregated gene-level abundance estimates.  The
      transcript to gene mapping should be provided as either a GTF file, or a
      in a simple tab-delimited format where each line contains the name of a
      transcript and the gene to which it belongs separated by a tab.  The
      extension of the file is used to determine how the file should be parsed. 
      Files ending in '.gtf’, ‘.gff’ or '.gff3’ are assumed to be in GTF format;
      files with any other extension are assumed to be in the simple format. In
      GTF/GFF format, the ‘transcript_id’ is assumed to contain the transcript
      identifier and the ‘gene_id’ is assumed to contain the corresponding gene
      identifier.
    format: 'GTF,GFF,GFF3'
    'sbg:includeInPorts': true
    'sbg:suggestedValue':
      class: File
      name: gencode.v27.annotation.gtf
      path: 5a6ba7f14f0c278a3ba2d1e3
    'sbg:x': -349
    'sbg:y': 506.34210205078125
  - id: max_number_of_parallel_jobs
    type: int?
    label: Maximum number of parallel jobs
    description: >-
      Maximum number of parallel jobs to allow in the tool downstream of this
      one.
    'sbg:category': Options
    'sbg:stageInput': null
    'sbg:suggestedValue': 4
    'sbg:toolDefaultValue': '4'
  - id: kmer_length
    type: int?
    label: K-mer length
    description: >-
      The size of k-mers that should be used for the quasi index. K-mer length
      should be an odd number.
    'sbg:category': Options
    'sbg:toolDefaultValue': '31'
  - id: gencode
    type: boolean?
    label: GENCODE FASTA
    description: >-
      This flag will expect the input transcript FASTA to be in GENCODE format
      and will split the transcript name at the first '|' character. These
      reduced names will be used in the output and when looking for these
      transcripts in a gene to transcript GTF.
    'sbg:category': Options
    'sbg:toolDefaultValue': 'off'
  - id: keep_duplicates
    type: boolean?
    label: Keep duplicates
    description: >-
      This flag will disable the default indexing behavior of discarding
      sequence-identical duplicate transcripts. If this flag is passed, then
      duplicate transcripts that appear in the input will be retained and
      quantified separately.
    'sbg:category': Options
    'sbg:suggestedValue': true
    'sbg:toolDefaultValue': 'Off'
  - id: write_unmapped_names
    type: boolean?
    label: Write unmapped names
    description: >-
      Write the names of unmapped reads to the file unmapped.txt in the
      auxiliary directory.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'off'
  - id: write_mappings
    type: boolean?
    label: Write mappings
    description: >-
      If this options is provided, then the quasi-mapping results/information
      will be written out in SAM-compatible format.
    'sbg:category': Basic options
    'sbg:toolDefaultValue': 'off'
  - id: vb_prior
    type: float?
    label: VBEM prior
    description: >-
      The prior that will be used VBEM algorithm. This is interpreted as a
      per-nucleotide prior, unlees the --perTranscriptPrior flag is also given,
      in which case this is used as a transcript-level prior.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '0.001'
  - id: use_vbopt
    type: boolean?
    label: Use Variational Bayesian optimization
    description: >-
      Use the Variational Bayesian EM rather than the traditional EM algorithm
      for optimization in the batch passes.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'off'
  - id: thinning_factor
    type: int?
    label: Thinning factor
    description: >-
      Number of steps to discard for every sample kept from the Gibbs chain. The
      larger this number, the less chance that subsequent samples are
      auto-correlated, but the slower sampling becomes.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '16'
  - id: strict_intersect
    type: boolean?
    label: Strict intersect
    description: >-
      Modifies how orphans are assigned. When this flag is set, if the
      intersection of the quasi-mapping for the left and right is empty, then
      all mappings for the left and all mappings for the right read are reported
      as orphan quasi-mappings.
    'sbg:category': Advanced options
    'sbg:toolDefaultValue': 'off'
  - id: seq_bias
    type: boolean?
    label: Sequence-specific bias correction
    description: Perform sequence-specific bias correction.
    'sbg:category': Basic options
    'sbg:toolDefaultValue': 'off'
  - id: reduce_GC_memory
    type: boolean?
    label: Reduce GC memory
    description: >-
      If this option is selected, a more memory efficient (but slightly slower)
      representation is used to compute fragment GC content. Enabling this will
      reduce memory usage, but can also reduce speed. However, the results
      themselves will remain the same.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'Off'
  - id: range_factorization_bins
    type: int?
    label: Range factorization bins
    description: >-
      Factorizes the likelihood used in quantification by addopting a new notion
      of equivalence classes based on the coniditonal probabilities with which
      fragments are generated from different transcripts. This is a more
      fine-grained factorization than the normal rich equivalence classes. The
      default value (0) corresponds to the standard rich equivalence classes and
      larger values imply a more fine-grained factorization. If range
      factorization is enabled, a common value to select for this parameter is
      4.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:suggestedValue': 4
    'sbg:toolDefaultValue': '0'
  - id: quasi_coverage
    type: float?
    label: Quasi coverage
    description: >-
      The fraction of the read that must be covered by MMPs (of length >= 31) if
      this read is to be considered as 'mapped'. This may help to avoid
      'spurious' mappings. A value of 0 (the default) denotes no coverage
      threshold (a single 31-mer can yield a mapping). Since coverage by exact
      matching, large, MMPs is a rather strict condition, this value should
      likely be set to something low, if used. This value is expressed as a
      number between 0 and 1; a larger value is more stringent and less likely
      to allow spurios mappings, but can reduce sensitivity (EXPERIMENTAL).
    'sbg:altPrefix': '--quasiCoverage'
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '0'
  - id: pos_bias
    type: boolean?
    label: Position bias
    description: >-
      Enable modeling of a position-specific fragment start distribution. This
      is meant to model non-uniform coverage biases that are sometimes present
      in RNA-seq data (e.g. 5' or 3' positional bias). Currently, a small and
      fixed number of models are learned for different length classes of
      transcripts.
    'sbg:category': Basic options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'Off'
  - id: per_transcript_prior
    type: boolean?
    label: Per transcript prior
    description: >-
      The prior (either the default, or the argument provided via --vbPrior)
      will be interpreted as a transcript-level prior (i.e. each transcript will
      be given a prior read count of this value).
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'off'
  - id: num_pre_aux_model_samples
    type: int?
    label: Number of pre auxiliary model samples
    description: >-
      The first this many samples will have their assignment likelihoods and
      contributions to the transcript abundances computed without applying any
      auxiliary models. The purpose of ignoring the auxiliary models for the
      first that many observations is to avoid applying these models before
      their parameters have been learned sufficiently well.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '1000000'
  - id: num_gibbs_samples
    type: int?
    label: Number of Gibbs samples
    description: The number of Gibbs sampling rounds to perform.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '0'
  - id: num_bootstraps
    type: int?
    label: Number of bootstraps
    description: >-
      The number of bootstrap samples to generate. Note: this is mutually
      exclusive with Gibbs sampling.
    'sbg:category': Advanced options
    'sbg:toolDefaultValue': '0'
  - id: num_bias_samples
    type: int?
    label: Number of bias samples
    description: >-
      Number of fragment mappings to use when learning the sequence-specific
      bias model.
    'sbg:category': Advanced options
    'sbg:toolDefaultValue': '2000000'
  - id: num_aux_model_samples
    type: int?
    label: Number of auxiliary model samples
    description: >-
      The first this many numbers are used to train the auxiliary model
      parameters (e.g. fragment length distribution, bias, etc.). After their
      first that many observations, the auxiliary model parameters will be
      assumed to have converged and will be fixed.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '5000000'
  - id: no_length_correction
    type: boolean?
    label: No length correction
    description: >-
      Entirely disables length correction when estimating abundance of
      transcripts. This option can be used with protocols where one expects that
      fragments derive from their underlying targets without regard to that
      target's length, e.g. QuantSeq (EXPERIMENTAL).
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'Off'
  - id: no_fragment_length_distribution
    type: boolean?
    label: No fragment length distribution
    description: >-
      [Experimental] Do not consider concordance with the learned fragment
      lenght distribution when trying to determine the probability that a
      fragment has originated from a specific location. Normally, fragments with
      unlikely lengths will be assigned a smaller relative probability than
      those with more likely lenghts. When this flag is passed in, the observed
      fragment length has no effect on that fragment's a priori probability.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'off'
  - id: no_effective_length_correction
    type: boolean?
    label: No effective length correction
    description: >-
      Disables effective lenght correction when computing the probability that a
      fragment was generated from a transcript. If this flag is passed in, the
      fragment lenght distribution is not taken into account when computing this
      probability.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'off'
  - id: no_bias_length_threshold
    type: boolean?
    label: No bias length threshold
    description: >-
      [Experimental] If this option is enabled, then no (lower) threshold will
      be set on how short bias correction can make effective lengths. This can
      increase precision of bias correction, but harm robustness. The default
      correction applies a threshold.
    'sbg:category': Advanced options
    'sbg:toolDefaultValue': 'off'
  - id: min_assigned_frags
    type: int?
    label: Minimum assigned fragments
    description: >-
      The minimum number of fragments that must be assigned to the
      transcriptome.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '10'
  - id: meta
    type: boolean?
    label: Meta
    description: >-
      If you're using Salmon on a metagenomic dataset, consider setting this
      flag to disable parts of the abundance estimation model that make less
      sense for metagenomic data.
    'sbg:category': Basic options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'Off'
  - id: max_read_occ
    type: int?
    label: Maximum read occurence
    description: Reads "mapping" to more than this many places won't be considered.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '100'
  - id: max_occ
    type: int?
    label: Maximum (S)MEM occurance
    description: (S)MEMs occuring more than this many times won't be considered.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '200'
  - id: init_uniform
    type: boolean?
    label: Initialize uniform parameters
    description: >-
      Initialize the offline inference with uniform parameters, rather than
      seeding with online parameters.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'off'
  - id: incompatible_prior
    type: float?
    label: Incompatible prior probability
    description: >-
      This option sets the prior probability that an alignment that disagrees
      with the specified library type (--libType) results from the true fragment
      origin. Setting this to 0 specifies that alignments that disagree with the
      library type should be "impossible", while setting it to 1 says that
      alignments that disagree with the library type are no less likely than
      those that do.
    'sbg:category': Basic options
    'sbg:toolDefaultValue': '9.9999999999999995e-21'
  - id: gc_size_samp
    type: int?
    label: GC size sample
    description: >-
      The value by which to downsample transcripts when representing the GC
      content. Larger values will reduce memory usage, but may decrease the
      fidelity of bias modeling results.
    'sbg:category': Advanced options
    'sbg:toolDefaultValue': '1'
  - id: gc_bias
    type: boolean?
    label: GC bias correction
    description: '[Biasl] Perform fragment GC bias correction.'
    'sbg:category': Basic options
    'sbg:toolDefaultValue': 'off'
  - id: forgetting_factor
    type: float?
    label: Forgetting factor
    description: >-
      The forgetting factor used in the online learning schedule. A smaller
      value results in quicker learning, but higher variance and may be
      unstable. A larger value results in slower learning but may be more
      stable. The input value should be in the interva (0.5, 1.0].
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '0.65000000000000002'
  - id: fld_sd
    type: int?
    label: Fragment length standard deviation
    description: The standard deviation used in the fragment length distribution prior.
    'sbg:category': Advanced options
    'sbg:toolDefaultValue': '80'
  - id: fld_mean
    type: int?
    label: Mean fragment length
    description: The mean used in the fragment lenght distribution prior.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '200'
  - id: fld_max
    type: int?
    label: Maximum fragment length
    description: >-
      The maximum fragment length to consider when building the empirical
      distribution.
    'sbg:category': Advanced options
    'sbg:toolDefaultValue': '1000'
  - id: faster_mapping
    type: boolean?
    label: Faster mapping
    description: >-
      [Developer]: Disables some extra checks during quasi-mapping. This may
      make mapping a little bit faster at the potential cost of returning too
      many mappings (i.e. some suboptimal mappings) for certain reads.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'Off'
  - id: dump_eq_weights
    type: boolean?
    label: Dump equivalence class weights
    description: >-
      Includes 'rich' equivalence class weights in the output when equivalence
      class information is being dumpes to file.
    'sbg:altPrefix': '--dumpEqWeights'
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'Off'
  - id: dump_eq
    type: boolean?
    label: Dump equivalence class counts
    description: Dump the equivalence class counts that were computed during quasi-mapping.
    'sbg:category': Advanced options
    'sbg:toolDefaultValue': 'Off'
  - id: discard_orphans_quasi
    type: boolean?
    label: Discard orphans in Quasi-mapping mode
    description: >-
      Quasi-mapping mode only: Discard orphans mapping in quasi-mapping mode. If
      this flag is passed then only paired mappings will be considered towards
      quantification estimates. The default behaviour is to consider orphan
      mappings if no valid paired mappings exist. This flag is independent of
      the option to write the oprhaned mappings to file (--writeOprhanLinks).
    'sbg:category': Basic Options
    'sbg:toolDefaultValue': 'Off'
  - id: consistent_hits
    type: boolean?
    label: Consistent hits
    description: >-
      Force hits gathered during quasi-mapping to be "consistent" (i.e.
      co-linear and approximately the right distance apart).
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'off'
  - id: bias_speed_samp
    type: int?
    label: Bias speed sample
    description: >-
      The value at which the fragment length PMF is down-sampled when evaluating
      sequence-specific and & GC fragment bias. Larger values speed up effective
      length correction, but may decrease the fidelity of bias modeling results.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': '1'
  - id: alternative_init_mode
    type: boolean?
    label: Alternative initialization mode
    description: >-
      Use an alternative strategy (rather than simple interpolation) between the
      online and uniform abundance estimates to initialize the EM/VBEM
      algorithm.
    'sbg:category': Advanced options
    'sbg:stageInput': null
    'sbg:toolDefaultValue': 'Off'
  - id: allow_orphans_fmd
    type: boolean?
    label: Allow orphans in FMD mode
    description: >-
      FMD-mapping mode only: Consider orphaned reads as valid hits when
      performing lightweight-alignment. This option will increase sensitivity
      (allow more reads to map and more transcripts to be detected), but may
      decrease specificity as orphaned alignments are more likely to be
      spurious.
    'sbg:category': Basic options
    'sbg:toolDefaultValue': 'off'
outputs:
  - id: unmapped_reads
    outputSource:
      - Salmon_Quant___Reads/unmapped_reads
    'sbg:fileTypes': TXT
    type: File?
    label: Unmapped reads
    description: >-
      File with the names of reads (or mates in paired-end reads) that do not
      map to the transcriptome.
    required: false
    'sbg:includeInPorts': true
    'sbg:x': 1128.7589372907369
    'sbg:y': -25.76091221400644
  - id: quant_sf
    outputSource:
      - Salmon_Quant___Reads/quant_sf
    'sbg:fileTypes': SF
    type: File?
    label: Transcript abundance estimates
    description: 'Salmon Quant output file, containing transcript abundance estimates.'
    required: false
    'sbg:includeInPorts': true
    'sbg:x': 1395.0780378069203
    'sbg:y': 38.57349940708707
  - id: quant_genes_sf
    outputSource:
      - Salmon_Quant___Reads/quant_genes_sf
    'sbg:fileTypes': SF
    type: File?
    label: Gene abundance estimates
    description: >-
      Salmon Quant output file, containing aggregated gene-level abundance
      estimates.
    required: false
    'sbg:includeInPorts': true
    'sbg:x': 1398.3593750000007
    'sbg:y': 471.95744105747804
  - id: mapping_info
    outputSource:
      - Salmon_Quant___Reads/mapping_info
    'sbg:fileTypes': SAM
    type: File?
    label: Mapping info
    description: Information about the quasi-mappings Salmon Quant uses for quantification.
    required: false
    'sbg:includeInPorts': true
    'sbg:x': 1140.326102120536
    'sbg:y': 545.0930786132815
  - id: bootstrap_data
    outputSource:
      - Salmon_Quant___Reads/bootstrap_data
    'sbg:fileTypes': TAR
    type: File?
    label: Bootstrap data
    description: >-
      A TAR bundle containing the bootstrap folder, if bootstrapping was
      performed.
    required: false
    'sbg:includeInPorts': true
    'sbg:x': 1141.6651262555806
    'sbg:y': 685.0272478376119
  - id: eq_classes
    outputSource:
      - Salmon_Quant___Reads/eq_classes
    'sbg:fileTypes': TXT
    type: File?
    label: Equivalence classes
    description: >-
      A file that contains the equivalence classes and corresponding counts that
      were computed during quasi-mapping.
    required: false
    'sbg:includeInPorts': true
    'sbg:x': 1401.7817905970987
    'sbg:y': 614.6217564174111
  - id: transcript_expression_matrix
    outputSource:
      - SBG_Create_Expression_Matrix___Transcripts/expression_matrix
    'sbg:fileTypes': TXT
    type: File?
    label: Transcript Expression Matrix
    description: >-
      A matrix of TPM values for transcript expression data, aggregated across
      all input samples.
    required: false
    'sbg:includeInPorts': true
    'sbg:x': 1397.6690673828132
    'sbg:y': 185.18794468470992
  - id: gene_expression_matrix
    outputSource:
      - SBG_Create_Expression_Matrix___Genes/expression_matrix
    'sbg:fileTypes': TXT
    type: File?
    label: Gene Expression Matrix
    description: >-
      A matrix of TPM values for gene expression data, aggregated across all
      input samples.
    required: false
    'sbg:includeInPorts': true
    'sbg:x': 1399.3231201171882
    'sbg:y': 335.6390380859377
  - id: salmon_quant_archive
    outputSource:
      - Salmon_Quant___Reads/salmon_quant_archive
    'sbg:fileTypes': TAR
    type: File?
    label: Salmon Quant archive
    description: >-
      Archive with all files outputted by Salmon Quant. This archive can be used
      with downstream differential expression tools like Sleuth.
    'sbg:includeInPorts': true
    'sbg:x': 1135.7143729073664
    'sbg:y': 118.57138497488872
steps:
  - id: SBG_Create_Expression_Matrix___Transcripts
    in:
      - id: output_name
        default: transcripts.expression_matrix.tpm.txt
      - id: abundance_estimates
        source:
          - Salmon_Quant___Reads/quant_sf
    out:
      - id: expression_matrix
    run:
      class: CommandLineTool
      cwlVersion: v1.0
      id: h-a6133803/h-c58a0dd6/h-23be1029/0
      baseCommand: []
      inputs:
        - 'sbg:category': Options
          'sbg:toolDefaultValue': '''expression_matrix.txt'''
          id: output_name
          type: string?
          label: Output file name
          doc: name of the outputted TPM counts matrix file.
        - default: tpm
          'sbg:category': Options
          'sbg:toolDefaultValue': '''tpm'''
          id: column_name
          type: string?
          inputBinding:
            position: 4
            prefix: '--column_name'
            shellQuote: false
          label: Column name
          doc: Column name chose to aggregate results over.
        - format: 'RESULTS, SF, TSV'
          required: false
          'sbg:category': Inputs
          id: abundance_estimates
          type: 'File[]?'
          inputBinding:
            position: 1
            prefix: '-i'
            itemSeparator: ','
            shellQuote: false
          label: Abundance estimates
          doc: >-
            Abundance estimates generated by tools like RSEM, Kallisto or
            Salmon.
      outputs:
        - id: expression_matrix
          doc: >-
            A single file containing expression values across all
            genes/transcripts for multiple provided inputs.
          label: Expression matrix
          type: File?
          outputBinding:
            glob: |-
              ${
                  if (inputs.abundance_estimates) {
                      var x = [].concat(inputs.abundance_estimates)
                      if (inputs.output_name) {
                          var suffix = inputs.output_name
                      } else {
                          var atr = inputs.column_name ? inputs.column_name : 'tpm'
                          var suffix = 'expression_matrix.' + atr + '.txt'
                      }
                      if (x.length == 1) {
                          if (x[0].metadata && x[0].metadata.sample_id) {
                              return x[0].metadata.sample_id + '.' + suffix
                          } else {
                              return x[0].path.split('/').pop().split('.')[0] + '.' + suffix
                          }
                      } else {
                          return suffix
                      }
                  }
              }
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.abundance_estimates)

              }
          format: TXT
      doc: >-
        This tool takes multiple abundance estimates files outputted by tools
        like RSEM, Kallisto or Salmon and creates a single expression counts
        matrix, based on the input column that the user specifies (the default
        is 'tpm', but any other string can be input here, like 'fpkm', 'counts'
        or similar), that can be used for further downstream analysis.


        This tool can also be used to aggregate any kind of results in
        tab-delimited format and create a matrix like file, it was just
        originally developed for creating expression matrices. 


        ### Common Issues ###

        None
      label: SBG Create Expression Matrix - Transcripts
      arguments:
        - position: 0
          separate: false
          shellQuote: false
          valueFrom: |-
            ${
                if ([].concat(inputs.abundance_estimates).length > 1) {
                    return "python create_tpm_matrix.py"
                } else {
                    return "echo 'Multiple samples not provided, doing passthrough'"
                }
            }
        - position: 2
          prefix: ''
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.abundance_estimates) {
                    var quants = [].concat(inputs.abundance_estimates)
                    var samples = []
                    if (quants[0] && quants[0].metadata && quants[0].metadata.sample_id) {
                        for (i = 0; i < quants.length; i++) {
                            samples = samples.concat(quants[i].metadata.sample_id)
                        }
                    } else {
                        for (i = 0; i < quants.length; i++) {
                            samples = samples.concat(quants[i].path.split('/').pop().split('.')[0])
                        }
                    }
                    return '--sample_ids ' + samples
                }
            }
        - position: 3
          prefix: ''
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.abundance_estimates) {
                    var x = [].concat(inputs.abundance_estimates)
                    if (inputs.output_name) {
                        var suffix = inputs.output_name
                    } else {
                        var atr = inputs.column_name ? inputs.column_name : 'tpm'
                        var suffix = 'expression_matrix.' + atr + '.txt'
                    }
                    if (x.length == 1) {
                        if (x[0].metadata && x[0].metadata.sample_id) {
                            return '-o ' + x[0].metadata.sample_id + '.' + suffix
                        } else {
                            return '-o ' + x[0].path.split('/').pop().split('.')[0] + '.' + suffix
                        }
                    } else {
                        return '-o ' + suffix
                    }
                }
            }
      requirements:
        - class: ShellCommandRequirement
        - class: ResourceRequirement
          ramMin: 1000
          coresMin: 1
        - class: DockerRequirement
          dockerPull: 'images.sbgenomics.com/dusan_randjelovic/sci-python:2.7'
        - class: InitialWorkDirRequirement
          listing:
            - entryname: create_tpm_matrix.py
              entry: >-
                import argparse



                def parse_quant_file(quant_files, sample_ids, out_name,
                column_name):

                    # Open all files for reading and an output file for writing; make the header
                    handles = []
                    writer = open(out_name, 'w')
                    writer.write('Gene_or_Transcript_ID')
                    
                    k = 0
                    for item in quant_files:
                        sample_name = sample_ids[k]
                        k = k+1
                        suppl = open(item)
                        header = [x.lower() for x in suppl.next().rstrip().split('\t')]
                        TPM_column = header.index(column_name)
                        #suppl.next()  # throw away the header
                        writer.write('\t' + sample_name)
                        handles.append(suppl)

                    # Iterate over files and lines
                    eof = False
                    while not eof:
                        writer.write('\n')
                        for i, suppl in enumerate(handles):
                            try:
                                items = suppl.next().rstrip().split('\t')
                            except StopIteration:
                                eof = True
                                break
                            if i == 0:
                                writer.write('{}\t{}'.format(items[0].split('|')[0], items[TPM_column]))
                            else:
                                writer.write('\t' + items[TPM_column])

                    writer.close()


                if __name__ == '__main__':

                    parser = argparse.ArgumentParser(description='Parse a set of abundance estimate files into a matrix of TPM values.')
                    parser.add_argument('--input', '-i', help='Comma-separated list of abundance estimate input files.')
                    parser.add_argument('--sample_ids', '-s', help='Comma-separated list of sample_ids.')
                    parser.add_argument('--out', '-o', help='Output file name.')
                    parser.add_argument('--column_name', '-c', help='Column name chosen to aggregate results over')
                    args = parser.parse_args()

                    quant_inputs = args.input.split(',')
                    samples = args.sample_ids.split(',')
                    parse_quant_file(quant_files=quant_inputs, sample_ids=samples, out_name=args.out, column_name = args.column_name)
              writable: false
        - class: InlineJavascriptRequirement
          expressionLib:
            - |-
              var updateMetadata = function(file, key, value) {
                  file['metadata'][key] = value;
                  return file;
              };


              var setMetadata = function(file, metadata) {
                  if (!('metadata' in file))
                      file['metadata'] = metadata;
                  else {
                      for (var key in metadata) {
                          file['metadata'][key] = metadata[key];
                      }
                  }
                  return file
              };

              var inheritMetadata = function(o1, o2) {
                  var commonMetadata = {};
                  if (!Array.isArray(o2)) {
                      o2 = [o2]
                  }
                  for (var i = 0; i < o2.length; i++) {
                      var example = o2[i]['metadata'];
                      for (var key in example) {
                          if (i == 0)
                              commonMetadata[key] = example[key];
                          else {
                              if (!(commonMetadata[key] == example[key])) {
                                  delete commonMetadata[key]
                              }
                          }
                      }
                  }
                  if (!Array.isArray(o1)) {
                      o1 = setMetadata(o1, commonMetadata)
                  } else {
                      for (var i = 0; i < o1.length; i++) {
                          o1[i] = setMetadata(o1[i], commonMetadata)
                      }
                  }
                  return o1;
              };

              var toArray = function(file) {
                  return [].concat(file);
              };

              var groupBy = function(files, key) {
                  var groupedFiles = [];
                  var tempDict = {};
                  for (var i = 0; i < files.length; i++) {
                      var value = files[i]['metadata'][key];
                      if (value in tempDict)
                          tempDict[value].push(files[i]);
                      else tempDict[value] = [files[i]];
                  }
                  for (var key in tempDict) {
                      groupedFiles.push(tempDict[key]);
                  }
                  return groupedFiles;
              };

              var orderBy = function(files, key, order) {
                  var compareFunction = function(a, b) {
                      if (a['metadata'][key].constructor === Number) {
                          return a['metadata'][key] - b['metadata'][key];
                      } else {
                          var nameA = a['metadata'][key].toUpperCase();
                          var nameB = b['metadata'][key].toUpperCase();
                          if (nameA < nameB) {
                              return -1;
                          }
                          if (nameA > nameB) {
                              return 1;
                          }
                          return 0;
                      }
                  };

                  files = files.sort(compareFunction);
                  if (order == undefined || order == "asc")
                      return files;
                  else
                      return files.reverse();
              };
      'sbg:appVersion':
        - v1.0
      'sbg:categories':
        - Other
      'sbg:cmdPreview': 'python create_tpm_matrix.py  --sample_ids SAMPLEA,SAMPLEB'
      'sbg:contributors':
        - uros_sipetic
      'sbg:createdBy': uros_sipetic
      'sbg:id': h-a6133803/h-c58a0dd6/h-23be1029/0
      'sbg:image_url': null
      'sbg:latestRevision': 11
      'sbg:license': Apache License 2.0
      'sbg:project': bix-demo/sbgtools-demo
      'sbg:publisher': sbg
      'sbg:revisionNotes': Update output filename
      'sbg:sbgMaintained': false
      'sbg:toolAuthor': Seven Bridges Genomics
      'sbg:toolkit': SBGTools
      'sbg:toolkitVersion': v1.0
      'sbg:validationErrors': []
      x: 1132.180350167411
      'y': 255.92727661132847
    label: SBG Create Expression Matrix - Transcripts
    'sbg:x': 1132.180350167411
    'sbg:y': 255.92727661132847
  - id: SBG_Create_Expression_Matrix___Genes
    in:
      - id: output_name
        default: genes.expression_matrix.tpm.txt
      - id: abundance_estimates
        source:
          - Salmon_Quant___Reads/quant_genes_sf
    out:
      - id: expression_matrix
    run:
      class: CommandLineTool
      cwlVersion: v1.0
      id: h-90ac60db/h-5eb38456/h-35ea6aab/0
      baseCommand: []
      inputs:
        - 'sbg:category': Options
          'sbg:toolDefaultValue': '''expression_matrix.txt'''
          id: output_name
          type: string?
          label: Output file name
          doc: name of the outputted TPM counts matrix file.
        - default: tpm
          'sbg:category': Options
          'sbg:toolDefaultValue': '''tpm'''
          id: column_name
          type: string?
          inputBinding:
            position: 4
            prefix: '--column_name'
            shellQuote: false
          label: Column name
          doc: Column name chose to aggregate results over.
        - format: 'RESULTS, SF, TSV'
          required: false
          'sbg:category': Inputs
          id: abundance_estimates
          type: 'File[]?'
          inputBinding:
            position: 1
            prefix: '-i'
            itemSeparator: ','
            shellQuote: false
          label: Abundance estimates
          doc: >-
            Abundance estimates generated by tools like RSEM, Kallisto or
            Salmon.
      outputs:
        - id: expression_matrix
          doc: >-
            A single file containing expression values across all
            genes/transcripts for multiple provided inputs.
          label: Expression matrix
          type: File?
          outputBinding:
            glob: |-
              ${
                  if (inputs.abundance_estimates) {
                      var x = [].concat(inputs.abundance_estimates)
                      if (inputs.output_name) {
                          var suffix = inputs.output_name
                      } else {
                          var atr = inputs.column_name ? inputs.column_name : 'tpm'
                          var suffix = 'expression_matrix.' + atr + '.txt'
                      }
                      if (x.length == 1) {
                          if (x[0].metadata && x[0].metadata.sample_id) {
                              return x[0].metadata.sample_id + '.' + suffix
                          } else {
                              return x[0].path.split('/').pop().split('.')[0] + '.' + suffix
                          }
                      } else {
                          return suffix
                      }
                  }
              }
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.abundance_estimates)

              }
          format: TXT
      doc: >-
        This tool takes multiple abundance estimates files outputted by tools
        like RSEM, Kallisto or Salmon and creates a single expression counts
        matrix, based on the input column that the user specifies (the default
        is 'tpm', but any other string can be input here, like 'fpkm', 'counts'
        or similar), that can be used for further downstream analysis.


        This tool can also be used to aggregate any kind of results in
        tab-delimited format and create a matrix like file, it was just
        originally developed for creating expression matrices. 


        ### Common Issues ###

        None
      label: SBG Create Expression Matrix - Genes
      arguments:
        - position: 0
          separate: false
          shellQuote: false
          valueFrom: |-
            ${
                if ([].concat(inputs.abundance_estimates).length > 1) {
                    return "python create_tpm_matrix.py"
                } else {
                    return "echo 'Multiple samples not provided, doing passthrough'"
                }
            }
        - position: 2
          prefix: ''
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.abundance_estimates) {
                    var quants = [].concat(inputs.abundance_estimates)
                    var samples = []
                    if (quants[0] && quants[0].metadata && quants[0].metadata.sample_id) {
                        for (i = 0; i < quants.length; i++) {
                            samples = samples.concat(quants[i].metadata.sample_id)
                        }
                    } else {
                        for (i = 0; i < quants.length; i++) {
                            samples = samples.concat(quants[i].path.split('/').pop().split('.')[0])
                        }
                    }
                    return '--sample_ids ' + samples
                }
            }
        - position: 3
          prefix: ''
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.abundance_estimates) {
                    var x = [].concat(inputs.abundance_estimates)
                    if (inputs.output_name) {
                        var suffix = inputs.output_name
                    } else {
                        var atr = inputs.column_name ? inputs.column_name : 'tpm'
                        var suffix = 'expression_matrix.' + atr + '.txt'
                    }
                    if (x.length == 1) {
                        if (x[0].metadata && x[0].metadata.sample_id) {
                            return '-o ' + x[0].metadata.sample_id + '.' + suffix
                        } else {
                            return '-o ' + x[0].path.split('/').pop().split('.')[0] + '.' + suffix
                        }
                    } else {
                        return '-o ' + suffix
                    }
                }
            }
      requirements:
        - class: ShellCommandRequirement
        - class: ResourceRequirement
          ramMin: 1000
          coresMin: 1
        - class: DockerRequirement
          dockerPull: 'images.sbgenomics.com/dusan_randjelovic/sci-python:2.7'
        - class: InitialWorkDirRequirement
          listing:
            - entryname: create_tpm_matrix.py
              entry: >-
                import argparse



                def parse_quant_file(quant_files, sample_ids, out_name,
                column_name):

                    # Open all files for reading and an output file for writing; make the header
                    handles = []
                    writer = open(out_name, 'w')
                    writer.write('Gene_or_Transcript_ID')
                    
                    k = 0
                    for item in quant_files:
                        sample_name = sample_ids[k]
                        k = k+1
                        suppl = open(item)
                        header = [x.lower() for x in suppl.next().rstrip().split('\t')]
                        TPM_column = header.index(column_name)
                        #suppl.next()  # throw away the header
                        writer.write('\t' + sample_name)
                        handles.append(suppl)

                    # Iterate over files and lines
                    eof = False
                    while not eof:
                        writer.write('\n')
                        for i, suppl in enumerate(handles):
                            try:
                                items = suppl.next().rstrip().split('\t')
                            except StopIteration:
                                eof = True
                                break
                            if i == 0:
                                writer.write('{}\t{}'.format(items[0].split('|')[0], items[TPM_column]))
                            else:
                                writer.write('\t' + items[TPM_column])

                    writer.close()


                if __name__ == '__main__':

                    parser = argparse.ArgumentParser(description='Parse a set of abundance estimate files into a matrix of TPM values.')
                    parser.add_argument('--input', '-i', help='Comma-separated list of abundance estimate input files.')
                    parser.add_argument('--sample_ids', '-s', help='Comma-separated list of sample_ids.')
                    parser.add_argument('--out', '-o', help='Output file name.')
                    parser.add_argument('--column_name', '-c', help='Column name chosen to aggregate results over')
                    args = parser.parse_args()

                    quant_inputs = args.input.split(',')
                    samples = args.sample_ids.split(',')
                    parse_quant_file(quant_files=quant_inputs, sample_ids=samples, out_name=args.out, column_name = args.column_name)
              writable: false
        - class: InlineJavascriptRequirement
          expressionLib:
            - |-
              var updateMetadata = function(file, key, value) {
                  file['metadata'][key] = value;
                  return file;
              };


              var setMetadata = function(file, metadata) {
                  if (!('metadata' in file))
                      file['metadata'] = metadata;
                  else {
                      for (var key in metadata) {
                          file['metadata'][key] = metadata[key];
                      }
                  }
                  return file
              };

              var inheritMetadata = function(o1, o2) {
                  var commonMetadata = {};
                  if (!Array.isArray(o2)) {
                      o2 = [o2]
                  }
                  for (var i = 0; i < o2.length; i++) {
                      var example = o2[i]['metadata'];
                      for (var key in example) {
                          if (i == 0)
                              commonMetadata[key] = example[key];
                          else {
                              if (!(commonMetadata[key] == example[key])) {
                                  delete commonMetadata[key]
                              }
                          }
                      }
                  }
                  if (!Array.isArray(o1)) {
                      o1 = setMetadata(o1, commonMetadata)
                  } else {
                      for (var i = 0; i < o1.length; i++) {
                          o1[i] = setMetadata(o1[i], commonMetadata)
                      }
                  }
                  return o1;
              };

              var toArray = function(file) {
                  return [].concat(file);
              };

              var groupBy = function(files, key) {
                  var groupedFiles = [];
                  var tempDict = {};
                  for (var i = 0; i < files.length; i++) {
                      var value = files[i]['metadata'][key];
                      if (value in tempDict)
                          tempDict[value].push(files[i]);
                      else tempDict[value] = [files[i]];
                  }
                  for (var key in tempDict) {
                      groupedFiles.push(tempDict[key]);
                  }
                  return groupedFiles;
              };

              var orderBy = function(files, key, order) {
                  var compareFunction = function(a, b) {
                      if (a['metadata'][key].constructor === Number) {
                          return a['metadata'][key] - b['metadata'][key];
                      } else {
                          var nameA = a['metadata'][key].toUpperCase();
                          var nameB = b['metadata'][key].toUpperCase();
                          if (nameA < nameB) {
                              return -1;
                          }
                          if (nameA > nameB) {
                              return 1;
                          }
                          return 0;
                      }
                  };

                  files = files.sort(compareFunction);
                  if (order == undefined || order == "asc")
                      return files;
                  else
                      return files.reverse();
              };
      'sbg:appVersion':
        - v1.0
      'sbg:categories':
        - Other
      'sbg:cmdPreview': 'python create_tpm_matrix.py  --sample_ids SAMPLEA,SAMPLEB'
      'sbg:contributors':
        - uros_sipetic
      'sbg:createdBy': uros_sipetic
      'sbg:id': h-90ac60db/h-5eb38456/h-35ea6aab/0
      'sbg:image_url': null
      'sbg:latestRevision': 11
      'sbg:license': Apache License 2.0
      'sbg:project': bix-demo/sbgtools-demo
      'sbg:publisher': sbg
      'sbg:revisionNotes': Update output filename
      'sbg:sbgMaintained': false
      'sbg:toolAuthor': Seven Bridges Genomics
      'sbg:toolkit': SBGTools
      'sbg:toolkitVersion': v1.0
      'sbg:validationErrors': []
      x: 1129.9248395647323
      'y': 407.2054399762839
    label: SBG Create Expression Matrix - Genes
    'sbg:x': 1129.9248395647323
    'sbg:y': 407.2054399762839
  - id: SBG_Pair_FASTQs_by_Metadata_1
    in:
      - id: fastq_list
        source:
          - reads
      - id: number_of_cpus
        default: 36
      - id: max_number_of_parallel_jobs
        source: max_number_of_parallel_jobs
    out:
      - id: tuple_list
      - id: number_of_elements
    run:
      class: CommandLineTool
      cwlVersion: v1.0
      id: h-0e5eefb3/h-40423e23/h-2b6e9240/0
      baseCommand:
        - echo
      inputs:
        - id: fastq_list
          type: 'File[]'
          label: List of FASTQ files
          doc: List of the FASTQ files with properly set metadata fileds.
        - 'sbg:category': Options
          'sbg:toolDefaultValue': '32'
          id: number_of_cpus
          type: int?
          label: Number of CPUs
          doc: >-
            Number of CPUs available in the workflow that uses this tool. This
            number will be used to determine the optimal number of threads to
            use in the tool downstream of this one.
        - 'sbg:category': Options
          'sbg:toolDefaultValue': '4'
          id: max_number_of_parallel_jobs
          type: int?
          label: Maximum number of parallel jobs
          doc: >-
            Maximum number of parallel jobs to allow in the tool downstream of
            this one.
      outputs:
        - id: tuple_list
          doc: List of grouped FASTQ files by metadata fields.
          label: List of grouped FASTQ files
          type:
            type: array
            items:
              items: File
              type: array
          outputBinding:
            outputEval: |-
              ${
                  function get_meta_map(m, file, meta) {
                      if (meta in file.metadata) {
                          return m[file.metadata[meta]]
                      } else {
                          return m['Undefined']
                      }
                  }

                  function create_new_map(map, file, meta) {
                      if (meta in file.metadata) {
                          map[file.metadata[meta]] = {}
                          return map[file.metadata[meta]]
                      } else {
                          map['Undefined'] = {}
                          return map['Undefined']
                      }
                  }

                  arr = [].concat(inputs.fastq_list)
                  map = {}

                  for (i in arr) {

                      sm_map = get_meta_map(map, arr[i], 'sample_id')
                      if (!sm_map) sm_map = create_new_map(map, arr[i], 'sample_id')

                      lb_map = get_meta_map(sm_map, arr[i], 'library_id')
                      if (!lb_map) lb_map = create_new_map(sm_map, arr[i], 'library_id')

                      pu_map = get_meta_map(lb_map, arr[i], 'platform_unit_id')
                      if (!pu_map) pu_map = create_new_map(lb_map, arr[i], 'platform_unit_id')

                      if ('file_segment_number' in arr[i].metadata) {
                          if (pu_map[arr[i].metadata['file_segment_number']]) {
                              a = pu_map[arr[i].metadata['file_segment_number']]
                              ar = [].concat(a)
                              ar = ar.concat(arr[i])
                              pu_map[arr[i].metadata['file_segment_number']] = ar
                          } else pu_map[arr[i].metadata['file_segment_number']] = [].concat(arr[i])
                      } else {
                          if (pu_map['Undefined']) {
                              a = pu_map['Undefined']
                              ar = [].concat(a)
                              ar = ar.concat(arr[i])
                              pu_map['Undefined'] = ar
                          } else {
                              pu_map['Undefined'] = [].concat(arr[i])
                          }
                      }
                  }
                  tuple_list = []
                  for (sm in map)
                      for (lb in map[sm])
                          for (pu in map[sm][lb]) {
                              for (fsm in map[sm][lb][pu]) {
                                  list = map[sm][lb][pu][fsm]
                                  tuple_list.push(list)
                              }
                          }
                  return tuple_list
              }
        - id: number_of_elements
          doc: Number of paired elements created from the input FASTQs
          label: Number of elements
          type: int?
          outputBinding:
            outputEval: |-
              ${
                  function get_meta_map(m, file, meta) {
                      if (meta in file.metadata) {
                          return m[file.metadata[meta]]
                      } else {
                          return m['Undefined']
                      }
                  }

                  function create_new_map(map, file, meta) {
                      if (meta in file.metadata) {
                          map[file.metadata[meta]] = {}
                          return map[file.metadata[meta]]
                      } else {
                          map['Undefined'] = {}
                          return map['Undefined']
                      }
                  }

                  arr = [].concat(inputs.fastq_list)
                  map = {}

                  for (i in arr) {

                      sm_map = get_meta_map(map, arr[i], 'sample_id')
                      if (!sm_map) sm_map = create_new_map(map, arr[i], 'sample_id')

                      lb_map = get_meta_map(sm_map, arr[i], 'library_id')
                      if (!lb_map) lb_map = create_new_map(sm_map, arr[i], 'library_id')

                      pu_map = get_meta_map(lb_map, arr[i], 'platform_unit_id')
                      if (!pu_map) pu_map = create_new_map(lb_map, arr[i], 'platform_unit_id')

                      if ('file_segment_number' in arr[i].metadata) {
                          if (pu_map[arr[i].metadata['file_segment_number']]) {
                              a = pu_map[arr[i].metadata['file_segment_number']]
                              ar = [].concat(a)
                              ar = ar.concat(arr[i])
                              pu_map[arr[i].metadata['file_segment_number']] = ar
                          } else pu_map[arr[i].metadata['file_segment_number']] = [].concat(arr[i])
                      } else {
                          if (pu_map['Undefined']) {
                              a = pu_map['Undefined']
                              ar = [].concat(a)
                              ar = ar.concat(arr[i])
                              pu_map['Undefined'] = ar
                          } else {
                              pu_map['Undefined'] = [].concat(arr[i])
                          }
                      }
                  }
                  tuple_list = []
                  for (sm in map)
                      for (lb in map[sm])
                          for (pu in map[sm][lb]) {
                              for (fsm in map[sm][lb][pu]) {
                                  list = map[sm][lb][pu][fsm]
                                  tuple_list.push(list)
                              }
                          }

                  var number_of_cpus = inputs.number_of_cpus ? inputs.number_of_cpus : 32
                  var threads = Math.floor(number_of_cpus / tuple_list.length)
                  return threads < number_of_cpus / inputs.max_number_of_parallel_jobs ? Math.floor(number_of_cpus / inputs.max_number_of_parallel_jobs) : threads
              }
      doc: >-
        Tool accepts list of FASTQ files groups them into separate lists. This
        grouping is done using metadata values and their hierarchy (Sample ID >
        Library ID > Platform unit ID > File segment number) which should create
        unique combinations for each pair of FASTQ files. Important metadata
        fields are Sample ID, Library ID, Platform unit ID and File segment
        number. Not all of these four metadata fields are required, but the
        present set has to be sufficient to create unique combinations for each
        pair of FASTQ files. Files with no paired end metadata are grouped in
        the same way as the ones with paired end metadata, generally they should
        be alone in a separate list. Files with no metadata set will be grouped
        together. 


        If there are more than two files in a group, this might create errors
        further down most pipelines and the user should check if the metadata
        fields for those files are set properly.
      label: SBG Pair FASTQs by Metadata
      arguments:
        - position: 1
          separate: false
          shellQuote: false
          valueFrom: '''Pairing'
        - position: 2
          separate: false
          shellQuote: false
          valueFrom: FASTQs!'
      requirements:
        - class: ShellCommandRequirement
        - class: ResourceRequirement
          ramMin: 1024
          coresMin: 1
        - class: DockerRequirement
          dockerImageId: d41a0837ab81
          dockerPull: alpine
        - class: InitialWorkDirRequirement
          listing:
            - $(inputs.fastq_list)
        - class: InlineJavascriptRequirement
          expressionLib:
            - |-
              var updateMetadata = function(file, key, value) {
                  file['metadata'][key] = value;
                  return file;
              };


              var setMetadata = function(file, metadata) {
                  if (!('metadata' in file))
                      file['metadata'] = metadata;
                  else {
                      for (var key in metadata) {
                          file['metadata'][key] = metadata[key];
                      }
                  }
                  return file
              };

              var inheritMetadata = function(o1, o2) {
                  var commonMetadata = {};
                  if (!Array.isArray(o2)) {
                      o2 = [o2]
                  }
                  for (var i = 0; i < o2.length; i++) {
                      var example = o2[i]['metadata'];
                      for (var key in example) {
                          if (i == 0)
                              commonMetadata[key] = example[key];
                          else {
                              if (!(commonMetadata[key] == example[key])) {
                                  delete commonMetadata[key]
                              }
                          }
                      }
                  }
                  if (!Array.isArray(o1)) {
                      o1 = setMetadata(o1, commonMetadata)
                  } else {
                      for (var i = 0; i < o1.length; i++) {
                          o1[i] = setMetadata(o1[i], commonMetadata)
                      }
                  }
                  return o1;
              };

              var toArray = function(file) {
                  return [].concat(file);
              };

              var groupBy = function(files, key) {
                  var groupedFiles = [];
                  var tempDict = {};
                  for (var i = 0; i < files.length; i++) {
                      var value = files[i]['metadata'][key];
                      if (value in tempDict)
                          tempDict[value].push(files[i]);
                      else tempDict[value] = [files[i]];
                  }
                  for (var key in tempDict) {
                      groupedFiles.push(tempDict[key]);
                  }
                  return groupedFiles;
              };

              var orderBy = function(files, key, order) {
                  var compareFunction = function(a, b) {
                      if (a['metadata'][key].constructor === Number) {
                          return a['metadata'][key] - b['metadata'][key];
                      } else {
                          var nameA = a['metadata'][key].toUpperCase();
                          var nameB = b['metadata'][key].toUpperCase();
                          if (nameA < nameB) {
                              return -1;
                          }
                          if (nameA > nameB) {
                              return 1;
                          }
                          return 0;
                      }
                  };

                  files = files.sort(compareFunction);
                  if (order == undefined || order == "asc")
                      return files;
                  else
                      return files.reverse();
              };
      appUrl: >-
        /u/uros_sipetic/salmon-workflow-0-9-1-demo/apps/#uros_sipetic/salmon-workflow-0-9-1-demo/sbg-pair-fastqs-by-metadata-custom/1
      'sbg:appVersion':
        - v1.0
      'sbg:categories':
        - Converters
        - Other
      'sbg:cmdPreview': echo 'Pairing FASTQs!'
      'sbg:contributors':
        - uros_sipetic
      'sbg:createdBy': uros_sipetic
      'sbg:id': h-0e5eefb3/h-40423e23/h-2b6e9240/0
      'sbg:image_url': null
      'sbg:latestRevision': 1
      'sbg:license': Apache License 2.0
      'sbg:project': uros_sipetic/salmon-workflow-0-9-1-demo
      'sbg:publisher': sbg
      'sbg:revisionNotes': Add support for better multi-threading of downstream tools.
      'sbg:sbgMaintained': false
      'sbg:toolAuthor': ''
      'sbg:toolkit': SBGTools
      'sbg:validationErrors': []
      x: 613.6842105263158
      'y': 373.0701647306744
    label: SBG Pair FASTQs by Metadata
    'sbg:x': -2.201730489730835
    'sbg:y': 351.447509765625
  - id: Salmon_Index
    in:
      - id: gencode
        source: gencode
      - id: keep_duplicates
        source: keep_duplicates
      - id: threads
        default: 32
      - id: transcripts
        source: transcriptome_fasta_or_salmon_index_archive
      - id: kmer_length
        source: kmer_length
    out:
      - id: salmon_index_archive
    run:
      class: CommandLineTool
      cwlVersion: v1.0
      id: admin/sbg-public-data/salmon-index-0-9-1/12
      baseCommand: []
      inputs:
        - 'sbg:category': Options
          'sbg:toolDefaultValue': 'off'
          id: gencode
          type: boolean?
          label: GENCODE FASTA
          doc: >-
            This flag will expect the input transcript FASTA to be in GENCODE
            format and will split the transcript name at the first '|'
            character. These reduced names will be used in the output and when
            looking for these transcripts in a gene to transcript GTF.
        - 'sbg:category': Options
          'sbg:toolDefaultValue': 'Off'
          id: keep_duplicates
          type: boolean?
          inputBinding:
            position: 9
            prefix: '--keepDuplicates'
            shellQuote: false
          label: Keep duplicates
          doc: >-
            This flag will disable the default indexing behavior of discarding
            sequence-identical duplicate transcripts. If this flag is passed,
            then duplicate transcripts that appear in the input will be retained
            and quantified separately.
        - default: 8
          'sbg:category': Basic options
          'sbg:toolDefaultValue': '8'
          id: threads
          type: int?
          inputBinding:
            position: 8
            prefix: '-p'
            shellQuote: false
          label: Number of threads
          doc: Number of threads to be used.
        - 'sbg:category': Options
          'sbg:toolDefaultValue': quasi
          id: index_type
          type:
            - 'null'
            - type: enum
              symbols:
                - quasi
                - fmd
              name: index_type
          inputBinding:
            position: 3
            prefix: '--type'
            shellQuote: false
          label: Index type
          doc: >-
            The type of index to build. Options are 'fmd' and 'quasi'. The
            former is for the SMEM based lightweight alignment (older) and the
            later is for the quasi-mapping (newer). 'Quasi' is recommended and
            'fmd' may be removed in the future.
        - 'sbg:category': Options
          'sbg:toolDefaultValue': '1'
          id: sa_samp
          type: int?
          inputBinding:
            position: 5
            prefix: '-s'
            shellQuote: false
          label: Sufix array sample
          doc: >-
            The interval at which the suffix array should be sampled. Smaller
            values are faster, but produce a larger index. The default value
            should be OK, unless Your transcriptome is huge. This value should
            be a power of 2.
        - 'sbg:category': options
          'sbg:toolDefaultValue': 'off'
          id: perfect_hash
          type: boolean?
          inputBinding:
            position: 7
            prefix: '--perfectHash'
            shellQuote: false
          label: Perfect hash
          doc: >-
            This option is for quasi index only. Build the index using a perfect
            hash rather than a dense hash. This will require less memory
            (especially during quantification), but will take longer to
            construct.
        - format: 'FASTA,FA,TAR,FASTA.GZ,FA.GZ'
          required: true
          'sbg:category': Options
          id: transcripts
          type: File
          inputBinding:
            position: 1
            prefix: '-t'
            shellQuote: false
          label: Transcriptome FASTA or Salmon Index
          doc: >-
            Transcriptome FASTA file, or an already generated Salmon index
            archive.
        - 'sbg:category': Options
          'sbg:toolDefaultValue': '31'
          id: kmer_length
          type: int?
          inputBinding:
            position: 4
            prefix: '-k'
            shellQuote: false
          label: K-mer length
          doc: >-
            The size of k-mers that should be used for the quasi index. K-mer
            length should be an odd number.
      outputs:
        - id: salmon_index_archive
          doc: >-
            Folder containing the indices from the specified alignment process
            (quasi or SMEM). To be used by Salmon Quant tool.
          label: Salmon index archive
          type: File?
          outputBinding:
            glob: '*tar'
            outputEval: |-
              ${
                  self = inheritMetadata(self[0], inputs.transcripts)
                  var fa = [].concat(inputs.transcripts)[0]
                  var indexName = ""
                  if (fa.path.toLowerCase().endsWith('gz')) {
                      var str = fa.path.split('/').pop().split('.').slice(0,-2).join('.')
                  } else {
                      var str = fa.path.split('/').pop().split('.').slice(0,-1).join('.')
                  }
                
                  var ext = fa.path.split('/').pop().split('.').pop()
                  if (ext.toLowerCase()=='fa' || ext.toLowerCase()=='fasta' || ext.toLowerCase()=='gz') {
                      indexName=str + "_salmon_index"
                  } else if (ext.toLowerCase()=='tar') {
                      indexName=inputs.transcripts.metadata.index_name
                  }

                  
                  return setMetadata(self, {'index_name': indexName})
              }
          format: TAR
      doc: >-
        **Salmon Index** tool builds an index from a transcriptome FASTA
        formatted file of target sequences, necessary for the **Salmon Quant**
        tool.  


        **Quasi-mapping** is a process of assigning reads to transcripts,
        without doing the exact base-to-base alignment. Seeing that for
        estimating transcript abundances, the main information needed is which
        transcript a read originates from and not the actual mapping
        coordinates, the idea with the **Salmon** tool was to implement a
        procedure that does exactly that [1, 2]. 


        The result is a software running at speeds orders of magnitude faster
        than other tools which utilize the full likelihood model, while keeping
        near-optimal probabilistic RNA-seq quantification results [1, 2]. 


        *A list of **all inputs and parameters** with corresponding descriptions
        can be found at the bottom of the page.*


        ### Common Use Cases


        - A **Transcriptome FASTA file** needs to be provided as an input to the
        tool. 


        ### Changes Introduced by Seven Bridges


        - An already generated **Salmon index archive** can be provided to the
        **Salmon Index** tool (**Transcriptome FASTA or Salmon Index Archive**
        input), in order to skip indexing and save a little bit of time if this
        tool is part of a bigger workflow and there already is an index file
        that can be provided.


        ### Common Issues and Important Notes


        - The input FASTA file (if provided instead of the already generated
        salmon index) should be a transcriptome FASTA, not a genomic FASTA.


        ### Performance Benchmarking


        The **Salmon Index** tool builds the index structure for **Salmon** in a
        very short time, therefore it is expected that all tasks using this tool
        should finish in under 5 minutes, costing around $0.05 on the default
        c4.2xlarge instance (AWS). 


        *Cost can be significantly reduced by using **spot instances**. Visit
        the [Knowledge
        Center](https://docs.sevenbridges.com/docs/about-spot-instances) for
        more details.*



        ### References


        [1] [Salmon
        paper](biorxiv.org/content/biorxiv/early/2016/08/30/021592.full.pdf)  

        [2] [Rapmap
        paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4908361/)
      label: Salmon Index
      arguments:
        - position: 0
          separate: false
          shellQuote: false
          valueFrom: |-
            ${
                var x = [].concat(inputs.transcripts)[0].path.split('/').pop()
                var y = x.split('.').pop().toLowerCase()
                if (y == 'fa' || y == 'fasta' || y == 'gz') {
                    return "salmon index"
                } else if (y == 'tar' || y == 'TAR') {
                    return "echo 'Tar bundle provided, skipping indexing.' "
                }
            }
        - position: 100
          shellQuote: false
          valueFrom: |-
            ${
                var fa = [].concat(inputs.transcripts)[0]
                if (fa.path.toLowerCase().endsWith('gz')) {
                    var str = fa.path.split('/').pop().split('.').slice(0, -2).join('.')
                } else {
                    var str = fa.path.split('/').pop().split('.').slice(0, -1).join('.')
                }
                var x1 = str + "_salmon_index"

                var ext = fa.path.split('/').pop().split('.').pop()
                if (ext.toLowerCase() == 'tar') {
                    return ""
                } else {
                    return "&& tar -vcf " + str + ".salmon-0.9.1-index-archive.tar " + x1
                }

            }
        - position: 2
          prefix: '-i'
          shellQuote: false
          valueFrom: |-
            ${
                var fa = [].concat(inputs.transcripts)[0]
                if (fa.path.toLowerCase().endsWith('gz')) {
                    var str = fa.path.split('/').pop().split('.').slice(0, -2).join('.')
                } else {
                    var str = fa.path.split('/').pop().split('.').slice(0, -1).join('.')
                }
                return str + "_salmon_index"
            }
        - position: 6
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.gencode) {
                    return "--gencode"
                } else if ([].concat(inputs.transcripts)[0].path.toLowerCase().indexOf('gencode') !== -1) {
                    return "--gencode"
                } else {
                    return ""
                }
            }
      requirements:
        - class: ShellCommandRequirement
        - class: ResourceRequirement
          ramMin: 7500
          coresMin: |-
            ${
                return inputs.threads ? inputs.threads : 8
            }
        - class: DockerRequirement
          dockerImageId: ea69041ddb8d42ee13362fe71f1149e5044edbd7cbf66ef4a1919f8736777007
          dockerPull: 'images.sbgenomics.com/uros_sipetic/salmon:0.9.1'
        - class: InitialWorkDirRequirement
          listing:
            - $(inputs.transcripts)
        - class: InlineJavascriptRequirement
          expressionLib:
            - |-
              var updateMetadata = function(file, key, value) {
                  file['metadata'][key] = value;
                  return file;
              };


              var setMetadata = function(file, metadata) {
                  if (!('metadata' in file))
                      file['metadata'] = metadata;
                  else {
                      for (var key in metadata) {
                          file['metadata'][key] = metadata[key];
                      }
                  }
                  return file
              };

              var inheritMetadata = function(o1, o2) {
                  var commonMetadata = {};
                  if (!Array.isArray(o2)) {
                      o2 = [o2]
                  }
                  for (var i = 0; i < o2.length; i++) {
                      var example = o2[i]['metadata'];
                      for (var key in example) {
                          if (i == 0)
                              commonMetadata[key] = example[key];
                          else {
                              if (!(commonMetadata[key] == example[key])) {
                                  delete commonMetadata[key]
                              }
                          }
                      }
                  }
                  if (!Array.isArray(o1)) {
                      o1 = setMetadata(o1, commonMetadata)
                  } else {
                      for (var i = 0; i < o1.length; i++) {
                          o1[i] = setMetadata(o1[i], commonMetadata)
                      }
                  }
                  return o1;
              };

              var toArray = function(file) {
                  return [].concat(file);
              };

              var groupBy = function(files, key) {
                  var groupedFiles = [];
                  var tempDict = {};
                  for (var i = 0; i < files.length; i++) {
                      var value = files[i]['metadata'][key];
                      if (value in tempDict)
                          tempDict[value].push(files[i]);
                      else tempDict[value] = [files[i]];
                  }
                  for (var key in tempDict) {
                      groupedFiles.push(tempDict[key]);
                  }
                  return groupedFiles;
              };

              var orderBy = function(files, key, order) {
                  var compareFunction = function(a, b) {
                      if (a['metadata'][key].constructor === Number) {
                          return a['metadata'][key] - b['metadata'][key];
                      } else {
                          var nameA = a['metadata'][key].toUpperCase();
                          var nameB = b['metadata'][key].toUpperCase();
                          if (nameA < nameB) {
                              return -1;
                          }
                          if (nameA > nameB) {
                              return 1;
                          }
                          return 0;
                      }
                  };

                  files = files.sort(compareFunction);
                  if (order == undefined || order == "asc")
                      return files;
                  else
                      return files.reverse();
              };
      'sbg:appVersion':
        - v1.0
      'sbg:categories':
        - RNA
        - Indexing
      'sbg:cmdPreview': >-
        salmon index -t /path/to/transcripts.gencode.fa.gz -i
        transcripts.gencode_salmon_index  && tar -vcf
        transcripts.gencode.salmon-0.9.1-index-archive.tar
        transcripts.gencode_salmon_index
      'sbg:contributors':
        - uros_sipetic
        - anamijalkovic
      'sbg:createdBy': uros_sipetic
      'sbg:id': admin/sbg-public-data/salmon-index-0-9-1/12
      'sbg:image_url': null
      'sbg:latestRevision': 12
      'sbg:license': GNU General Public License v3.0 only
      'sbg:links':
        - id: 'http://combine-lab.github.io/salmon/'
          label: Salmon Homepage
        - id: 'https://github.com/COMBINE-lab/salmon'
          label: Salmon Source Code
        - id: 'https://github.com/COMBINE-lab/salmon/releases/tag/v0.9.1'
          label: Salmon Download
        - id: 'http://biorxiv.org/content/early/2015/10/03/021592'
          label: Salmon Publications
        - id: 'http://salmon.readthedocs.org/en/latest/'
          label: Salmon Documentation
      'sbg:project': uros_sipetic/salmon-0-9-1-demo
      'sbg:publisher': sbg
      'sbg:revisionNotes': Rename 'type' id to 'index_type'
      'sbg:sbgMaintained': false
      'sbg:toolAuthor': 'Rob Patro, Carl Kingsford, Steve Mount, Mohsen Zakeri'
      'sbg:toolkit': Salmon
      'sbg:toolkitVersion': 0.9.1
      'sbg:validationErrors': []
      x: 614.1699539987665
      'y': 233.3265766344572
    label: Salmon Index
    'sbg:x': 2.570194721221924
    'sbg:y': 198.0526885986328
  - id: Salmon_Quant___Reads
    in:
      - id: no_effective_length_correction
        source: no_effective_length_correction
      - id: quasi_coverage
        source: quasi_coverage
      - id: fld_mean
        source: fld_mean
      - id: dump_eq_weights
        source: dump_eq_weights
      - id: vb_prior
        source: vb_prior
      - id: num_gibbs_samples
        source: num_gibbs_samples
      - id: consistent_hits
        source: consistent_hits
      - id: bias_speed_samp
        source: bias_speed_samp
      - id: discard_orphans_quasi
        source: discard_orphans_quasi
      - id: num_pre_aux_model_samples
        source: num_pre_aux_model_samples
      - id: gene_map
        source: gtf
      - id: write_mappings
        source: write_mappings
      - id: num_bootstraps
        source: num_bootstraps
      - id: meta
        source: meta
      - id: max_read_occ
        source: max_read_occ
      - id: min_assigned_frags
        source: min_assigned_frags
      - id: fld_max
        source: fld_max
      - id: salmon_index_archive
        source: Salmon_Index/salmon_index_archive
      - id: range_factorization_bins
        source: range_factorization_bins
      - id: faster_mapping
        source: faster_mapping
      - id: per_transcript_prior
        source: per_transcript_prior
      - id: write_unmapped_names
        source: write_unmapped_names
      - id: dump_eq
        source: dump_eq
      - id: read_files
        source:
          - SBG_Pair_FASTQs_by_Metadata_1/tuple_list
      - id: init_uniform
        source: init_uniform
      - id: no_bias_length_threshold
        source: no_bias_length_threshold
      - id: incompatible_prior
        source: incompatible_prior
      - id: allow_orphans_fmd
        source: allow_orphans_fmd
      - id: max_occ
        source: max_occ
      - id: use_vbopt
        source: use_vbopt
      - id: gc_bias
        source: gc_bias
      - id: pos_bias
        source: pos_bias
      - id: num_aux_model_samples
        source: num_aux_model_samples
      - id: no_fragment_length_distribution
        source: no_fragment_length_distribution
      - id: num_bias_samples
        source: num_bias_samples
      - id: reduce_GC_memory
        source: reduce_GC_memory
      - id: thinning_factor
        source: thinning_factor
      - id: gc_size_samp
        source: gc_size_samp
      - id: strict_intersect
        source: strict_intersect
      - id: fld_sd
        source: fld_sd
      - id: forgetting_factor
        source: forgetting_factor
      - id: alternative_init_mode
        source: alternative_init_mode
      - id: seq_bias
        source: seq_bias
      - id: no_length_correction
        source: no_length_correction
      - id: threads
        source: SBG_Pair_FASTQs_by_Metadata_1/number_of_elements
    out:
      - id: eq_classes
      - id: mapping_info
      - id: bootstrap_data
      - id: unmapped_reads
      - id: quant_genes_sf
      - id: salmon_quant_archive
      - id: quant_sf
    run:
      class: CommandLineTool
      cwlVersion: v1.0
      $namespaces:
        sbg: 'https://sevenbridges.com'
      id: admin/sbg-public-data/salmon-quant-reads-0-9-1/11
      baseCommand:
        - tar
      inputs:
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: no_effective_length_correction
          type: boolean?
          inputBinding:
            position: 24
            prefix: '--noEffectiveLengthCorrection'
            shellQuote: false
          label: No effective length correction
          doc: >-
            Disables effective lenght correction when computing the probability
            that a fragment was generated from a transcript. If this flag is
            passed in, the fragment lenght distribution is not taken into
            account when computing this probability.
        - 'sbg:altPrefix': '--quasiCoverage'
          'sbg:category': Advanced options
          'sbg:toolDefaultValue': '0'
          id: quasi_coverage
          type: float?
          inputBinding:
            position: 44
            prefix: '-x'
            shellQuote: false
          label: Quasi coverage
          doc: >-
            The fraction of the read that must be covered by MMPs (of length >=
            31) if this read is to be considered as 'mapped'. This may help to
            avoid 'spurious' mappings. A value of 0 (the default) denotes no
            coverage threshold (a single 31-mer can yield a mapping). Since
            coverage by exact matching, large, MMPs is a rather strict
            condition, this value should likely be set to something low, if
            used. This value is expressed as a number between 0 and 1; a larger
            value is more stringent and less likely to allow spurios mappings,
            but can reduce sensitivity (EXPERIMENTAL).
        - default: A
          'sbg:category': Basic options
          'sbg:toolDefaultValue': A
          id: lib_type
          type: string?
          inputBinding:
            position: 6
            prefix: '-l'
            shellQuote: false
          label: Library type
          doc: >-
            Format string describing the library type. As of version 0.7.0,
            Salmon also has the ability to automatically infer (i.e. guess) the
            library type based on how the first few thousand reads map to the
            transcriptome. To allow Salmon to automatically infer the library
            type, simply provide the letter 'A' as an input to this parameter
            (also the default behaviour). Otherwise, the input string should be
            in the format of maximum three uppercase letters ('SSS'). The first
            part of the library string (relative orientation) is only provided
            if the library is paired-end. The possible options are: I=inward,
            O=outword, M=matching. The second part of the read library string
            specifies whether the protocol is stranded or unstranded; the
            options are: S=stranded, U=unstranded. If the protocol is
            unstranded, then we’re done. The final part of the library string
            specifies the strand from which the read originates in a
            strand-specific protocol — it is only provided if the library is
            stranded (i.e. if the library format string is of the form S). The
            possible values are: F=read 1 (or single-end read) comes from the
            forward strand, R=read 1 (or single-end read) comes from the reverse
            strand. Examples: IU, SF, OSR.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '200'
          id: fld_mean
          type: int?
          inputBinding:
            position: 19
            prefix: '--fldMean'
            shellQuote: false
          label: Mean fragment length
          doc: The mean used in the fragment lenght distribution prior.
        - 'sbg:altPrefix': '--dumpEqWeights'
          'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'Off'
          id: dump_eq_weights
          type: boolean?
          inputBinding:
            position: 42
            prefix: '-d'
            shellQuote: false
          label: Dump equivalence class weights
          doc: >-
            Includes 'rich' equivalence class weights in the output when
            equivalence class information is being dumpes to file.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '0.001'
          id: vb_prior
          type: float?
          inputBinding:
            position: 31
            prefix: '--vbPrior'
            shellQuote: false
          label: VBEM prior
          doc: >-
            The prior that will be used VBEM algorithm. This is interpreted as a
            per-nucleotide prior, unlees the --perTranscriptPrior flag is also
            given, in which case this is used as a transcript-level prior.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '0'
          id: num_gibbs_samples
          type: int?
          inputBinding:
            position: 33
            prefix: '--numGibbsSamples'
            shellQuote: false
          label: Number of Gibbs samples
          doc: The number of Gibbs sampling rounds to perform.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: consistent_hits
          type: boolean?
          inputBinding:
            position: 14
            prefix: '-c'
            shellQuote: false
          label: Consistent hits
          doc: >-
            Force hits gathered during quasi-mapping to be "consistent" (i.e.
            co-linear and approximately the right distance apart).
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '1'
          id: bias_speed_samp
          type: int?
          inputBinding:
            position: 17
            prefix: '--biasSpeedSamp'
            shellQuote: false
          label: Bias speed sample
          doc: >-
            The value at which the fragment length PMF is down-sampled when
            evaluating sequence-specific and & GC fragment bias. Larger values
            speed up effective length correction, but may decrease the fidelity
            of bias modeling results.
        - 'sbg:category': Basic options
          'sbg:toolDefaultValue': 'Off'
          id: discard_orphans_quasi
          type: boolean?
          inputBinding:
            position: 9
            prefix: '--discardOrphansQuasi'
            shellQuote: false
          label: Discard orphans in Quasi-mapping mode
          doc: >-
            Quasi-mapping mode only: Discard orphans mapping in quasi-mapping
            mode. If this flag is passed then only paired mappings will be
            considered towards quantification estimates. The default behaviour
            is to consider orphan mappings if no valid paired mappings exist.
            This flag is independent of the option to write the oprhaned
            mappings to file (--writeOprhanLinks).
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '1000000'
          id: num_pre_aux_model_samples
          type: int?
          inputBinding:
            position: 29
            prefix: '--numPreAuxModelSamples'
            shellQuote: false
          label: Number of pre auxiliary model samples
          doc: >-
            The first this many samples will have their assignment likelihoods
            and contributions to the transcript abundances computed without
            applying any auxiliary models. The purpose of ignoring the auxiliary
            models for the first that many observations is to avoid applying
            these models before their parameters have been learned sufficiently
            well.
        - format: 'GTF,GFF,GFF3'
          'sbg:category': Inputs
          id: gene_map
          type: File?
          inputBinding:
            position: 13
            prefix: '-g'
            shellQuote: false
          label: Gene map
          doc: >-
            File containing a mapping of transcripts to genes.  If this file is
            provided Salmon will output both quant.sf and quant.genes.sf files,
            where the latter contains aggregated gene-level abundance
            estimates.  The transcript to gene mapping should be provided as
            either a GTF file, or a in a simple tab-delimited format where each
            line contains the name of a transcript and the gene to which it
            belongs separated by a tab.  The extension of the file is used to
            determine how the file should be parsed.  Files ending in '.gtf’,
            ‘.gff’ or '.gff3’ are assumed to be in GTF format; files with any
            other extension are assumed to be in the simple format. In GTF/GFF
            format, the ‘transcript_id’ is assumed to contain the transcript
            identifier and the ‘gene_id’ is assumed to contain the corresponding
            gene identifier.
        - 'sbg:category': Basic options
          'sbg:toolDefaultValue': 'off'
          id: write_mappings
          type: boolean?
          inputBinding:
            position: 39
            separate: false
            shellQuote: false
            valueFrom: |-
              ${
                  if (inputs.write_mappings) {
                      function sharedStart(array) {
                          var A = array.concat().sort(),
                              a1 = A[0],
                              a2 = A[A.length - 1],
                              L = a1.length,
                              i = 0;
                          while (i < L && a1.charAt(i) === a2.charAt(i)) i++;
                          return a1.substring(0, i);
                      }

                      if (inputs.read_files) {
                          arr = [].concat(inputs.read_files)
                          path_list = []
                          arr.forEach(function(f) {
                              return path_list.push(f.path.replace(/\\/g, '/').replace(/.*\//, ''))
                          })
                          common_prefix = sharedStart(path_list)
                          var x = common_prefix.replace(/\-$|\_$|\.$/, '')
                          return "--writeMappings=" + x + "_salmon_quant/" + x + ".salmon_quant_mapping_info.sam"
                      }
                  }
              }
          label: Write mappings
          doc: >-
            If this options is provided, then the quasi-mapping
            results/information will be written out in SAM-compatible format.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '0'
          id: num_bootstraps
          type: int?
          inputBinding:
            position: 34
            prefix: '--numBootstraps'
            shellQuote: false
          label: Number of bootstraps
          doc: >-
            The number of bootstrap samples to generate. Note: this is mutually
            exclusive with Gibbs sampling.
        - 'sbg:category': Basic options
          'sbg:toolDefaultValue': 'Off'
          id: meta
          type: boolean?
          inputBinding:
            position: 41
            prefix: '--meta'
            shellQuote: false
          label: Meta
          doc: >-
            If you're using Salmon on a metagenomic dataset, consider setting
            this flag to disable parts of the abundance estimation model that
            make less sense for metagenomic data.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '100'
          id: max_read_occ
          type: int?
          inputBinding:
            position: 23
            prefix: '-w'
            shellQuote: false
          label: Maximum read occurence
          doc: Reads "mapping" to more than this many places won't be considered.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '10'
          id: min_assigned_frags
          type: int?
          inputBinding:
            position: 46
            prefix: '--minAssignedFrags'
            shellQuote: false
          label: Minimum assigned fragments
          doc: >-
            The minimum number of fragments that must be assigned to the
            transcriptome.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '1000'
          id: fld_max
          type: int?
          inputBinding:
            position: 18
            prefix: '--fldMax'
            shellQuote: false
          label: Maximum fragment length
          doc: >-
            The maximum fragment length to consider when building the empirical
            distribution.
        - format: TAR
          'sbg:category': Inputs
          id: salmon_index_archive
          type: File
          label: Salmon index archive
          doc: Archive outputed by Salmon Index tool.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '0'
          id: range_factorization_bins
          type: int?
          inputBinding:
            position: 49
            prefix: '--rangeFactorizationBins'
            shellQuote: false
          label: Range factorization bins
          doc: >-
            Factorizes the likelihood used in quantification by addopting a new
            notion of equivalence classes based on the coniditonal probabilities
            with which fragments are generated from different transcripts. This
            is a more fine-grained factorization than the normal rich
            equivalence classes. The default value (0) corresponds to the
            standard rich equivalence classes and larger values imply a more
            fine-grained factorization. If range factorization is enabled, a
            common value to select for this parameter is 4.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'Off'
          id: faster_mapping
          type: boolean?
          inputBinding:
            position: 48
            prefix: '--fasterMapping'
            shellQuote: false
          label: Faster mapping
          doc: >-
            [Developer]: Disables some extra checks during quasi-mapping. This
            may make mapping a little bit faster at the potential cost of
            returning too many mappings (i.e. some suboptimal mappings) for
            certain reads.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: per_transcript_prior
          type: boolean?
          inputBinding:
            position: 30
            prefix: '--perTranscriptPrior'
            shellQuote: false
          label: Per transcript prior
          doc: >-
            The prior (either the default, or the argument provided via
            --vbPrior) will be interpreted as a transcript-level prior (i.e.
            each transcript will be given a prior read count of this value).
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: write_unmapped_names
          type: boolean?
          inputBinding:
            position: 35
            prefix: '--writeUnmappedNames'
            shellQuote: false
          label: Write unmapped names
          doc: >-
            Write the names of unmapped reads to the file unmapped.txt in the
            auxiliary directory.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'Off'
          id: dump_eq
          type: boolean?
          inputBinding:
            position: 15
            prefix: '--dumpEq'
            shellQuote: false
          label: Dump equivalence class counts
          doc: >-
            Dump the equivalence class counts that were computed during
            quasi-mapping.
        - format: FASTQ
          'sbg:category': Inputs
          id: read_files
          type: 'File[]'
          inputBinding:
            position: 7
            itemSeparator: ' '
            shellQuote: false
            valueFrom: |-
              ${
                  function get_meta_map(m, file, meta) {
                      if (meta in file.metadata) {
                          return m[file.metadata[meta]]
                      } else {
                          return m['Undefined']
                      }
                  }

                  function create_new_map(map, file, meta) {
                      if (meta in file.metadata) {
                          map[file.metadata[meta]] = {}
                          return map[file.metadata[meta]]
                      } else {
                          map['Undefined'] = {}
                          return map['Undefined']
                      }
                  }

                  arr = [].concat(inputs.read_files)
                  map = {}

                  if (arr.length == 1) {
                      return "-r " + arr[0].path
                  }

                  for (i in arr) {

                      sm_map = get_meta_map(map, arr[i], 'sample_id')
                      if (!sm_map) sm_map = create_new_map(map, arr[i], 'sample_id')

                      lb_map = get_meta_map(sm_map, arr[i], 'library_id')
                      if (!lb_map) lb_map = create_new_map(sm_map, arr[i], 'library_id')

                      pu_map = get_meta_map(lb_map, arr[i], 'platform_unit_id')
                      if (!pu_map) pu_map = create_new_map(lb_map, arr[i], 'platform_unit_id')

                      if ('file_segment_number' in arr[i].metadata) {
                          if (pu_map[arr[i].metadata['file_segment_number']]) {
                              a = pu_map[arr[i].metadata['file_segment_number']]
                              ar = [].concat(a)
                              ar = ar.concat(arr[i])
                              pu_map[arr[i].metadata['file_segment_number']] = ar
                          } else pu_map[arr[i].metadata['file_segment_number']] = [].concat(arr[i])
                      } else {
                          if (pu_map['Undefined']) {
                              a = pu_map['Undefined']
                              ar = [].concat(a)
                              ar = ar.concat(arr[i])
                              pu_map['Undefined'] = ar
                          } else {
                              pu_map['Undefined'] = [].concat(arr[i])
                          }
                      }
                  }
                  tuple_list = []
                  for (sm in map)
                      for (lb in map[sm])
                          for (pu in map[sm][lb]) {
                              list = []
                              for (fsm in map[sm][lb][pu]) {
                                  list = map[sm][lb][pu][fsm]
                                  tuple_list.push(list)
                              }
                          }
                  //return tuple_list[0][0].path

                  pe_1 = []
                  pe_2 = []
                  se = []
                  if (tuple_list[0].length == 1) {
                      for (i = 0; i < tuple_list.length; i++) {
                          se = se.concat(tuple_list[i][0].path)
                      }
                  }
                  for (i = 0; i < tuple_list.length; i++) {
                      for (j = 0; j < tuple_list[i].length; j++) {
                          if (tuple_list[i][j].metadata.paired_end == 1) {
                              pe_1 = pe_1.concat(tuple_list[i][j].path)
                          } else if (tuple_list[i][j].metadata.paired_end == 2) {
                              pe_2 = pe_2.concat(tuple_list[i][j].path)
                          }
                      }
                  }


                  if (pe_2.length == 0) {
                      cmd = ""
                      if (se.length > 0) {
                          tmp = se
                      } else if (pe_1.length > 0) {
                          tmp = pe_1
                      }
                      for (i = 0; i < tmp.length; i++) {
                          cmd += tmp[i] + " "
                      }
                      return "-r " + cmd
                  } else if (pe_2.length > 0) {
                      cmd1 = ""
                      cmd2 = ""
                      for (i = 0; i < pe_1.length; i++) {
                          cmd1 += pe_1[i] + " "
                          cmd2 += pe_2[i] + " "
                      }
                      return "-1 " + cmd1 + " -2 " + cmd2
                  } else {
                      return ""
                  }

              }
          label: FASTQ Read files
          doc: Input FASTQ read files.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: init_uniform
          type: boolean?
          inputBinding:
            position: 22
            prefix: '--initUniform'
            shellQuote: false
          label: Initialize uniform parameters
          doc: >-
            Initialize the offline inference with uniform parameters, rather
            than seeding with online parameters.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: no_bias_length_threshold
          type: boolean?
          inputBinding:
            position: 26
            prefix: '--noBiasLengthThreshold'
            shellQuote: false
          label: No bias length threshold
          doc: >-
            [Experimental] If this option is enabled, then no (lower) threshold
            will be set on how short bias correction can make effective lengths.
            This can increase precision of bias correction, but harm robustness.
            The default correction applies a threshold.
        - 'sbg:category': Basic options
          'sbg:toolDefaultValue': '9.9999999999999995e-21'
          id: incompatible_prior
          type: float?
          inputBinding:
            position: 12
            prefix: '--incompatPrior'
            shellQuote: false
          label: Incompatible prior probability
          doc: >-
            This option sets the prior probability that an alignment that
            disagrees with the specified library type (--libType) results from
            the true fragment origin. Setting this to 0 specifies that
            alignments that disagree with the library type should be
            "impossible", while setting it to 1 says that alignments that
            disagree with the library type are no less likely than those that
            do.
        - 'sbg:category': Basic options
          'sbg:toolDefaultValue': 'off'
          id: allow_orphans_fmd
          type: boolean?
          inputBinding:
            position: 9
            prefix: '--allowOrphansFMD'
            shellQuote: false
          label: Allow orphans in FMD mode
          doc: >-
            FMD-mapping mode only: Consider orphaned reads as valid hits when
            performing lightweight-alignment. This option will increase
            sensitivity (allow more reads to map and more transcripts to be
            detected), but may decrease specificity as orphaned alignments are
            more likely to be spurious.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '200'
          id: max_occ
          type: int?
          inputBinding:
            position: 22
            prefix: '-m'
            shellQuote: false
          label: Maximum (S)MEM occurance
          doc: (S)MEMs occuring more than this many times won't be considered.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: use_vbopt
          type: boolean?
          inputBinding:
            position: 32
            prefix: '--useVBOpt'
            shellQuote: false
          label: Use Variational Bayesian optimization
          doc: >-
            Use the Variational Bayesian EM rather than the traditional EM
            algorithm for optimization in the batch passes.
        - 'sbg:category': Basic options
          'sbg:toolDefaultValue': 'off'
          id: gc_bias
          type: boolean?
          inputBinding:
            position: 11
            prefix: '--gcBias'
            shellQuote: false
          label: GC bias correction
          doc: '[Biasl] Perform fragment GC bias correction.'
        - 'sbg:category': Basic options
          'sbg:toolDefaultValue': 'Off'
          id: pos_bias
          type: boolean?
          inputBinding:
            position: 50
            prefix: '--posBias'
            shellQuote: false
          label: Position bias
          doc: >-
            Enable modeling of a position-specific fragment start distribution.
            This is meant to model non-uniform coverage biases that are
            sometimes present in RNA-seq data (e.g. 5' or 3' positional bias).
            Currently, a small and fixed number of models are learned for
            different length classes of transcripts.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '5000000'
          id: num_aux_model_samples
          type: int?
          inputBinding:
            position: 28
            prefix: '--numAuxModelSamples'
            shellQuote: false
          label: Number of auxiliary model samples
          doc: >-
            The first this many numbers are used to train the auxiliary model
            parameters (e.g. fragment length distribution, bias, etc.). After
            their first that many observations, the auxiliary model parameters
            will be assumed to have converged and will be fixed.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: no_fragment_length_distribution
          type: boolean?
          inputBinding:
            position: 25
            prefix: '--noFragLengthDist'
            shellQuote: false
          label: No fragment length distribution
          doc: >-
            [Experimental] Do not consider concordance with the learned fragment
            lenght distribution when trying to determine the probability that a
            fragment has originated from a specific location. Normally,
            fragments with unlikely lengths will be assigned a smaller relative
            probability than those with more likely lenghts. When this flag is
            passed in, the observed fragment length has no effect on that
            fragment's a priori probability.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '2000000'
          id: num_bias_samples
          type: int?
          inputBinding:
            position: 27
            prefix: '--numBiasSamples'
            shellQuote: false
          label: Number of bias samples
          doc: >-
            Number of fragment mappings to use when learning the
            sequence-specific bias model.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'Off'
          id: reduce_GC_memory
          type: boolean?
          inputBinding:
            position: 47
            prefix: '--reduceGCMemory'
            shellQuote: false
          label: Reduce GC memory
          doc: >-
            If this option is selected, a more memory efficient (but slightly
            slower) representation is used to compute fragment GC content.
            Enabling this will reduce memory usage, but can also reduce speed.
            However, the results themselves will remain the same.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '16'
          id: thinning_factor
          type: int?
          inputBinding:
            position: 40
            prefix: '--thinningFactor'
            shellQuote: false
          label: Thinning factor
          doc: >-
            Number of steps to discard for every sample kept from the Gibbs
            chain. The larger this number, the less chance that subsequent
            samples are auto-correlated, but the slower sampling becomes.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '1'
          id: gc_size_samp
          type: int?
          inputBinding:
            position: 16
            prefix: '--gcSizeSamp'
            shellQuote: false
          label: GC size sample
          doc: >-
            The value by which to downsample transcripts when representing the
            GC content. Larger values will reduce memory usage, but may decrease
            the fidelity of bias modeling results.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'off'
          id: strict_intersect
          type: boolean?
          inputBinding:
            position: 17
            prefix: '--strictIntersect'
            shellQuote: false
          label: Strict intersect
          doc: >-
            Modifies how orphans are assigned. When this flag is set, if the
            intersection of the quasi-mapping for the left and right is empty,
            then all mappings for the left and all mappings for the right read
            are reported as orphan quasi-mappings.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '80'
          id: fld_sd
          type: int?
          inputBinding:
            position: 20
            prefix: '--fldSD'
            shellQuote: false
          label: Fragment length standard deviation
          doc: >-
            The standard deviation used in the fragment length distribution
            prior.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': '0.65000000000000002'
          id: forgetting_factor
          type: float?
          inputBinding:
            position: 21
            prefix: '-f'
            shellQuote: false
          label: Forgetting factor
          doc: >-
            The forgetting factor used in the online learning schedule. A
            smaller value results in quicker learning, but higher variance and
            may be unstable. A larger value results in slower learning but may
            be more stable. The input value should be in the interva (0.5, 1.0].
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'Off'
          id: alternative_init_mode
          type: boolean?
          inputBinding:
            position: 45
            prefix: '--alternativeInitMode'
            shellQuote: false
          label: Alternative initialization mode
          doc: >-
            Use an alternative strategy (rather than simple interpolation)
            between the online and uniform abundance estimates to initialize the
            EM/VBEM algorithm.
        - 'sbg:category': Basic options
          'sbg:toolDefaultValue': 'off'
          id: seq_bias
          type: boolean?
          inputBinding:
            position: 10
            prefix: '--seqBias'
            shellQuote: false
          label: Sequence-specific bias correction
          doc: Perform sequence-specific bias correction.
        - 'sbg:category': Advanced options
          'sbg:toolDefaultValue': 'Off'
          id: no_length_correction
          type: boolean?
          inputBinding:
            position: 43
            prefix: '--noLengthCorrection'
            shellQuote: false
          label: No length correction
          doc: >-
            Entirely disables length correction when estimating abundance of
            transcripts. This option can be used with protocols where one
            expects that fragments derive from their underlying targets without
            regard to that target's length, e.g. QuantSeq (EXPERIMENTAL).
        - default: 8
          'sbg:category': Basic options
          'sbg:includeInPorts': true
          'sbg:toolDefaultValue': '8'
          id: threads
          type: int?
          inputBinding:
            position: 37
            prefix: '-p'
            shellQuote: false
          label: Number of threads
          doc: Number of threads to be used.
      outputs:
        - id: eq_classes
          doc: >-
            A file that contains the equivalence classes and corresponding
            counts that were computed during quasi-mapping.
          label: Equivalent class counts
          type: File?
          outputBinding:
            glob: |-
              ${
                  if (inputs.read_files) {
                      var arr = [].concat(inputs.read_files)
                      if (arr[0].metadata && arr[0].metadata.sample_id) {
                          var basename = arr[0].metadata.sample_id
                      } else {
                          var basename = arr[0].path.split('/').pop().split('.')[0]
                      }
                      x = basename + ".salmon_quant"
                      return x + "/aux_info/" + x + ".eq_classes.txt"
                  }
              }
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.read_files)

              }
          format: TXT
        - id: mapping_info
          doc: >-
            Information about the quasi-mappings Salmon Quant uses for
            quantification.
          label: Mapping info
          type: File?
          outputBinding:
            glob: |-
              ${
                  if (inputs.read_files) {
                      var arr = [].concat(inputs.read_files)
                      if (arr[0].metadata && arr[0].metadata.sample_id) {
                          var basename = arr[0].metadata.sample_id
                      } else {
                          var basename = arr[0].path.split('/').pop().split('.')[0]
                      }
                      x = basename + ".salmon_quant"
                      return x + "_salmon_quant/" + x + ".salmon_quant_mapping_info.sam"
                  }
              }
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.read_files)

              }
          format: SAM
        - id: bootstrap_data
          doc: >-
            A TAR bundle containing the bootstrap folder, if bootstrapping was
            performed.
          label: Bootstrap data
          type: File?
          outputBinding:
            glob: '*salmon_quant_bootstrap_folder.tar'
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.read_files)

              }
          format: TAR
        - id: unmapped_reads
          doc: >-
            File with the names of reads (or mates in paired-end reads) that do
            not map to the transcriptome.
          label: Unmapped reads
          type: File?
          outputBinding:
            glob: |-
              ${
                  if (inputs.read_files) {
                      var arr = [].concat(inputs.read_files)
                      if (arr[0].metadata && arr[0].metadata.sample_id) {
                          var basename = arr[0].metadata.sample_id
                      } else {
                          var basename = arr[0].path.split('/').pop().split('.')[0]
                      }
                      x = basename + ".salmon_quant"
                      return x + "/aux_info/" + x + ".unmapped_names.txt"
                  }
              }
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.read_files)

              }
          format: TXT
        - id: quant_genes_sf
          doc: File containing aggregated gene-level abundance estimates.
          label: Gene-level quantification file
          type: File?
          outputBinding:
            glob: |-
              ${
                  if (inputs.read_files) {
                      var arr = [].concat(inputs.read_files)
                      if (arr[0].metadata && arr[0].metadata.sample_id) {
                          var basename = arr[0].metadata.sample_id
                      } else {
                          var basename = arr[0].path.split('/').pop().split('.')[0]
                      }
                      x = basename + ".salmon_quant"
                      return x + "/" + x + ".genes.sf"
                  }
              }
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.read_files)

              }
          format: SF
        - id: salmon_quant_archive
          doc: >-
            All files outputed by Salmon Quant tool. Contains quantification
            files.
          label: Salmon Quant archive
          type: File?
          outputBinding:
            glob: '*salmon_quant_archive.tar'
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.read_files)

              }
          format: TAR
        - id: quant_sf
          doc: 'Salmon Quant output file, containing quantification results.'
          label: Quantification file
          type: File?
          outputBinding:
            glob: |-
              ${
                  if (inputs.read_files) {
                      var arr = [].concat(inputs.read_files)
                      if (arr[0].metadata && arr[0].metadata.sample_id) {
                          var basename = arr[0].metadata.sample_id
                      } else {
                          var basename = arr[0].path.split('/').pop().split('.')[0]
                      }
                      x = basename + ".salmon_quant"
                      return x + "/" + x + ".sf"
                  }
              }
            outputEval: |-
              ${
                  return inheritMetadata(self, inputs.read_files)

              }
          format: SF
      doc: >-
        **Salmon Quant - Reads** infers transcript abundance estimates from
        **RNA-seq data**, using a process called **quasi-mapping**. 


        **Quasi-mapping** is a process of assigning reads to transcripts,
        without doing the exact base-to-base alignment. Seeing that for
        estimating transcript abundances, the main information needed is which
        transcript a read originates from and not the actual mapping
        coordinates, the idea with the **Salmon** tool was to implement a
        procedure that does exactly that [1, 2]. 


        The result is a software running at speeds orders of magnitude faster
        than other tools which utilize the full likehood model, while keeping
        near-optimal probabilistic RNA-seq quantification results [1, 2]. 


        The latest version of Salmon (0.9.x) introduces some novel concepts,
        like **Rich Factorization Classes**, which further increase the
        precision of the results, at a very negligible increase in runtime. This
        version of Salmon also supports quantification from already aligned BAM
        files, utilizing the full likelihood model (the same one as in RSEM),
        where the results are the same as RSEM, but the execution time is much
        shorter than in RSEM, this time due to engineering only [3].


        *A list of **all inputs and parameters** with corresponding descriptions
        can be found at the bottom of the page.*


        ### Common Use Cases


        - The main input to the tool are **FASTQ read files** (single end or
        paired end). 

        - A **Salmon index archive** (`-i`) also needs to be provided, in
        addition to an optional **Gene map** (`--geneMap`) file (which should be
        of the same annotations that were used in generating the **Transcriptome
        FASTA file**) if gene-level abundance results are desired. 

        - The tool will generate transcript abundance estimates in plaintext
        format, and an optional file containing gene abundance estimates, if the
        input **Gene map** (`--gene-map`) file is provided. 

        - In addition to the default output (**Quantification file**),
        additional outputs can be produced if the proper options are turned on
        for them (e.g. **Equivalent class counts** by setting `--dumpEq`,
        **Unmapped reads** by setting `--writeUnmappedNames`, **Bootstrap data**
        by setting `--numBootstraps` or `--numGibbsSamples`, **Mapping info** by
        setting `--write-mappings`...).

        - The **GC bias correction** option (`--gcBias`) will correct for GC
        bias and improve quantification accuracy, but at the cost of increased
        runtime (a rough estimate would be a **double** increase in runtime per
        sample).  

        - The use of *data-driven likelihood factorization* is achieved with the
        **Range factorization bins** parameter (`--rangeFactorizationBins`) and
        can be used to bring an increase in accuracy at a very small increase in
        runtime [3]. 


        ### Changes Introduced by Seven Bridges


        - All output files will be prefixed by the input sample ID (inferred
        from **Sample ID** metadata if existent, or from filename otherwise),
        instead of having identical names between runs. 


        ### Common Issues and Important Notes


        - For paired-end read files, it is important to properly set the
        **Paired End** metadata field on your read files.

        - For FASTQ reads in multi-file format (i.e. two FASTQ files for
        paired-end 1 and two FASTQ files for paired-end2), the proper metadata
        needs to be set (the following hierarchy is valid: **Sample ID/Library
        ID/Platform Unit ID/File Segment Number)**.

        - The GTF and FASTA files need to have compatible transcript IDs. 


        ### Performance Benchmarking


        The main advantage of the Salmon software is that it is not
        computationally challenging, as alignment in the traditional sense is
        not performed. 

        Below is a table describing the runtimes and task costs for a couple of
        samples with different file sizes:


        | Experiment type |  Input size | Paired-end | # of reads | Read length
        | Duration |  Cost |  Instance (AWS) |

        |:---------------:|:-----------:|:----------:|:----------:|:-----------:|:--------:|:-----:|:----------:|

        |     RNA-Seq     |  2 x 4.5 GB |     Yes    |     20M     |     101    
        |   5min   | $0.05| c4.2xlarge |

        |     RNA-Seq     | 2 x 17.4 GB |     Yes    |     76M     |     101    
        |   15min  | $0.15 | c4.2xlarge |


        *Cost can be significantly reduced by using **spot instances**. Visit
        the [Knowledge
        Center](https://docs.sevenbridges.com/docs/about-spot-instances) for
        more details.*


        ### References


        [1] [Salmon
        paper](biorxiv.org/content/biorxiv/early/2016/08/30/021592.full.pdf)   

        [2] [Rapmap
        paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4908361/)   

        [3] [Data-driven likelihood
        factorization](https://academic.oup.com/bioinformatics/article/33/14/i142/3953977)
      label: Salmon Quant - Reads
      arguments:
        - position: 1
          separate: false
          shellQuote: false
          valueFrom: '-xf'
        - position: 2
          separate: false
          shellQuote: false
          valueFrom: |-
            ${
                var str = [].concat(inputs.salmon_index_archive)[0].path.split("/").pop();
                return str

            }
        - position: 3
          separate: false
          shellQuote: false
          valueFrom: '&&'
        - position: 4
          separate: false
          shellQuote: false
          valueFrom: salmon
        - position: 5
          separate: false
          shellQuote: false
          valueFrom: quant
        - position: 5
          prefix: '-i'
          shellQuote: false
          valueFrom: |-
            ${
                return inputs.salmon_index_archive.metadata.index_name
            }
        - position: 99
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.read_files) {
                    var arr = [].concat(inputs.read_files)
                    if (arr[0].metadata && arr[0].metadata.sample_id) {
                        var basename = arr[0].metadata.sample_id
                    } else {
                        var basename = arr[0].path.split('/').pop().split('.')[0]
                    }
                    x = basename + ".salmon_quant"
                    return "&& tar -cf " + x + "_archive.tar " + x
                }
            }
        - position: 103
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.read_files) {
                    var arr = [].concat(inputs.read_files)
                    if (arr[0].metadata && arr[0].metadata.sample_id) {
                        var basename = arr[0].metadata.sample_id
                    } else {
                        var basename = arr[0].path.split('/').pop().split('.')[0]
                    }
                    x = basename + ".salmon_quant"
                    y = x + "/quant.sf"
                    z = x + "/" + x + ".sf"
                    return "&& mv " + y + " " + z
                }
            }
        - position: 36
          prefix: '-o'
          shellQuote: false
          valueFrom: |-
            ${
                var arr = [].concat(inputs.read_files)
                if (arr[0].metadata && arr[0].metadata.sample_id) {
                    var basename = arr[0].metadata.sample_id
                } else {
                    var basename = arr[0].path.split('/').pop().split('.')[0]
                }
                return basename + ".salmon_quant"
            }
        - position: 102
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.gene_map) {
                    var arr = [].concat(inputs.read_files)
                    if (arr[0].metadata && arr[0].metadata.sample_id) {
                        var basename = arr[0].metadata.sample_id
                    } else {
                        var basename = arr[0].path.split('/').pop().split('.')[0]
                    }
                    x = basename + ".salmon_quant"
                    y = x + "/quant.genes.sf"
                    z = x + "/" + x + ".genes.sf"
                    return "&& mv " + y + " " + z
                }
            }
        - position: 101
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.dump_eq) {
                    var arr = [].concat(inputs.read_files)
                    if (arr[0].metadata && arr[0].metadata.sample_id) {
                        var basename = arr[0].metadata.sample_id
                    } else {
                        var basename = arr[0].path.split('/').pop().split('.')[0]
                    }
                    x = basename + ".salmon_quant"
                    y = x + "/aux_info/eq_classes.txt"
                    z = x + "/aux_info/" + x + ".eq_classes.txt"
                    return "&& mv " + y + " " + z
                }
            }
        - position: 100
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.write_unmapped_names) {
                    var arr = [].concat(inputs.read_files)
                    if (arr[0].metadata && arr[0].metadata.sample_id) {
                        var basename = arr[0].metadata.sample_id
                    } else {
                        var basename = arr[0].path.split('/').pop().split('.')[0]
                    }
                    x = basename + ".salmon_quant"
                    y = x + "/aux_info/unmapped_names.txt"
                    z = x + "/aux_info/" + x + ".unmapped_names.txt"
                    return "&& mv " + y + " " + z
                }
            }
        - position: 38
          prefix: '--auxDir'
          shellQuote: false
          valueFrom: aux_info
        - position: 105
          shellQuote: false
          valueFrom: |-
            ${
                if (inputs.num_bootstraps || inputs.num_gibbs_samples) {
                    var arr = [].concat(inputs.read_files)
                    if (arr[0].metadata && arr[0].metadata.sample_id) {
                        var basename = arr[0].metadata.sample_id
                    } else {
                        var basename = arr[0].path.split('/').pop().split('.')[0]
                    }
                    x = basename + ".salmon_quant"
                    return "&& tar -cf " + x + "_bootstrap_folder.tar " + x + '/aux_info/bootstrap'
                }
            }
      requirements:
        - class: ShellCommandRequirement
        - class: ResourceRequirement
          ramMin: 7500
          coresMin: |-
            ${
                return inputs.threads ? inputs.threads : 8
            }
        - class: DockerRequirement
          dockerImageId: ea69041ddb8d42ee13362fe71f1149e5044edbd7cbf66ef4a1919f8736777007
          dockerPull: 'images.sbgenomics.com/uros_sipetic/salmon:0.9.1'
        - class: InitialWorkDirRequirement
          listing:
            - $(inputs.salmon_index_archive)
        - class: InlineJavascriptRequirement
          expressionLib:
            - |-
              var updateMetadata = function(file, key, value) {
                  file['metadata'][key] = value;
                  return file;
              };


              var setMetadata = function(file, metadata) {
                  if (!('metadata' in file))
                      file['metadata'] = metadata;
                  else {
                      for (var key in metadata) {
                          file['metadata'][key] = metadata[key];
                      }
                  }
                  return file
              };

              var inheritMetadata = function(o1, o2) {
                  var commonMetadata = {};
                  if (!Array.isArray(o2)) {
                      o2 = [o2]
                  }
                  for (var i = 0; i < o2.length; i++) {
                      var example = o2[i]['metadata'];
                      for (var key in example) {
                          if (i == 0)
                              commonMetadata[key] = example[key];
                          else {
                              if (!(commonMetadata[key] == example[key])) {
                                  delete commonMetadata[key]
                              }
                          }
                      }
                  }
                  if (!Array.isArray(o1)) {
                      o1 = setMetadata(o1, commonMetadata)
                  } else {
                      for (var i = 0; i < o1.length; i++) {
                          o1[i] = setMetadata(o1[i], commonMetadata)
                      }
                  }
                  return o1;
              };

              var toArray = function(file) {
                  return [].concat(file);
              };

              var groupBy = function(files, key) {
                  var groupedFiles = [];
                  var tempDict = {};
                  for (var i = 0; i < files.length; i++) {
                      var value = files[i]['metadata'][key];
                      if (value in tempDict)
                          tempDict[value].push(files[i]);
                      else tempDict[value] = [files[i]];
                  }
                  for (var key in tempDict) {
                      groupedFiles.push(tempDict[key]);
                  }
                  return groupedFiles;
              };

              var orderBy = function(files, key, order) {
                  var compareFunction = function(a, b) {
                      if (a['metadata'][key].constructor === Number) {
                          return a['metadata'][key] - b['metadata'][key];
                      } else {
                          var nameA = a['metadata'][key].toUpperCase();
                          var nameB = b['metadata'][key].toUpperCase();
                          if (nameA < nameB) {
                              return -1;
                          }
                          if (nameA > nameB) {
                              return 1;
                          }
                          return 0;
                      }
                  };

                  files = files.sort(compareFunction);
                  if (order == undefined || order == "asc")
                      return files;
                  else
                      return files.reverse();
              };
      'sbg:appVersion':
        - v1.0
      'sbg:categories':
        - RNA
        - Quantification
      'sbg:cmdPreview': >-
        tar -xf salmon_index_archive.tar.gz && salmon quant -i salmon_index  -r
        /path/to/sampleA_lane1_pe1.fastq -o sampleA_lane1_pe1.salmon_quant
        --auxDir aux_info  && tar -cf sampleA_lane1_pe1.salmon_quant_archive.tar
        sampleA_lane1_pe1.salmon_quant  && mv
        sampleA_lane1_pe1.salmon_quant/aux_info/unmapped_names.txt
        sampleA_lane1_pe1.salmon_quant/aux_info/sampleA_lane1_pe1.salmon_quant.unmapped_names.txt 
        && mv sampleA_lane1_pe1.salmon_quant/aux_info/eq_classes.txt
        sampleA_lane1_pe1.salmon_quant/aux_info/sampleA_lane1_pe1.salmon_quant.eq_classes.txt 
        && mv sampleA_lane1_pe1.salmon_quant/quant.genes.sf
        sampleA_lane1_pe1.salmon_quant/sampleA_lane1_pe1.salmon_quant.genes.sf 
        && mv sampleA_lane1_pe1.salmon_quant/quant.sf
        sampleA_lane1_pe1.salmon_quant/sampleA_lane1_pe1.salmon_quant.sf  && tar
        -cf sampleA_lane1_pe1.salmon_quant_bootstrap_folder.tar
        sampleA_lane1_pe1.salmon_quant/aux_info/bootstrap
      'sbg:contributors':
        - uros_sipetic
        - anamijalkovic
      'sbg:createdBy': uros_sipetic
      'sbg:id': admin/sbg-public-data/salmon-quant-reads-0-9-1/11
      'sbg:image_url': null
      'sbg:latestRevision': 11
      'sbg:license': GNU General Public License v3.0 only
      'sbg:links':
        - id: 'http://combine-lab.github.io/salmon/'
          label: Salmon Homepage
        - id: 'https://github.com/COMBINE-lab/salmon'
          label: Salmon Source Code
        - id: 'https://github.com/COMBINE-lab/salmon/releases/tag/v0.9.1'
          label: Salmon Download
        - id: 'http://biorxiv.org/content/early/2015/10/03/021592'
          label: Salmon Publications
        - id: 'http://salmon.readthedocs.org/en/latest/'
          label: Salmon Documentation
      'sbg:project': uros_sipetic/salmon-0-9-1-demo
      'sbg:publisher': sbg
      'sbg:revisionNotes': >-
        Output Salmon archive without renaming files inside (to comply with
        Sleuth).
      'sbg:sbgMaintained': false
      'sbg:toolAuthor': 'Rob Patro, Carl Kingsford, Steve Mount, Mohsen Zakeri'
      'sbg:toolkit': Salmon
      'sbg:toolkitVersion': 0.9.1
      'sbg:validationErrors': []
    label: Salmon Quant - Reads
    scatter:
      - read_files
    'sbg:x': 611.9122924804688
    'sbg:y': 356.1403503417969
hints:
  - class: 'sbg:AWSInstanceType'
    value: c4.8xlarge;ebs-gp2;1024
requirements:
  - class: ScatterFeatureRequirement
description: >-
  The **Salmon workflow** infers maximum likelihood estimates of transcript
  abundances from RNA-Seq data using a process called **Quasi-mapping**.


  **Quasi-mapping** is a process of assigning reads to transcripts without doing
  an exact base-to-base alignment. The **Salmon** tool implements a procedure
  geared towards knowing the transcript from which a read originates rather than
  the actual mapping coordinates, since the former is crucial to estimating
  transcript abundances [1, 2]. 


  The result is a software running at speeds orders of magnitude faster than
  other tools which utilize the full likelihood model while obtaining
  near-optimal probabilistic RNA-seq quantification results [1, 2, 3]. 


  The latest version of Salmon (0.9.x) introduces some novel concepts, like
  **Rich Factorization Classes**, which further increases the precision of the
  results, at a very negligible increase in runtime. This version of Salmon also
  supports quantification from already aligned BAM files, utilizing the full
  likelihood model (the same one as in RSEM), whereby the results are the same
  as RSEM but the execution time is much shorter than in RSEM, this time due
  only to engineering [3].


  *A list of **all inputs and parameters** with corresponding descriptions can
  be found at the bottom of this page.*


  ### Common Use Cases


  - The workflow consists of three steps: **Salmon Index**, **Salmon Quant**,
  and **Salmon Quantmerge**.

  - The main input to the workflow are **FASTQ read files** (single end or
  paired end). 

  - A **Transcriptome FASTA file** (`--transcripts`) also needs to be provided
  in addition to an optional **Gene map** (`--geneMap`) file (which should be of
  the same annotations that were used in generating the **Transcriptome FASTA
  file** - usually a GTF file can be provided here) if gene-level abundance
  results are desired. 

  - An already generated **Salmon index archive** can be provided to the
  **Salmon Index** tool (**Transcriptome FASTA or Salmon Index Archive** input)
  in order to skip indexing and save some time. 

  - The workflow will generate transcript abundance estimates in plaintext
  format (**Transcript Abundance Estimates**), and an optional file containing
  **Gene Abundance Estimates**, if the input **Gene map** (`--gene-map`) file is
  provided. 

  - In addition to the default output (**Quantification file**), additional
  outputs can be produced if the proper options are turned on for them (e.g.
  **Equivalent class counts** by setting `--dumpEq`, **Unmapped reads** by
  setting `--writeUnmappedNames`, **Bootstrap data** by setting
  `--numBootstraps` or `--numGibbsSamples`, **Mapping info** by setting
  `--write-mappings`...).

  - A **Transcript Expression Matrix** and a **Gene Expression Matrix** will be
  generated if more than one sample is provided. 

  - The **GC bias correction** option (`--gcBias`) will correct for GC bias and
  improve quantification accuracy but at the cost of increased runtime (a rough
  estimate would be a **double** increase in runtime per sample). 

  - The workflow is optimized to run in scatter mode. To run it successfully,
  just supply it with multiple samples (paired end or single end, with properly
  filled out **Sample ID** and **Paired End** metadata). 

  - The use of *data-driven likelihood factorization* is turned on with the
  **Range factorization bins** parameter (`--rangeFactorizationBins=4`) by
  default in this workflow, as it can bring an increase in accuracy at a very
  small increase in runtime [3]. 

  - The **Salmon Quant archive** output can be used for downstream differential
  expression analysis tools, like Sleuth. 


  ### Changes Introduced by Seven Bridges


  - All output files will be prefixed by the input sample ID (inferred from the
  **Sample ID** metadata if existent, of from filename otherwise), instead of
  having identical names between runs. 


  ### Common Issues and Important Notes


  - For paired-end read files, it is important to properly set the **Paired
  End** metadata field on your read files.

  - The input FASTA file (if provided instead of the already generated Salmon
  index archive) should be a transcriptome FASTA, not a genomic FASTA.

  - For FASTQ reads in multi-file format (i.e. two FASTQ files for paired-end 1
  and two FASTQ files for paired-end2), the proper metadata needs to be set (the
  following hierarchy is valid: **Sample ID/Library ID/Platform Unit ID/File
  Segment Number)**.

  - The GTF and FASTA files need to have compatible transcript IDs. 


  ### Performance Benchmarking


  The main advantage of the Salmon software is that it is not computationally
  challenging, as alignment in the traditional sense is not performed.
  Therefore, it is optimized to be run in scatter mode, so a c4.8xlarge instance
  (AWS) is used by default. 

  Below is a table describing the runtimes and task costs for a couple of
  samples with different file sizes:


  | Experiment type |  Input size | Paired-end | # of reads | Read length |
  Duration |  Cost |  Instance (AWS) |

  |:---------------:|:-----------:|:----------:|:----------:|:-----------:|:--------:|:-----:|:----------:|

  |     RNA-Seq     |  4 x 4.5 GB |     Yes    |     20M     |     101     |  
  16min   | $0.40| c4.8xlarge |

  |     RNA-Seq     | 2 x 17.4 GB, 2 x 19 GB |     Yes    |     76M & 84M   
  |     101     |   45min  | $1.20 | c4.8xlarge |


  *Cost can be significantly reduced by using **spot instances**. Visit the
  [Knowledge Center](https://docs.sevenbridges.com/docs/about-spot-instances)
  for more details.*


  ### API Python Implementation

  The workflow's draft task can also be submitted via the **API**. In order to
  learn how to get your **Authentication token** and **API endpoint** for
  corresponding platform visit our
  [documentation](https://github.com/sbg/sevenbridges-python#authentication-and-configuration).


  ```python

  from sevenbridges import Api


  # Enter api credentials

  authentication_token, api_endpoint = "enter_your_token", "enter_api_endpoint"

  api = Api(token=authentication_token, url=api_endpoint)


  # Get project_id/workflow_id from your address bar. Example:
  https://igor.sbgenomics.com/u/your_username/project/workflow

  project_id, workflow_id = "your_username/project",
  "your_username/project/workflow"


  # Get file names from files in your project. File names below are just as an
  example.

  inputs = {
          'reads': list(api.files.query(project=project_id, names=['sample_pe1.fq', 'sample_pe2.fq'])),
          'gtf': list(api.files.query(project=project_id, names=['gtf_file.gtf'])),
          'transcriptome_fasta_or_salmon_index_archive': list(api.files.query(project=project_id, names=['transcriptome_fasta_file.fa']))
          }

  # Run the task

  task = api.tasks.create(name='Salmon 0.9.1 workflow - API Example',
  project=project_id, app=workflow_id, inputs=inputs, run=True)

  ```

  Instructions for installing and configuring the API Python client, are
  provided on [github](https://github.com/sbg/sevenbridges-python#installation).
  For more information about using the API Python client, consult
  [sevenbridges-python
  documentation](http://sevenbridges-python.readthedocs.io/en/latest/). **More
  examples** are available [here](https://github.com/sbg/okAPI).


  Additionally, [API R](https://github.com/sbg/sevenbridges-r) and [API
  Java](https://github.com/sbg/sevenbridges-java) clients are available. To
  learn more about using these API clients please refer to the [API R client
  documentation](https://sbg.github.io/sevenbridges-r/), and [API Java client
  documentation](https://docs.sevenbridges.com/docs/java-library-quickstart).


  ### References


  [1] [Salmon
  paper](biorxiv.org/content/biorxiv/early/2016/08/30/021592.full.pdf)   

  [2] [Rapmap paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4908361/)   

  [3] [Data-driven likelihood
  factorization](https://academic.oup.com/bioinformatics/article/33/14/i142/3953977)
'sbg:appVersion':
  - v1.0
'sbg:canvas_x': -93
'sbg:canvas_y': 66
'sbg:canvas_zoom': 0.6999999999999997
'sbg:categories':
  - RNA
  - Quantification
  - CWL1.0
'sbg:content_hash': null
'sbg:contributors':
  - admin
'sbg:createdBy': admin
'sbg:createdOn': 1523623643
'sbg:expand_workflow': false
'sbg:id': admin/sbg-public-data/salmon-workflow-0-9-1-cwl-1-0/18
'sbg:image_url': >-
  https://igor.sbgenomics.com/ns/brood/images/admin/sbg-public-data/salmon-workflow-0-9-1-cwl-1-0/18.png
'sbg:latestRevision': 18
'sbg:license': GNU General Public License v3.0 only
'sbg:links':
  - id: 'http://combine-lab.github.io/salmon/'
    label: Salmon Homepage
  - id: 'https://github.com/COMBINE-lab/salmon'
    label: Salmon Source Code
  - id: 'https://github.com/COMBINE-lab/salmon/releases/tag/v0.9.1'
    label: Salmon Download
  - id: 'http://biorxiv.org/content/early/2015/10/03/021592'
    label: Salmon Publications
  - id: 'http://salmon.readthedocs.org/en/latest/'
    label: Salmon Documentation
'sbg:modifiedBy': admin
'sbg:modifiedOn': 1529412848
'sbg:project': admin/sbg-public-data
'sbg:projectName': SBG Public Data
'sbg:publisher': sbg
'sbg:revision': 18
'sbg:revisionNotes': Update mem requirements
'sbg:revisionsInfo':
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523623643
    'sbg:revision': 0
    'sbg:revisionNotes': >-
      Copy of
      uros_sipetic/salmon-kallisto-workflows-dev/salmon-workflow-0-8-0/24
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625824
    'sbg:revision': 1
    'sbg:revisionNotes': >-
      Copy of
      uros_sipetic/salmon-kallisto-workflows-dev/salmon-workflow-0-8-0/24
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625824
    'sbg:revision': 2
    'sbg:revisionNotes': >-
      Copy of
      uros_sipetic/salmon-kallisto-workflows-dev/salmon-workflow-0-8-0/25
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625824
    'sbg:revision': 3
    'sbg:revisionNotes': >-
      Copy of
      uros_sipetic/salmon-workflow-0-9-1-demo/salmon-workflow-0-9-1-cwl-1-0/0
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625824
    'sbg:revision': 4
    'sbg:revisionNotes': ''
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625824
    'sbg:revision': 5
    'sbg:revisionNotes': ''
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625824
    'sbg:revision': 6
    'sbg:revisionNotes': ''
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625825
    'sbg:revision': 7
    'sbg:revisionNotes': ''
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625825
    'sbg:revision': 8
    'sbg:revisionNotes': ''
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625825
    'sbg:revision': 9
    'sbg:revisionNotes': >-
      Copy of
      uros_sipetic/salmon-kallisto-workflows-dev/salmon-workflow-0-8-0/26
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625825
    'sbg:revision': 10
    'sbg:revisionNotes': Category CWL1.0 added
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523625825
    'sbg:revision': 11
    'sbg:revisionNotes': ''
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523636657
    'sbg:revision': 12
    'sbg:revisionNotes': Parameters
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523969026
    'sbg:revision': 13
    'sbg:revisionNotes': >-
      Update input and output descriptions and set default values on some
      parameters
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523992271
    'sbg:revision': 14
    'sbg:revisionNotes': >-
      Copy of
      uros_sipetic/salmon-kallisto-workflows-dev/salmon-workflow-0-8-0/26
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523992271
    'sbg:revision': 15
    'sbg:revisionNotes': >-
      Rewise to exposing parameters as ports, until missing descriptions bug is
      fixed
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1523992271
    'sbg:revision': 16
    'sbg:revisionNotes': >-
      Rewise to exposing parameters as ports, until missing descriptions and
      default params bug is fixed
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1524746254
    'sbg:revision': 17
    'sbg:revisionNotes': Add proper default values to the workflow.
  - 'sbg:modifiedBy': admin
    'sbg:modifiedOn': 1529412848
    'sbg:revision': 18
    'sbg:revisionNotes': Update mem requirements
'sbg:sbgMaintained': false
'sbg:toolAuthor': 'Rob Patro, Carl Kingsford, Steve Mount, Mohsen Zakeri'
'sbg:toolkit': Salmon
'sbg:toolkitVersion': 0.9.1
'sbg:validationErrors': []
