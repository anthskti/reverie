def calculate_environmental_impact(weight_kg: float, fabric_type: str) -> dict:
    """Calculates the environmental savings of diverting a garment from a landfill."""
    multiplier = 2700 if fabric_type.lower() == "cotton" else 1000
    return {
        "water_saved_liters": weight_kg * multiplier,
        "co2_offset_kg": weight_kg * 15.0,
        "landfill_diverted_kg": weight_kg,
    }
