"""
Dr.Egeria v2 Namespace
"""
from .extraction import UniversalExtractor, DrECommand
from .parsing import AttributeFirstParser, parse_dr_egeria_content
from .utils import parse_key_value
from .processors import AsyncBaseCommandProcessor
from .dispatcher import v2Dispatcher
from .glossary import GlossaryProcessor, TermProcessor, TermRelationshipProcessor
from .data_designer import (
    DataCollectionProcessor, DataStructureProcessor, 
    DataFieldProcessor, DataClassProcessor
)
from .solution_architect import (
    BlueprintProcessor, ComponentProcessor,
    SupplyChainProcessor, SolutionLinkProcessor
)
from .project import ProjectProcessor, ProjectLinkProcessor
from .product_manager import (
    CollectionProcessor, ProductProcessor, 
    AgreementProcessor, CSVElementProcessor,
    ProductLinkProcessor
)
from .governance import (
    GovernanceProcessor, GovernanceLinkProcessor,
    GovernanceContextProcessor
)
from .feedback import (
    FeedbackProcessor, TagProcessor,
    ExternalReferenceProcessor, FeedbackLinkProcessor
)
