## Common metadata validation errors and solutions

##### ERROR:'\<column header\>' is a required property
| | |
| --- | --- |
| Reason | Required metadata is missing from the metadata file. |
| Solution | Add missing metadata as a new column in metadata file.|
  
##### ERROR:\<column header\>: only alphanumeric characters and underscore allowed in metadata name
| | |
| --- | --- |
|  Reason  | Valid characters for metadata names is limited. |
|  Solution  | Remove all non-alphanumeric characters (except underscore) from column header. |
 
##### ERROR:Numeric annotation, \<column header\>, contains non-numeric data (or unidentified NA values)
| | |
| --- | --- |
|  Reason  | Metadata TYPE declared as numeric but column contains strings or empty cells. |
|  Solution  | Ensure that all values for \<metadata\> are numeric. |
   
##### ERROR:\<column header\>: Could not parse provided ontology id, "PATO_0000461, PATO_0000461, PATO_0000461"
| | |
| --- | --- |
|  Reason  | Arrays of metadata information must be delimited by the pipe (\|) symbol. |
|  Solution  | Replace with pipe(\|) delimiter. |
  
##### ERROR:\<column header\>: '\<text\>' does not match '\^[-A-Za-z0-9]+[_:][-A-Za-z0-9]+' 
| | |
| --- | --- |
|  Reason  | Metadata validation expected ontology IDs as values for the specified column header. |
|  Solution  | Browse the ontology listed in [required conventional metadata](https://github.com/broadinstitute/single_cell_portal/wiki/Metadata-File#required-conventional-metadata) and select terms that best describe your data. Note that an ontology_label column with the natural language name is also required. |


