class: Workflow
cwlVersion: v1.0
id: kghose/benten-demo/wf3/1
label: wf3
$namespaces:
  sbg: 'https://sevenbridges.com'
inputs:
  - id: input
    type: File?
    'sbg:x': -306.39886474609375
    'sbg:y': -53
outputs:
  - id: output
    outputSource:
      - wf2/output
    type: File?
    'sbg:x': 182
    'sbg:y': -331.0932312011719
  - id: merge_out_1
    outputSource:
      - wf2/merge_out_1
    type: File?
    'sbg:x': 89
    'sbg:y': -234
  - id: merge_out
    outputSource:
      - wf2/merge_out
    type: File?
    'sbg:x': 172
    'sbg:y': -127
  - id: output_1
    outputSource:
      - wf1/output
    type: File?
    'sbg:x': 59
    'sbg:y': -15
  - id: merge_out_2
    outputSource:
      - wf1/merge_out
    type: File?
    'sbg:x': 56.60113525390625
    'sbg:y': 121.84903717041016
  - id: merge_out_3
    outputSource:
      - wf0/merge_out
    type: File?
    'sbg:x': 62.60113525390625
    'sbg:y': 240.8490447998047
steps:
  - id: wf0
    in:
      - id: input
        source: input
    out:
      - id: merge_out
    run:
      class: Workflow
      cwlVersion: v1.0
      id: kghose/benten-demo/wf0/1
      label: wf0
      $namespaces:
        sbg: 'https://sevenbridges.com'
      inputs:
        - id: input
          type: File?
          'sbg:x': -658.5054321289062
          'sbg:y': -34
      outputs:
        - id: merge_out
          outputSource:
            - merge/merge_out
          type: File?
          'sbg:x': -162
          'sbg:y': -35
      steps:
        - id: split
          in:
            - id: input
              source: input
          out:
            - id: output
          run:
            class: CommandLineTool
            cwlVersion: v1.0
            $namespaces:
              sbg: 'https://sevenbridges.com'
            id: kghose/benten-demo/split/0
            baseCommand:
              - split
            inputs:
              - id: input
                type: File?
                inputBinding:
                  position: 0
            outputs:
              - id: output
                type: 'File[]?'
                outputBinding:
                  glob: out-*
            label: split
            arguments:
              - position: 0
                prefix: '-l'
                valueFrom: '1'
              - position: 100
                prefix: ''
                valueFrom: out-
            requirements:
              - class: DockerRequirement
                dockerPull: alpine
            'sbg:appVersion':
              - v1.0
            'sbg:id': kghose/benten-demo/split/0
            'sbg:revision': 0
            'sbg:revisionNotes': null
            'sbg:modifiedOn': 1549637768
            'sbg:modifiedBy': kghose
            'sbg:createdOn': 1549637768
            'sbg:createdBy': kghose
            'sbg:project': kghose/benten-demo
            'sbg:projectName': Benten Demo
            'sbg:sbgMaintained': false
            'sbg:validationErrors': []
            'sbg:contributors':
              - kghose
            'sbg:latestRevision': 0
            'sbg:revisionsInfo':
              - 'sbg:revision': 0
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549637768
                'sbg:revisionNotes': null
            'sbg:image_url': null
            'sbg:publisher': sbg
            'sbg:content_hash': aa38db7a720e5140a5cebcab1cf2040da92fb709685d5131ff3bdecb7b078f78c
          label: split
          'sbg:x': -527
          'sbg:y': -35
        - id: pass_through
          in:
            - id: input
              source: split/output
          out:
            - id: output
          run:
            class: CommandLineTool
            cwlVersion: v1.0
            $namespaces:
              sbg: 'https://sevenbridges.com'
            id: kghose/benten-demo/pass-through/0
            baseCommand:
              - cat
            inputs:
              - id: input
                type: File?
                inputBinding:
                  position: 0
              - id: dummy
                type: string?
                inputBinding:
                  position: 0
            outputs:
              - id: output
                type: File?
                outputBinding:
                  glob: '*.txt'
            label: pass-through
            requirements:
              - class: DockerRequirement
                dockerPull: alpine
            stdout: out.txt
            'sbg:appVersion':
              - v1.0
            'sbg:id': kghose/benten-demo/pass-through/0
            'sbg:revision': 0
            'sbg:revisionNotes': null
            'sbg:modifiedOn': 1549637816
            'sbg:modifiedBy': kghose
            'sbg:createdOn': 1549637816
            'sbg:createdBy': kghose
            'sbg:project': kghose/benten-demo
            'sbg:projectName': Benten Demo
            'sbg:sbgMaintained': false
            'sbg:validationErrors': []
            'sbg:contributors':
              - kghose
            'sbg:latestRevision': 0
            'sbg:revisionsInfo':
              - 'sbg:revision': 0
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549637816
                'sbg:revisionNotes': null
            'sbg:image_url': null
            'sbg:publisher': sbg
            'sbg:content_hash': a8640c61b8b5e973945f9aa2860f431446d5a56d7482f7a6bd247e545723dbe7d
          label: pass-through
          scatter:
            - input
          scatterMethod: dotproduct
          'sbg:x': -404
          'sbg:y': -34
        - id: merge
          in:
            - id: merge_in
              source:
                - pass_through/output
          out:
            - id: merge_out
          run:
            class: CommandLineTool
            cwlVersion: v1.0
            $namespaces:
              sbg: 'https://sevenbridges.com'
            id: kghose/benten-demo/merge/0
            baseCommand:
              - cat
            inputs:
              - id: merge_in
                type: 'File[]?'
                inputBinding:
                  position: 0
            outputs:
              - id: merge_out
                type: File?
                outputBinding:
                  glob: '*.txt'
            label: merge
            requirements:
              - class: DockerRequirement
                dockerPull: alpine
            stdout: out.txt
            'sbg:appVersion':
              - v1.0
            'sbg:id': kghose/benten-demo/merge/0
            'sbg:revision': 0
            'sbg:revisionNotes': null
            'sbg:modifiedOn': 1549637845
            'sbg:modifiedBy': kghose
            'sbg:createdOn': 1549637845
            'sbg:createdBy': kghose
            'sbg:project': kghose/benten-demo
            'sbg:projectName': Benten Demo
            'sbg:sbgMaintained': false
            'sbg:validationErrors': []
            'sbg:contributors':
              - kghose
            'sbg:latestRevision': 0
            'sbg:revisionsInfo':
              - 'sbg:revision': 0
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549637845
                'sbg:revisionNotes': null
            'sbg:image_url': null
            'sbg:publisher': sbg
            'sbg:content_hash': ad668fe28ff2c111fd8bc64c93b2a3e1ac8f2608b75a18d1980730c694ae3e53f
          label: merge
          'sbg:x': -287
          'sbg:y': -35
      requirements:
        - class: ScatterFeatureRequirement
      'sbg:projectName': Benten Demo
      'sbg:revisionsInfo':
        - 'sbg:revision': 0
          'sbg:modifiedBy': kghose
          'sbg:modifiedOn': 1549637914
          'sbg:revisionNotes': null
        - 'sbg:revision': 1
          'sbg:modifiedBy': kghose
          'sbg:modifiedOn': 1549637993
          'sbg:revisionNotes': Initial rev
      'sbg:image_url': 'https://cgc.sbgenomics.com/ns/brood/images/kghose/benten-demo/wf0/1.png'
      'sbg:appVersion':
        - v1.0
      'sbg:id': kghose/benten-demo/wf0/1
      'sbg:revision': 1
      'sbg:revisionNotes': Initial rev
      'sbg:modifiedOn': 1549637993
      'sbg:modifiedBy': kghose
      'sbg:createdOn': 1549637914
      'sbg:createdBy': kghose
      'sbg:project': kghose/benten-demo
      'sbg:sbgMaintained': false
      'sbg:validationErrors': []
      'sbg:contributors':
        - kghose
      'sbg:latestRevision': 1
      'sbg:publisher': sbg
      'sbg:content_hash': af85a83fbafe3d6b9e7cc3fadee8d67bd68ef5ea8ace6498979f2434e6e969111
    label: wf0
    'sbg:x': -95
    'sbg:y': 231.08436584472656
  - id: wf1
    in:
      - id: input
        source: input
    out:
      - id: merge_out
      - id: output
    run:
      class: Workflow
      cwlVersion: v1.0
      id: kghose/benten-demo/wf1/1
      label: wf1
      $namespaces:
        sbg: 'https://sevenbridges.com'
      inputs:
        - id: input
          type: File?
          'sbg:x': -312
          'sbg:y': -104
      outputs:
        - id: merge_out
          outputSource:
            - wf0/merge_out
          type: File?
          'sbg:x': 46
          'sbg:y': -34
        - id: output
          outputSource:
            - pass_through/output
          type: File?
          'sbg:x': 50
          'sbg:y': -157
      steps:
        - id: wf0
          in:
            - id: input
              source: input
          out:
            - id: merge_out
          run:
            class: Workflow
            cwlVersion: v1.0
            id: kghose/benten-demo/wf0/1
            label: wf0
            $namespaces:
              sbg: 'https://sevenbridges.com'
            inputs:
              - id: input
                type: File?
                'sbg:x': -658.5054321289062
                'sbg:y': -34
            outputs:
              - id: merge_out
                outputSource:
                  - merge/merge_out
                type: File?
                'sbg:x': -162
                'sbg:y': -35
            steps:
              - id: split
                in:
                  - id: input
                    source: input
                out:
                  - id: output
                run:
                  class: CommandLineTool
                  cwlVersion: v1.0
                  $namespaces:
                    sbg: 'https://sevenbridges.com'
                  id: kghose/benten-demo/split/0
                  baseCommand:
                    - split
                  inputs:
                    - id: input
                      type: File?
                      inputBinding:
                        position: 0
                  outputs:
                    - id: output
                      type: 'File[]?'
                      outputBinding:
                        glob: out-*
                  label: split
                  arguments:
                    - position: 0
                      prefix: '-l'
                      valueFrom: '1'
                    - position: 100
                      prefix: ''
                      valueFrom: out-
                  requirements:
                    - class: DockerRequirement
                      dockerPull: alpine
                  'sbg:appVersion':
                    - v1.0
                  'sbg:id': kghose/benten-demo/split/0
                  'sbg:revision': 0
                  'sbg:revisionNotes': null
                  'sbg:modifiedOn': 1549637768
                  'sbg:modifiedBy': kghose
                  'sbg:createdOn': 1549637768
                  'sbg:createdBy': kghose
                  'sbg:project': kghose/benten-demo
                  'sbg:projectName': Benten Demo
                  'sbg:sbgMaintained': false
                  'sbg:validationErrors': []
                  'sbg:contributors':
                    - kghose
                  'sbg:latestRevision': 0
                  'sbg:revisionsInfo':
                    - 'sbg:revision': 0
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637768
                      'sbg:revisionNotes': null
                  'sbg:image_url': null
                  'sbg:publisher': sbg
                  'sbg:content_hash': >-
                    aa38db7a720e5140a5cebcab1cf2040da92fb709685d5131ff3bdecb7b078f78c
                label: split
                'sbg:x': -527
                'sbg:y': -35
              - id: pass_through
                in:
                  - id: input
                    source: split/output
                out:
                  - id: output
                run:
                  class: CommandLineTool
                  cwlVersion: v1.0
                  $namespaces:
                    sbg: 'https://sevenbridges.com'
                  id: kghose/benten-demo/pass-through/0
                  baseCommand:
                    - cat
                  inputs:
                    - id: input
                      type: File?
                      inputBinding:
                        position: 0
                    - id: dummy
                      type: string?
                      inputBinding:
                        position: 0
                  outputs:
                    - id: output
                      type: File?
                      outputBinding:
                        glob: '*.txt'
                  label: pass-through
                  requirements:
                    - class: DockerRequirement
                      dockerPull: alpine
                  stdout: out.txt
                  'sbg:appVersion':
                    - v1.0
                  'sbg:id': kghose/benten-demo/pass-through/0
                  'sbg:revision': 0
                  'sbg:revisionNotes': null
                  'sbg:modifiedOn': 1549637816
                  'sbg:modifiedBy': kghose
                  'sbg:createdOn': 1549637816
                  'sbg:createdBy': kghose
                  'sbg:project': kghose/benten-demo
                  'sbg:projectName': Benten Demo
                  'sbg:sbgMaintained': false
                  'sbg:validationErrors': []
                  'sbg:contributors':
                    - kghose
                  'sbg:latestRevision': 0
                  'sbg:revisionsInfo':
                    - 'sbg:revision': 0
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637816
                      'sbg:revisionNotes': null
                  'sbg:image_url': null
                  'sbg:publisher': sbg
                  'sbg:content_hash': >-
                    a8640c61b8b5e973945f9aa2860f431446d5a56d7482f7a6bd247e545723dbe7d
                label: pass-through
                scatter:
                  - input
                scatterMethod: dotproduct
                'sbg:x': -404
                'sbg:y': -34
              - id: merge
                in:
                  - id: merge_in
                    source:
                      - pass_through/output
                out:
                  - id: merge_out
                run:
                  class: CommandLineTool
                  cwlVersion: v1.0
                  $namespaces:
                    sbg: 'https://sevenbridges.com'
                  id: kghose/benten-demo/merge/0
                  baseCommand:
                    - cat
                  inputs:
                    - id: merge_in
                      type: 'File[]?'
                      inputBinding:
                        position: 0
                  outputs:
                    - id: merge_out
                      type: File?
                      outputBinding:
                        glob: '*.txt'
                  label: merge
                  requirements:
                    - class: DockerRequirement
                      dockerPull: alpine
                  stdout: out.txt
                  'sbg:appVersion':
                    - v1.0
                  'sbg:id': kghose/benten-demo/merge/0
                  'sbg:revision': 0
                  'sbg:revisionNotes': null
                  'sbg:modifiedOn': 1549637845
                  'sbg:modifiedBy': kghose
                  'sbg:createdOn': 1549637845
                  'sbg:createdBy': kghose
                  'sbg:project': kghose/benten-demo
                  'sbg:projectName': Benten Demo
                  'sbg:sbgMaintained': false
                  'sbg:validationErrors': []
                  'sbg:contributors':
                    - kghose
                  'sbg:latestRevision': 0
                  'sbg:revisionsInfo':
                    - 'sbg:revision': 0
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637845
                      'sbg:revisionNotes': null
                  'sbg:image_url': null
                  'sbg:publisher': sbg
                  'sbg:content_hash': >-
                    ad668fe28ff2c111fd8bc64c93b2a3e1ac8f2608b75a18d1980730c694ae3e53f
                label: merge
                'sbg:x': -287
                'sbg:y': -35
            requirements:
              - class: ScatterFeatureRequirement
            'sbg:projectName': Benten Demo
            'sbg:revisionsInfo':
              - 'sbg:revision': 0
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549637914
                'sbg:revisionNotes': null
              - 'sbg:revision': 1
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549637993
                'sbg:revisionNotes': Initial rev
            'sbg:image_url': >-
              https://cgc.sbgenomics.com/ns/brood/images/kghose/benten-demo/wf0/1.png
            'sbg:appVersion':
              - v1.0
            'sbg:id': kghose/benten-demo/wf0/1
            'sbg:revision': 1
            'sbg:revisionNotes': Initial rev
            'sbg:modifiedOn': 1549637993
            'sbg:modifiedBy': kghose
            'sbg:createdOn': 1549637914
            'sbg:createdBy': kghose
            'sbg:project': kghose/benten-demo
            'sbg:sbgMaintained': false
            'sbg:validationErrors': []
            'sbg:contributors':
              - kghose
            'sbg:latestRevision': 1
            'sbg:publisher': sbg
            'sbg:content_hash': af85a83fbafe3d6b9e7cc3fadee8d67bd68ef5ea8ace6498979f2434e6e969111
          label: wf0
          'sbg:x': -135
          'sbg:y': -33
        - id: pass_through
          in:
            - id: input
              source: input
          out:
            - id: output
          run:
            class: CommandLineTool
            cwlVersion: v1.0
            $namespaces:
              sbg: 'https://sevenbridges.com'
            id: kghose/benten-demo/pass-through/0
            baseCommand:
              - cat
            inputs:
              - id: input
                type: File?
                inputBinding:
                  position: 0
              - id: dummy
                type: string?
                inputBinding:
                  position: 0
            outputs:
              - id: output
                type: File?
                outputBinding:
                  glob: '*.txt'
            label: pass-through
            requirements:
              - class: DockerRequirement
                dockerPull: alpine
            stdout: out.txt
            'sbg:appVersion':
              - v1.0
            'sbg:id': kghose/benten-demo/pass-through/0
            'sbg:revision': 0
            'sbg:revisionNotes': null
            'sbg:modifiedOn': 1549637816
            'sbg:modifiedBy': kghose
            'sbg:createdOn': 1549637816
            'sbg:createdBy': kghose
            'sbg:project': kghose/benten-demo
            'sbg:projectName': Benten Demo
            'sbg:sbgMaintained': false
            'sbg:validationErrors': []
            'sbg:contributors':
              - kghose
            'sbg:latestRevision': 0
            'sbg:revisionsInfo':
              - 'sbg:revision': 0
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549637816
                'sbg:revisionNotes': null
            'sbg:image_url': null
            'sbg:publisher': sbg
            'sbg:content_hash': a8640c61b8b5e973945f9aa2860f431446d5a56d7482f7a6bd247e545723dbe7d
          label: pass-through
          'sbg:x': -137.39886474609375
          'sbg:y': -157
      requirements:
        - class: SubworkflowFeatureRequirement
      'sbg:projectName': Benten Demo
      'sbg:revisionsInfo':
        - 'sbg:revision': 0
          'sbg:modifiedBy': kghose
          'sbg:modifiedOn': 1549638004
          'sbg:revisionNotes': null
        - 'sbg:revision': 1
          'sbg:modifiedBy': kghose
          'sbg:modifiedOn': 1549638068
          'sbg:revisionNotes': Initial rev
      'sbg:image_url': 'https://cgc.sbgenomics.com/ns/brood/images/kghose/benten-demo/wf1/1.png'
      'sbg:appVersion':
        - v1.0
      'sbg:id': kghose/benten-demo/wf1/1
      'sbg:revision': 1
      'sbg:revisionNotes': Initial rev
      'sbg:modifiedOn': 1549638068
      'sbg:modifiedBy': kghose
      'sbg:createdOn': 1549638004
      'sbg:createdBy': kghose
      'sbg:project': kghose/benten-demo
      'sbg:sbgMaintained': false
      'sbg:validationErrors': []
      'sbg:contributors':
        - kghose
      'sbg:latestRevision': 1
      'sbg:publisher': sbg
      'sbg:content_hash': ad9214775ba95dac4947d4188c9d5daf5003fe2eb90493ae9e0116baa968cc8f4
    label: wf1
    'sbg:x': -100
    'sbg:y': 63
  - id: wf2
    in:
      - id: input
        source: input
    out:
      - id: merge_out
      - id: output
      - id: merge_out_1
    run:
      class: Workflow
      cwlVersion: v1.0
      id: kghose/benten-demo/wf2/1
      label: wf2
      $namespaces:
        sbg: 'https://sevenbridges.com'
      inputs:
        - id: input
          type: File?
          'sbg:x': -331
          'sbg:y': -63
      outputs:
        - id: merge_out
          outputSource:
            - wf0/merge_out
          type: File?
          'sbg:x': 5
          'sbg:y': 37
        - id: output
          outputSource:
            - wf1/output
          type: File?
          'sbg:x': 0
          'sbg:y': -211
        - id: merge_out_1
          outputSource:
            - wf1/merge_out
          type: File?
          'sbg:x': 2
          'sbg:y': -88
      steps:
        - id: wf0
          in:
            - id: input
              source: input
          out:
            - id: merge_out
          run:
            class: Workflow
            cwlVersion: v1.0
            id: kghose/benten-demo/wf0/1
            label: wf0
            $namespaces:
              sbg: 'https://sevenbridges.com'
            inputs:
              - id: input
                type: File?
                'sbg:x': -658.5054321289062
                'sbg:y': -34
            outputs:
              - id: merge_out
                outputSource:
                  - merge/merge_out
                type: File?
                'sbg:x': -162
                'sbg:y': -35
            steps:
              - id: split
                in:
                  - id: input
                    source: input
                out:
                  - id: output
                run:
                  class: CommandLineTool
                  cwlVersion: v1.0
                  $namespaces:
                    sbg: 'https://sevenbridges.com'
                  id: kghose/benten-demo/split/0
                  baseCommand:
                    - split
                  inputs:
                    - id: input
                      type: File?
                      inputBinding:
                        position: 0
                  outputs:
                    - id: output
                      type: 'File[]?'
                      outputBinding:
                        glob: out-*
                  label: split
                  arguments:
                    - position: 0
                      prefix: '-l'
                      valueFrom: '1'
                    - position: 100
                      prefix: ''
                      valueFrom: out-
                  requirements:
                    - class: DockerRequirement
                      dockerPull: alpine
                  'sbg:appVersion':
                    - v1.0
                  'sbg:id': kghose/benten-demo/split/0
                  'sbg:revision': 0
                  'sbg:revisionNotes': null
                  'sbg:modifiedOn': 1549637768
                  'sbg:modifiedBy': kghose
                  'sbg:createdOn': 1549637768
                  'sbg:createdBy': kghose
                  'sbg:project': kghose/benten-demo
                  'sbg:projectName': Benten Demo
                  'sbg:sbgMaintained': false
                  'sbg:validationErrors': []
                  'sbg:contributors':
                    - kghose
                  'sbg:latestRevision': 0
                  'sbg:revisionsInfo':
                    - 'sbg:revision': 0
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637768
                      'sbg:revisionNotes': null
                  'sbg:image_url': null
                  'sbg:publisher': sbg
                  'sbg:content_hash': >-
                    aa38db7a720e5140a5cebcab1cf2040da92fb709685d5131ff3bdecb7b078f78c
                label: split
                'sbg:x': -527
                'sbg:y': -35
              - id: pass_through
                in:
                  - id: input
                    source: split/output
                out:
                  - id: output
                run:
                  class: CommandLineTool
                  cwlVersion: v1.0
                  $namespaces:
                    sbg: 'https://sevenbridges.com'
                  id: kghose/benten-demo/pass-through/0
                  baseCommand:
                    - cat
                  inputs:
                    - id: input
                      type: File?
                      inputBinding:
                        position: 0
                    - id: dummy
                      type: string?
                      inputBinding:
                        position: 0
                  outputs:
                    - id: output
                      type: File?
                      outputBinding:
                        glob: '*.txt'
                  label: pass-through
                  requirements:
                    - class: DockerRequirement
                      dockerPull: alpine
                  stdout: out.txt
                  'sbg:appVersion':
                    - v1.0
                  'sbg:id': kghose/benten-demo/pass-through/0
                  'sbg:revision': 0
                  'sbg:revisionNotes': null
                  'sbg:modifiedOn': 1549637816
                  'sbg:modifiedBy': kghose
                  'sbg:createdOn': 1549637816
                  'sbg:createdBy': kghose
                  'sbg:project': kghose/benten-demo
                  'sbg:projectName': Benten Demo
                  'sbg:sbgMaintained': false
                  'sbg:validationErrors': []
                  'sbg:contributors':
                    - kghose
                  'sbg:latestRevision': 0
                  'sbg:revisionsInfo':
                    - 'sbg:revision': 0
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637816
                      'sbg:revisionNotes': null
                  'sbg:image_url': null
                  'sbg:publisher': sbg
                  'sbg:content_hash': >-
                    a8640c61b8b5e973945f9aa2860f431446d5a56d7482f7a6bd247e545723dbe7d
                label: pass-through
                scatter:
                  - input
                scatterMethod: dotproduct
                'sbg:x': -404
                'sbg:y': -34
              - id: merge
                in:
                  - id: merge_in
                    source:
                      - pass_through/output
                out:
                  - id: merge_out
                run:
                  class: CommandLineTool
                  cwlVersion: v1.0
                  $namespaces:
                    sbg: 'https://sevenbridges.com'
                  id: kghose/benten-demo/merge/0
                  baseCommand:
                    - cat
                  inputs:
                    - id: merge_in
                      type: 'File[]?'
                      inputBinding:
                        position: 0
                  outputs:
                    - id: merge_out
                      type: File?
                      outputBinding:
                        glob: '*.txt'
                  label: merge
                  requirements:
                    - class: DockerRequirement
                      dockerPull: alpine
                  stdout: out.txt
                  'sbg:appVersion':
                    - v1.0
                  'sbg:id': kghose/benten-demo/merge/0
                  'sbg:revision': 0
                  'sbg:revisionNotes': null
                  'sbg:modifiedOn': 1549637845
                  'sbg:modifiedBy': kghose
                  'sbg:createdOn': 1549637845
                  'sbg:createdBy': kghose
                  'sbg:project': kghose/benten-demo
                  'sbg:projectName': Benten Demo
                  'sbg:sbgMaintained': false
                  'sbg:validationErrors': []
                  'sbg:contributors':
                    - kghose
                  'sbg:latestRevision': 0
                  'sbg:revisionsInfo':
                    - 'sbg:revision': 0
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637845
                      'sbg:revisionNotes': null
                  'sbg:image_url': null
                  'sbg:publisher': sbg
                  'sbg:content_hash': >-
                    ad668fe28ff2c111fd8bc64c93b2a3e1ac8f2608b75a18d1980730c694ae3e53f
                label: merge
                'sbg:x': -287
                'sbg:y': -35
            requirements:
              - class: ScatterFeatureRequirement
            'sbg:projectName': Benten Demo
            'sbg:revisionsInfo':
              - 'sbg:revision': 0
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549637914
                'sbg:revisionNotes': null
              - 'sbg:revision': 1
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549637993
                'sbg:revisionNotes': Initial rev
            'sbg:image_url': >-
              https://cgc.sbgenomics.com/ns/brood/images/kghose/benten-demo/wf0/1.png
            'sbg:appVersion':
              - v1.0
            'sbg:id': kghose/benten-demo/wf0/1
            'sbg:revision': 1
            'sbg:revisionNotes': Initial rev
            'sbg:modifiedOn': 1549637993
            'sbg:modifiedBy': kghose
            'sbg:createdOn': 1549637914
            'sbg:createdBy': kghose
            'sbg:project': kghose/benten-demo
            'sbg:sbgMaintained': false
            'sbg:validationErrors': []
            'sbg:contributors':
              - kghose
            'sbg:latestRevision': 1
            'sbg:publisher': sbg
            'sbg:content_hash': af85a83fbafe3d6b9e7cc3fadee8d67bd68ef5ea8ace6498979f2434e6e969111
          label: wf0
          'sbg:x': -144
          'sbg:y': 16
        - id: wf1
          in:
            - id: input
              source: input
          out:
            - id: merge_out
            - id: output
          run:
            class: Workflow
            cwlVersion: v1.0
            id: kghose/benten-demo/wf1/1
            label: wf1
            $namespaces:
              sbg: 'https://sevenbridges.com'
            inputs:
              - id: input
                type: File?
                'sbg:x': -312
                'sbg:y': -104
            outputs:
              - id: merge_out
                outputSource:
                  - wf0/merge_out
                type: File?
                'sbg:x': 46
                'sbg:y': -34
              - id: output
                outputSource:
                  - pass_through/output
                type: File?
                'sbg:x': 50
                'sbg:y': -157
            steps:
              - id: wf0
                in:
                  - id: input
                    source: input
                out:
                  - id: merge_out
                run:
                  class: Workflow
                  cwlVersion: v1.0
                  id: kghose/benten-demo/wf0/1
                  label: wf0
                  $namespaces:
                    sbg: 'https://sevenbridges.com'
                  inputs:
                    - id: input
                      type: File?
                      'sbg:x': -658.5054321289062
                      'sbg:y': -34
                  outputs:
                    - id: merge_out
                      outputSource:
                        - merge/merge_out
                      type: File?
                      'sbg:x': -162
                      'sbg:y': -35
                  steps:
                    - id: split
                      in:
                        - id: input
                          source: input
                      out:
                        - id: output
                      run:
                        class: CommandLineTool
                        cwlVersion: v1.0
                        $namespaces:
                          sbg: 'https://sevenbridges.com'
                        id: kghose/benten-demo/split/0
                        baseCommand:
                          - split
                        inputs:
                          - id: input
                            type: File?
                            inputBinding:
                              position: 0
                        outputs:
                          - id: output
                            type: 'File[]?'
                            outputBinding:
                              glob: out-*
                        label: split
                        arguments:
                          - position: 0
                            prefix: '-l'
                            valueFrom: '1'
                          - position: 100
                            prefix: ''
                            valueFrom: out-
                        requirements:
                          - class: DockerRequirement
                            dockerPull: alpine
                        'sbg:appVersion':
                          - v1.0
                        'sbg:id': kghose/benten-demo/split/0
                        'sbg:revision': 0
                        'sbg:revisionNotes': null
                        'sbg:modifiedOn': 1549637768
                        'sbg:modifiedBy': kghose
                        'sbg:createdOn': 1549637768
                        'sbg:createdBy': kghose
                        'sbg:project': kghose/benten-demo
                        'sbg:projectName': Benten Demo
                        'sbg:sbgMaintained': false
                        'sbg:validationErrors': []
                        'sbg:contributors':
                          - kghose
                        'sbg:latestRevision': 0
                        'sbg:revisionsInfo':
                          - 'sbg:revision': 0
                            'sbg:modifiedBy': kghose
                            'sbg:modifiedOn': 1549637768
                            'sbg:revisionNotes': null
                        'sbg:image_url': null
                        'sbg:publisher': sbg
                        'sbg:content_hash': >-
                          aa38db7a720e5140a5cebcab1cf2040da92fb709685d5131ff3bdecb7b078f78c
                      label: split
                      'sbg:x': -527
                      'sbg:y': -35
                    - id: pass_through
                      in:
                        - id: input
                          source: split/output
                      out:
                        - id: output
                      run:
                        class: CommandLineTool
                        cwlVersion: v1.0
                        $namespaces:
                          sbg: 'https://sevenbridges.com'
                        id: kghose/benten-demo/pass-through/0
                        baseCommand:
                          - cat
                        inputs:
                          - id: input
                            type: File?
                            inputBinding:
                              position: 0
                          - id: dummy
                            type: string?
                            inputBinding:
                              position: 0
                        outputs:
                          - id: output
                            type: File?
                            outputBinding:
                              glob: '*.txt'
                        label: pass-through
                        requirements:
                          - class: DockerRequirement
                            dockerPull: alpine
                        stdout: out.txt
                        'sbg:appVersion':
                          - v1.0
                        'sbg:id': kghose/benten-demo/pass-through/0
                        'sbg:revision': 0
                        'sbg:revisionNotes': null
                        'sbg:modifiedOn': 1549637816
                        'sbg:modifiedBy': kghose
                        'sbg:createdOn': 1549637816
                        'sbg:createdBy': kghose
                        'sbg:project': kghose/benten-demo
                        'sbg:projectName': Benten Demo
                        'sbg:sbgMaintained': false
                        'sbg:validationErrors': []
                        'sbg:contributors':
                          - kghose
                        'sbg:latestRevision': 0
                        'sbg:revisionsInfo':
                          - 'sbg:revision': 0
                            'sbg:modifiedBy': kghose
                            'sbg:modifiedOn': 1549637816
                            'sbg:revisionNotes': null
                        'sbg:image_url': null
                        'sbg:publisher': sbg
                        'sbg:content_hash': >-
                          a8640c61b8b5e973945f9aa2860f431446d5a56d7482f7a6bd247e545723dbe7d
                      label: pass-through
                      scatter:
                        - input
                      scatterMethod: dotproduct
                      'sbg:x': -404
                      'sbg:y': -34
                    - id: merge
                      in:
                        - id: merge_in
                          source:
                            - pass_through/output
                      out:
                        - id: merge_out
                      run:
                        class: CommandLineTool
                        cwlVersion: v1.0
                        $namespaces:
                          sbg: 'https://sevenbridges.com'
                        id: kghose/benten-demo/merge/0
                        baseCommand:
                          - cat
                        inputs:
                          - id: merge_in
                            type: 'File[]?'
                            inputBinding:
                              position: 0
                        outputs:
                          - id: merge_out
                            type: File?
                            outputBinding:
                              glob: '*.txt'
                        label: merge
                        requirements:
                          - class: DockerRequirement
                            dockerPull: alpine
                        stdout: out.txt
                        'sbg:appVersion':
                          - v1.0
                        'sbg:id': kghose/benten-demo/merge/0
                        'sbg:revision': 0
                        'sbg:revisionNotes': null
                        'sbg:modifiedOn': 1549637845
                        'sbg:modifiedBy': kghose
                        'sbg:createdOn': 1549637845
                        'sbg:createdBy': kghose
                        'sbg:project': kghose/benten-demo
                        'sbg:projectName': Benten Demo
                        'sbg:sbgMaintained': false
                        'sbg:validationErrors': []
                        'sbg:contributors':
                          - kghose
                        'sbg:latestRevision': 0
                        'sbg:revisionsInfo':
                          - 'sbg:revision': 0
                            'sbg:modifiedBy': kghose
                            'sbg:modifiedOn': 1549637845
                            'sbg:revisionNotes': null
                        'sbg:image_url': null
                        'sbg:publisher': sbg
                        'sbg:content_hash': >-
                          ad668fe28ff2c111fd8bc64c93b2a3e1ac8f2608b75a18d1980730c694ae3e53f
                      label: merge
                      'sbg:x': -287
                      'sbg:y': -35
                  requirements:
                    - class: ScatterFeatureRequirement
                  'sbg:projectName': Benten Demo
                  'sbg:revisionsInfo':
                    - 'sbg:revision': 0
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637914
                      'sbg:revisionNotes': null
                    - 'sbg:revision': 1
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637993
                      'sbg:revisionNotes': Initial rev
                  'sbg:image_url': >-
                    https://cgc.sbgenomics.com/ns/brood/images/kghose/benten-demo/wf0/1.png
                  'sbg:appVersion':
                    - v1.0
                  'sbg:id': kghose/benten-demo/wf0/1
                  'sbg:revision': 1
                  'sbg:revisionNotes': Initial rev
                  'sbg:modifiedOn': 1549637993
                  'sbg:modifiedBy': kghose
                  'sbg:createdOn': 1549637914
                  'sbg:createdBy': kghose
                  'sbg:project': kghose/benten-demo
                  'sbg:sbgMaintained': false
                  'sbg:validationErrors': []
                  'sbg:contributors':
                    - kghose
                  'sbg:latestRevision': 1
                  'sbg:publisher': sbg
                  'sbg:content_hash': >-
                    af85a83fbafe3d6b9e7cc3fadee8d67bd68ef5ea8ace6498979f2434e6e969111
                label: wf0
                'sbg:x': -135
                'sbg:y': -33
              - id: pass_through
                in:
                  - id: input
                    source: input
                out:
                  - id: output
                run:
                  class: CommandLineTool
                  cwlVersion: v1.0
                  $namespaces:
                    sbg: 'https://sevenbridges.com'
                  id: kghose/benten-demo/pass-through/0
                  baseCommand:
                    - cat
                  inputs:
                    - id: input
                      type: File?
                      inputBinding:
                        position: 0
                    - id: dummy
                      type: string?
                      inputBinding:
                        position: 0
                  outputs:
                    - id: output
                      type: File?
                      outputBinding:
                        glob: '*.txt'
                  label: pass-through
                  requirements:
                    - class: DockerRequirement
                      dockerPull: alpine
                  stdout: out.txt
                  'sbg:appVersion':
                    - v1.0
                  'sbg:id': kghose/benten-demo/pass-through/0
                  'sbg:revision': 0
                  'sbg:revisionNotes': null
                  'sbg:modifiedOn': 1549637816
                  'sbg:modifiedBy': kghose
                  'sbg:createdOn': 1549637816
                  'sbg:createdBy': kghose
                  'sbg:project': kghose/benten-demo
                  'sbg:projectName': Benten Demo
                  'sbg:sbgMaintained': false
                  'sbg:validationErrors': []
                  'sbg:contributors':
                    - kghose
                  'sbg:latestRevision': 0
                  'sbg:revisionsInfo':
                    - 'sbg:revision': 0
                      'sbg:modifiedBy': kghose
                      'sbg:modifiedOn': 1549637816
                      'sbg:revisionNotes': null
                  'sbg:image_url': null
                  'sbg:publisher': sbg
                  'sbg:content_hash': >-
                    a8640c61b8b5e973945f9aa2860f431446d5a56d7482f7a6bd247e545723dbe7d
                label: pass-through
                'sbg:x': -137.39886474609375
                'sbg:y': -157
            requirements:
              - class: SubworkflowFeatureRequirement
            'sbg:projectName': Benten Demo
            'sbg:revisionsInfo':
              - 'sbg:revision': 0
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549638004
                'sbg:revisionNotes': null
              - 'sbg:revision': 1
                'sbg:modifiedBy': kghose
                'sbg:modifiedOn': 1549638068
                'sbg:revisionNotes': Initial rev
            'sbg:image_url': >-
              https://cgc.sbgenomics.com/ns/brood/images/kghose/benten-demo/wf1/1.png
            'sbg:appVersion':
              - v1.0
            'sbg:id': kghose/benten-demo/wf1/1
            'sbg:revision': 1
            'sbg:revisionNotes': Initial rev
            'sbg:modifiedOn': 1549638068
            'sbg:modifiedBy': kghose
            'sbg:createdOn': 1549638004
            'sbg:createdBy': kghose
            'sbg:project': kghose/benten-demo
            'sbg:sbgMaintained': false
            'sbg:validationErrors': []
            'sbg:contributors':
              - kghose
            'sbg:latestRevision': 1
            'sbg:publisher': sbg
            'sbg:content_hash': ad9214775ba95dac4947d4188c9d5daf5003fe2eb90493ae9e0116baa968cc8f4
          label: wf1
          'sbg:x': -154
          'sbg:y': -140
      requirements:
        - class: SubworkflowFeatureRequirement
      'sbg:projectName': Benten Demo
      'sbg:revisionsInfo':
        - 'sbg:revision': 0
          'sbg:modifiedBy': kghose
          'sbg:modifiedOn': 1549638080
          'sbg:revisionNotes': null
        - 'sbg:revision': 1
          'sbg:modifiedBy': kghose
          'sbg:modifiedOn': 1549638539
          'sbg:revisionNotes': Initial revision
      'sbg:image_url': 'https://cgc.sbgenomics.com/ns/brood/images/kghose/benten-demo/wf2/1.png'
      'sbg:appVersion':
        - v1.0
      'sbg:id': kghose/benten-demo/wf2/1
      'sbg:revision': 1
      'sbg:revisionNotes': Initial revision
      'sbg:modifiedOn': 1549638539
      'sbg:modifiedBy': kghose
      'sbg:createdOn': 1549638080
      'sbg:createdBy': kghose
      'sbg:project': kghose/benten-demo
      'sbg:sbgMaintained': false
      'sbg:validationErrors': []
      'sbg:contributors':
        - kghose
      'sbg:latestRevision': 1
      'sbg:publisher': sbg
      'sbg:content_hash': a02fdc6b8eb2ea15652f8b219ffb7c86e277e19ea4e3c8368fba8a3d5b6d600f4
    label: wf2
    'sbg:x': -107
    'sbg:y': -230
requirements:
  - class: SubworkflowFeatureRequirement
'sbg:projectName': Benten Demo
'sbg:revisionsInfo':
  - 'sbg:revision': 0
    'sbg:modifiedBy': kghose
    'sbg:modifiedOn': 1549638554
    'sbg:revisionNotes': null
  - 'sbg:revision': 1
    'sbg:modifiedBy': kghose
    'sbg:modifiedOn': 1549638645
    'sbg:revisionNotes': Initial rev
'sbg:image_url': 'https://cgc.sbgenomics.com/ns/brood/images/kghose/benten-demo/wf3/1.png'
'sbg:appVersion':
  - v1.0
'sbg:id': kghose/benten-demo/wf3/1
'sbg:revision': 1
'sbg:revisionNotes': Initial rev
'sbg:modifiedOn': 1549638645
'sbg:modifiedBy': kghose
'sbg:createdOn': 1549638554
'sbg:createdBy': kghose
'sbg:project': kghose/benten-demo
'sbg:sbgMaintained': false
'sbg:validationErrors': []
'sbg:contributors':
  - kghose
'sbg:latestRevision': 1
'sbg:publisher': sbg
'sbg:content_hash': abc6fe168cdce043d7e52f2d6df85d35af77c3793c1ad046b5e4276bfc4c3942c
