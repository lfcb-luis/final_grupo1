# tests/test_preprocessing.py
import pytest
import numpy as np
from src.preprocessing.image_processor import ImageProcessor
from config.settings import IMAGE_MIN_SIZE, IMAGE_MAX_SIZE

class TestImageProcessor:
    """Pruebas para el procesador de imágenes."""

    @pytest.fixture
    def processor(self):
        """Fixture que proporciona una instancia de ImageProcessor."""
        return ImageProcessor()

    @pytest.fixture
    def sample_image(self):
        """Fixture que proporciona una imagen de prueba básica."""
        return np.ones((100, 100), dtype=np.uint8) * 255

    @pytest.fixture
    def noisy_image(self):
        """Fixture que proporciona una imagen con ruido."""
        image = np.ones((100, 100), dtype=np.uint8) * 255
        noise = np.random.normal(0, 50, (100, 100))
        noisy_image = image + noise.astype(np.uint8)
        return noisy_image

    def test_preprocess_image(self, processor, sample_image):
        """Prueba el preprocesamiento básico de una imagen."""
        processed = processor.preprocess_image(sample_image)
        assert processed is not None
        assert processed.shape == sample_image.shape
        assert processed.dtype == np.uint8

    def test_resize_image_small(self, processor):
        """Prueba el redimensionamiento de una imagen pequeña."""
        small_image = np.ones((50, 50), dtype=np.uint8)
        resized = processor.resize_image(small_image)
        assert resized.shape[0] >= IMAGE_MIN_SIZE or resized.shape[1] >= IMAGE_MIN_SIZE

    def test_resize_image_large(self, processor):
        """Prueba el redimensionamiento de una imagen grande."""
        large_image = np.ones((3000, 3000), dtype=np.uint8)
        resized = processor.resize_image(large_image)
        assert resized.shape[0] <= IMAGE_MAX_SIZE and resized.shape[1] <= IMAGE_MAX_SIZE

    def test_resize_maintains_aspect_ratio(self, processor):
        """Prueba que el redimensionamiento mantiene la proporción de aspecto."""
        original = np.ones((200, 400), dtype=np.uint8)
        resized = processor.resize_image(original)
        original_ratio = original.shape[1] / original.shape[0]
        resized_ratio = resized.shape[1] / resized.shape[0]
        assert abs(original_ratio - resized_ratio) < 0.1

    def test_deskew_straight_image(self, processor, sample_image):
        """Prueba la corrección de inclinación en una imagen recta."""
        deskewed = processor.deskew(sample_image)
        assert deskewed.shape == sample_image.shape

    # En el método test_process_complete_pipeline
    def test_process_complete_pipeline(self, processor, noisy_image):
        """Prueba el pipeline completo de procesamiento."""
        processed = processor.process(noisy_image)  # Pasamos directamente el array
        assert processed is not None
        assert processed.dtype == np.uint8
        assert len(processed.shape) == 2  # Debe ser una imagen en escala de grises

    def test_error_handling(self, processor):
        """Prueba el manejo de errores con entrada inválida."""
        with pytest.raises(Exception):
            processor.process(None)

    def test_image_enhancement(self, processor, noisy_image):
        """Prueba la mejora de calidad de imagen."""
        processed = processor.preprocess_image(noisy_image)
        # Verificar que el ruido se ha reducido
        original_std = np.std(noisy_image)
        processed_std = np.std(processed)
        assert processed_std < original_std