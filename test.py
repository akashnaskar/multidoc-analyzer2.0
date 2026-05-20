import os
from pathlib import Path

from multidocchat.src.document_analyzer.data_analysis import DocumentAnalyzer
from multidocchat.src.document_ingestion.data_ingestion import DocHandler

###Path to the file to be tested
PDF_PATH="/Users/apple/Documents/Dev_Stuff/Resume_projects/multidoc-analyzer2.0/data/Attention_is_all_you_need.pdf"

#Dummy file wrapper to upload file
class DummyFile:
    def __init__(self, file_path):
        self.name = Path(file_path).name
        self.file_path= file_path

    def getbuffer(self):
        return open(self.file_path, "rb").read()
    
def main():
    try:
        # step 1: Data analysis
        print("Start Data ingestion")
        dummy_pdf = DummyFile(PDF_PATH)
        handler = DocHandler(data_dir="./data", session_id="test_ingestion_analysis")

        saved_path = handler.save_pdf(dummy_pdf)
        print(f"PDF saved at : {saved_path}")

        text_content = handler.read_pdf(saved_path)
        print(f"Extracted text length: {len(text_content)} chars\n")

        #Data analysis
        print("starting metadata analysis")
        analyzer = DocumentAnalyzer() #Loads LLM + parser

        analysis_result = analyzer.analyze_document(text_content)

        #Step 3: Display result
        print("\n=== METADATA ANALYSIS RESULT ===")
        for key, value in analysis_result.items():
            print(f"{key}: {value}")


    except Exception as e:
        print(f"Test failed: {e}")
        
if __name__=="__main__":
    main()

### Change the prompt registry data again before using
