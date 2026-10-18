
# CareFlow: Initial Process Mining Results

## Dataset
- Source: HospitalOPD dataset from Mendeley Data
- Original records: 62,422
- Original columns: 25
- Working columns after removing one empty column: 24
- Unique appointment IDs: 49,912

## Data quality checks
- No completely duplicated rows were detected.
- The Unnamed: 2 column was completely empty and removed from the working copy.
- Some service timestamps were missing.
- Some laboratory and imaging timestamps occurred before the recorded appointment start.

## Initial process mining
- An initial event log was created from appointment, prescription, laboratory,
  imaging, and pharmacy start timestamps.
- The most frequent observed transition was Appointment -> Prescription Started.
- Repeated activity transitions require further validation before clinical interpretation.

## Next steps
- Investigate repeated service records and timestamp ordering.
- Validate appointment-level event sequences.
- Develop a process map and dashboard after data validation.
