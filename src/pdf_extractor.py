import fitz
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
import numpy as np

class UniversalPDFExtractor:
    """Universal PDF extractor that works for any document type"""
    
    def __init__(self, max_workers: int = 4, timeout: int = 30):
        self.max_workers = max_workers
        self.timeout = timeout
        
    def extract_pdf_with_metadata(self, pdf_path: str) -> List[Dict]:
        """Extract PDF with enhanced metadata for universal processing"""
        try:
            doc = fitz.open(pdf_path)
            pages = []
            
            for i, page in enumerate(doc):
                # Get text with multiple extraction methods for robustness
                text = page.get_text("text")
                dict_data = page.get_text("dict")
                
                # Extract comprehensive font metadata
                font_info = self._extract_font_metadata(dict_data)
                
                # Calculate text statistics for universal analysis
                text_stats = self._calculate_text_statistics(text)
                
                pages.append({
                    "page_number": i + 1,
                    "text": text,
                    "font_info": font_info,
                    "text_statistics": text_stats,
                    "char_count": len(text),
                    "line_count": len(text.split('\n')),
                    "word_count": len(text.split())
                })
            
            doc.close()
            return pages
            
        except Exception as e:
            logging.error(f"Error extracting PDF {pdf_path}: {e}")
            return []
    
    def _extract_font_metadata(self, dict_data: Dict) -> List[Dict]:
        """Extract font metadata for section detection"""
        font_info = []
        blocks = dict_data.get("blocks", [])
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        font_info.append({
                            'size': span.get('size', 0),
                            'flags': span.get('flags', 0),
                            'font': span.get('font', ''),
                            'text': span.get('text', ''),
                            'bbox': span.get('bbox', [])
                        })
        return font_info
    
    def _calculate_text_statistics(self, text: str) -> Dict:
        """Calculate universal text statistics"""
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        return {
            'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
            'avg_sentence_length': np.mean([len(s.split()) for s in sentences]) if sentences else 0,
            'sentence_count': len(sentences),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0
        }
    
    def extract_documents_text(self, pdf_filenames: List[str], docs_dir: str = "data/docs") -> Dict:
        """Universal document extraction with parallel processing"""
        extracted = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for fname in pdf_filenames:
                pdf_path = os.path.join(docs_dir, fname)
                if os.path.isfile(pdf_path):
                    futures[executor.submit(self.extract_pdf_with_metadata, pdf_path)] = fname
            
            for future in futures:
                fname = futures[future]
                try:
                    result = future.result(timeout=self.timeout)
                    if result:
                        extracted[fname] = result
                    else:
                        logging.warning(f"No content extracted from {fname}")
                except Exception as e:
                    logging.error(f"Failed to process {fname}: {e}")
        
        return extracted

# Factory function for backwards compatibility
def extract_documents_text(pdf_filenames: List[str], docs_dir: str = "data/docs") -> Dict:
    extractor = UniversalPDFExtractor()
    return extractor.extract_documents_text(pdf_filenames, docs_dir)
