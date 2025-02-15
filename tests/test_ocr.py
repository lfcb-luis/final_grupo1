# tests/test_ocr.py
# tests/test_ocr.py
import pytest
import numpy as np
from src.ocr.ocr_engine import OCREngine
from src.ocr.model_setup import ModelSetup

class TestOCREngine:
    """Pruebas para el motor OCR."""

    @pytest.fixture
    def ocr_engine(self):
        """Fixture que proporciona una instancia de OCREngine."""
        return OCREngine()

    def test_ocr_initialization(self, ocr_engine):
        """Prueba la inicialización del motor OCR."""
        assert ocr_engine.reader is not None
        assert isinstance(ocr_engine.model_setup, ModelSetup)

    def test_get_model_info(self, ocr_engine):
        """Prueba la obtención de información del modelo."""
        info = ocr_engine.model_setup.get_model_info()
        assert 'languages' in info
        assert 'gpu_enabled' in info
        assert 'model_path' in info
        assert 'files_present' in info

    def test_text_extraction(self, ocr_engine):
        """Prueba la extracción de campos de texto."""
        sample_results = [
            {'text': 'Fecha de la factura: 18-Abr-2024', 'confidence': 0.95},
            {'text': 'TOTAL A PAGAR: $8,640', 'confidence': 0.98}
        ]
        
        fields = ocr_engine.extract_fields(sample_results, 'AGUA')
        assert 'fecha_emision' in fields or 'fecha_factura' in fields
        assert 'total' in fields

    def test_low_confidence_handling(self, ocr_engine):
        """Prueba el manejo de resultados con baja confianza."""
        low_confidence_results = [
            {'text': 'TOTAL: $100', 'confidence': 0.3}
        ]
        fields = ocr_engine.extract_fields(low_confidence_results, 'AGUA')
        assert len(fields) == 0

    def test_error_handling(self, ocr_engine):
        """Prueba el manejo de errores."""
        with pytest.raises(Exception):
            ocr_engine.process_image(None)