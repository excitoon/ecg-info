Tools for dumping and analyzing ECG data.

# `schiller-dump`

Produces TSV file with Schiller ECG data.

## Usage

```
schiller-dump filename.raw
```

# `myocard-dump`

Produces TSV file with Myocard ECG data.

## Usage

```
myocard-dump data-path
```

# `ecg-view`

View TSV file (starting at `d:hh:mm:ss`):

```
ecg-view filename.tsv [d:]hh:mm:ss [duration]
```

## Dependencies

```
pip3 install matplotlib
```

# Supported formats

- Schiller MT-101
- МИОКАРД-ХОЛТЕР 2
