_adapter_registry = {}


def register_adapter(cls):
    """Class decorator to register a bank adapter."""
    _adapter_registry[cls.bank_code] = cls
    return cls


def get_adapter(bank_code):
    """Get adapter class by bank code."""
    adapter_cls = _adapter_registry.get(bank_code)
    if not adapter_cls:
        raise ValueError(f"No adapter registered for bank code: {bank_code}")
    return adapter_cls


def get_available_banks():
    """Return list of (bank_code, bank_name) tuples for all registered adapters."""
    return [(cls.bank_code, cls.bank_name) for cls in _adapter_registry.values()]
