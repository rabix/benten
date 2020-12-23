# How to generate schema.json 

The schema files are generated from the CWL schema as follows.

```
schema-salad-tool --print-avro ~/path/to/cwl/schemas/CommonWorkflowLanguage.yml > schema.json
```

As of 2019.09 Benten uses patched versions of both v1.0 and v1.1 specs
which fix errors in the officially published specs. These are found at
`https://github.com/kaushik-work/cwl-v1.1` and 
`https://github.com/kaushik-work/common-workflow-language`
