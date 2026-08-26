"""
Dr.Egeria v2 Namespace
"""
from .extraction import UniversalExtractor, DrECommand
from .parsing import AttributeFirstParser, parse_dr_egeria_content
from .utils import parse_key_value
from .processors import AsyncBaseCommandProcessor
from .dispatcher import V2Dispatcher
from .glossary import GlossaryProcessor, TermProcessor, TermRelationshipProcessor, GlossaryClassifyProcessor, QuestionProcessor, TermAsContextProcessor
from .data_designer import (
    DataCollectionProcessor, DataStructureProcessor, 
    DataFieldProcessor, DataClassProcessor,
    DataGrainProcessor, LinkDataFieldProcessor, LinkFieldToStructureProcessor,
    LinkDataValueDefinitionProcessor, LinkDataValueCompositionProcessor,
    LinkDataClassCompositionProcessor, LinkCertificationTypeToStructureProcessor,
    DataValueSpecificationProcessor
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
from .action_author import ActionProcessStepLinkProcessor, ActionExecutorTargetLinkProcessor
from .feedback import (
    FeedbackProcessor, TagProcessor,
    ExternalReferenceProcessor, FeedbackLinkProcessor
)
from .view import ViewProcessor
from .actor_manager import ActorManagerProcessor, ActorManagerLinkProcessor
from .dashboard_sheet import CreateDashboardSheetProcessor, LinkReportToDashboardSheetProcessor, AddTextOnDashboardSheetProcessor
from .report import ReportProcessor
from .saved_query import SavedQueryProcessor, SmartQueryLinkProcessor
from .curation import CurationClassifyProcessor, CurationLinkProcessor, CLASSIFICATION_METHODS
from .reference_data import ReferenceDataLinkProcessor, ValidMetadataValueProcessor
from .embedded_process import EmbeddedProcessProcessor
from .engine_action import InitiateEngineActionProcessor, CancelEngineActionProcessor
from .lineage_linker import LineageLinkProcessor, UpdateLineageRelationshipProcessor
