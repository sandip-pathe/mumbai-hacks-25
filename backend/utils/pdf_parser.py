"""
PDF parsing utilities
Fallback to pdfplumber if Azure Document Intelligence not available
"""
import pdfplumber
import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)


async def parse_pdf_with_pdfplumber(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text from PDF using pdfplumber (fallback method)
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dict with 'text', 'page_count'
    """
    try:
        full_text = []
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text()
                if text:
                    full_text.append(f"[Page {page_num}]\n{text}")
                
                # Extract tables
                page_tables = page.extract_tables()
                for table in page_tables:
                    tables.append({
                        "page": page_num,
                        "data": table
                    })
        
        combined_text = "\n\n".join(full_text)
        
        logger.info(f"✅ PDF parsed with pdfplumber: {len(combined_text)} chars, {page_count} pages")
        
        return {
            "text": combined_text,
            "page_count": page_count,
            "tables": tables,
            "method": "pdfplumber"
        }
        
    except Exception as e:
        logger.error(f"❌ pdfplumber parsing failed: {e}")
        raise


async def save_uploaded_pdf(file_content: bytes, filename: str) -> str:
    """
    Save uploaded PDF file to temporary directory
    
    Args:
        file_content: PDF file bytes
        filename: Original filename
        
    Returns:
        Path to saved file
    """
    try:
        # Create temp directory if not exists
        temp_dir = "/tmp/anaya_pdfs"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"✅ PDF saved: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"❌ Failed to save PDF: {e}")
        raise
