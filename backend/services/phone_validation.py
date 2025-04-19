# Service for phone validation, including E.164, disposable, VoIP, carrier, region

def is_disposable_or_voip(phone_number: str) -> bool:
    # Placeholder: In production, use a 3rd party API or database
    # For now, treat numbers starting with '+999' as disposable/VoIP for testing
    return phone_number.startswith('+999')

def is_allowed_carrier_and_region(phone_number: str) -> bool:
    # Placeholder: In production, use carrier lookup APIs or DB
    # For now, block numbers starting with '+888' for region/carrier restriction
    return not phone_number.startswith('+888')
