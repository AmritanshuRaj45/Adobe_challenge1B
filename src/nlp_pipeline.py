import re
import string
import spacy
from typing import List, Tuple, Dict, Optional
import numpy as np

# Load spaCy model with error handling
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: en_core_web_sm not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

class UniversalSectionDetector:
    """Universal section detection that works across domains"""
    
    def __init__(self):
        # Universal patterns that work across domains
        self.header_patterns = [
            re.compile(r'^([A-Z][A-Za-z\s&:\-]{3,50})$'),          # Title case headers
            re.compile(r'^([A-Z0-9\s]{4,50})$'),                   # ALL CAPS headers
            re.compile(r'^(\d+\.?\s+[A-Za-z].{3,50})$'),           # Numbered sections
            re.compile(r'^([A-Za-z\s]+:)$'),                       # Colon endings
            re.compile(r'^([IVX]+\.?\s+[A-Za-z].{3,50})$'),        # Roman numerals
            re.compile(r'^([A-Za-z]\.\s+[A-Za-z].{3,50})$'),       # Letter sections
        ]
        
        # Universal structural indicators
        self.structure_indicators = [
            'introduction', 'conclusion', 'summary', 'overview', 'background',
            'methodology', 'methods', 'results', 'discussion', 'references',
            'appendix', 'chapter', 'section', 'part', 'table', 'figure'
        ]
    
    def detect_sections_universal(self, page_text: str, font_info: List[Dict] = None) -> List[Tuple[str, str]]:
        """Universal section detection using multiple heuristics"""
        lines = page_text.split('\n')
        sections = []
        current_title = None
        current_content = []
        
        # Calculate font statistics if available
        font_stats = self._calculate_font_statistics(font_info) if font_info else None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            is_header = self._is_likely_header(line_stripped, font_stats, i, font_info)
            
            if is_header:
                # Save previous section
                if current_title or current_content:
                    content = '\n'.join(current_content).strip()
                    if content:  # Only add non-empty sections
                        sections.append((current_title or "Untitled Section", content))
                
                current_title = line_stripped
                current_content = []
            else:
                current_content.append(line)
        
        # Add final section
        if current_title or current_content:
            content = '\n'.join(current_content).strip()
            if content:
                sections.append((current_title or "Untitled Section", content))
        
        return sections
    
    def _calculate_font_statistics(self, font_info: List[Dict]) -> Dict:
        """Calculate font statistics for header detection"""
        if not font_info:
            return {}
        
        sizes = [f['size'] for f in font_info if f['size'] > 0]
        flags = [f['flags'] for f in font_info]
        
        return {
            'avg_size': np.mean(sizes) if sizes else 12,
            'std_size': np.std(sizes) if len(sizes) > 1 else 0,
            'max_size': max(sizes) if sizes else 12,
            'bold_ratio': sum(1 for f in flags if f & 16) / len(flags) if flags else 0
        }
    
    def _is_likely_header(self, line: str, font_stats: Dict, line_idx: int, font_info: List[Dict]) -> bool:
        """Determine if a line is likely a header using multiple heuristics"""
        # Pattern-based detection
        for pattern in self.header_patterns:
            if pattern.match(line):
                return True
        
        # Font-based detection
        if font_stats and font_info and line_idx < len(font_info):
            font_data = font_info[line_idx]
            size_threshold = font_stats['avg_size'] + 0.5 * font_stats['std_size']
            
            if (font_data['size'] > size_threshold or 
                font_data['flags'] & 16 or  # Bold
                font_data['flags'] & 4):    # Italic
                return True
        
        # Structure-based detection
        line_lower = line.lower()
        if any(indicator in line_lower for indicator in self.structure_indicators):
            return True
        
        # Length and format heuristics
        if (len(line) < 100 and 
            len(line.split()) <= 10 and
            not line.endswith('.') and
            line[0].isupper() and
            ':' not in line):
            return True
        
        return False

class UniversalTextProcessor:
    """Universal text processing for any domain"""
    
    def __init__(self, config: Dict = None):
        """Initialize with configuration"""
        self.config = config or {}
        self.section_detector = UniversalSectionDetector()
    
    def split_documents_into_sections(self, docs_text: Dict) -> List[Dict]:
        """Universal section splitting with config support"""
        section_chunks = []
        min_section_length = self.config.get('min_section_length', 30)
        
        for doc_name, pages in docs_text.items():
            for page in pages:
                page_num = page['page_number']
                page_text = page['text']
                font_info = page.get('font_info', [])
                
                sections = self.section_detector.detect_sections_universal(page_text, font_info)
                
                for section_title, section_text in sections:
                    # Use config for minimum section length
                    if len(section_text.strip()) < min_section_length:
                        continue
                    
                    # Universal section metadata
                    section_chunks.append({
                        "document": doc_name,
                        "page_number": page_num,
                        "section_title": section_title,
                        "section_text": section_text,
                        "word_count": len(section_text.split()),
                        "char_count": len(section_text),
                        "sentence_count": len([s for s in section_text.split('.') if s.strip()]),
                        "has_numbers": bool(re.search(r'\d', section_text)),
                        "has_references": bool(re.search(r'\[(.*?)\]|\b\d{4}\b', section_text)),
                        "section_type": self._classify_section_type(section_title, section_text)
                    })
        
        return section_chunks
    
    def _classify_section_type(self, title: str, content: str) -> str:
        """Universal section type classification"""
        title_lower = title.lower()
        
        # Universal section types
        if any(word in title_lower for word in ['introduction', 'intro', 'overview', 'background']):
            return 'introduction'
        elif any(word in title_lower for word in ['conclusion', 'summary', 'final', 'end']):
            return 'conclusion'
        elif any(word in title_lower for word in ['method', 'approach', 'technique', 'process']):
            return 'methodology'
        elif any(word in title_lower for word in ['result', 'finding', 'outcome', 'data']):
            return 'results'
        elif any(word in title_lower for word in ['discussion', 'analysis', 'interpretation']):
            return 'discussion'
        elif 'reference' in title_lower or 'bibliograph' in title_lower:
            return 'references'
        else:
            return 'content'
    
    def clean_text(self, text: str) -> str:
        """Universal text cleaning"""
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def spacy_tokenize(self, text: str) -> List[str]:
        """Universal tokenization with fallback"""
        if nlp is None:
            # Fallback tokenization
            words = self.clean_text(text).split()
            return [w for w in words if len(w) > 2 and not w.isdigit()]
        
        doc = nlp(text)
        tokens = [t.lemma_ for t in doc if not t.is_stop and not t.is_punct and t.is_alpha and len(t.text) > 2]
        return tokens
    
    def preprocess_for_vector(self, text: str) -> str:
        """Universal preprocessing for vectorization"""
        return ' '.join(self.spacy_tokenize(text))
    
    def extract_refined_snippet(self, section_text: str, query_vector: str, max_length: int = 250) -> str:
        """Universal snippet extraction with config support"""
        sentences = [s.strip() for s in section_text.split('.') if s.strip() and len(s.strip()) > 20]
        if not sentences:
            return section_text[:max_length]
        
        query_words = set(query_vector.lower().split())
        
        # Score sentences by relevance
        sentence_scores = []
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            
            # Basic overlap score
            overlap_score = len(query_words & sentence_words) / (len(sentence_words) + 1)
            
            # Position bonus (earlier sentences might be more important)
            position_bonus = (len(sentences) - sentences.index(sentence)) / len(sentences) * 0.1
            
            # Length penalty for very short or very long sentences
            length_penalty = 0
            if len(sentence) < 50 or len(sentence) > 200:
                length_penalty = -0.1
            
            final_score = overlap_score + position_bonus + length_penalty
            sentence_scores.append((sentence, final_score))
        
        # Return best sentences within length limit
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        result = ""
        for sentence, score in sentence_scores:
            if len(result + sentence + ". ") <= max_length:
                result += sentence + ". "
            else:
                break
        
        return result.strip() if result else sentences[0][:max_length]

# Factory functions for backwards compatibility
def split_documents_into_sections(docs_text: Dict) -> List[Dict]:
    processor = UniversalTextProcessor()
    return processor.split_documents_into_sections(docs_text)

def preprocess_for_vector(text: str) -> str:
    processor = UniversalTextProcessor()
    return processor.preprocess_for_vector(text)

def extract_refined_snippet(section_text: str, query_vector: str, max_length: int = 250) -> str:
    processor = UniversalTextProcessor()
    return processor.extract_refined_snippet(section_text, query_vector, max_length)
