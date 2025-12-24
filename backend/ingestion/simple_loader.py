from ingestion.loaders.unified_scheme_loader import UnifiedSchemeLoader

loader = UnifiedSchemeLoader()
schemes = loader.load_all_schemes()

for s in schemes:
    print("-", s["title"])
