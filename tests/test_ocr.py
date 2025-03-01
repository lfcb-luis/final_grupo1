# tests/test_ocr.py
import pytest
from src.ocr.ocr_engine import OCREngine

class TestOCREngine:
    """Pruebas para el motor OCR."""

    @pytest.fixture
    def ocr_engine(self):
        """Fixture que proporciona una instancia de OCREngine."""
        return OCREngine()

    # def test_extract_date(self, ocr_engine):
    #     """Prueba la extracción de fechas."""
    #     sample_results = [
    #         {'text': 'Fecha de la factura: 18-Abr-2024', 'confidence': 0.95},
    #         {'text': 'Fecha de vencimiento: 30-Abr-2024', 'confidence': 0.92}
    #     ]
    #     date_info = ocr_engine.extract_date(sample_results)
    #     assert date_info['fecha_emision'] == '2024-04-18'
    #     assert len(date_info['raw_dates']) == 1

    # def test_extract_total(self, ocr_engine):
    #     """Prueba la extracción de totales."""
    #     sample_results = [
    #         {'text': 'Subtotal: $1,500', 'confidence': 0.98},
    #         {'text': 'Impuestos: $300', 'confidence': 0.97},
    #         {'text': 'TOTAL: $1,800', 'confidence': 0.99}
    #     ]
    #     total_info = ocr_engine.extract_total(sample_results)
    #     assert total_info['total'] == '1800.00'
    #     assert len(total_info['raw_amounts']) == 1

    def test_standardize_date(self, ocr_engine):
        """Prueba la estandarización de fechas."""
        date_str = '18/04/2024'
        standardized_date = ocr_engine._standardize_date(date_str)
        assert standardized_date == '2024-04-18'

    def test_standardize_amount(self, ocr_engine):
        """Prueba la estandarización de importes."""
        amount_str = '$1,500.00'
        standardized_amount = ocr_engine._standardize_amount(amount_str)
        assert standardized_amount == '1500.00'

    def test_process_image_with_no_text(self, ocr_engine, mocker):
        """Prueba el procesamiento de una imagen sin texto."""
        mocker.patch.object(OCREngine, 'extract_date', return_value={'fecha_emision': None, 'raw_dates': []})
        mocker.patch.object(OCREngine, 'extract_total', return_value={'total': None, 'raw_amounts': []})
        
        result = ocr_engine.process_image([])
        assert result['fields'] == {}
        assert result['confidence'] == 0
        assert result['raw_text'] == "No se detectó texto"