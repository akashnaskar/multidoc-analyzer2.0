import os
import sys
from multidocchat.utils.model_loader import ModelLoader
from multidocchat.model.models import Metadata
from multidocchat.exception.custom_exception import DocumentPortalException
from multidocchat.logger import GLOBAL_LOGGER as log
from multidocchat.model.models import *
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from multidocchat.prompts.prompt_library import document_analysis_prompt
 # type: ignore


class DocumentAnalyzer:
    """
    Analyzes using a pretrained model.
    Automatically logs all actions and supports session based organisation
    """

    def __init__(self):
        try:
            self.loader = ModelLoader()
            self.llm= self.loader.load_llm()

            self.parser= JsonOutputParser(pydantic_object= Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser= self.parser, llm= self.llm)
            #self.prompt = PROMPT_REGISTRY["document_analysis"]
            self.prompt = document_analysis_prompt
            log.info("DocumentAnalyzer initialised succesfully")

        except Exception as e:
            log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPortalException("Error in DocumentAnalyzer initialization", sys)

    def analyze_document(self, document_text: str)-> dict:
        """
        Analyze documents text and extract structured metadtaa and summary
        """
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            log.info("Meta-data analysis chain initialised")
            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text":document_text
            })
            log.info("Metadata extraction successful", keys=list(response.keys()))
            return response
        
        except Exception as e:
            log.error("Metadata analysis failed", error=str(e))
            raise DocumentPortalException("Metadata extraction failed",sys)

