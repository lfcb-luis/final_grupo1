# tests/test_features_extractor_generic.py
import pytest
from src.features.feature_extractor import FeatureExtractor

class TestFeatureExtractorGeneric:
    """Pruebas genéricas para el extractor de características."""

    @pytest.fixture
    def extractor(self):
        """Fixture que proporciona una instancia de FeatureExtractor."""
        return FeatureExtractor()

    @pytest.fixture
    def factura_gas(self):
        """Fixture con datos de ejemplo de una factura de gas."""
        return [
            {
                'text': 'EFIGAS GAS NATURAL S.A E.S.P',
                'confidence': 0.98,
                'bbox': [10, 10, 200, 30]
            },
            {
                'text': 'Nro de identificación: 222222222',
                'confidence': 0.95,
                'bbox': [10, 40, 200, 60]
            },
            {
                'text': 'Tu factura fue generada el 04/02/2025 01:00:44',
                'confidence': 0.97,
                'bbox': [10, 70, 200, 90]
            },
            {
                'text': 'TOTAL A PAGAR: $ 23.286',
                'confidence': 0.99,
                'bbox': [10, 100, 200, 120]
            },
            {
                'text': 'Si no pagas antes de 17/02/2025',
                'confidence': 0.96,
                'bbox': [10, 130, 200, 150]
            }
        ]

    @pytest.fixture
    def factura_luz(self):
        """Fixture con datos de ejemplo de una factura de luz."""
        return [
            {
                'text': 'MATRÍCULA >>> 2121717',
                'confidence': 0.98,
                'bbox': [10, 10, 200, 30]
            },
            {
                'text': 'Fecha de Emisión: 17/MAY/2024',
                'confidence': 0.97,
                'bbox': [10, 40, 200, 60]
            },
            {
                'text': 'Tengo plazo para pagar hasta: 27/MAY/2024',
                'confidence': 0.96,
                'bbox': [10, 70, 200, 90]
            },
            {
                'text': 'TOTAL $35,643',
                'confidence': 0.99,
                'bbox': [10, 100, 200, 120]
            }
        ]

    def test_campos_comunes_gas(self, extractor, factura_gas):
        """Prueba la extracción de campos comunes en factura de gas."""
        fields = extractor.extract_fields(factura_gas)
        
        assert 'identificacion' in fields
        assert 'fecha_expedicion' in fields
        assert 'fecha_vencimiento' in fields
        assert 'total' in fields
        
        assert fields['identificacion'] == '222222222'
        assert '2025' in fields['fecha_expedicion']
        assert '17-02-2025' in fields['fecha_vencimiento']
        assert fields['total'] == '23286'

    def test_campos_comunes_luz(self, extractor, factura_luz):
        """Prueba la extracción de campos comunes en factura de luz."""
        fields = extractor.extract_fields(factura_luz)
        
        assert 'identificacion' in fields
        assert 'fecha_expedicion' in fields
        assert 'fecha_vencimiento' in fields
        assert 'total' in fields
        
        assert fields['identificacion'] == '2121717'
        assert 'MAY-2024' in fields['fecha_expedicion']
        assert '27-MAY-2024' in fields['fecha_vencimiento']
        assert fields['total'] == '35643'

    def test_baja_confianza(self, extractor):
        """Prueba el manejo de datos con baja confianza."""
        text_blocks = [
            {
                'text': 'TOTAL A PAGAR: $100',
                'confidence': 0.3  # Baja confianza
            }
        ]
        fields = extractor.extract_fields(text_blocks)
        assert len(fields) == 0

    def test_diferentes_formatos_fecha(self, extractor):
        """Prueba diferentes formatos de fecha."""
        formatos_fecha = [
            {'text': 'Fecha de emisión: 01/05/2024', 'confidence': 0.95},
            {'text': 'Fecha de emisión: 01-Mayo-2024', 'confidence': 0.95},
            {'text': 'Fecha de emisión: 2024/05/01', 'confidence': 0.95}
        ]
        
        for block in formatos_fecha:
            fields = extractor.extract_fields([block])
            assert 'fecha_expedicion' in fields

    def test_diferentes_formatos_total(self, extractor):
        """Prueba diferentes formatos de total."""
        formatos_total = [
            {'text': 'Total a pagar: $1,234.56', 'confidence': 0.95},
            {'text': 'TOTAL: $1.234,56', 'confidence': 0.95},
            {'text': 'Total: 1234.56', 'confidence': 0.95}
        ]
        
        for block in formatos_total:
            fields = extractor.extract_fields([block])
            assert 'total' in fields

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