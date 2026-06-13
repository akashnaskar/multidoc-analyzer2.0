from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from typing import List, Optional, Any,  Dict
from multidocchat.src.document_ingestion.data_ingestion import (
    DocHandler,  DocumentComparator, FaissManager,  ChatIngestor
)
from multidocchat.src.document_analyzer.data_analysis import DocumentAnalyzer
from multidocchat.src.document_compare.document_comparator import DocumentComparatorLLM
from multidocchat.src.document_chat.retrieval import ConversationalRAG

FAISS_BASE= os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")

app=FastAPI(title = "Document Portal API", version=  "0.1")
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
print (BASE_DIR)
# app.mount("/static", StaticFiles(directory=str(BASE_DIR/"static")), name ="static")
# templates =Jinja2Templates(directory= str(BASE_DIR /"templates"))

