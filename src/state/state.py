"""
State class
Define the state data structure for the Agent
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

@dataclass
class Search:
    """
    Search result
    """
    query: str = ''
    url: str = ''
    title: str = ''
    content: str = ''
    score: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Search to a dictionary
        """
        return {
            'query': self.query,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'score': self.score,
            'timestamp': self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Search':
        """
        Create a Search from a dictionary
        """
        return cls(
            query=data.get('query', ''),
            url=data.get('url', ''),
            title=data.get('title', ''),
            content=data.get('content', ''),
            score=data.get('score'),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
        )

@dataclass
class Research:
    """
    paragraph research process status
    """
    search_history: List[Search] = field(default_factory=list) # search history
    latest_summary: str = '' # latest summary of the paragraph
    reflection_iteration: int = 0 # reflection iteration
    is_finished: bool = False # whether the research is finished

    def add_search(self, search: Search):
        """
        Add a search to the search history
        """
        self.search_history.append(search)

    def add_search_results(self, query: str, results: List[Dict[str, Any]]):
        """
        Add search results to the search history
        """
        for result in results:
            search = Search(
                query=query,
                url = result.get('url', ''),
                title = result.get('title', ''),
                content = result.get('content', ''),
                score = result.get('score'),
            )
            self.add_search(search)

    def get_search_count(self) -> int:
        """
        Get the number of searches
        """
        return len(self.search_history)

    def increment_reflection_iteration(self):
        """
        Increment the reflection iteration
        """
        self.reflection_iteration += 1

    def mark_completed(self):
        """
        Mark the research as completed
        """
        self.is_finished = True
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Research to a dictionary
        """
        return {
            'search_history': [search.to_dict() for search in self.search_history],
            'latest_summary': self.latest_summary,
            'reflection_iteration': self.reflection_iteration,
            'is_finished': self.is_finished,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Research':
        """
        Create a Research from a dictionary
        """
        return cls(
            search_history=[Search.from_dict(search) for search in data.get('search_history', [])],
            latest_summary=data.get('latest_summary', ''),
            reflection_iteration=data.get('reflection_iteration', 0),
            is_finished=data.get('is_finished', False),
        )

@dataclass
class Paragraph:
    """
    Paragraph class
    """
    title: str = '' # title of the paragraph
    content: str = '' # content of the paragraph
    research: Research = field(default_factory=Research) # research status of the paragraph
    order: int = 0 # order of the paragraph

    def is_finished(self) -> bool:
        """
        Check if the paragraph is finished
        """
        return self.research.is_finished and bool(self.research.latest_summary)
    
    def get_final_content(self) -> str:
        """
        Get the final content of the paragraph
        """
        return self.research.latest_summary or self.content

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Paragraph to a dictionary
        """
        return {
            'title': self.title,
            'content': self.content,
            'research': self.research.to_dict(),
            'order': self.order,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paragraph':
        """
        Create a Paragraph from a dictionary
        """
        research_data = data.get("research", {})
        research = Research.from_dict(research_data) if research_data else Research()
        
        return cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            research=research,
            order=data.get("order", 0)
        )
        
@dataclass
class State:
    """
    State class
    """
    query: str = ""                                                # original query
    report_title: str = ""                                         # report title
    paragraphs: List[Paragraph] = field(default_factory=list)     # paragraphs of the report
    final_report: str = ""                                         # final report content
    is_completed: bool = False                                     # whether the report is finished
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_paragraph(self, title: str, content: str) -> int:
        """
        Add a paragraph to the report
        """
        order = len(self.paragraphs)
        paragraph = Paragraph(title=title, content=content, order=order)
        self.paragraphs.append(paragraph)
        self.update_timestamp()
        return order

    def get_paragraphs(self, index: int) -> Optional[Paragraph]:
        """
        Get a paragraph by index
        """
        if 0 <= index < len(self.paragraphs):
            return self.paragraphs[index]
        return None
        
    def get_completed_paragraphs_count(self) -> int:
        """
        Get the number of completed paragraphs
        """
        return sum(1 for paragraph in self.paragraphs if paragraph.is_finished())
        
    def get_total_paragraphs_count(self) -> int:
        """
        Get the total number of paragraphs
        """
        return len(self.paragraphs)
        
    def is_all_paragraphs_completed(self) -> bool:
        """
        Check if all paragraphs are completed
        """
        return all(p.is_finished() for p in self.paragraphs) if self.paragraphs else False
        
    def mark_completed(self):
        """
        Mark the report as completed
        """
        self.is_completed = True
        self.update_timestamp()
        
    def update_timestamp(self):
        """
        Update the timestamp
        """
        self.updated_at = datetime.now().isoformat()
        
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get the progress summary
        """
        completed = self.get_completed_paragraphs_count()
        total = self.get_total_paragraphs_count()
        return {
            "total_paragraphs": total,
            "completed_paragraphs": completed,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "is_completed": self.is_completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the State to a dictionary
        """
        return {
            'query': self.query,
            'report_title': self.report_title,
            'paragraphs': [p.to_dict() for p in self.paragraphs],
            'final_report': self.final_report,
            'is_completed': self.is_completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Convert the State to a JSON string
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'State':
        """
        Create a State from a dictionary
        """
        return cls(
            query=data.get('query', ''),
            report_title=data.get('report_title', ''),
            paragraphs=[Paragraph.from_dict(p) for p in data.get('paragraphs', [])],
            final_report=data.get('final_report', ''),
            is_completed=data.get('is_completed', False),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'State':
        """
        Create a State from a JSON string
        """
        return cls.from_dict(json.loads(json_str))

    def save_to_file(self, file_path: str):
        """
        Save the State to a file
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> 'State':
        """
        Load the State from a file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    