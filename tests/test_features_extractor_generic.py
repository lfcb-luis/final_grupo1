# tests/test_features_extractor_generic.py
import pytest
from src.features.feature_extractor import FeatureExtractor

class TestFeatureExtractorGeneric:
    """Pruebas genéricas para el extractor de características de fechas y totales."""

    @pytest.fixture
    def extractor(self):
        """Fixture que proporciona una instancia de FeatureExtractor."""
        return FeatureExtractor()

    def test_diferentes_formatos_fecha(self, extractor):
        """Prueba diferentes formatos de fecha."""
        formatos_fecha = [
            {'text': 'Fecha de emisión: 01/05/2024', 'confidence': 0.95},
            {'text': 'Fecha de emisión: 01-Mayo-2024', 'confidence': 0.95},
            {'text': 'Fecha de emisión: 2024/05/01', 'confidence': 0.95},
            {'text': 'Fecha de emisión: 17/MAY/2024', 'confidence': 0.95},
            {'text': 'Fecha de emisión: 01-abril-2024', 'confidence': 0.95}
        ]
        
        for block in formatos_fecha:
            fields = extractor.extract_fields([block])
            assert 'fecha_expedicion' in fields, f"Falló con formato: {block['text']}"

    def test_diferentes_formatos_total(self, extractor):
        """Prueba diferentes formatos de total."""
        formatos_total = [
            {'text': 'Total a pagar: $1,234.56', 'confidence': 0.95},
            {'text': 'TOTAL: $1.234,56', 'confidence': 0.95},
            {'text': 'Total: 1234.56', 'confidence': 0.95},
            {'text': 'TOTAL A PAGAR: $ 23.286', 'confidence': 0.95},
            {'text': 'TOTAL $35,643', 'confidence': 0.95}
        ]
        
        for block in formatos_total:
            fields = extractor.extract_fields([block])
            assert 'total' in fields, f"Falló con formato: {block['text']}"

    def test_casos_especificos_fecha(self, extractor):
        """Prueba casos específicos de extracción de fecha."""
        casos_fecha = [
            {'text': 'Factura generada el 04/02/2025', 'confidence': 0.97},
            {'text': 'Fecha limite: 27/MAY/2024', 'confidence': 0.96}
        ]
        
        for block in casos_fecha:
            fields = extractor.extract_fields([block])
            assert 'fecha_expedicion' in fields or 'fecha_vencimiento' in fields, \
                f"Falló con formato: {block['text']}"

    def test_casos_especificos_total(self, extractor):
        """Prueba casos específicos de extracción de total."""
        casos_total = [
            {'text': 'TOTAL A PAGAR: $ 23.286', 'confidence': 0.99},
            {'text': 'Importe total: $35,643', 'confidence': 0.98}
        ]
        
        for block in casos_total:
            fields = extractor.extract_fields([block])
            assert 'total' in fields, f"Falló con formato: {block['text']}"

    def test_entrada_invalida(self, extractor):
        """Prueba el manejo de entradas inválidas."""
        with pytest.raises(ValueError):
            extractor.extract_fields(None)
        
        with pytest.raises(ValueError):
            extractor.extract_fields("no soy una lista")

    def test_texto_vacio(self, extractor):
        """Prueba el manejo de texto vacío."""
        fields = extractor.extract_fields([])
        assert len(fields) == 0
        
        fields = extractor.extract_fields([{'text': '', 'confidence': 0.95}])
        assert len(fields) == 0