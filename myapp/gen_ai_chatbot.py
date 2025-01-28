

# import os
# import pickle
# import json
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain.chains import RetrievalQA
# from langchain_community.llms import HuggingFacePipeline
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import transformers
# from transformers import AutoTokenizer, AutoModelForCausalLM
# from PyPDF2 import PdfReader


# class PDFQuestionAnswering:
#     def __init__(self, folder_path, model_path):  # Fixed the constructor method
#         self.folder_path = folder_path
#         self.model_path = model_path
#         self.setup_system()

#     def is_valid_pdf(self, file_path):
#         """Check if the given file is a valid and readable PDF."""
#         try:
#             with open(file_path, "rb") as f:
#                 reader = PdfReader(f)
#                 if len(reader.pages) > 0:
#                     return True
#         except Exception:
#             return False
#         return False

#     def setup_system(self):
#         # Check if processed data exists
#         if os.path.exists("processed_data.pkl"):
#             print("Loading preprocessed data...")
#             with open("processed_data.pkl", "rb") as f:
#                 self.all_splits = pickle.load(f)
#         else:
#             print("Processing new PDFs...")
#             # Step 1: Load PDFs from the folder
#             all_docs = []
#             for file_name in os.listdir(self.folder_path):
#                 if file_name.endswith(".pdf"):
#                     pdf_path = os.path.join(self.folder_path, file_name)
                    
#                     if not self.is_valid_pdf(pdf_path):
#                         print(f"Skipping invalid or corrupted PDF: {file_name}")
#                         continue
                    
#                     print(f"Processing valid PDF: {file_name}")
#                     loader = PyPDFLoader(pdf_path)
#                     docs = loader.load()
#                     all_docs.extend(docs)

#             if not all_docs:
#                 raise Exception("No valid PDFs found in the folder.")

#             # Step 2: Split documents
#             text_splitter = RecursiveCharacterTextSplitter(
#                 chunk_size=1000,
#                 chunk_overlap=200,
#                 length_function=len
#             )
#             self.all_splits = text_splitter.split_documents(all_docs)

#             # Step 3: Save the splits to a file
#             with open("processed_data.pkl", "wb") as f:
#                 pickle.dump(self.all_splits, f)

#         # Step 4: Create embeddings and vector store
#         embedding_model = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2"
#         )
        
#         self.vectorstore = Chroma.from_documents(
#             documents=self.all_splits,
#             embedding=embedding_model,
#             persist_directory="pdf_db"
#         )
#         self.vectorstore_client = self.vectorstore.as_retriever(
#             search_kwargs={"k": 3}
#         )

#         # Setup language model
#         try:
#             self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
#             self.model = AutoModelForCausalLM.from_pretrained(
#                 self.model_path,
#                 device_map="auto"
#             )
#         except Exception as e:
#             raise Exception(f"Error loading language model: {str(e)}")

#         # Setup pipeline
#         self.query_pipeline = transformers.pipeline(
#             "text-generation",
#             model=self.model,
#             tokenizer=self.tokenizer,
#             return_full_text=False,
#             temperature=0.4,       # Slightly higher for diverse outputs
#             top_p=0.9,            # Probability of considering top tokens
#             top_k=50,             # Consider top-k tokens for sampling
#             max_new_tokens=100,
#             repetition_penalty=1.2,  # Penalize repetitive outputs
#             # device_map="auto"
#         )

#         # Create LangChain pipeline
#         llm = HuggingFacePipeline(pipeline=self.query_pipeline)

#         # Setup QA chain
#         self.qa_chain = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=self.vectorstore_client,
#             return_source_documents=False,
#             verbose=True
#         )

#     def ask_question(self, question):
#         """Ask a question and get an answer."""
#         try:
#             result = self.qa_chain({"query": question})
#             answer = result['result']
#             return {
#                 'answer': answer.strip()
#             }
#         except Exception as e:
#             return {
#                 'error': f"Error processing question: {str(e)}"
#             }

#     def save_conversation(self, question, answer):
#         """Save conversation (question and answer) in JSON format."""
#         file_name = "conversation_log.json"
#         conversation = {"question": question, "answer": answer}
        
#         # Load existing conversations
#         if os.path.exists(file_name):
#             with open(file_name, "r") as file:
#                 data = json.load(file)
#         else:
#             data = []

#         # Append new conversation and save back
#         data.append(conversation)
#         with open(file_name, "w") as file:
#             json.dump(data, file, indent=4)
#         print("Conversation saved successfully!")

#     def collect_student_details(self):
#         """Collect details from a new student and save them in a JSON file."""
#         student_details = {}
        
#         student_details['name'] = input("Please provide your name: ")
#         student_details['phone'] = input("Please provide your phone number: ")
#         student_details['email'] = input("Please provide your email: ")
#         student_details['education'] = input("Please provide your educational details: ")

#         # Save details in JSON format
#         with open("student_details.json", "w") as json_file:
#             json.dump(student_details, json_file, indent=4)

#         print("Thanks for providing your details!")

# def main():
#     # Define the paths
#     pdf_folder_path = r"C:\Anam - learn\Freelancing\CNC\Project API\myproject\Courses info2"  # Replace with your local PDF folder path
#     model_path = r"C:\Anam - learn\Freelancing\CNC\Project API\myproject\jsadjbasno"  # Replace with your local model path
    
#     # Initialize the system
#     qa_system = PDFQuestionAnswering(pdf_folder_path, model_path)
#     print("System initialized successfully!\n")

#     # Greeting and ask if the user is new or old student
#     print("Hi, how can I help you?")
#     user_type = input("Are you a new student or an old student? (new/old): ").strip().lower()

#     if user_type == "new":
#         qa_system.collect_student_details()
    
#     # Interaction loop
#     print("You can now ask questions. Type 'exit' to quit.")
#     while True:
#         question = input("\nEnter your question (or 'exit' to quit): ").strip()
        
#         if question.lower() == 'exit':
#             print("Goodbye!")
#             break
        
#         if not question:
#             print("Please enter a valid question.")
#             continue
            
#         result = qa_system.ask_question(question)
#         if 'error' in result:
#             print(f"Error: {result['error']}")
#         else:
#             answer = result['answer']
#             print("\nAnswer:", answer)
            
#             # Save the conversation
#             qa_system.save_conversation(question, answer)

# if __name__ == "__main__":
#     main()









import os
import pickle
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
from PyPDF2 import PdfReader

class PDFQuestionAnswering:
    def __init__(self, folder_path, model_path):
        self.folder_path = folder_path
        self.model_path = model_path
        self.setup_system()

    def is_valid_pdf(self, file_path):
        """Check if the given file is a valid and readable PDF."""
        try:
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                return len(reader.pages) > 0
        except Exception:
            return False

    def setup_system(self):
        # Load or process PDFs
        if os.path.exists("processed_data.pkl"):
            print("Loading preprocessed data...")
            with open("processed_data.pkl", "rb") as f:
                self.all_splits = pickle.load(f)
        else:
            print("Processing new PDFs...")
            all_docs = []
            
            # Check if folder exists
            if not os.path.exists(self.folder_path):
                raise FileNotFoundError(f"Folder not found: {self.folder_path}")
            
            for file_name in os.listdir(self.folder_path):
                if file_name.endswith(".pdf"):
                    pdf_path = os.path.join(self.folder_path, file_name)
                    
                    if not self.is_valid_pdf(pdf_path):
                        print(f"Skipping invalid PDF: {file_name}")
                        continue
                    
                    print(f"Processing PDF: {file_name}")
                    loader = PyPDFLoader(pdf_path)
                    docs = loader.load()
                    all_docs.extend(docs)

            if not all_docs:
                raise Exception("No valid PDFs found in the folder.")

            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            self.all_splits = text_splitter.split_documents(all_docs)

            # Save splits
            with open("processed_data.pkl", "wb") as f:
                pickle.dump(self.all_splits, f)

        # Create embeddings
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=self.all_splits,
            embedding=embedding_model,
            persist_directory="pdf_db"
        )
        self.vectorstore_client = self.vectorstore.as_retriever(
            search_kwargs={"k": 3}
        )

        # Load language model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map="auto"
            )
        except Exception as e:
            raise Exception(f"Error loading language model: {str(e)}")

        # Create query pipeline
        self.query_pipeline = transformers.pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            return_full_text=False,
            temperature=0.4,
            top_p=0.9,
            top_k=50,
            max_new_tokens=100,
            repetition_penalty=1.2,
            device_map="auto"

        )

        # Create LangChain pipeline
        llm = HuggingFacePipeline(pipeline=self.query_pipeline)

        # Setup QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore_client,
            return_source_documents=False,
            verbose=True
        )

    def ask_question(self, question):
        """Ask a question and get an answer."""
        try:
            result = self.qa_chain({"query": question})
            answer = result['result']
            return {
                'answer': answer.strip()
            }
        except Exception as e:
            return {
                'error': f"Error processing question: {str(e)}"
            }

    def save_conversation(self, question, answer):
        """Save conversation in JSON format."""
        file_name = "conversation_log.json"
        conversation = {"question": question, "answer": answer}
        
        # Load existing conversations
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                data = json.load(file)
        else:
            data = []

        # Append new conversation
        data.append(conversation)
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)
        print("Conversation saved successfully!")

def main():
    # Define paths (IMPORTANT: Replace with your actual paths)
    pdf_folder_path = r"C:\Anam - learn\Freelancing\CNC\Project API\myproject\Courses info2"  
    model_path = r"C:\Anam - learn\Freelancing\CNC\Project API\myproject\jsadjbasno"
    
    # Initialize the system
    try:
        qa_system = PDFQuestionAnswering(pdf_folder_path, model_path)
        print("System initialized successfully!")

        # Example question
        question = "What is the main topic of these PDFs?"
        result = qa_system.ask_question(question)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print("\nAnswer:", result['answer'])
            
            # Save conversation
            qa_system.save_conversation(question, result['answer'])

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()



