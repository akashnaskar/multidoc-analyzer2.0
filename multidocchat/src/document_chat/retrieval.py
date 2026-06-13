import sys
import os
from operator import itemgetter
from typing import List, Optional, Dict, Any

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS

from multidocchat.utils.model_loader import ModelLoader
from multidocchat.exception.custom_exception import DocumentPortalException
from multidocchat.logger import GLOBAL_LOGGER as log
from multidocchat.prompts.prompt_library import PROMPT_REGISTRY
from multidocchat.model.models import PromptType

class ConversationalRAG:
    '''lCEL based conversational. rAG. with lazy retriever initialization

    Ex Usage:
        rag = ConversationalRAG(session_id="abc")
        rag.load_retriever_from_faiss(index_path="faiss_index/abc", k=5, index_name="index")
        answer = rag.invoke("What is ...?", chat_history=[])
    '''
    def __init__(self, session_id: Optional[str], retriever= None):
        try:
            self.session_id = session_id
            self.llm= self._load_llm()
            self.contextualize_prompt: ChatPromptTemplate= PROMPT_REGISTRY[
                                                            PromptType.CONTEXTUALIZE_QUESTION.value
            ]
            self.qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY[
                PromptType.CONTEXT_QA.value
            ]
            self.retriever = retriever
            self.chain= None
            if self.retriever is not None:
                self._build_lcel_chain()

            log.info("ConversationalRAG initialised", session_id=self.session_id)
        except Exception as e:
            log.error("Failed to initialize ConversationalRAG", error=str(e))
            raise DocumentPortalException("Initialization error in ConversationalRAG", sys)

    def load_retriever_from_faiss(
            self,
            index_path: str,
            k: int=5,
            index_name: str = "index",
            search_type: str="similarity",
            search_kwargs: Optional[Dict[str, Any]]= None,
    ):
        """
        Load FAISS vectorstore from disk and build retriever +LCEL chain
        """
        try:
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            embeddings = ModelLoader().load_embeddings()
            vectorstore = FAISS.load_local(
                index_path,
                embeddings=embeddings,
                index_name=index_name,
                allow_dangerous_deserialization= True,
            )
            if search_kwargs is None:
                search_kwargs = {"k": k}
            
            self.retriever = vectorstore.as_retriever(search_type= search_type, search_kwargs= search_kwargs)
            self.build_lcel_chain()
            log.info("FAISS loaded succesfully",   
                     index_path=index_path,
                     index_name= index_name,
                     k=k,
                     session_id =self.session_id)
            return self.retriever
        except Exception as e:
            log.error("Failed to load retriever from FAISS", error=str(e))
            raise DocumentPortalException("Loading error in ConversationalRAG", sys)
        
    def invoke(self, user_input: str, chat_history: Optional[List[BaseMessage]]=None)-> str:
        """Invoke the LCEL pipeline"""
        try:
            if self.chain is None:
                raise DocumentPortalException(
                    "RAG chain is not initialized. Call load_retreiver_from_faiss() before invoke()", sys
                )
            chat_history= chat_history or []
            payload = {"input":user_input, "chat_history": chat_history}
            answer = self.chain.invoke(payload)
            if not answer:
                log.warning("No answer generated", user_input = user_input, session_id= self.session_id)
                return "no answer generated"
            log.info("Chain invoked succesfully",
                     session_id =self.session_id,
                     user_input = user_input,
                     answer_preview = str(answer)[:150])
            return answer
        except Exception as e:
            log.error("Failed to invoke ConversationalRAG", error=str(e))
            raise DocumentPortalException("Invocation error in ConversationalRAG", sys)
        

        #--------   HELPER FUNCTIONS   ---------------
    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM could not be loaded")
            log.info("LLM loaded suvvesfully", session_id = self.session_id)
            return llm
        except Exception as e:
            return DocumentPortalException("LLM loading error in conversationalRAG", sys)
        
    @staticmethod
    def _format_docs(docs) -> str:
        return "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)
        
    def _build_lcel_chain(self):
        try:
            if self.retreiver is None:
                raise DocumentPortalException("No retreiver set before building chain", sys)
            
            #rewrite the user question with chat user history context
            question_rewriter= (
                {"input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
                | self.contextualize_prompt
                | self.llm
                |StrOutputParser()
            )

            # 2.Retreive docs for the rewritten question
            retrieve_docs = question_rewriter | self.retriever | self._format_docs

            # 3.Answer using retrueved context +. original input +chat history
            self.chain = (
                {"context": retrieve_docs,
                 "input": itemgetter("input"),
                 "chat_history": itemgetter("chat_history"),
                 }
                 |self.qa_prompt
                 |self.llm
                 |StrOutputParser()
            )
            log.info("LCEL graph built succesfully", session_id=self.session_id)
        
        except Exception as e:
            log.error("Failed to build LCEL chain", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to build LCEL chain", sys)