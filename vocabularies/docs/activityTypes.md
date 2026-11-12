---
comment: | 
  WARNING: This file is generated. Any edits will be lost!
format:
  html:
    ascii: true
    toc: true
    toc-depth: 4
    number-sections: true
    anchor-sections: false
    number-depth: 8
execute:
  echo: false
---

[]{#CDIFprovenanceactivitytypes}

# **Concept scheme:** CDIF provenance activity types

Vocabulary last modified:  2026-10-27

subtitle: 
  Kinds of activity in a research, laboratory or data workflow. A workflow step (schema:step, or a prov:Activity in a multi-activity chain) is typed with one of these concepts through schema:additionalType, while its schema:name stays free to say what the step specifically did. Each concept is mapped to the provenance activity classes proposed at the Dagstuhl workshop (PROV_Classes.ttl).

Namespace: 
[`https://w3id.org/cdif/provenance/activityType`](https://w3id.org/cdif/provenance/activityType)

- **Deprecated.**
- **Replaced by:** [`cdifact:conceptScheme`](https://w3id.org/cdif/concepts/provenance/activity/conceptScheme)
- **Editorial note:** DEPRECATED 2026-11-11. Superseded by the CDIF
provenance activity vocabulary,
https://w3id.org/cdif/concepts/provenance/activity/conceptScheme. Each
concept here is owl:deprecated: the generic ones point to their
replacement with dcterms:isReplacedBy; the ADA laboratory steps moved
to the geochemistry activity vocabulary,
https://w3id.org/geochem/vocabulary/activityTypes; four have no
replacement, and extracting has only related concepts. These IRIs stay
resolvable.
- **Editorial note:** Draft, 2026-10-27. Two layers. The top layer is
every activity class on the Activity sheet of the ProvWork2025
spreadsheet (23 classes; definitions and examples from the sheet, with
its spelling slips fixed as PROV_Classes.ttl fixes them). Data
cleaning and Deriving sit under Data transforming and Creating because
their sheet definitions say so ('A data transformation during
which...', 'A creation process during which...'); the rest are top
concepts.
- **Editorial note:** The Dagstuhl class URIs (dag: prefix) are taken
from PROV_Classes.ttl in this repository; the sheet has labels but no
URIs. That namespace is a draft and may not resolve. Each top-layer
concept is a skos:exactMatch to its class; the ADA-derived concepts
carry skos:broadMatch to the class of the concept they sit under.
Concepts the workshop marked as tentative (a question mark on the
label, or 'potential new categories, components of other classes, or
folded into context') say so in their own editorial note; revisit
them, and the ADA concepts under them, when the workshop settles them.
- **Editorial note:** The
https://w3id.org/cdif/provenance/activityType identifiers do not
resolve yet; they need a w3id.org redirect.
- **Editorial note:** The narrower layer is the laboratory steps
actually used in the 500 TAPP plans in the ADA method registry (Sample
preparation 320, Data processing 264, Data acquisition 147, Quality
control 86, Instrument calibration 83, Ion milling 39, Sample
digestion 30, and seven technique-specific variants used by 1 to 4
plans each). Each sits under the general activity it specialises; the
sheet's Geochemistry column supports Sample preparation under
Conditioning (intentional) ('crushing, milling; dissolution, leaching,
extraction'), Data acquisition under Observing / measuring and Data
processing under Data transforming.

**History**


- [Accessing](#accessing)

- [Aggregating](#aggregating)

- [Analysing](#analysing)

- [Archiving](#archiving)

- [Cataloguing](#cataloguing)

- [Consuming](#consuming)

- [Data validating](#datavalidating)

- [Extracting](#extracting)

- [Harmonising](#harmonising)

- [Integrating](#integrating)

- [Conditioning (passive)](#passiveconditioning)

- [Preserving](#preserving)

- [Provisioning](#provisioning)

- [Sampling](#sampling)

- [Calibrating](#calibrating)
    - [Instrument calibration](#instrumentcalibration)

- [Configuring](#configuring)
    - [Instrument tuning](#instrumenttuning)

- [Creating](#creating)
    - [Deriving](#deriving)

- [Conditioning (intentional)](#intentionalconditioning)
    - [Sample preparation](#samplepreparation)
        - [Ion milling](#ionmilling)
        - [Sample digestion](#sampledigestion)

- [Observing / measuring](#observingmeasuring)
    - [Data acquisition](#dataacquisition)

- [Quality controlling](#qualitycontrolling)
    - [Quality control](#qualitycontrol)

- [Data transforming](#datatransforming)
    - [Data cleaning](#datacleaning)
    - [Data processing](#dataprocessing)

**Concepts**

[]{#accessing}

##  Accessing
- **Deprecated.**
- **Replaced by:** [`cdifact:Access`](https://w3id.org/cdif/concepts/provenance/activity/Access)
- An activity during which an agent realises its rights and abilities
to approach and interact with an entity.
- Concept URI: https://w3id.org/cdif/provenance/activityType/accessing



[]{#aggregating}

##  Aggregating
- **Deprecated.**
- **Replaced by:** [`cdifact:Aggregation`](https://w3id.org/cdif/concepts/provenance/activity/Aggregation)
- **Editorial note:** Tentative in ProvWork2025: the workshop marked
this class as a potential new category, a component of other classes,
or something to fold into context.
- An activity during which multiple entities are gathered together and
assembled into a whole based on a defined set of criteria.
- Concept URI: https://w3id.org/cdif/provenance/activityType/aggregating



[]{#analysing}

##  Analysing
- **Deprecated.**
- **Replaced by:** [`cdifact:Analysis`](https://w3id.org/cdif/concepts/provenance/activity/Analysis)
- An activity during which one or more entities are studied by
examining their constituent parts and the interrelationships between
those parts in order to increase one's knowledge about those entities.
- Concept URI: https://w3id.org/cdif/provenance/activityType/analysing



[]{#archiving}

##  Archiving
- **Deprecated.**
- **Replaced by:** [`cdifact:Archiving`](https://w3id.org/cdif/concepts/provenance/activity/Archiving)
- An activity during which an entity is transferred to a facility
charged with its long-term (generally >10 years) preservation.
- Concept URI: https://w3id.org/cdif/provenance/activityType/archiving



[]{#cataloguing}

##  Cataloguing
- **Deprecated.**
- **Replaced by:** [`cdifact:Cataloguing`](https://w3id.org/cdif/concepts/provenance/activity/Cataloguing)
- An activity during which the existence of an entity is described in
a systematic list.
- Concept URI: https://w3id.org/cdif/provenance/activityType/cataloguing



[]{#consuming}

##  Consuming
- **Deprecated.**
- **Editorial note:** Deprecated 2026-11-11 with no replacement: the
CDIF provenance activity vocabulary has no counterpart.
- An activity during which an agent acquires and uses an entity.
- Concept URI: https://w3id.org/cdif/provenance/activityType/consuming



[]{#datavalidating}

##  Data validating
- **Deprecated.**
- **Replaced by:** [`cdifact:DataValidation`](https://w3id.org/cdif/concepts/provenance/activity/DataValidation)
- An activity during which a volume of data is evaluated in relation
to some specification or criteria, usually assessing its soundness,
justifiability, or appropriateness for a given purpose.
- Concept URI: https://w3id.org/cdif/provenance/activityType/dataValidating



[]{#extracting}

##  Extracting
- **Deprecated.**
- **Editorial note:** Deprecated 2026-11-11 with no replacement: no
concept in the CDIF provenance activity vocabulary means moving an
entity to a new location. Data Extraction and Extraction (Sample) are
related, not equivalent.
- An activity during which an entity is moved to a new location.
- Concept URI: https://w3id.org/cdif/provenance/activityType/extracting



[]{#harmonising}

##  Harmonising
- **Deprecated.**
- **Replaced by:** [`cdifact:DataHarmonisation`](https://w3id.org/cdif/concepts/provenance/activity/DataHarmonisation)
- **Editorial note:** Tentative in ProvWork2025: the workshop marked
this class as a potential new category, a component of other classes,
or something to fold into context.
- An activity during which a set of entities are transformed to
regularise their properties, allowing meaningful collective treatment.
- Concept URI: https://w3id.org/cdif/provenance/activityType/harmonising



[]{#integrating}

##  Integrating
- **Deprecated.**
- **Replaced by:** [`cdifact:DataIntegration`](https://w3id.org/cdif/concepts/provenance/activity/DataIntegration)
- **Editorial note:** Tentative in ProvWork2025: the workshop marked
this class as a potential new category, a component of other classes,
or something to fold into context.
- An activity during which multiple entities are unified into a
coherent whole, often losing their distinctiveness.
- Concept URI: https://w3id.org/cdif/provenance/activityType/integrating



[]{#passiveconditioning}

##  Conditioning (passive)
- **Deprecated.**
- **Editorial note:** Deprecated 2026-11-11 with no replacement: the
CDIF provenance activity vocabulary has no counterpart.
- A non-intentional process in which the state of an entity is
changed, such that it impacts or precipitates a planned and subsequent
activity.
- Concept URI: https://w3id.org/cdif/provenance/activityType/passiveConditioning



[]{#preserving}

##  Preserving
- **Deprecated.**
- **Replaced by:** [`cdifact:DigitalPreservation`](https://w3id.org/cdif/concepts/provenance/activity/DigitalPreservation)
- An activity during which an entity is modified to stabilise its
make-up and properties, facilitating future use.
- Concept URI: https://w3id.org/cdif/provenance/activityType/preserving



[]{#provisioning}

##  Provisioning
- **Deprecated.**
- **Editorial note:** Deprecated 2026-11-11 with no replacement: the
CDIF provenance activity vocabulary has no counterpart.
- An activity during which an agent supplies an entity to other
agents.
- Concept URI: https://w3id.org/cdif/provenance/activityType/provisioning



[]{#sampling}

##  Sampling
- **Deprecated.**
- **Replaced by:** [`cdifact:Sampling`](https://w3id.org/cdif/concepts/provenance/activity/Sampling)
- An activity in which a portion or part of an entity is extracted
from or identified within a whole.
- Concept URI: https://w3id.org/cdif/provenance/activityType/sampling



[]{#calibrating}

##  Calibrating
- **Deprecated.**
- **Replaced by:** [`cdifact:Calibration`](https://w3id.org/cdif/concepts/provenance/activity/Calibration)
- **Editorial note:** Tentative in ProvWork2025: the workshop marked
this class as a potential new category, a component of other classes,
or something to fold into context.
- An activity during which measurement data produced by an entity are
compared to a reference dataset with known accuracy in order to
establish, verify, or document the accuracy of the entity.
- Concept URI: https://w3id.org/cdif/provenance/activityType/calibrating


[]{#instrumentcalibration}

###  Instrument calibration
- **Deprecated.**
- **Replaced by:** [`geochemvoc:instrumentCalibration`](https://w3id.org/geochem/vocabulary/instrumentCalibration)
- Child of:
 [`calibrating`](#calibrating)
- An activity that measures reference materials or standards of known
value to establish the relationship between the instrument's response
and the quantity being measured.
- Concept URI: https://w3id.org/cdif/provenance/activityType/instrumentCalibration



[]{#configuring}

##  Configuring
- **Deprecated.**
- **Replaced by:** [`cdifact:Configuration`](https://w3id.org/cdif/concepts/provenance/activity/Configuration)
- **Editorial note:** Tentative in ProvWork2025: the workshop marked
this class as a potential new category, a component of other classes,
or something to fold into context.
- An activity during which an entity is modified to grant it desirable
properties or dispose it to desirable behaviour.
- Concept URI: https://w3id.org/cdif/provenance/activityType/configuring


[]{#instrumenttuning}

###  Instrument tuning
- **Deprecated.**
- **Replaced by:** [`geochemvoc:instrumentTuning`](https://w3id.org/geochem/vocabulary/instrumentTuning)
- Child of:
 [`configuring`](#configuring)
- An activity that adjusts instrument settings to optimise performance
for a measurement, judged by the instrument's response rather than
against reference materials of known value.
- Concept URI: https://w3id.org/cdif/provenance/activityType/instrumentTuning



[]{#creating}

##  Creating
- **Deprecated.**
- **Replaced by:** [`cdifact:Creation`](https://w3id.org/cdif/concepts/provenance/activity/Creation)
- An activity through which an entity is brought into existence.
Serves as a superclass for other more expressive classes that create
entities, such as authoring.
- Concept URI: https://w3id.org/cdif/provenance/activityType/creating


[]{#deriving}

###  Deriving
- **Deprecated.**
- **Replaced by:** [`cdifact:Derivation`](https://w3id.org/cdif/concepts/provenance/activity/Derivation)
- **Editorial note:** Tentative in ProvWork2025: the workshop marked
this class as a potential new category, a component of other classes,
or something to fold into context.
- Child of:
 [`creating`](#creating)
- A creation process during which a new entity arises from parts or
all of pre-existing entities.
- Concept URI: https://w3id.org/cdif/provenance/activityType/deriving



[]{#intentionalconditioning}

##  Conditioning (intentional)
- **Deprecated.**
- **Editorial note:** Deprecated 2026-11-11 with no replacement: the
CDIF provenance activity vocabulary has no counterpart.
- An activity in which the state of an entity is intentionally changed
by an agent, in preparation for a specified and subsequent activity.
- Concept URI: https://w3id.org/cdif/provenance/activityType/intentionalConditioning


[]{#samplepreparation}

###  Sample preparation
- **Deprecated.**
- **Replaced by:** [`geochemvoc:samplePreparation`](https://w3id.org/geochem/vocabulary/samplePreparation)
- Child of:
 [`intentionalConditioning`](#intentionalConditioning)
- An activity that changes the physical or chemical state of a sample
to make it suitable for measurement, for example cutting, mounting,
polishing, coating, crushing, sieving or dissolving it.
- Concept URI: https://w3id.org/cdif/provenance/activityType/samplePreparation


[]{#ionmilling}

####  Ion milling
- **Deprecated.**
- **Replaced by:** [`geochemvoc:ionMilling`](https://w3id.org/geochem/vocabulary/ionMilling)
- Child of:
 [`samplePreparation`](#samplePreparation)
- Sample preparation that thins or shapes a sample by sputtering it
with an ion beam, for example to make an electron-transparent section.
- Concept URI: https://w3id.org/cdif/provenance/activityType/ionMilling


[]{#sampledigestion}

####  Sample digestion
- **Deprecated.**
- **Replaced by:** [`geochemvoc:sampleDigestion`](https://w3id.org/geochem/vocabulary/sampleDigestion)
- Child of:
 [`samplePreparation`](#samplePreparation)
- Sample preparation that dissolves a solid sample, typically in acid,
to produce a solution for analysis.
- Concept URI: https://w3id.org/cdif/provenance/activityType/sampleDigestion



[]{#observingmeasuring}

##  Observing / measuring
- **Deprecated.**
- **Replaced by:** [`cdifact:Measurement`](https://w3id.org/cdif/concepts/provenance/activity/Measurement)
- **Replaced by:** [`cdifact:Observation`](https://w3id.org/cdif/concepts/provenance/activity/Observation)
- An activity during which an entity gathers data or information about
another entity or itself. Measuring is observing during which
reference standards or similar entities are used for the quantitative
comparison of properties.
- Concept URI: https://w3id.org/cdif/provenance/activityType/observingMeasuring


[]{#dataacquisition}

###  Data acquisition
- **Deprecated.**
- **Replaced by:** [`geochemvoc:dataAcquisition`](https://w3id.org/geochem/vocabulary/dataAcquisition)
- Child of:
 [`observingMeasuring`](#observingMeasuring)
- An activity in which an instrument or observer measures or observes
the object of study and records the result as data.
- Concept URI: https://w3id.org/cdif/provenance/activityType/dataAcquisition



[]{#qualitycontrolling}

##  Quality controlling
- **Deprecated.**
- **Replaced by:** [`cdifact:QualityControl`](https://w3id.org/cdif/concepts/provenance/activity/QualityControl)
- **Editorial note:** Tentative in ProvWork2025: the workshop label
carries a question mark.
- An activity during which an entity's compliance to a set of defined
criteria is assessed, resulting in acceptance or rejection of that
entity in a set of further activities.
- Concept URI: https://w3id.org/cdif/provenance/activityType/qualityControlling


[]{#qualitycontrol}

###  Quality control
- **Deprecated.**
- **Replaced by:** [`geochemvoc:qualityControl`](https://w3id.org/geochem/vocabulary/qualityControl)
- Child of:
 [`qualityControlling`](#qualityControlling)
- An activity that assesses data or a process against defined
criteria, for example measuring secondary standards, checking
precision and accuracy, or flagging anomalous values.
- Concept URI: https://w3id.org/cdif/provenance/activityType/qualityControl



[]{#datatransforming}

##  Data transforming
- **Deprecated.**
- **Replaced by:** [`cdifact:DataTransformation`](https://w3id.org/cdif/concepts/provenance/activity/DataTransformation)
- An activity during which a volume of data is modified.
- Concept URI: https://w3id.org/cdif/provenance/activityType/dataTransforming


[]{#datacleaning}

###  Data cleaning
- **Deprecated.**
- **Replaced by:** [`cdifact:DataCleaning`](https://w3id.org/cdif/concepts/provenance/activity/DataCleaning)
- Child of:
 [`dataTransforming`](#dataTransforming)
- A data transformation during which erroneous, duplicated, or
corrupted data is removed from a volume of data.
- Concept URI: https://w3id.org/cdif/provenance/activityType/dataCleaning


[]{#dataprocessing}

###  Data processing
- **Deprecated.**
- **Replaced by:** [`geochemvoc:dataProcessing`](https://w3id.org/geochem/vocabulary/dataProcessing)
- Child of:
 [`dataTransforming`](#dataTransforming)
- An activity that transforms acquired data into reported results, for
example background and blank correction, drift correction, matrix
correction, applying a calibration, or converting units.
- **Alternate labels:**
Data reduction
- Concept URI: https://w3id.org/cdif/provenance/activityType/dataProcessing



