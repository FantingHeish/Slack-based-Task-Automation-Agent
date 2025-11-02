# RAG-Knowledge-Retrieval-Agent（文件檢索式問答系統）

以 **Retrieval-Augmented Generation（RAG）** 架構建立的智慧問答系統，  
整合文件語意檢索與大型語言模型（LLM），能根據使用者問題自動查找知識內容並生成精確答案。  
應用於企業內部知識查詢、金融報告摘要、自動客服問答等情境。

## 專案簡介
本專案採用 **LangChain + Hugging Face Transformers + ChromaDB** 架構，  
建立一個可擴充的文件檢索式問答流程，結合語意嵌入、重排序、回覆生成與可靠性評估。  
系統能針對長文件進行內容擷取與語意比對，並藉由 reranking 與 hallucination 檢測提升回答精確度。  


## 技術架構

| 模組 | 技術 |
|------|------|
| **開發框架** | LangChain、ChromaDB、OpenAI / HuggingFace Transformers |
| **核心流程** | Chunking → Embedding → Retrieval → Reranking → LLM Response |
| **模型支援** | OpenAI GPT-4、ChatGLM3-6B、Mistral-7B-Instruct |
| **資料庫** | 向量資料庫（ChromaDB） |
| **功能模組** | Query Router、Retrieval Grader、Pointwise & Pairwise Rerank、Hallucination & Answer Grader |
| **部署方式** | Streamlit / Gradio Web 介面 |

---

## 系統架構圖
flowchart TD
    A[使用者輸入問題] --> B[Query Router]
    B --> C["Retriever (Vectorstore / Web)"]
    C --> D[Retrieval Grader]
    D --> E[Pointwise & Pairwise Reranker]
    E --> F[LLM Responder]
    F --> G[Hallucination / Answer Grader]
    G --> H[最終回覆輸出]


### 專案檔案說明
- `Semiconductor_Anomaly_Detection.ipynb`：主要模型訓練與分析流程  
- `requirements.txt`：環境套件清單  
- `model_results.png`：結果視覺化圖表  

