Tools for dumping and analyzing ECG data.

### Usage

Produce TSV file with ECG data:

```
ecg-dump filename.raw
```

View TSV file:

```
ecg-view filename.tsv [d:]hh:mm:ss [duration]
```

### Dependencies

```
pip3 install matplotlib
pip3 install progress
```

### Supported formats

- Schiller MT-101
