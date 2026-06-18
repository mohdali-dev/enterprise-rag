from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Tuple


class RAGChain:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent document assistant.
Answer questions based on the provided context.

RULES:
- Only answer based on provided context
- If unsure, say "I don't have enough information"
- Always cite your sources with page numbers when available
- Be concise but comprehensive
- Use bullet points for lists
- Highlight key information with **bold**

CONTEXT:
{context}
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
        
        relevant_docs = self.vector_store.similarity_search(
            query=question,
            k=5,
            filter_source=filter_source
        )
        
        if not relevant_docs:
            return ("No relevant information found in the documents.", [])
        
        context = self.format_context(relevant_docs)
        formatted_history = self.format_chat_history(chat_history)
        
        chain = self.rag_prompt | self.llm
        
        response = chain.invoke({
            "context": context,
            "chat_history": formatted_history,
            "question": question
        })
        
        return response.content, relevant_docs
    
    def summarize_document(self, source: str) -> str:
        docs = self.vector_store.similarity_search(
            query="main topics key points summary overview",
            k=10,
            filter_source=source
        )
        
        if not docs:
            return "Could not retrieve document content."
        
        context = self.format_context(docs)
        
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """Create a comprehensive summary of the document.
Include:
1. **Main Topic**: What is this document about?
2. **Key Points**: 5-7 most important points
3. **Important Data**: Any critical numbers/dates
4. **Conclusions**: Main takeaways

Be structured and clear."""),
            ("human", f"Summarize this document:\n\n{context}")
        ])
        
        chain = summary_prompt | self.llm
        response = chain.invoke({})
        
        return response.content
    
    def extract_key_insights(self, source: str) -> str:
        docs = self.vector_store.similarity_search(
            query="insights findings recommendations conclusions data",
            k=8,
            filter_source=source
        )
        
        if not docs:
            return "Could not extract insights."
        
        context = self.format_context(docs)
        
        insights_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract key insights and actionable items.
Format as:

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
            ("human", f"Extract insights from:\n\n{context}")
        ])
        
        chain = insights_prompt | self.llm
        response = chain.invoke({})
        
        return response.content