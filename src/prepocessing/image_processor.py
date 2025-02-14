# src/preprocessing/image_processor.py
import cv2
import numpy as np
from typing import Union, Tuple
import logging
from config.settings import IMAGE_MIN_SIZE, IMAGE_MAX_SIZE, IMAGE_QUALITY

class ImageProcessor:
    """Clase para el procesamiento de imágenes antes del OCR."""
    
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """
        Carga una imagen desde una ruta.
        
        Args:
            image_path (str): Ruta de la imagen
            
        Returns:
            np.ndarray: Imagen cargada
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
        return image

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocesa la imagen para mejorar el OCR.
        
        Args:
            image (np.ndarray): Imagen original
            
        Returns:
            np.ndarray: Imagen procesada
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar umbral adaptativo
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        # Reducir ruido
        denoised = cv2.fastNlMeansDenoising(binary)
        
        # Mejorar contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        return enhanced

    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Redimensiona la imagen manteniendo la proporción.
        
        Args:
            image (np.ndarray): Imagen original
            
        Returns:
            np.ndarray: Imagen redimensionada
        """
        height, width = image.shape[:2]
        
        # Calcular nueva dimensión manteniendo proporción
        if width < height:
            if width < IMAGE_MIN_SIZE:
                new_width = IMAGE_MIN_SIZE
                new_height = int(height * (IMAGE_MIN_SIZE / width))
            elif width > IMAGE_MAX_SIZE:
                new_width = IMAGE_MAX_SIZE
                new_height = int(height * (IMAGE_MAX_SIZE / width))
            else:
                return image
        else:
            if height < IMAGE_MIN_SIZE:
                new_height = IMAGE_MIN_SIZE
                new_width = int(width * (IMAGE_MIN_SIZE / height))
            elif height > IMAGE_MAX_SIZE:
                new_height = IMAGE_MAX_SIZE
                new_width = int(width * (IMAGE_MAX_SIZE / height))
            else:
                return image
                
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    def deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Corrige la inclinación de la imagen.
        
        Args:
            image (np.ndarray): Imagen original
            
        Returns:
            np.ndarray: Imagen corregida
        """
        # Detectar bordes
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Detectar líneas
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
        
        if lines is not None:
            # Calcular ángulo promedio
            angles = []
            for rho, theta in lines[0]:
                angle = np.degrees(theta)
                if angle < 45:
                    angles.append(angle)
                elif angle > 135:
                    angles.append(angle - 180)
                    
            if angles:
                median_angle = np.median(angles)
                
                # Rotar imagen
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                rotated = cv2.warpAffine(
                    image, M, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
                return rotated
                
        return image

    def process(self, image_path: str) -> np.ndarray:
        """
        Procesa una imagen aplicando todas las mejoras necesarias.
        
        Args:
            image_path (str): Ruta de la imagen
            
        Returns:
            np.ndarray: Imagen procesada
        """
        try:
            # Cargar imagen
            image = self.load_image(image_path)
            
            # Redimensionar si es necesario
            image = self.resize_image(image)
            
            # Corregir inclinación
            image = self.deskew(image)
            
            # Preprocesar
            processed = self.preprocess_image(image)
            
            return processed
            
        except Exception as e:
            logging.error(f"Error procesando imagen {image_path}: {str(e)}")
            raise