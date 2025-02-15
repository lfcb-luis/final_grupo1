# tests/test_features.py
import pytest
from src.features.feature_extractor import FeatureExtractor

class TestFeatureExtractor:
    """Pruebas para el extractor de características."""

    @pytest.fixture
    def extractor(self):
        """Fixture que proporciona una instancia de FeatureExtractor."""
        return FeatureExtractor()

    @pytest.fixture
    def sample_text_blocks_agua(self):
        """Fixture con datos de ejemplo de una factura de agua."""
        return [
            {'text': 'Fecha de la factura: 18-Abr-2024', 'bbox': [10, 10, 100, 30]},
            {'text': 'TOTAL A PAGAR: $8,640', 'bbox': [10, 40, 100, 60]},
            {'text': 'Fecha limite sin recargo: 02-May-2024', 'bbox': [10, 70, 100, 90]}
        ]

    @pytest.fixture
    def sample_text_blocks_luz(self):
        """Fixture con datos de ejemplo de una factura de luz."""
        return [
            {'text': 'MATRÍCULA >> 2121717', 'bbox': [10, 10, 100, 30]},
            {'text': 'Fecha de Emisión: 17/MAY/2024', 'bbox': [10, 40, 100, 60]},
            {'text': 'TOTAL $35,643', 'bbox': [10, 70, 100, 90]}
        ]

    def test_extract_matricula(self, extractor, sample_text_blocks_luz):
        """Prueba la extracción del número de matrícula."""
        fields = extractor.extract_fields(sample_text_blocks_luz)
        assert fields['matricula'] == '2121717'

    def test_extract_fecha_emision(self, extractor, sample_text_blocks_agua):
        """Prueba la extracción de la fecha de emisión."""
        fields = extractor.extract_fields(sample_text_blocks_agua)
        assert fields['fecha_emision'] == '18-Abr-2024'

    def test_extract_total(self, extractor, sample_text_blocks_agua):
        """Prueba la extracción del monto total."""
        fields = extractor.extract_fields(sample_text_blocks_agua)
        assert fields['total'] == '8,640'

    def test_extract_fecha_vencimiento(self, extractor, sample_text_blocks_agua):
        """Prueba la extracción de la fecha de vencimiento."""
        fields = extractor.extract_fields(sample_text_blocks_agua)
        assert fields['fecha_vencimiento'] == '02-May-2024'

    def test_missing_fields(self, extractor):
        """Prueba el manejo de campos faltantes."""
        empty_blocks = [{'text': 'Texto irrelevante', 'bbox': [0, 0, 10, 10]}]
        fields = extractor.extract_fields(empty_blocks)
        assert fields['matricula'] is None
        assert fields['fecha_emision'] is None
        assert fields['total'] is None

    def test_get_field_location(self, extractor, sample_text_blocks_agua):
        """Prueba la obtención de coordenadas de un campo."""
        location = extractor.get_field_location(sample_text_blocks_agua, 'TOTAL')
        assert location == [10, 40, 100, 60]

    def test_get_field_location_not_found(self, extractor, sample_text_blocks_agua):
        """Prueba cuando no se encuentra un campo."""
        location = extractor.get_field_location(sample_text_blocks_agua, 'Campo inexistente')
        assert location is None