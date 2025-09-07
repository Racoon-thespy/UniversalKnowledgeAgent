from typing import Dict
import streamlit as st
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI  
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.query_router import QueryRouter
from src.web_searcher import WebSearcher
from config.settings import *


class UniversalChatbot:
    def __init__(self):
        try:
            print("[Chatbot] Initializing LLM with official Gemini integration...")
            model_name = LLM_MODEL if LLM_MODEL else "gemini-2.5-flash"
            print(f"[Chatbot] Using model: {model_name}")
            
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,  
                google_api_key=GEMINI_API_KEY,
                temperature=0.7,
                convert_system_message_to_human=True 
            )
            
            test_response = self.llm.invoke("Test connection")
            print(f"[Chatbot]  LLM test successful, response type: {type(test_response)}")

            print("[Chatbot] Initializing components...")
            self.document_processor = DocumentProcessor(CHUNK_SIZE, CHUNK_OVERLAP)
            self.vector_store = VectorStore(VECTOR_DB_PATH)
            self.query_router = QueryRouter()
            self.web_searcher = WebSearcher()

            self.qa_chain = None
            self._setup_qa_chain()
            print("[Chatbot]  Initialized successfully with Gemini Pro")
            
        except Exception as e:
            print(f"[Chatbot]  Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _setup_qa_chain(self):
        """Setup QA chain for document retrieval"""
        retriever = self.vector_store.get_retriever()
        if retriever:
            try:
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=retriever,
                    return_source_documents=True,
                    verbose=True  
                )
                print("[Chatbot]  QA chain initialized successfully")
            except Exception as e:
                print(f"[Chatbot] Error setting up QA chain: {e}")
                self.qa_chain = None
        else:
            print("[Chatbot] No QA chain - no documents loaded")
            self.qa_chain = None

    def process_uploaded_file(self, uploaded_file) -> bool:
        """Process and add uploaded file to vector store"""
        try:
            import os
            os.makedirs("data/uploads", exist_ok=True)
            
            file_path = f"data/uploads/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            print(f"[Chatbot] Processing document: {uploaded_file.name}")
            documents = self.document_processor.process_document(file_path, uploaded_file.name)
            print(f"[Chatbot] Generated {len(documents)} document chunks")
            
            if documents:
                print(f"[Chatbot] Sample chunk: {documents[0].page_content[:200]}...")
                
            self.vector_store.add_documents(documents)

            self._setup_qa_chain()
            print(f"[Chatbot] Successfully processed {uploaded_file.name}")
            return True

        except Exception as e:
            st.error(f"File processing error: {str(e)}")
            print(f"[Chatbot] Error processing {uploaded_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def answer_query(self, query: str) -> Dict:
        """Route and answer query"""
        has_docs = self.qa_chain is not None
        route = self.query_router.route_query(query, has_docs)

        response = {"answer": "", "sources": [], "route_used": route}
        
        print(f"[Chatbot] Query: {query}")
        print(f"[Chatbot] Route: {route}")

        if route == "document":
            response.update(self._answer_from_documents(query))
        elif route == "web":
            response.update(self._answer_from_web(query))
        else:  # hybrid response
            response.update(self._answer_hybrid(query))

        return response

    def _answer_from_documents(self, query: str) -> Dict:
        """Answer using only documents"""
        if not self.qa_chain:
            return {
                "answer": "No documents available. Please upload some documents first.",
                "sources": ["system"],
            }

        try:
            # check if relevant documents present
            print("[Debug] Searching for relevant documents...")
            relevant_docs = self.vector_store.similarity_search(query, k=5)
            
            if not relevant_docs:
                return {
                    "answer": "No relevant documents found for this query.",
                    "sources": ["documents"],
                }

            print(f"[Debug] Found {len(relevant_docs)} relevant documents")

            try:
                print("[Debug] Invoking QA chain...")
                result = self.qa_chain.invoke({"query": query})
                
                print(f"[Debug] QA chain result type: {type(result)}")
                print(f"[Debug] QA chain result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                # extract answer
                if isinstance(result, dict):
                    answer = result.get("result")
                    if not answer:
                        answer = result.get("answer", result.get("output_text", str(result)))
                    
                    # Get source documents if available
                    source_docs = result.get("source_documents", [])
                    sources = []
                    for doc in source_docs:
                        filename = doc.metadata.get("filename", "Unknown")
                        if filename not in sources:
                            sources.append(filename)
                else:
                    answer = str(result)
                    sources = [doc.metadata.get("filename", "Unknown") for doc in relevant_docs]
                
                if hasattr(answer, 'content'):
                    answer = answer.content
                elif not isinstance(answer, str):
                    answer = str(answer)
                
                print(f"[Debug] QA chain succeeded, answer length: {len(answer) if answer else 0}")
                
            except Exception as e:
                print(f"[Debug] QA chain failed: {str(e)}")
                # Fallback to direct LLM call
                print("[Debug] Using direct LLM fallback...")
                
                context_parts = []
                for i, doc in enumerate(relevant_docs[:3]):
                    context_parts.append(f"Document {i+1}:\n{doc.page_content}")
                
                context = "\n\n".join(context_parts)
                
                prompt = f"""Based on the following documents, please provide a comprehensive answer to the question:

Documents:
{context}

Question: {query}

Answer:"""
                
                try:
                    response = self.llm.invoke(prompt)
                    if hasattr(response, 'content'):
                        answer = response.content
                    else:
                        answer = str(response)
                        
                    sources = [doc.metadata.get("filename", "Unknown") for doc in relevant_docs]
                    sources = list(set(sources))
                    
                except Exception as fallback_error:
                    print(f"[Debug]  Fallback also failed: {str(fallback_error)}")
                    return {"answer": f"Error processing documents: {str(fallback_error)}", "sources": ["error"]}
            
            # Final validation
            if not answer or answer.strip() == "":
                answer = "No answer could be generated from the documents."
            
            if not sources:
                sources = ["documents"]

            print(f"[Chatbot]  Document answer generated: {len(answer)} chars, {len(sources)} sources")
            return {"answer": answer, "sources": sources}
            
        except Exception as e:
            print(f"[Chatbot]  Document search error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"answer": f"Error processing your request: {str(e)}", "sources": ["error"]}

    def _answer_from_web(self, query: str) -> Dict:
        """Answer using direct Google search (no API needed)"""
        try:
            #  Use enhanced search with news if relevant
            search_results = self.web_searcher.enhanced_search(query, include_news=True)
            
            if not search_results:
                return {
                    "answer": "No web search results found. This might be due to network issues or search limitations.", 
                    "sources": ["web"]
                }

            context = self.web_searcher.format_results(search_results)
            prompt = f"""Based on the following web search results, provide a comprehensive and factual answer. 
Synthesize information from multiple sources and provide a well-structured response.

{context}

Question: {query}

Detailed Answer:"""

            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
                
            sources = [result.get("link", "Unknown") for result in search_results[:3]]
            
            print(f"[Chatbot] Web answer generated from {len(search_results)} sources")
            return {"answer": answer, "sources": sources}
            
        except Exception as e:
            print(f"[Chatbot] Web search error: {e}")
            return {"answer": f"Web search error: {str(e)}", "sources": ["error"]}

    def _answer_hybrid(self, query: str) -> Dict:
        """Answer using both documents and web search"""
        try:
            doc_response = self._answer_from_documents(query)
            web_response = self._answer_from_web(query)

            combined_prompt = f"""You have information from both uploaded documents and web search. 
Provide a unified, factually correct, and helpful answer that combines relevant information from both sources.

Document-based answer: {doc_response['answer']}

Web-based answer: {web_response['answer']}

Question: {query}

Final Answer:"""

            response = self.llm.invoke(combined_prompt)
            
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
                
            sources = list(set(doc_response["sources"] + web_response["sources"]))
            
            print(f"[Chatbot] Hybrid answer generated, {len(sources)} sources")
            return {"answer": answer, "sources": sources}
            
        except Exception as e:
            print(f"[Chatbot] Hybrid search error: {e}")
            return {"answer": f"Hybrid search error: {str(e)}", "sources": ["error"]}