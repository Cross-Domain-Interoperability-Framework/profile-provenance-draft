# Climate Profile Model Review

Problems found in `climate-profile-BB.jsonld`, a DDI-CDI 1.1 beta description of the EURO-CORDEX climate-profile workflow, while turning it into CDIF provenance records.

**179** top-level nodes **3,849** RDF triples Context: `ddi-cdi.github.io/m2t-ng/DDI-CDI_1-1beta/…/ddi-cdi.jsonld`

Breaks links the graph does not connect what the file means to connect 

Inconsistent two parts of the file disagree 

Minor missing detail or a typo

## Summary

**31** separate pieces when the file is read as RDF

**82** links written as strings, not as links

**2** groups of nodes nothing refers to, even reading the strings as links

**2** activities in the sequence with no steps, inputs or outputs



Read as JSON, with every `uri` treated as a link, the file is almost one connected graph: two small groups hang loose. 



Read as RDF, it falls into 31 pieces, because the links between activities and datasets, between parameters and what they are bound to, and to the GSBPM concepts are all written as `Reference` objects whose `uri` is a typed string. 



Beyond connectivity, the steps and their activities disagree about inputs and outputs in several places, and the final profile outputs have no file location.



### Process and data are separate graphs in RDF

82 links are `Reference` objects whose `uri` is an `xsd:anyURI` literal, so in RDF they connect nothing:

|Property|Count|What it should link|
|-|-|-|
|`Parameter.entityBound`|38|each parameter to its variable or dataset|
|`Activity.entityProduced`|15|activities to their outputs|
|`standardModelMapping`|14|activities and steps to their GSBPM concept|
|`Activity.entityUsed`|13|activities to their inputs (one is the external CDS URL)|
|`AgentInRole.reference`|2|the processing agent's creators to the two Individuals|

The result is 31 pieces: the process side (the sequence, 7 activities, 8 steps, 40 parameters and the processing agent, 64 nodes) in one; each dataset with its variables on its own (19 pieces); the agent listing with the two Individuals and the organization; and each of the 9 GSBPM concepts alone. Links written directly, such as `has_Step`, `receives`, `produces` and `has_InstanceVariable`, do come through.

This looks like it follows from DDI-CDI typing these properties as `Reference`. Worth checking whether DDI-CDI offers a direct association for links within one file, or whether consumers are expected to resolve `Reference.uri` themselves.





### `temperature indices thresholds` is not referenced

This DataSet and its three variables (`SU_THRESHOLD`, `HD_THRESHOLD`, `TR_THRESHOLD`) are not referenced by any activity, step or parameter. The activity they belong with, *Compute temperature indices* ("Summer Days (SU), Hot Days (HD), Tropical Nights (TR)"), has no steps, inputs or outputs.

Give *Compute temperature indices* a step whose parameters bind the threshold variables, or list the dataset in its `entityUsed`.





### `wind_speed_2026_2030` is not referenced

This DataSet and its physical dataset (`physicalFileURL` `Downloads/10m_wind_speed_2026_2030_CROPPED.nc`) are used and produced by nothing. Step S2 has two parameters bound to nothing: it receives `10m_wind_speed` and produces `wind_speed`. That output may have been meant for this dataset.

Bind S2's `wind_speed` parameter to this dataset, or remove the dataset if it is a leftover test file.

## Activities and steps



### Two activities in the sequence do nothing

*Compute temperature indices* (position 5) has a description and a GSBPM mapping but no steps, inputs or outputs. *Heatwave indices* (position 6) has only a name, with a trailing space.

Fill them in, or mark them as planned and take them out of the sequence until they are.





### Steps cover one variable where their activities cover seven

*Climate Data Preparation* lists the seven merged `.nc` files as outputs, but its step S3 produces only `10m_wind_speed-2025-2049.nc`. *Climate Indicator Generation* uses all seven, but its step S4 receives only the wind-speed file.

If the step runs once per variable, say so (a parameter for the variable, and all seven files bound), or bind all seven files to the step.





### S6.3 reads the wrong dataset

S6.2 produces *Spatial Mean Climate Time Series*, but no step uses it. S6.3, whose description says it combines the spatial averages, receives *Continuous Scenario Climate Dataset* instead. As written, the CSV, TXT and NetCDF profiles are made from the continuous scenario data, not from the spatial means.

Bind S6.3's input to *Spatial Mean Climate Time Series*.





### Other input and output mismatches

* *Raw Data Collection* uses the CDS URL, but no step receives it.
* *Climate Profile Generation* lists *Climate Indicator Dataset Collection* as both used and produced. At step level S6.1 produces it and S6.2 reads it, so it is internal to the activity, not an input.
* *Historical Annual Climate Dataset* is read by S5, but nothing produces it and it has no description or variables, so where it comes from is not recorded.
* Two steps produce a variable of a dataset they also read: S1's `CDS API` is bound to `json` in `configure_climate_data`, and S6.3's `Scenario` to a variable of the Continuous Scenario dataset.



Minor

### Missing detail

* No activity or step has `start` or `end` times.
* *Climate Profile Generation* has no description.
* S6.1 and S6.3 have no `script`; the other six cite `copernikus_down.ipynb`.

## Parameters

Inconsistent

### One name for different variables, several names for one variable

* `Climate Variable` in S4 is bound to the `Climate Variable` variable of *Climate Datasets Step 4*; in S5 it is bound to `variable_name` of `configure_climate_data`.
* `variable_name` is received as `variable_name` (S1), `variable` (S3) and `Climate Variable` (S5).
* S3 has two parameters, `OUT_DIR` and `out_dir`, bound to the same variable.
* An output and the next step's input often differ in name: `CDS API` / `cds_request`, `final_climate_dataset` / `Final Climate Dataset`, `Annual Climate Indicator Dataset` / `Scenario Annual Climate Dataset`. That is allowed, but makes the chain harder to read.





### Two datasets hold the run settings

`configure_climate_data` holds 11 settings (bounding box, model, scenario, `start_year`, `end_year`, `variable_name`, `OUT_DIR`, `json`). *Climate Datasets Step 4* holds two more, `Climate Variable` and `Analysis Period`, which overlap `variable_name` and the start and end years. Its name reads like a placeholder.

Keep the settings in one dataset, or rename the second one for what it holds.

Minor

### No values

Parameters name a slot and what fills it, but never the value used in a run, such as which scenario or analysis period was chosen.



## Datasets



### The final profile has no file location

The physical datasets for *Climate Profile CSV* and *Climate Profile NetCDF* have no `physicalFileURL`. *Climate Profile TXT* has no physical dataset and no variables at all. So the workflow's actual deliverables are the only outputs without a file.



### One time series described three times

*Spatial Mean Climate Time Series*, *Climate Profile CSV* and *Climate Profile NetCDF* each list the same eight variables (`year`, the temperatures, precipitation flux, humidity, radiation and wind speed), but as 24 separate InstanceVariable nodes, so nothing says they are the same series.

If they are one series in different formats, describe one DataSet and point each physical dataset at it with `correspondsTo_DataSet`.



Minor

### File paths and thin descriptions

* Every `physicalFileURL` is a bare filename or a local path (`Downloads/…_CROPPED.nc`), not a resolvable URL.
* `cropped_climate_dataset`, *Historical Annual Climate Dataset* and *Climate Indicator Dataset Collection* have no variables and no description.
* No logical DataSet has a description; where there is one, it is on the physical dataset's `overview`.
* *Continuous Scenario Climate Dataset* lists one variable, `Scenario`.

## Agents and concepts

Minor

### Agents are not tied to the work

* The processing agent names its two creators, Nandia Politi and Thanasis Sfetsos, only through `AgentInRole.reference` strings, and has no `performs` link to activities or steps.
* The processing agent is not in the agent listing, which holds the two Individuals and the organization.
* The Individuals have no identifier (such as an ORCID) or contact; the organization is named only `NSCRD`.

Minor

### GSBPM concepts

* The nine concept IRIs start `http://unece.org/`, but their `skos:inScheme` is `http://www.unece.org/GSBPM-5.2`.



Minor

### Typos

* Trailing spaces in the names `Heatwave indices ` and `Mean precipitation flux `.
* S6.3 description: "spacial average".
* S2 description: "Output put in OUT\_DIR".

How this was checked: the file was parsed as JSON, following every reference by `@id` or `uri`, and as RDF with rdflib using its own context, counting only links between nodes defined in the file. Step and activity inputs and outputs were compared through the datasets each parameter's `entityBound` names.

