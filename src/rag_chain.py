from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict, Tuple
import logging


class RAGChain:
    def __init__(self, vector_store):
        self.vector_store = vector_store

        # Using a low temperature for highly factual retrieval
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )

        # 1. Query Rewriter Prompt (For handling conversational follow-ups)
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])
        self.question_rewriter = self.contextualize_q_prompt | self.llm | StrOutputParser()

        # 2. Main RAG Prompt (Hardened with XML tags)
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent document assistant.
The CONTEXT below contains extracted text from the user's uploaded files. 
When the user refers to "this file", "the document", or "it", they are referring to the information in this CONTEXT.

RULES:
- Answer questions based strictly on the provided context.
- If unsure, say "I don't have enough information based on the documents."
- Always cite your sources using the source names provided.
- Be concise but comprehensive.

CONTEXT:
<document_content>
{context}
</document_content>
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

    def format_context(self, docs: List[Dict]) -> str:
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc["metadata"].get("source", "Unknown")
            page = doc["metadata"].get("page", "")
            page_info = f", Page {page}" if page else ""

            context_parts.append(
                f"[Source {i}: {source}{page_info}]\n{doc['content']}\n"
            )

        return "\n".join(context_parts)

    def format_chat_history(self, history: List[Dict]) -> List:
        messages = []
        # Keep only the last 6 messages to prevent context bloat
        for msg in history[-6:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        return messages

    def get_answer(
        self,
        question: str,
        chat_history: List[Dict],
        filter_source: str = None
    ) -> Tuple[str, List[Dict]]:

        formatted_history = self.format_chat_history(chat_history)

        # Step 1: Reformulate the query if there is a chat history
        if formatted_history:
            try:
                standalone_question = self.question_rewriter.invoke({
                    "chat_history": formatted_history,
                    "question": question
                })
            except Exception as e:
                logging.warning(
                    f"Failed to rewrite question, falling back to original: {e}")
                standalone_question = question
        else:
            standalone_question = question

        # Step 2: Search the Vector DB using the standalone question
        relevant_docs = self.vector_store.similarity_search(
            query=standalone_question,
            k=5,
            filter_source=filter_source
        )

        if not relevant_docs:
            return ("No relevant information found in the documents.", [])

        # Step 3: Generate the final answer
        context = self.format_context(relevant_docs)
        chain = self.rag_prompt | self.llm

        try:
            response = chain.invoke({
                "context": context,
                "chat_history": formatted_history,
                "question": standalone_question
            })
            return response.content, relevant_docs
        except Exception as e:
            logging.error(f"Error generating RAG answer: {e}")
            raise e

    def summarize_document(self, source: str) -> str:
        # Fetch ALL chunks sequentially to summarize the actual full document
        all_docs = self.vector_store.get_all_chunks(filter_source=source)

        if not all_docs:
            return "Could not retrieve document content from the database."

        full_text = "\n".join([doc["content"] for doc in all_docs])

        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """Create a comprehensive summary of the provided document.
Include:
1. **Main Topic**: What is this document about?
2. **Key Points**: 5-7 most important points
3. **Important Data**: Any critical numbers/dates
4. **Conclusions**: Main takeaways

Be structured and clear."""),
            ("human",
             f"Summarize this document:\n\n<document_content>\n{full_text}\n</document_content>")
        ])

        chain = summary_prompt | self.llm
        try:
            response = chain.invoke({})
            return response.content
        except Exception as e:
            logging.error(f"Summarization error: {e}")
            return f"An error occurred while summarizing the document: {str(e)}"

    def extract_key_insights(self, source: str) -> str:
        # Fetch ALL chunks sequentially to analyze the entire document
        all_docs = self.vector_store.get_all_chunks(filter_source=source)

        if not all_docs:
            return "Could not retrieve document content for insights."

        full_text = "\n".join([doc["content"] for doc in all_docs])

        insights_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract key insights and actionable items from the document.
Format exactly as follows:

🔍 **Key Insights:**
- Insight 1
- Insight 2

✅ **Action Items:**
- Action 1
- Action 2

⚠️ **Important Notes:**
- Note 1

💡 **Recommendations:**
- Recommendation 1
"""),
            ("human",
             f"Extract insights from:\n\n<document_content>\n{full_text}\n</document_content>")
        ])

        chain = insights_prompt | self.llm
        try:
            response = chain.invoke({})
            return response.content
        except Exception as e:
            logging.error(f"Extraction error: {e}")
            return f"An error occurred while extracting insights: {str(e)}"
