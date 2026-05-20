# import os
# from pathlib import Path

# from multidocchat.src.document_analyzer.data_analysis import DocumentAnalyzer
# from multidocchat.src.document_ingestion.data_ingestion import DocHandler

# ###Path to the file to be tested
# PDF_PATH="/Users/apple/Documents/Dev_Stuff/Resume_projects/multidoc-analyzer2.0/data/Attention_is_all_you_need.pdf"

# #Dummy file wrapper to upload file
# class DummyFile:
#     def __init__(self, file_path):
#         self.name = Path(file_path).name
#         self.file_path= file_path

#     def getbuffer(self):
#         return open(self.file_path, "rb").read()
    
# def main():
#     try:
#         # step 1: Data analysis
#         print("Start Data ingestion")
#         dummy_pdf = DummyFile(PDF_PATH)
#         handler = DocHandler(data_dir="./data", session_id="test_ingestion_analysis")

#         saved_path = handler.save_pdf(dummy_pdf)
#         print(f"PDF saved at : {saved_path}")

#         text_content = handler.read_pdf(saved_path)
#         print(f"Extracted text length: {len(text_content)} chars\n")

#         #Data analysis
#         print("starting metadata analysis")
#         analyzer = DocumentAnalyzer() #Loads LLM + parser

#         analysis_result = analyzer.analyze_document(text_content)

#         #Step 3: Display result
#         print("\n=== METADATA ANALYSIS RESULT ===")
#         for key, value in analysis_result.items():
#             print(f"{key}: {value}")


#     except Exception as e:
#         print(f"Test failed: {e}")
        
# if __name__=="__main__":
#     main()

### Change the prompt registry data again before using

#-----------------DOCUMENT COMPARATOR testing---------
import io
from pathlib import Path
from multidocchat.src.document_ingestion.data_ingestion import DocumentComparator
from multidocchat.src.document_compare.document_comparator import DocumentComparatorLLM

#Setup local PDFs as if they were uploaded
def load_fake_uploaded_file(file_path: Path):
    return io.BytesIO(file_path.read_bytes())

#Save anbd combine PDFs
def test_compare_documents():
    ref_path = Path("/Users/apple/Documents/Dev_Stuff/Resume_projects/multidoc-analyzer2.0/data/document_compare/Long_Report_V1.pdf")
    act_path = Path("/Users/apple/Documents/Dev_Stuff/Resume_projects/multidoc-analyzer2.0/data/document_compare/Long_Report_V2.pdf")

    #wrap streamlit like UploadFile-style
    class FakeUpload:
        def __init__(self, file_path: Path):
            self.name = file_path.name
            self._buffer = file_path.read_bytes()

        def getbuffer(self):
            return self._buffer
        
    #Instatntiate
    comparator = DocumentComparator()
    ref_upload = FakeUpload(ref_path)
    act_upload = FakeUpload(act_path)

    #Save files and combine 
    ref_file, act_file = comparator.save_uploaded_files(ref_upload, act_upload)
    combined_text = comparator.combine_documents()
    comparator.clean_old_sessions(keep_latest=3)

    print("\n Combined text preview (first 1000 chars): \n")
    print(combined_text[:1000])

    #Step 2: run the LLM comparison
    llm_comparator = DocumentComparatorLLM()
    df = llm_comparator.compare_documents(combined_text)

    print("\n Comparison Dataframe : \n")
    print(df)

if __name__=="__main__":
    test_compare_documents()
