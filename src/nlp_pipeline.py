import re
import string
import spacy
from typing import List, Tuple, Dict, Optional

try:
    nlp = spacy.load("en_core_web_md")  # Use the medium model for semantics
except OSError:
    print("Warning: en_core_web_md not found. Install with: python -m spacy download en_core_web_md")
    nlp = None

class UniversalSectionDetector:
    HEADER_PATTERNS = [
        re.compile(r"^[A-Z][^\.\n]{10,100}$"),
        re.compile(r"^(?:[A-Z][a-z0-9 \-&\(\),:]{8,120})$"),
        re.compile(r"^([A-Z][a-z]+(?: [A-Z][a-z]+)+)$"),
        re.compile(r"^(?:[A-Za-z].*Guide|Checklist|Tips|Things to Do)")
    ]
    FOCUS_KEYWORDS = [
        "guide", "how to", "create", "convert", "edit", "checklist", "tips", "tricks",
        "introduction", "overview", "summary", "activity", "activities",
        "culinary", "nightlife", "entertainment", "forms", "sign"
    ]
    def detect_sections(self, page_text: str, font_info: List[Dict] = None) -> List[Tuple[str, str]]:
        lines = [l.strip() for l in page_text.split('\n')]
        n = len(lines)
        heading_idxs = []
        for i, line in enumerate(lines):
            if self._is_heading(line):
                heading_idxs.append(i)
            elif nlp:
                doc = nlp(line)
                # Accept line as heading if noun-chunk and no main verb (not a sentence)
                if (len(line) > 10 and not line.endswith('.')
                    and any(chunk.root.pos_ == "NOUN" for chunk in doc.noun_chunks)
                    and not any(t.pos_ == "VERB" for t in doc)):
                    heading_idxs.append(i)
        heading_idxs = sorted(set(heading_idxs))
        sections = []
        for i, hidx in enumerate(heading_idxs):
            hend = heading_idxs[i+1] if (i+1 < len(heading_idxs)) else n
            title = lines[hidx].strip()
            if not self._is_usable_title(title): continue
            content = "\n".join([l for l in lines[hidx+1:hend] if l.strip()]).strip()
            if len(content) < 30: continue
            sections.append((title, content))
        if not sections and nlp and page_text.strip():
            lines_non_bullet = [l for l in lines if len(l) >= 10 and l not in {"•","●","-","*"} and l[0].isupper() and " " in l]
            if lines_non_bullet:
                best_title = max(lines_non_bullet, key=len)
                if self._is_usable_title(best_title):
                    sections.append((best_title, page_text.strip()))
            else:
                doc = nlp(page_text)
                chunks = [chunk.text.strip().title() for chunk in doc.noun_chunks if len(chunk.text.strip()) > 12]
                for probable in chunks:
                    if self._is_usable_title(probable):
                        sections.append((probable, page_text.strip()))
                        break
        if not sections and len(page_text.strip()) >= 30:
            # Absolute last resort, skip rather than insert "Untitled Section"
            return []
        return sections
    def _is_heading(self, line: str) -> bool:
        if not line: return False
        lclean = line.strip()
        if lclean.lower() in {"untitled section", "section", "heading", "index"}: return False
        if lclean in {"•","●","-","*","."}: return False
        if lclean.endswith('.'): return False
        if len(lclean) < 10: return False
        if any(pat.match(lclean) for pat in self.HEADER_PATTERNS): return True
        if any(k in lclean.lower()[:50] for k in self.FOCUS_KEYWORDS): return True
        return False
    def _is_usable_title(self, title: str) -> bool:
        if not title or len(title) < 10: return False
        t = title.strip()
        if t.lower() == "untitled section": return False
        if t.endswith(('.', '*', ':', ';')): return False
        if t in {"•","●","-","*"}: return False
        if not any(c.isalpha() for c in t): return False
        if t.lower() in {"section", "heading"}: return False
        words = t.split()
        if len(words) < 2: return False
        if t[0].islower(): return False
        return True

class UniversalTextProcessor:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.section_detector = UniversalSectionDetector()

    def split_documents_into_sections(self, docs_text: Dict) -> List[Dict]:
        section_chunks = []
        min_section_length = self.config.get("min_section_length", 30)
        for doc_name, pages in docs_text.items():
            for page in pages:
                page_num = page['page_number']
                page_text = page['text']
                font_info = page.get('font_info', [])
                for section_title, section_text in self.section_detector.detect_sections(page_text, font_info):
                    if len(section_text.strip()) < min_section_length:
                        continue
                    section_chunks.append({
                        "document": doc_name,
                        "page_number": page_num,
                        "section_title": section_title,
                        "section_text": section_text,
                        "word_count": len(section_text.split()),
                        "char_count": len(section_text),
                        "sentence_count": len([s for s in section_text.split('.') if s.strip()]),
                        "section_type": self._classify_section_type(section_title, section_text)
                    })
        return section_chunks

    def _classify_section_type(self, title: str, content: str) -> str:
        t = (title or "").lower()
        if "guide" in t: return "guide"
        if "convert" in t or "export" in t: return "conversion"
        if "sign" in t or "signature" in t: return "signatures"
        if "checklist" in t: return "checklist"
        if "activity" in t or "things to do" in t: return "activity"
        if "packing" in t: return "tips"
        if "tips" in t or "trick" in t: return "tips"
        if "nightlife" in t or "entertainment" in t: return "entertainment"
        return "content"

    def clean_text(self, text: str) -> str:
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def spacy_tokenize(self, text: str) -> List[str]:
        if nlp is None:
            return [w for w in self.clean_text(text).split() if len(w) > 2]
        doc = nlp(text)
        return [token.lemma_ for token in doc if not token.is_stop and token.is_alpha and len(token) > 2]

    def preprocess_for_vector(self, text: str) -> str:
        return ' '.join(self.spacy_tokenize(text))

    def extract_refined_snippet(self, section_text: str, query_vector: str, persona: str = "", max_length: int = 320) -> str:
        if not section_text.strip(): return ""
        import re
        sentences = [s.strip() for s in re.split('[\.\n]', section_text) if len(s.strip()) > 10]
        if not sentences:
            return section_text[:max_length]
        if nlp:
            query_doc = nlp((persona + " " + query_vector).strip())
            ranked = sorted(
                sentences,
                key=lambda s: query_doc.similarity(nlp(s)),
                reverse=True)
        else:
            qwords = set(query_vector.lower().split())
            ranked = sorted(
                sentences,
                key=lambda s: len(set(s.lower().split()) & qwords),
                reverse=True)
        result = ""
        for sent in ranked:
            if len(result) + len(sent) + 2 <= max_length:
                result += sent + ". "
            else:
                break
        if persona and result:
            if "HR" in persona:
                result = "For HR professionals: " + result
            if "Travel" in persona:
                result = "Travel planner note: " + result
        return result.strip() if result else sentences[0][:max_length]

# Factory functions for backwards compatibility
def split_documents_into_sections(docs_text: Dict) -> List[Dict]:
    processor = UniversalTextProcessor()
    return processor.split_documents_into_sections(docs_text)
def preprocess_for_vector(text: str) -> str:
    processor = UniversalTextProcessor()
    return processor.preprocess_for_vector(text)
def extract_refined_snippet(section_text: str, query_vector: str, max_length: int = 320) -> str:
    processor = UniversalTextProcessor()
    return processor.extract_refined_snippet(section_text, query_vector, max_length=max_length)
