"""
Dr.Egeria v2 Namespace
"""
from .extraction import UniversalExtractor, DrECommand
from .parsing import AttributeFirstParser, parse_dr_egeria_content
from .utils import parse_key_value
from .processors import AsyncBaseCommandProcessor
from .dispatcher import V2Dispatcher
from .glossary import GlossaryProcessor, TermProcessor, TermRelationshipProcessor
from .data_designer import (
    DataCollectionProcessor, DataStructureProcessor, 
    DataFieldProcessor, DataClassProcessor,
    DataGrainProcessor, LinkDataFieldProcessor, LinkFieldToStructureProcessor,
    LinkDataValueDefinitionProcessor, LinkDataValueCompositionProcessor,
    LinkDataClassCompositionProcessor, LinkCertificationTypeToStructureProcessor,
    AttachDataDescriptionProcessor, DataValueSpecificationProcessor
)
from .solution_architect import (
    BlueprintProcessor, ComponentProcessor,
    SupplyChainProcessor, SolutionLinkProcessor,
    SolutionArchitectProcessor
)
from .project import ProjectProcessor, ProjectLinkProcessor
from .collection_manager_processor import (
    CollectionManagerProcessor, CSVElementProcessor,
    CollectionLinkProcessor
)
from .governance import (
    GovernanceProcessor, GovernanceLinkProcessor,
    GovernanceContextProcessor
)
from .feedback import (
    FeedbackProcessor, TagProcessor,
    ExternalReferenceProcessor, FeedbackLinkProcessor
)
from .view import ViewProcessor
