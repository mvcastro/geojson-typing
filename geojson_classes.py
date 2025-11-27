from typing import Any, Literal, Union

from pydantic import BaseModel, Field

type Position = tuple[float, float]

type LinearRing = list[Position]  # Um anel linear (primeiro e último ponto são iguais)
type PolygonCoords = list[LinearRing]
type MultiPolygonCoords = list[PolygonCoords]


class Point(BaseModel):
    """Modelo para uma geometria do tipo Ponto."""

    type: Literal["Point"]
    coordinates: Position


class MultiPolygon(BaseModel):
    """Modelo para uma geometria do tipo MultiPolygon."""

    type: Literal["MultiPolygon"]
    coordinates: MultiPolygonCoords


Geometry = Union[Point, MultiPolygon]


class Feature(BaseModel):
    """Modelo para um objeto Feature GeoJSON."""

    type: Literal["Feature"]
    # O campo 'geometry' pode ser qualquer um dos tipos definidos em 'Geometry'.
    # Pydantic usará o campo 'type' dentro do objeto de geometria para validar.
    geometry: Geometry = Field(..., discriminator="type")
    properties: dict[str, Any]


class FeatureCollection(BaseModel):
    """Modelo para um objeto FeatureCollection GeoJSON."""

    type: Literal["FeatureCollection"]
    features: list[Feature]
