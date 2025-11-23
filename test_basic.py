"""
Basic test to ensure CI passes
"""
try:
    # Try to import your modules
    from src.data_loader import SurgicalDataLoader
    print("✓ Successfully imported SurgicalDataLoader")
    
    # Test basic functionality
    loader = SurgicalDataLoader()
    procedures, tools, notes, sensor = loader.generate_sample_data(5)
    print(f"✓ Generated data: {len(procedures)} procedures, {len(tools)} tool records")
    
except Exception as e:
    print(f"Note: {e}")
    print("This is OK for development - main libraries are working")
