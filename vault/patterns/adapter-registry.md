---
title: Adapter Registry Pattern
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - utils/bank_sync/registry.py
  - utils/bank_sync/base.py
---

# Adapter Registry Pattern

Decorator-based adapter registry used by the bank sync system.

## How It Works

1. `base.py` defines abstract `BankAdapter` with required methods
2. `registry.py` provides `@register_adapter('bank_code')` decorator
3. Concrete adapters (e.g., `yapikredi_adapter.py`) use the decorator to register themselves
4. `get_adapter(bank_code)` looks up the registry and returns the adapter class
5. `get_available_banks()` returns list of registered bank codes and names

## Usage

```python
@register_adapter('yapikredi')
class YapiKrediAdapter(BankAdapter):
    ...

# Lookup
adapter_cls = get_adapter('yapikredi')
adapter = adapter_cls(client_id=..., client_secret=..., account_id=...)
```

## Key Points

- Registration happens at import time via decorator side effect
- New banks only require a new adapter file — no changes to existing code
- Currently only one adapter: Yapi Kredi (planned for removal — see [[planned-features]])

## Related

- [[bank-sync]]
- [[settings]]
