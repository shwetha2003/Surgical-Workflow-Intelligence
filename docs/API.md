# API Documentation

## SurgicalDataLoader
```python
loader = SurgicalDataLoader(data_path="data/")
procedures, tools, notes, sensor = loader.generate_sample_data(500)
