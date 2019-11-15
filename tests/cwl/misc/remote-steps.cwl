cwlVersion: v1.0

class: Workflow
label: WIP-DAPHNI DNA Pre-Processing

requirements:
  InlineJavascriptRequirement: {}
  MultipleInputFeatureRequirement: {}
  StepInputExpressionRequirement: {}

inputs:
  ForwardReads: File
  ReverseReads: File
  BWA-Index: File
  MaxThreads: int
  SampleID: string #normal or tumor
  KnownSiteVCF: File

steps:
  Alignment:
    run: https://gitlab.com/iidsgt/biocwl/raw/master/Tools/BWA/BWA-Mem.cwl
    in:
      InputFile: [ForwardReads, ReverseReads]
      Index: BWA-Index
      isMarkShortSplit:
        default: true
      RgLine:
        valueFrom: $("@RG\\tID:" + inputs.SampleID + "\\tSM:sample\\tLB:sample\\tPL:ILLUMINA\\tPU:0")
      VerboseLevel:
        default: 1
      Threads: MaxThreads

    out: [reads_stdout]

  ConvertSamToBam:
    run: https://gitlab.com/iidsgt/biocwl/raw/master/Tools/Samtools-View.cwl
    in:
      InputFile: Alignment/reads_stdout
      Format:
        valueFrom: |
          ${ return {"BAM": true}}
      Threads: MaxThreads

    out: [alignment]

  FixMateInformation:
    run: https://gitlab.com/iidsgt/biocwl/raw/master/Tools/GATK-FixMateInformation.cwl
    in:
      InputFile: ConvertSamToBam/alignment
      MaxRecordsRam:
        default: 2000000
      SortOrder:
        default: coordinate
      ValidationStringency:
        default: STRICT

    out: [alignment]

  MarkDuplicates:
    run: https://gitlab.com/iidsgt/biocwl/raw/master/Tools/GATK-MarkDuplicates.cwl
    in:
      InputFile: FixMateInformation/alignment

    out: [alignment, metrics]

  #BQSR:
  #  run: ../Tools/GATK-BQSRPipelineSpark.cwl
  #  in:
  #    InputFile: [MarkDuplicates/index]
  #    SparkMaster:
  #      source: MaxThreads
  #      valueFrom: $("local[" + self + "]")
  #    Reference: 2BitReference
  #    KnownSites: KnownSiteVCF
  #    isCreateBamIndex:
  #      default: true
  #  out:
  #    [index]

  BaseRecalibrator:
    run: https://gitlab.com/iidsgt/biocwl/raw/master/Tools/GATK-BaseRecalibrator.cwl
    in:
      InputFile: MarkDuplicates/alignment
      Reference: BWA-Index
      KnownSites: KnownSiteVCF
      isCreateBamIndex:
        default: false
    out: [table]

  ApplyBQSR:
    run: https://gitlab.com/iidsgt/biocwl/raw/master/Tools/GATK-ApplyBQSR.cwl
    in:
      InputFile: MarkDuplicates/alignment
      BaseRecalFile: BaseRecalibrator/table
      isCreateBamIndex:
        default: true
    out: [alignment, index]

outputs:
  Final_Bam:
    type: File
    outputSource: ApplyBQSR/alignment

  Final_Bam_Index:
    type: File
    outputSource: ApplyBQSR/index

  MarkDuplicates_Metrics:
    type: File
    outputSource: MarkDuplicates/metrics


