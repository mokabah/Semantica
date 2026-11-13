"""Optional interfaces for external models. No model implementation is shipped."""

from semantica.integrations.model_interface import FluencyModel, SimilarityModel, validated_score

__all__ = ["FluencyModel", "SimilarityModel", "validated_score"]
