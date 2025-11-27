import pytest
from pydantic import ValidationError

from geojson_classes import Feature, FeatureCollection, MultiPolygon, Point

# --- Dados de Teste Válidos ---

GEOJSON_POINT_FEATURE = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [-46.6333, -23.5505]},
    "properties": {"name": "São Paulo"},
}

GEOJSON_MULTIPOLYGON_FEATURE = {
    "type": "Feature",
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
            [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
            [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]],
        ],
    },
    "properties": {"name": "Regiões Exemplo"},
}


def test_point_model_success():
    """Testa a validação bem-sucedida de uma geometria Point."""
    data = {"type": "Point", "coordinates": [-46.6333, -23.5505]}
    point = Point.model_validate(data)
    assert point.type == "Point"
    assert point.coordinates == (-46.6333, -23.5505)


def test_multipolygon_model_success():
    """Testa a validação bem-sucedida de uma geometria MultiPolygon."""
    data = GEOJSON_MULTIPOLYGON_FEATURE["geometry"]
    multipolygon = MultiPolygon.model_validate(data)
    assert multipolygon.type == "MultiPolygon"
    assert len(multipolygon.coordinates) == 2
    assert len(multipolygon.coordinates[0][0]) == 5  # 5 posições no primeiro polígono


def test_feature_with_point_success():
    """Testa a validação bem-sucedida de uma Feature com um Point."""
    feature = Feature.model_validate(GEOJSON_POINT_FEATURE)
    assert feature.type == "Feature"
    assert isinstance(feature.geometry, Point)
    assert feature.geometry.type == "Point"


def test_feature_collection_success():
    """Testa a validação bem-sucedida de uma FeatureCollection."""
    data = {
        "type": "FeatureCollection",
        "features": [GEOJSON_POINT_FEATURE, GEOJSON_MULTIPOLYGON_FEATURE],
    }
    collection = FeatureCollection.model_validate(data)
    assert collection.type == "FeatureCollection"
    assert len(collection.features) == 2
    assert isinstance(collection.features[0].geometry, Point)
    assert isinstance(collection.features[1].geometry, MultiPolygon)


# --- Testes de Validação com Falha ---


def test_point_invalid_coordinates_type():
    """Testa a falha de validação para Point com coordenadas de tipo errado."""
    invalid_data = {"type": "Point", "coordinates": ["a", "b"]}
    with pytest.raises(ValidationError):
        Point.model_validate(invalid_data)


def test_point_invalid_coordinates_length():
    """Testa a falha de validação para Point com número incorreto de coordenadas."""
    invalid_data = {"type": "Point", "coordinates": [-46.6333]}
    with pytest.raises(ValidationError):
        Point.model_validate(invalid_data)


def test_feature_missing_properties():
    """Testa a falha de validação para Feature sem o campo 'properties'."""
    invalid_data = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-46.6333, -23.5505]},
        # "properties": {} // Campo obrigatório ausente
    }
    with pytest.raises(ValidationError) as excinfo:
        Feature.model_validate(invalid_data)
    # Verifica se o erro é sobre o campo 'properties' ausente
    assert "properties" in str(excinfo.value)


def test_feature_unknown_geometry_type():
    """Testa a falha de validação para Feature com um tipo de geometria desconhecido."""
    invalid_data = {
        "type": "Feature",
        "geometry": {"type": "Triangle", "coordinates": [[0, 0], [1, 1], [0, 1]]},
        "properties": {},
    }
    with pytest.raises(ValidationError): # as excinfo:
        Feature.model_validate(invalid_data)
    # O discriminador 'type' não encontrará um modelo correspondente
    # assert "No match for discriminator 'type'" in str(excinfo.value)


def test_feature_collection_invalid_feature():
    """Testa a falha de validação para FeatureCollection com uma feature inválida."""
    invalid_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point"}}
        ],  # Geometria inválida
    }
    with pytest.raises(ValidationError):
        FeatureCollection.model_validate(invalid_data)
