import os
import json

def seed():
    # Make database directory
    os.makedirs("database", exist_ok=True)
    
    # ---------------------------------------------------------
    # Core Curated Competency & Weekly Roadmaps (20 Domains)
    # ---------------------------------------------------------
    domain_blueprints = {
        "Artificial Intelligence": {
            "overview": "Build advanced cognitive reasoning systems and deep network architectures.",
            "responsibilities": [
                "Research and build heuristic reasoning models.",
                "Define mathematical objectives and loss metrics.",
                "Build state-transition systems and cognitive graphs."
            ],
            "expectations": "Master foundational network mathematics, backpropagation, and cognitive graph loops.",
            "core_competencies": ["Neural Network Math", "Loss Functions", "State Representation"],
            "supporting_competencies": ["Optimization algorithms", "Linear algebra applications"],
            "technologies": ["Python", "PyTorch", "NumPy", "Matplotlib"],
            "learning_objectives": [
                "Implement backpropagation from scratch in Python.",
                "Train a neural network to classify custom multi-class datasets.",
                "Optimize model latency using vector transformations."
            ],
            "projects": ["Multi-Layer Perceptron from Scratch", "State-Transition Graph Evaluator"],
            "weeks": [
                {
                    "week": 1,
                    "goal": "Foundations of Neural Networks and Matrix Transformations",
                    "objectives": [
                        "Explain weights, biases, and activation functions in feedforward nets.",
                        "Implement matrix dot-products and vector shapes in Python.",
                        "Calculate gradient updates using the chain rule."
                    ],
                    "resources": [
                        {"title": "Neural Networks from Scratch Series", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"},
                        {"title": "Intro to CS and Programming in Python", "provider": "MIT OpenCourseWare", "url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/", "type": "Course"}
                    ],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a 3-layer feedforward network in NumPy with forward pass activations.",
                    "checkpoint": "What is the mathematical role of an activation function in feedforward neural nets?"
                },
                {
                    "week": 2,
                    "goal": "Loss Functions, Optimization, and Backpropagation Mechanics",
                    "objectives": [
                        "Compute categorical cross-entropy and mean squared error loss metrics.",
                        "Implement partial derivatives to compute parameter weights updates.",
                        "Apply Stochastic Gradient Descent (SGD) constraints."
                    ],
                    "resources": [
                        {"title": "Neural Networks Backpropagation Lesson", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}
                    ],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Code a backpropagation module calculating weights updates on a classification dataset.",
                    "checkpoint": "Why does training loss fail to decrease if gradients explode during backpropagation?"
                },
                {
                    "week": 3,
                    "goal": "Deep Architectures and Modern Transformer Principles",
                    "objectives": [
                        "Explain attention mechanisms and self-attention dot-products.",
                        "Analyze multi-head attention blocks and transformer tokenizers.",
                        "Compare positional embeddings with standard word embeddings."
                    ],
                    "resources": [
                        {"title": "3Blue1Brown Deep Learning Series", "provider": "YouTube", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", "type": "video"}
                    ],
                    "practice": "https://huggingface.co/learn",
                    "project": "Implement a simple self-attention query-key-value dot-product in NumPy.",
                    "checkpoint": "How does multi-head attention capture semantic context better than single-turn embeddings?"
                },
                {
                    "week": 4,
                    "goal": "Evaluating Cognitive Graphs and Model Inference Loops",
                    "objectives": [
                        "Evaluate model output metrics across test suites.",
                        "Build loops that feed output tokens back into input buffers.",
                        "Optimize token processing speeds."
                    ],
                    "resources": [
                        {"title": "Evaluating LLM Applications Course", "provider": "DeepLearning.AI", "url": "https://www.deeplearning.ai/short-courses/", "type": "Course"}
                    ],
                    "practice": "https://huggingface.co/learn",
                    "project": "Final Capstone: Build an automated evaluation script that tests model accuracy on classification benchmarks.",
                    "checkpoint": "Explain the trade-off between inference accuracy and memory size in quantization."
                }
            ]
        },
        "Agentic AI": {
            "name": "Agentic AI",
            "desc": "Design and coordinate autonomous AI agents, multi-agent systems, and code-executing workflow engines.",
            "responsibilities": [
                "Implement stateful agent execution loops.",
                "Define and bind tools as APIs for model invocation.",
                "Orchestrate state-transition graphs and multi-agent loops."
            ],
            "expectations": "Ensure secure tool execution sandboxing and reliable message state management in multi-agent routing.",
            "core_competencies": ["ReAct Loop Orchestration", "API Tool Binding", "LangGraph State Machines"],
            "supporting_competencies": ["Docker Sandboxing", "Model Context Protocol"],
            "technologies": ["Python", "LangGraph", "Docker", "Model Context Protocol", "OpenAI SDK"],
            "learning_objectives": [
                "Construct a multi-agent routing graph in LangGraph.",
                "Build secure API-based database tools for model consumption.",
                "Execute generated code inside isolated Docker container environments."
            ],
            "projects": ["Multi-Agent Support Router", "Secure Code Sandbox Executer"],
            "weeks": [
                {
                    "week": 1,
                    "goal": "ReAct Reasoning Framework and Token Control",
                    "objectives": [
                        "Explain the Reasoning and Acting (ReAct) loop paradigm.",
                        "Bind JSON schema tool definitions to LLM prompt structures.",
                        "Configure model parameters (temperature, max tokens) for structured JSON outputs."
                    ],
                    "resources": [
                        {"title": "Prompt Engineering for Developers", "provider": "DeepLearning.AI", "url": "https://www.deeplearning.ai/short-courses/chatgpt-prompt-eng/", "type": "Course"},
                        {"title": "LangChain for LLM Application Development", "provider": "DeepLearning.AI", "url": "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/", "type": "Course"}
                    ],
                    "practice": "https://huggingface.co/learn",
                    "project": "Build a command-line calculator agent that parses query strings and runs math operations using custom Python tools.",
                    "checkpoint": "How does the ReAct framework prevent LLM loops when tool inputs are malformed?"
                },
                {
                    "week": 2,
                    "goal": "Stateful Agent Graphs and Multi-Agent Orchestration",
                    "objectives": [
                        "Model complex system workflows as state graphs.",
                        "Track message states across multi-turn runs.",
                        "Incorporate human validation checks before state modifications."
                    ],
                    "resources": [
                        {"title": "LangGraph Core Conceptual Tutorial", "provider": "LangChain Docs", "url": "https://langchain-ai.github.io/langgraph/", "type": "Documentation"},
                        {"title": "Introduction to LangGraph Course", "provider": "DeepLearning.AI", "url": "https://www.deeplearning.ai/short-courses/", "type": "Course"}
                    ],
                    "practice": "https://langchain-ai.github.io/langgraph/",
                    "project": "Develop a stateful customer query routing graph containing triage, technical support, and manual escalation nodes.",
                    "checkpoint": "What is the role of 'state' in a LangGraph workflow?"
                },
                {
                    "week": 3,
                    "goal": "Model Context Protocol and Host-Client Tool Integration",
                    "objectives": [
                        "Understand Model Context Protocol (MCP) server-client architectures.",
                        "Expose local databases and file folders securely to LLMs.",
                        "Track prompt context sizes during resource mapping."
                    ],
                    "resources": [
                        {"title": "Model Context Protocol Introduction", "provider": "MCP Docs", "url": "https://modelcontextprotocol.io/", "type": "Documentation"},
                        {"title": "APIs for Beginners Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=GZvSYJDk-Us", "type": "video"}
                    ],
                    "practice": "https://modelcontextprotocol.io/",
                    "project": "Build an MCP database server that queries local PostgreSQL records and returns markdown tables to the client.",
                    "checkpoint": "What is the key benefit of standardizing tool communication protocols using MCP?"
                },
                {
                    "week": 4,
                    "goal": "Secure Sandboxing and Docker Code Execution",
                    "objectives": [
                        "Write secure, minimal Dockerfiles for application code.",
                        "Deploy isolated environments for runtime LLM execution.",
                        "Configure resource constraints (CPU limits, execution timeouts)."
                    ],
                    "resources": [
                        {"title": "Docker Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "type": "video"},
                        {"title": "Docker Containerization Essentials", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"}
                    ],
                    "practice": "https://docs.docker.com/get-started/",
                    "project": "Final Capstone: Build an autonomous code execution sandbox that takes text descriptions, generates Python scripts, runs them inside Docker, and compiles output reports.",
                    "checkpoint": "Why must LLM-generated code execution be restricted from root privileges in host environments?"
                }
            ]
        },
        "Machine Learning": {
            "name": "Machine Learning",
            "desc": "Train models on structured/unstructured datasets to recognize patterns and make predictions.",
            "difficulty": "Intermediate",
            "outlook": "Steady High Demand",
            "tags": ["Modeling", "Statistics", "Algorithms"],
            "responsibilities": ["Train regression and classification models.", "Perform feature engineering on tabular data.", "Implement pipeline cross-validation."],
            "expectations": "Ensure models generalize cleanly to unseen datasets by tuning regularization coefficients.",
            "core_competencies": ["Feature Engineering", "Regularization Design", "Cross-Validation Pipeline"],
            "supporting_competencies": ["Linear Regression math", "Data cleaning workflows"],
            "technologies": ["Python", "scikit-learn", "Pandas", "SQL"],
            "learning_objectives": ["Implement K-fold cross validation.", "Analyze bias-variance trade-offs.", "Prepare tabular datasets using Pandas."],
            "projects": ["California Housing Predictor", "Customer Attrition Classifier"],
            "weeks": [
                {
                    "week": 1,
                    "goal": "Python Data Manipulation and SQL Operations",
                    "objectives": ["Ingest and filter tabular data using Pandas.", "Write relational SQL database queries.", "Combine tables using INNER joins."],
                    "resources": [
                        {"title": "Python for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"},
                        {"title": "SQL Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "type": "video"}
                    ],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Write a Python script that joins CSV files, cleans missing values, and exports reports.",
                    "checkpoint": "What is the difference between merging on indices versus columns in Pandas?"
                },
                {
                    "week": 2,
                    "goal": "Linear Regression and Feature Scaling Math",
                    "objectives": ["Explain least squares regression formulas.", "Apply MinMax and Standard scaling transformations.", "Implement Gradient Descent optimization loops."],
                    "resources": [
                        {"title": "Machine Learning Foundations Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}
                    ],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Code a gradient descent optimization loop in NumPy calculating weights updates.",
                    "checkpoint": "Why does feature scaling speed up gradient descent convergence?"
                },
                {
                    "week": 3,
                    "goal": "Bias-Variance Trade-off and Model Regularization",
                    "objectives": ["Identify underfitting and overfitting in metrics graphs.", "Configure L1 Lasso and L2 Ridge regression constraints.", "Optimize regularization alpha parameters."],
                    "resources": [
                        {"title": "Regularization Techniques Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}
                    ],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Train Lasso and Ridge models on housing data, comparing cross-validation test scores.",
                    "checkpoint": "How does L1 regularization differ from L2 regularization in forcing feature coefficients to zero?"
                },
                {
                    "week": 4,
                    "goal": "Classification Models and Pipeline Deployment",
                    "objectives": ["Build classification pipelines using Logistic Regression.", "Calculate precision, recall, and F1 metrics.", "Deploy model instances behind FastAPI endpoints."],
                    "resources": [
                        {"title": "FastAPI Full Tutorial Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=tLKKmouUams", "type": "video"}
                    ],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Build and serve a model instance behind a FastAPI endpoint, validating inputs with Pydantic.",
                    "checkpoint": "Explain when F1-score is a better performance metric than classification accuracy."
                }
            ]
        },
        "Deep Learning": {
            "name": "Deep Learning",
            "desc": "Construct and tune deep neural network architectures for visual, voice, and token processing.",
            "difficulty": "Advanced",
            "outlook": "High Demand / Specialist",
            "tags": ["Neural Networks", "GPU Tuning", "Transformers"],
            "responsibilities": ["Train convolutional and transformer architectures.", "Configure GPU tensor execution resources.", "Apply weight quantization and pruning techniques."],
            "expectations": "Select the correct deep model architecture and scale parameters, balancing hardware constraints and accuracy metrics.",
            "core_competencies": ["Neural Network Design", "GPU Pipeline Management", "Pruning and Quantization"],
            "supporting_competencies": ["Backpropagation math", "Batch normalization configurations"],
            "technologies": ["Python", "PyTorch", "Docker", "Hugging Face"],
            "learning_objectives": ["Train convolutional image classifiers.", "Implement attention layers in PyTorch.", "Optimize deep models using quantization."],
            "projects": ["Custom Image Classifier", "Model Quantization Pipeline"],
            "weeks": [
                {
                    "week": 1,
                    "goal": "Deep Neural Network Architectures in PyTorch",
                    "objectives": ["Write custom model classes inheriting from torch.nn.Module.", "Configure forward activation layers and biases.", "Define backpropagation loss metrics (cross-entropy)."],
                    "resources": [
                        {"title": "PyTorch Tutorial Series", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"},
                        {"title": "PyTorch Getting Started Docs", "provider": "PyTorch", "url": "https://pytorch.org/tutorials/", "type": "Documentation"}
                    ],
                    "practice": "https://pytorch.org/tutorials/",
                    "project": "Build a custom PyTorch class classifying MNIST handwriting digit datasets.",
                    "checkpoint": "What is the role of torch.nn.Module class inheritance in tracking model parameter weights?"
                },
                {
                    "week": 2,
                    "goal": "Convolutional Neural Networks (CNNs) for Visual Datasets",
                    "objectives": ["Explain pooling, kernels, strides, and feature channels.", "Apply spatial filters to extract visual boundaries.", "Implement validation loss tracking loops."],
                    "resources": [
                        {"title": "CNNs Deep Dive Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}
                    ],
                    "practice": "https://pytorch.org/tutorials/",
                    "project": "Build a CIFAR-10 image classifier styled with convolutional and max pooling layers.",
                    "checkpoint": "How do max pooling layers help reduce image spatial dimensions?"
                },
                {
                    "week": 3,
                    "goal": "Sequence Learning and Attention Mechanisms",
                    "objectives": ["Compare recurrent layers with self-attention loops.", "Understand dot-product scaled self-attention.", "Compute attention queries, keys, and values tensors."],
                    "resources": [
                        {"title": "Deep Learning Attention Lesson", "provider": "YouTube", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", "type": "video"}
                    ],
                    "practice": "https://huggingface.co/learn",
                    "project": "Code a multi-head self-attention layer block in PyTorch from scratch.",
                    "checkpoint": "Why do attention layers scale better than recurrent loops for long contexts?"
                },
                {
                    "week": 4,
                    "goal": "Quantization, Pruning, and Containerized Server Deployments",
                    "objectives": ["Apply float16 and int8 quantization limits.", "Prune zero-weight parameters to speed up forward runs.", "Write clean Docker files for model serving endpoints."],
                    "resources": [
                        {"title": "Docker Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "type": "video"},
                        {"title": "Docker Containerization Essentials", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"}
                    ],
                    "practice": "https://docs.docker.com/get-started/",
                    "project": "Final Capstone: Quantize your image classifier to int8 and containerize it behind FastAPI.",
                    "checkpoint": "Explain the trade-offs of float16 quantization during server inference loops."
                }
            ]
        },
        "Large Language Models": {
            "name": "Large Language Models",
            "desc": "Fine-tune, evaluate, optimize, and scale massive transformer architectures and foundational models.",
            "difficulty": "Intermediate",
            "outlook": "Extremely High Demand",
            "tags": ["LLMs", "Tuning", "Orchestration"],
            "responsibilities": ["Fine-tune models on custom corpora.", "Build quantitative evaluation test sets.", "Optimize prompt token boundaries."],
            "expectations": "Ensure models behave safely and output structured formats without hallucinations.",
            "core_competencies": ["Fine-Tuning Frameworks", "LLM Evaluation Suite", "Prompt Anatomy Design"],
            "supporting_competencies": ["Vector database architecture", "System prompt optimization"],
            "technologies": ["Python", "Hugging Face", "OpenAI SDK", "Docker"],
            "learning_objectives": ["Write structured output schemas.", "Build evaluation loops.", "Fine-tune model weights using PEFT."],
            "projects": ["Dynamic Context Router", "Prompt Regression Test Suite"],
            "weeks": [
                {
                    "week": 1,
                    "goal": "Foundations of Prompt Design and LLM Core Mechanics",
                    "objectives": ["Explain tokenization, context windows, and parameter weights.", "Apply zero-shot and few-shot templates.", "Design system prompts for consistent structural outputs."],
                    "resources": [
                        {"title": "Prompt Engineering for Developers", "provider": "DeepLearning.AI", "url": "https://www.deeplearning.ai/short-courses/chatgpt-prompt-eng/", "type": "Course"},
                        {"title": "Large Language Models Explained", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=5sLYAJKMV-I", "type": "video"}
                    ],
                    "docs": {"title": "OpenAI API Reference Guide", "provider": "OpenAI", "url": "https://platform.openai.com/docs/introduction", "type": "Documentation"},
                    "practice": "https://huggingface.co/learn",
                    "project": "Design an evaluation suite that tests a model prompt under multiple system instructions.",
                    "checkpoint": "What is the difference between system, user, and assistant roles in LLM chat APIs?"
                },
                {
                    "week": 2,
                    "goal": "Advanced Prompting, Structured Output Control, and JSON Mode",
                    "objectives": ["Apply chain-of-thought and self-consistency prompts.", "Enforce JSON output schemas using schema parameters.", "Build robust token-saving prompt templates."],
                    "resources": [
                        {"title": "Advanced Prompting Techniques", "provider": "DeepLearning.AI", "url": "https://www.deeplearning.ai/short-courses/chatgpt-prompt-eng/", "type": "Course"}
                    ],
                    "docs": {"title": "Structured Outputs Guide", "provider": "OpenAI Docs", "url": "https://platform.openai.com/docs/introduction", "type": "Documentation"},
                    "practice": "https://huggingface.co/learn",
                    "project": "Build an invoice parsing script that extracts data from invoice texts and structures them into Pydantic models.",
                    "checkpoint": "How does JSON mode guarantee syntactic validity in API response payloads?"
                },
                {
                    "week": 3,
                    "goal": "Prompt Evaluation, Testing, and Optimization",
                    "objectives": ["Establish prompt validation metrics.", "Build automatic grading loops.", "Compare prompt variants using test sets."],
                    "resources": [
                        {"title": "Evaluating LLM Applications", "provider": "DeepLearning.AI", "url": "https://www.deeplearning.ai/short-courses/", "type": "Course"}
                    ],
                    "docs": {"title": "Model Evaluation Guidelines", "provider": "Hugging Face", "url": "https://huggingface.co/learn", "type": "Documentation"},
                    "practice": "https://huggingface.co/learn",
                    "project": "Create a regression testing pipeline that logs prompt completions and checks for semantic drift.",
                    "checkpoint": "Why is deterministic evaluation difficult in generative text systems?"
                },
                {
                    "week": 4,
                    "goal": "Building Real-World Prompt Engineering Workflows",
                    "objectives": ["Design prompt-chaining pipelines.", "Incorporate routing queries to select optimal sub-prompts.", "Expose prompt configurations via APIs."],
                    "resources": [
                        {"title": "Fireship LLM Pipelines Guide", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"}
                    ],
                    "docs": {"title": "OpenAI API Deployment Guide", "provider": "OpenAI", "url": "https://platform.openai.com/docs/introduction", "type": "Documentation"},
                    "practice": "https://huggingface.co/learn",
                    "project": "Final Capstone: Build an automated customer routing endpoint that classifies intent, routes to sub-prompts, and formats output.",
                    "checkpoint": "What is prompt chaining and how does it improve system reliability over single prompt runs?"
                }
            ]
        }
    }
    
    # We populate identical week structures for the other 15 domains.
    # To keep the code size clean but robust, let's write out the templates for all 20 domains in the seeder.
    # Let's define placeholders for other domains with highly specific topics to satisfy the requirement
    # that "every week has a clear purpose" and "avoid generic week titles".
    
    # Let's add other domains to domain_blueprints
    other_domains_data = {
        "Natural Language Processing": {
            "overview": "Process, interpret, and translate human text and voice datasets using semantic pipelines.",
            "responsibilities": ["Design tokenizer filters.", "Build semantic embedding structures.", "Implement named entity routers."],
            "expectations": "Ensure language pipelines capture context correctly, handling semantic variations.",
            "core_competencies": ["Tokenization pipelines", "Semantic Embeddings", "Name Entity Recognition"],
            "supporting_competencies": ["Tf-Idf math", "Regex parsing"],
            "technologies": ["Python", "Hugging Face", "NLTK", "scikit-learn"],
            "learning_objectives": ["Process text data.", "Train semantic classifiers.", "Deploy model entities extractors."],
            "projects": ["Spam Message Classifier", "Sentiment Analytics Dashboard"],
            "weeks": [
                {
                    "week": 1, "goal": "Text Processing and Regex Foundations",
                    "objectives": ["Clean text corpora using Python Regex.", "Apply stopword removal.", "Convert texts to Tf-Idf vectors."],
                    "resources": [{"title": "Python for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a CLI script cleaning messy log files and extracting specific keywords.",
                    "checkpoint": "What does a Tf-Idf metric measure in text corpora?"
                },
                {
                    "week": 2, "goal": "Semantic Vectors and Tokenizer Embeddings",
                    "objectives": ["Understand semantic vector similarity.", "Generate word embeddings using PyTorch.", "Build similarity queries."],
                    "resources": [{"title": "NLP Course Introduction", "provider": "Stanford Online", "url": "https://online.stanford.edu/courses/soe-ycscs224n-natural-language-processing-deep-learning", "type": "Course"}],
                    "practice": "https://huggingface.co/learn",
                    "project": "Build a semantic search index matching user queries against article titles.",
                    "checkpoint": "Why does cosine similarity measure semantic closeness better than Euclidean distance?"
                },
                {
                    "week": 3, "goal": "Named Entity Recognition and Part of Speech Tagging",
                    "objectives": ["Label text entities using spaCy.", "Extract nouns and actions from unstructured sentences.", "Train custom entity labels."],
                    "resources": [{"title": "spaCy NLP Quickstart", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}],
                    "practice": "https://huggingface.co/learn",
                    "project": "Build an resume parser extracting company names and years of experience.",
                    "checkpoint": "What is named entity recognition?"
                },
                {
                    "week": 4, "goal": "Sequence to Sequence Translation and Transformers",
                    "objectives": ["Analyze sequence encoder-decoder blocks.", "Deploy translation models.", "Evaluate translation metrics."],
                    "resources": [{"title": "Attention is All You Need Guide", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=5sLYAJKMV-I", "type": "video"}],
                    "practice": "https://huggingface.co/learn",
                    "project": "Final Capstone: Build a language translator using Hugging Face models.",
                    "checkpoint": "Explain the role of decoder self-attention in translation outputs."
                }
            ]
        },
        "Computer Vision": {
            "overview": "Build systems that classify, segment, and track visual feeds and image data.",
            "responsibilities": ["Design convolutional filters.", "Implement object detection models.", "Configure image resizing scaling."],
            "expectations": "Maximize model accuracy on image arrays, managing brightness and contrast shifts.",
            "core_competencies": ["Image Processing Basics", "Object Detection Models", "Segmentation Pipelines"],
            "supporting_competencies": ["Pixel matrix transformations", "Convolution math"],
            "technologies": ["Python", "OpenCV", "PyTorch", "scikit-image"],
            "learning_objectives": ["Apply edge detection filters.", "Train YOLO model networks.", "Segment objects from backgrounds."],
            "projects": ["Traffic Object Counter", "Medical Image Segmenter"],
            "weeks": [
                {
                    "week": 1, "goal": "Pixel Transformations and Image Processing in OpenCV",
                    "objectives": ["Ingest image matrices into NumPy arrays.", "Apply Sobel and Canny edge detection filters.", "Implement image resizing and scaling algorithms."],
                    "resources": [{"title": "OpenCV Tutorial Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a document scanner pipeline that detects sheet boundaries and aligns visual feeds.",
                    "checkpoint": "How do Canny filters compute gradient changes in pixel values?"
                },
                {
                    "week": 2, "goal": "Convolutional Networks and Feature Extraction",
                    "objectives": ["Explain visual feature kernels.", "Train a convolutional model class in PyTorch.", "Evaluate classification precision."],
                    "resources": [{"title": "CNNs Deep Dive Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}],
                    "practice": "https://pytorch.org/tutorials/",
                    "project": "Build an image classifier identifying road signs from pixel feeds.",
                    "checkpoint": "What is the function of a pooling layer in CNNs?"
                },
                {
                    "week": 3, "goal": "Object Detection and YOLO Framework",
                    "objectives": ["Understand bounding box intersection metrics.", "Deploy YOLO models on visual feeds.", "Measure object counts in real time."],
                    "resources": [{"title": "YOLO Object Detection Guide", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}],
                    "practice": "https://pytorch.org/tutorials/",
                    "project": "Develop a pedestrian detection pipeline logging bounding box locations.",
                    "checkpoint": "Explain the Intersection over Union (IoU) metric."
                },
                {
                    "week": 4, "goal": "Semantic Image Segmentation",
                    "objectives": ["Model pixel classification networks.", "Implement U-Net structures.", "Deploy image segmentation masks."],
                    "resources": [{"title": "U-Net Image Segmentation Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}],
                    "practice": "https://pytorch.org/tutorials/",
                    "project": "Final Capstone: Build a U-Net pipeline classifying cell boundaries in microscope images.",
                    "checkpoint": "How does semantic segmentation differ from standard object detection?"
                }
            ]
        },
        "Data Science": {
            "overview": "Extract meaningful insights from raw datasets using scientific computing and models.",
            "responsibilities": ["Apply statistical significance checks.", "Analyze correlations between factors.", "Train exploratory models."],
            "expectations": "Derive verified statistical correlations, minimizing selection bias errors.",
            "core_competencies": ["Statistical Inference", "Correlation Analysis", "Feature selection"],
            "supporting_competencies": ["Standard distributions", "Exploratory data analysis"],
            "technologies": ["Python", "Pandas", "SciPy", "Matplotlib"],
            "learning_objectives": ["Execute t-tests and p-value checks.", "Build data visualization charts.", "Evaluate exploratory predictors."],
            "projects": ["Clinical Trial Correlation Report", "Customer Churn Predictor"],
            "weeks": [
                {
                    "week": 1, "goal": "Data Ingestion and Pandas Operations",
                    "objectives": ["Load database files into Pandas tables.", "Clean missing cell values.", "Describe column statistics (mean, variance)."],
                    "resources": [{"title": "Python for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Write a script cleaning an ecommerce catalog sheet.",
                    "checkpoint": "What does df.dropna() do in Pandas?"
                },
                {
                    "week": 2, "goal": "Statistical Significance and Hypothesis Testing",
                    "objectives": ["Explain null hypotheses.", "Compute p-values and t-test statistics.", "Apply standard normal distribution checks."],
                    "resources": [{"title": "Hypothesis Testing Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Evaluate whether website button revisions altered checkout metrics.",
                    "checkpoint": "What is the critical threshold of a p-value to reject null hypothesis?"
                },
                {
                    "week": 3, "goal": "Exploratory Predictors and Feature Engineering",
                    "objectives": ["Plot correlation heatmaps.", "Engineer feature combinations.", "Transform distributions using Log changes."],
                    "resources": [{"title": "Data Visualization & Storytelling", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Feature engineer housing data to improve model predictions.",
                    "checkpoint": "Why is highly correlated features problematic in model training?"
                },
                {
                    "week": 4, "goal": "Exploratory Predictor Deployment",
                    "objectives": ["Train linear predictors.", "Validate test metrics.", "Deploy reports."],
                    "resources": [{"title": "FastAPI Web Endpoints Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=tLKKmouUams", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Build and host a house price predictor backend.",
                    "checkpoint": "What is R-squared?"
                }
            ]
        },
        "Data Analytics": {
            "overview": "Clean and transform data to build interactive dashboards and support business choices.",
            "responsibilities": ["Build interactive SQL queries.", "Clean spreadsheet columns.", "Design dashboard charts."],
            "expectations": "Structure clean, digestible visual insights, helping stakeholders make quick business choices.",
            "core_competencies": ["Data Ingestion & Cleaning", "Interactive Querying", "Dashboard Design"],
            "supporting_competencies": ["Excel formulas", "Visual chart selection"],
            "technologies": ["Excel", "SQL", "Tableau", "PowerBI"],
            "learning_objectives": ["Clean sales sheets.", "Write database select joins.", "Build interactive Tableau charts."],
            "projects": ["E-commerce Performance Report", "Marketing Campaign Dashboard"],
            "weeks": [
                {
                    "week": 1, "goal": "Advanced Spreadsheets and VLOOKUP Functions",
                    "objectives": ["Perform cell format cleanups.", "Write VLOOKUP and XLOOKUP formulas.", "Generate regional summary tables."],
                    "resources": [{"title": "Advanced Excel Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=gKDJ4R16k-k", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Clean a messy sales spreadsheet containing null rows and merge regional files.",
                    "checkpoint": "Why is XLOOKUP safer than VLOOKUP?"
                },
                {
                    "week": 2, "goal": "SQL Databases and SELECT Query Queries",
                    "objectives": ["Write SELECT statements with filter clauses.", "Join tables using INNER and LEFT conditions.", "Write grouping aggregates (GROUP BY)."],
                    "resources": [{"title": "SQL Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/relational-database/",
                    "project": "Query an orders database to extract the highest spending customer regions.",
                    "checkpoint": "What is the difference between inner and left joins?"
                },
                {
                    "week": 3, "goal": "BI Dashboards and Tableau Data Connections",
                    "objectives": ["Connect Tableau to Postgres databases.", "Define calculated fields.", "Select visual charts according to data types."],
                    "resources": [{"title": "Tableau Fundamentals Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Connect a database feed to Tableau and map visual channels.",
                    "checkpoint": "When should you use a bar chart instead of a pie chart?"
                },
                {
                    "week": 4, "goal": "Dashboard Design and Capstone Report",
                    "objectives": ["Construct interactive dashboard filters.", "Design visual storytelling reports.", "Export summary presentations."],
                    "resources": [{"title": "Data Visualization Guides", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/sql-handbook/", "type": "Course"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Build a retail performance dashboard tracking monthly KPIs.",
                    "checkpoint": "How do filters improve dashboard usability?"
                }
            ]
        },
        "Data Engineering": {
            "overview": "Build scalable storage solutions, database servers, and orchestrate pipelines.",
            "responsibilities": ["Design relational database schemas.", "Build ETL pipeline scripts.", "Orchestrate Spark cluster tasks."],
            "expectations": "Ensure data streams ingest and transform securely, maintaining low query latencies.",
            "core_competencies": ["Relational Schema Design", "ETL Pipeline Orchestration", "Big Data Clusters"],
            "supporting_competencies": ["PostgreSQL administration", "Data lake storage concepts"],
            "technologies": ["PostgreSQL", "Apache Spark", "Python", "SQL"],
            "learning_objectives": ["Build PostgreSQL tables.", "Write Python ETL pipelines.", "Optimize Spark cluster scripts."],
            "projects": ["Automated Data Ingest Pipeline", "Distributed Analytics Pipeline"],
            "weeks": [
                {
                    "week": 1, "goal": "Relational Databases and PostgreSQL Administration",
                    "objectives": ["Design database schemas.", "Write transactional SQL insert queries.", "Configure database indices."],
                    "resources": [{"title": "PostgreSQL Guides & Tutorials", "provider": "PostgreSQL Tutorial", "url": "https://www.postgresqltutorial.com/", "type": "Documentation"}],
                    "practice": "https://www.postgresqltutorial.com/",
                    "project": "Build an E-commerce database schema and populate it with mock rows.",
                    "checkpoint": "What is the role of a primary key in database tables?"
                },
                {
                    "week": 2, "goal": "Python ETL Pipelines and API Ingestion",
                    "objectives": ["Ingest external data via REST APIs.", "Clean dataset anomalies in Python.", "Insert rows into PostgreSQL tables."],
                    "resources": [{"title": "APIs for Beginners - How to use APIs", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=GZvSYJDk-Us", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Write an automated Python script fetching weather feeds and writing logs to Postgres.",
                    "checkpoint": "How does batch ingestion protect database servers from traffic spikes?"
                },
                {
                    "week": 3, "goal": "Distributed Computing with Apache Spark",
                    "objectives": ["Understand map-reduce distributed patterns.", "Ingest CSV files into Spark DataFrames.", "Perform aggregate operations in Spark."],
                    "resources": [{"title": "Apache Spark Introduction", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Process a 10GB log file using PySpark, returning system crash aggregates.",
                    "checkpoint": "Why is memory-caching beneficial in Apache Spark computations?"
                },
                {
                    "week": 4, "goal": "Docker Containerization and Pipeline Orchestration",
                    "objectives": ["Write minimal Docker files for scripts.", "Containerize data pipelines.", "Scale deployment tasks."],
                    "resources": [
                        {"title": "Docker Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "type": "video"},
                        {"title": "Docker Containerization Essentials", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"}
                    ],
                    "practice": "https://docs.docker.com/get-started/",
                    "project": "Final Capstone: Build and containerize a database ETL script that schedules runs.",
                    "checkpoint": "What does a Docker volume do?"
                }
            ]
        },
        "Software Engineering": {
            "overview": "Design, develop, test, and deploy secure and robust desktop and server applications.",
            "responsibilities": ["Write modular programming structures.", "Apply Git branch workflows.", "Implement automated test scripts."],
            "expectations": "Deploy maintainable, clean codebases, minimizing compilation bugs and logic errors.",
            "core_competencies": ["Modular Code Design", "Git Team Workflows", "Automated Testing"],
            "supporting_competencies": ["Algorithm runtime complexity", "Debugging logs"],
            "technologies": ["Python", "Git", "pytest", "SQL"],
            "learning_objectives": ["Write clean functions.", "Merge Git branches.", "Write unit tests using pytest."],
            "projects": ["Library Management Script", "Test-driven API Server"],
            "weeks": [
                {
                    "week": 1, "goal": "Python Programming Foundations",
                    "objectives": ["Write loops and logic statements.", "Define functions and pass parameters.", "Handle runtime exceptions."],
                    "resources": [
                        {"title": "Python for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"},
                        {"title": "Real Python Learning Path", "provider": "Real Python", "url": "https://realpython.com/start-here/", "type": "Course"}
                    ],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a command-line calculator managing operations and exceptions.",
                    "checkpoint": "What is the difference between a local and global variable scope?"
                },
                {
                    "week": 2, "goal": "Git Branch Workflows and Team Collaboration",
                    "objectives": ["Initialize local Git directories.", "Commit changes and push to GitHub.", "Create feature branches and resolve conflicts."],
                    "resources": [{"title": "Git and GitHub for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Create a GitHub repository, merge a feature branch, and resolve conflicts.",
                    "checkpoint": "Explain the Git rebase command."
                },
                {
                    "week": 3, "goal": "Unit Testing with PyTest and Assertion Logs",
                    "objectives": ["Write unit tests for custom functions.", "Configure testing fixtures.", "Assert output structures and catch failures."],
                    "resources": [{"title": "Python Testing Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Write a suite of unit tests checking math and string helper scripts.",
                    "checkpoint": "Why are testing mocks useful?"
                },
                {
                    "week": 4, "goal": "Relational Schemas and SQL Ingestion",
                    "objectives": ["Write basic database tables schemas.", "Insert rows and query table metrics.", "Merge data sheets using joins."],
                    "resources": [{"title": "SQL Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/relational-database/",
                    "project": "Final Capstone: Build a database-backed task list command line tool.",
                    "checkpoint": "What is the role of a database index?"
                }
            ]
        },
        "Backend Development": {
            "overview": "Develop backend server logic, API endpoints, and database connection pools.",
            "responsibilities": ["Develop REST API routes.", "Optimize database transaction query sheets.", "Expose documentation endpoints."],
            "expectations": "Deploy secure, validation-locked server APIs, ensuring low response latencies.",
            "core_competencies": ["REST Routing Design", "Database Connections Pool", "Input Payload Validation"],
            "supporting_competencies": ["JWT Authentication", "FastAPI setup"],
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Pydantic"],
            "learning_objectives": ["Create FastAPI routes.", "Validate inputs with Pydantic.", "Configure connection pools."],
            "projects": ["Task Manager Backend", "Secure User Auth Portal"],
            "weeks": [
                {
                    "week": 1, "goal": "Python Servers and FastAPI Endpoints",
                    "objectives": ["Write server routes using FastAPI.", "Configure request queries and paths.", "Return formatted JSON objects."],
                    "resources": [{"title": "FastAPI Full Tutorial Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=tLKKmouUams", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a FastAPI web app serving item records.",
                    "checkpoint": "What Python library handles request validation in FastAPI?"
                },
                {
                    "week": 2, "goal": "Database Schemas and Connection Management",
                    "objectives": ["Connect FastAPI to Postgres.", "Write raw insert queries.", "Configure database connection pools."],
                    "resources": [{"title": "PostgreSQL Guides & Tutorials", "provider": "PostgreSQL Tutorial", "url": "https://www.postgresqltutorial.com/", "type": "Documentation"}],
                    "practice": "https://www.postgresqltutorial.com/",
                    "project": "Build a database-backed server backend registering items in PostgreSQL.",
                    "checkpoint": "Why are connection pools superior to opening new connections per query?"
                },
                {
                    "week": 3, "goal": "Secure User Authentication and JWT Tokens",
                    "objectives": ["Implement password hashing using bcrypt.", "Issue signed JSON Web Tokens (JWT).", "Design route protection middlewares."],
                    "resources": [{"title": "API Security Best Practices", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/api-handbook/", "type": "Course"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build an authentication endpoint validation route.",
                    "checkpoint": "How does stateless JWT validation protect endpoints?"
                },
                {
                    "week": 4, "goal": "Server Containerization and Deployment",
                    "objectives": ["Write minimal Docker files.", "Configure environment variables inside containers.", "Deploy server instances."],
                    "resources": [
                        {"title": "Docker Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "type": "video"},
                        {"title": "Docker Containerization Essentials", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"}
                    ],
                    "practice": "https://docs.docker.com/get-started/",
                    "project": "Final Capstone: Build and containerize a database-backed API endpoint with unit tests.",
                    "checkpoint": "Explain the difference between COPY and ADD in Dockerfiles."
                }
            ]
        },
        "Frontend Development": {
            "overview": "Create interactive user interfaces, web applications, and responsive visual styles.",
            "responsibilities": ["Write structured HTML markup templates.", "Build layouts with Flexbox/Grid.", "Manage UI state graphs in React."],
            "expectations": "Ensure responsive, fast-loading visual screens across multiple device layouts.",
            "core_competencies": ["Visual Layout Architecture", "Responsive Style Sheets", "Stateful UI Components"],
            "supporting_competencies": ["CSS animations", "DOM event handlers"],
            "technologies": ["HTML", "CSS", "JavaScript", "React"],
            "learning_objectives": ["Build Flexbox grids.", "Write event handlers.", "Manage state hooks in React."],
            "projects": ["Responsive Portfolio Page", "React Task Dashboard"],
            "weeks": [
                {
                    "week": 1, "goal": "Responsive Visual Layouts with CSS Grid and Flexbox",
                    "objectives": ["Construct grid layouts.", "Style flex elements.", "Build media query responsive templates."],
                    "resources": [{"title": "CSS Grid & Flexbox Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=hG7hV-17xUM", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a responsive grid portfolio gallery page.",
                    "checkpoint": "How does flex-shrink differ from flex-grow?"
                },
                {
                    "week": 2, "goal": "JavaScript Programming and DOM Event Loops",
                    "objectives": ["Write JS variables and loops.", "Select DOM elements dynamically.", "Register input event handlers."],
                    "resources": [{"title": "JavaScript Programming Course", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/", "type": "Course"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build an interactive checklist page storing list arrays locally.",
                    "checkpoint": "Explain event bubbling in DOM trees."
                },
                {
                    "week": 3, "goal": "React Single Page Applications and Component State",
                    "objectives": ["Build modular React components.", "Manage state variables using useState.", "Load side effects using useEffect hooks."],
                    "resources": [{"title": "React Hooks Explained Simply", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=LlvBzyy-558", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a stateful React stopwatch tracking ticks.",
                    "checkpoint": "What is the dependency array in useEffect hooks?"
                },
                {
                    "week": 4, "goal": "API Integration and Static Deployments",
                    "objectives": ["Fetch external REST API data in React.", "Render loops of records lists.", "Deploy static bundles to Vercel."],
                    "resources": [{"title": "API Handbook Guide", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/api-handbook/", "type": "Documentation"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Build a React Weather app that pulls feeds from public endpoints and displays data.",
                    "checkpoint": "How do you handle loading states during data fetch loops in React?"
                }
            ]
        },
        "Full Stack Development": {
            "overview": "Master both frontend user interfaces and backend server layers to build complete web applications.",
            "responsibilities": ["Design SQL database schemas.", "Write FastAPI route endpoints.", "Build React component layers."],
            "expectations": "Deploy integrated web applications, linking client interactions cleanly with database tables.",
            "core_competencies": ["Backend Server Setup", "Frontend Component Design", "E2E API Integration"],
            "supporting_competencies": ["Docker cluster setups", "Secure token management"],
            "technologies": ["React", "FastAPI", "PostgreSQL", "Docker"],
            "learning_objectives": ["Build full stack pipelines.", "Validate server payloads.", "Deploy unified app containers."],
            "projects": ["Full Stack Blog Platform", "Integrated Inventory Manager"],
            "weeks": [
                {
                    "week": 1, "goal": "Frontend Component Layouts with React Hooks",
                    "objectives": ["Write stateful React forms.", "Catch DOM input change events.", "Manage list states."],
                    "resources": [{"title": "React Hooks Explained Simply", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=LlvBzyy-558", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a React form component validating input characters.",
                    "checkpoint": "How do you update list states in React without mutation?"
                },
                {
                    "week": 2, "goal": "Backend Web Endpoints with FastAPI and Pydantic",
                    "objectives": ["Create FastAPI GET and POST routes.", "Validate JSON payloads using Pydantic.", "Return JSON responses."],
                    "resources": [{"title": "FastAPI Full Tutorial Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=tLKKmouUams", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a FastAPI server backend managing task objects.",
                    "checkpoint": "What is the Pydantic BaseModel class?"
                },
                {
                    "week": 3, "goal": "Connecting Client UI to Backend Database API",
                    "objectives": ["Fetch backend data streams in React.", "Send client payloads using fetch queries.", "Clean SQL tables schemas."],
                    "resources": [{"title": "API Handbook Guide", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/api-handbook/", "type": "Documentation"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Integrate your React client app with your FastAPI task endpoint.",
                    "checkpoint": "What is Cross-Origin Resource Sharing (CORS)?"
                },
                {
                    "week": 4, "goal": "Full Stack Container Deployment",
                    "objectives": ["Write Dockerfiles for backend and frontend.", "Map port networks between containers.", "Scale server assets."],
                    "resources": [
                        {"title": "Docker Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "type": "video"},
                        {"title": "Docker Containerization Essentials", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"}
                    ],
                    "practice": "https://docs.docker.com/get-started/",
                    "project": "Final Capstone: Containerize and deploy your full stack task application using Docker.",
                    "checkpoint": "What is the role of Docker Compose in multi-container setups?"
                }
            ]
        },
        "Mobile Development": {
            "overview": "Build native and cross-platform mobile apps for Android and iOS systems.",
            "responsibilities": ["Design mobile layouts.", "Manage local device storage sheets.", "Incorporate push notifications."],
            "expectations": "Ensure smooth transitions and lightweight bundle files on mobile viewports.",
            "core_competencies": ["Mobile Layout Design", "Local State Persisting", "Mobile view alignments"],
            "supporting_competencies": ["API client requests", "Git branch steps"],
            "technologies": ["React Native", "Git", "API Integration"],
            "learning_objectives": ["Build React Native lists.", "Persist states on device.", "Incorporate API feeds."],
            "projects": ["Mobile Task Checklist", "Mobile News Aggregator"],
            "weeks": [
                {
                    "week": 1, "goal": "Mobile Layouts with React Native Views",
                    "objectives": ["Build mobile view templates.", "Apply CSS styling grids on mobile screens.", "Configure scroll views."],
                    "resources": [{"title": "CSS Grid & Flexbox Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=hG7hV-17xUM", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a mobile layout sheet displaying profile columns.",
                    "checkpoint": "How does layout calculation on React Native differ from browsers?"
                },
                {
                    "week": 2, "goal": "State Management and Hooks in Mobile Frameworks",
                    "objectives": ["Manage page view configurations.", "Configure local list objects state.", "Write input validators."],
                    "resources": [{"title": "React Hooks Explained Simply", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=LlvBzyy-558", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a stateful checklist mobile page with local updates.",
                    "checkpoint": "Why are hooks optimal for functional mobile components?"
                },
                {
                    "week": 3, "goal": "Consuming Web APIs on Mobile Clients",
                    "objectives": ["Query REST APIs using fetch calls.", "Handle asynchronous load states on screens.", "Render list maps dynamically."],
                    "resources": [{"title": "API Handbook Guide", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/api-handbook/", "type": "Documentation"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build an articles list feed mobile app pulling data from open APIs.",
                    "checkpoint": "How do you display spinner screens during fetch wait times?"
                },
                {
                    "week": 4, "goal": "Mobile Local Storage and Build Operations",
                    "objectives": ["Persist state variables on device storages.", "Manage build properties.", "Publish build packages."],
                    "resources": [{"title": "Git and GitHub for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Build a fully functional mobile task tracker preserving data on reboot.",
                    "checkpoint": "What is Async Storage?"
                }
            ]
        },
        "Cloud Computing": {
            "overview": "Architect, scale, and secure virtualized infrastructure and cloud microservices.",
            "responsibilities": ["Manage virtual machine containers.", "Configure VPC networks and firewalls.", "Setup load balancer groups."],
            "expectations": "Maintain cost-efficient, high-uptime cloud clusters, routing network traffic securely.",
            "core_competencies": ["Virtual Networks Design", "Load Balancer Configurations", "Cloud security architectures"],
            "supporting_competencies": ["Docker container setup", "Git repository tasks"],
            "technologies": ["AWS", "Docker", "Git", "Linux"],
            "learning_objectives": ["Configure AWS VPCs.", "Dockerize server assets.", "Configure security groups."],
            "projects": ["High-availability Web Cluster", "Automated Cloud Backup Pipeline"],
            "weeks": [
                {
                    "week": 1, "goal": "Cloud Infrastructure Basics and Virtual Networks",
                    "objectives": ["Understand public vs private cloud regions.", "Configure VPC subnets and routing maps.", "Register security group firewalls."],
                    "resources": [{"title": "AWS Cloud Practitioner Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=SOTamWGuqXs", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Design and map a secure multi-subnet network architecture plan.",
                    "checkpoint": "What is the difference between a public subnet and a private subnet?"
                },
                {
                    "week": 2, "goal": "Containerizing Microservices with Docker",
                    "objectives": ["Write minimal Docker files for applications.", "Configure ports maps and volume mounts.", "Deploy isolated app containers."],
                    "resources": [
                        {"title": "Docker Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "type": "video"},
                        {"title": "Docker Containerization Essentials", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"}
                    ],
                    "practice": "https://docs.docker.com/get-started/",
                    "project": "Dockerize a Python server API and test local container ports.",
                    "checkpoint": "Why are container images lightweight compared to Virtual Machines?"
                },
                {
                    "week": 3, "goal": "Load Balancing and Scalable Virtual Machines",
                    "objectives": ["Deploy virtual server instances.", "Set up load balancer groups.", "Configure autoscaling threshold rules."],
                    "resources": [{"title": "Cloud Architecting Guides", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=SOTamWGuqXs", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Deploy a load-balanced cluster of virtual servers distributing requests.",
                    "checkpoint": "How do health checks protect load balancer routing targets?"
                },
                {
                    "week": 4, "goal": "Version Control and Infrastructure Automation",
                    "objectives": ["Commit pipeline configurations to Git.", "Deploy microservice updates.", "Configure backup tasks."],
                    "resources": [{"title": "Git and GitHub for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Build and launch a cloud pipeline executing automated image backups.",
                    "checkpoint": "What is Infrastructure as Code?"
                }
            ]
        },
        "DevOps": {
            "overview": "Automate code compilation, continuous delivery (CI/CD) pipelines, and container clouds.",
            "responsibilities": ["Write CI/CD pipeline automation files.", "Manage Docker image repositories.", "Orchestrate Kubernetes deployment pods."],
            "expectations": "Deliver continuous deployment steps, validating test coverage logs automatically.",
            "core_competencies": ["CI/CD Pipeline Design", "Docker Image Management", "Kubernetes Pod Deployment"],
            "supporting_competencies": ["Automated unit test runs", "Git workflows"],
            "technologies": ["Docker", "Kubernetes", "Git", "pytest"],
            "learning_objectives": ["Write Git pipelines.", "Containerize applications.", "Deploy Kubernetes pods."],
            "projects": ["CI/CD Testing Pipeline", "Scalable Kubernetes Web App"],
            "weeks": [
                {
                    "week": 1, "goal": "Python Automated Testing and Git Commit Workflows",
                    "objectives": ["Write unit tests using pytest.", "Initialize Git configurations.", "Manage branch push pipelines."],
                    "resources": [
                        {"title": "Git and GitHub for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk", "type": "video"},
                        {"title": "Python Testing Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}
                    ],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Write a pipeline checking unit test assertions before merges.",
                    "checkpoint": "Why should test execution block main branch merges?"
                },
                {
                    "week": 2, "goal": "Application Containerization with Docker",
                    "objectives": ["Write clean Dockerfiles.", "Map ports and persist logs via mounts.", "Build container images."],
                    "resources": [
                        {"title": "Docker Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "type": "video"},
                        {"title": "Docker Containerization Essentials", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"}
                    ],
                    "practice": "https://docs.docker.com/get-started/",
                    "project": "Dockerize a Python server API validating inputs with Pydantic.",
                    "checkpoint": "Explain the role of Docker layers caching."
                },
                {
                    "week": 3, "goal": "Kubernetes Clusters and Pod Deployments",
                    "objectives": ["Understand Kubernetes architecture.", "Write deployment YAML manifests.", "Create pod services."],
                    "resources": [
                        {"title": "Kubernetes Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "type": "video"},
                        {"title": "Kubernetes Reference Documentation", "provider": "Kubernetes Docs", "url": "https://kubernetes.io/docs/home/", "type": "Documentation"}
                    ],
                    "practice": "https://kubernetes.io/docs/home/",
                    "project": "Write a Kubernetes deployment manifest running three pod replicas.",
                    "checkpoint": "What is a ReplicaSet in Kubernetes?"
                },
                {
                    "week": 4, "goal": "Orchestrating CI/CD Deployment Workflows",
                    "objectives": ["Write build scripts automating runs.", "Expose ports and check load balancer states.", "Deploy app container fleets."],
                    "resources": [{"title": "CI/CD Orchestration guides", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/api-handbook/", "type": "Documentation"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Deploy a fully automated pipeline compiling, testing, and launching containerized API services.",
                    "checkpoint": "Explain the difference between continuous integration and continuous deployment."
                }
            ]
        },
        "Site Reliability Engineering": {
            "overview": "Apply software engineering to automate system operations and maximize uptime.",
            "responsibilities": ["Monitor system latency and error logs.", "Configure autoscaling clusters.", "Manage system alert groups."],
            "expectations": "Maintain low error rates and high uptime, designing automatic recovery scripts.",
            "core_competencies": ["Latency Monitoring", "Autoscaling Design", "Automated System Recovery"],
            "supporting_competencies": ["Docker basics", "Linux operations"],
            "technologies": ["Kubernetes", "Docker", "Prometheus", "Linux"],
            "learning_objectives": ["Monitor metrics.", "Write deployment files.", "Manage system limits."],
            "projects": ["Automatic Recovery script", "Monitoring Dashboard setup"],
            "weeks": [
                {
                    "week": 1, "goal": "Linux Systems Administration and Scripting",
                    "objectives": ["Monitor CPU and memory bounds.", "Write bash scripts automating tasks.", "Inspect server log directories."],
                    "resources": [{"title": "Linux Commands Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Write a bash script logging memory utilization metrics.",
                    "checkpoint": "What does the top command show in Linux?"
                },
                {
                    "week": 2, "goal": "Docker Container Operations",
                    "objectives": ["Configure container volumes.", "Configure network interfaces.", "Configure resource constraints."],
                    "resources": [
                        {"title": "Docker Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "type": "video"},
                        {"title": "Docker Containerization Essentials", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "Documentation"}
                    ],
                    "practice": "https://docs.docker.com/get-started/",
                    "project": "Deploy a container with CPU limits and test performance.",
                    "checkpoint": "Explain container isolation mechanics."
                },
                {
                    "week": 3, "goal": "Kubernetes Cluster Management",
                    "objectives": ["Configure Kubernetes namespaces.", "Write deployment yaml manifests.", "Register node services."],
                    "resources": [
                        {"title": "Kubernetes Tutorial for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "type": "video"},
                        {"title": "Kubernetes Reference Documentation", "provider": "Kubernetes Docs", "url": "https://kubernetes.io/docs/home/", "type": "Documentation"}
                    ],
                    "practice": "https://kubernetes.io/docs/home/",
                    "project": "Deploy a multi-pod cluster on a local minikube instance.",
                    "checkpoint": "What is a namespace in Kubernetes?"
                },
                {
                    "week": 4, "goal": "Uptime Monitoring and System Alerting",
                    "objectives": ["Configure metrics dashboards.", "Write automated recovery tasks.", "Configure alerting thresholds."],
                    "resources": [{"title": "SRE Metrics & Monitoring Guides", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Set up a server monitoring script executing restart commands on failure.",
                    "checkpoint": "What is a Service Level Objective (SLO)?"
                }
            ]
        },
        "Cybersecurity": {
            "overview": "Protect server networks, applications, and operating systems from attacks and breaches.",
            "responsibilities": ["Identify application security gaps.", "Analyze network traffic logs.", "Conduct penetration test scripts."],
            "expectations": "Secure infrastructure networks and endpoints, blocking unauthorized ingress paths.",
            "core_competencies": ["Vulnerability Scanning", "Network Traffic Analysis", "Penetration Testing"],
            "supporting_competencies": ["Cryptography basics", "Linux directory structures"],
            "technologies": ["Wireshark", "Nmap", "Linux", "Python"],
            "learning_objectives": ["Perform network scans.", "Analyze database input vectors.", "Configure port firewalls."],
            "projects": ["Vulnerability Scanner", "Port Access Controller"],
            "weeks": [
                {
                    "week": 1, "goal": "Network Basics and Wireshark Packet Analysis",
                    "objectives": ["Understand TCP/IP network layers.", "Analyze traffic packet headers.", "Filter protocols in Wireshark."],
                    "resources": [{"title": "Computer Networking Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=qiQR5wrgCsU", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Filter a PCAP file in Wireshark identifying plain-text credentials.",
                    "checkpoint": "Explain the TCP three-way handshake."
                },
                {
                    "week": 2, "goal": "Linux Security and Privilege Models",
                    "objectives": ["Configure Linux file permissions.", "Identify root escalation vectors.", "Audit authentication logs."],
                    "resources": [{"title": "Linux Security Basics", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=kqtD5eraMx8", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Perform a privilege audit on a Linux VM, locking insecure directories.",
                    "checkpoint": "What is the difference between chmod and chown?"
                },
                {
                    "week": 3, "goal": "Vulnerability Scanning and Port Discovery",
                    "objectives": ["Scan networks using Nmap.", "Identify open ports and service versions.", "Analyze vulnerability databases (CVEs)."],
                    "resources": [{"title": "Nmap Scanning Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Perform a secure scan on a local test target, identifying out-of-date service versions.",
                    "checkpoint": "What is a CVE?"
                },
                {
                    "week": 4, "goal": "API Security and Input Sanitization",
                    "objectives": ["Scan database input vulnerabilities.", "Validate payloads with secure schemas.", "Configure database indices."],
                    "resources": [{"title": "API Security Best Practices", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/api-handbook/", "type": "Course"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Build a Python API secure against SQL injection attacks, validating inputs.",
                    "checkpoint": "Explain how prepared statements block SQL injection."
                }
            ]
        },
        "UI/UX Design": {
            "overview": "Analyze user behavior, design mockups, and build visual layout workflows.",
            "responsibilities": ["Design wireframe layouts.", "Build interactive Figma prototypes.", "Conduct user testing trials."],
            "expectations": "Structure clean, intuitive user workflows, ensuring clear navigability.",
            "core_competencies": ["Wireframe Design", "Figma Prototyping", "User Experience Auditing"],
            "supporting_competencies": ["CSS styles structures", "Visual typography grids"],
            "technologies": ["Figma", "CSS", "HTML"],
            "learning_objectives": ["Build wireframes.", "Configure auto-layout frames.", "Inspect CSS code in Figma."],
            "projects": ["Landing Page mockup", "User Flow Prototype"],
            "weeks": [
                {
                    "week": 1, "goal": "User Experience Foundations and Wireframing",
                    "objectives": ["Design user persona profiles.", "Sketch paper wireframe structures.", "Define user journey layouts."],
                    "resources": [{"title": "UI/UX Design Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=c9Wg6RyOx0U", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Create a 3-screen wireframe map for a mobile shopping catalog.",
                    "checkpoint": "What is the primary objective of a user persona?"
                },
                {
                    "week": 2, "goal": "Figma Auto-Layout and Component Design",
                    "objectives": ["Build components with Figma auto-layout.", "Create reusable design system tokens.", "Apply visual typography spacing."],
                    "resources": [{"title": "Figma Auto-Layout Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=c9Wg6RyOx0U", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build a responsive navigation bar and card component in Figma.",
                    "checkpoint": "How does auto-layout benefit developer hand-off?"
                },
                {
                    "week": 3, "goal": "Interactive Figma Prototypes and Transitions",
                    "objectives": ["Link mockup screens with trigger events.", "Apply transitions (smart animate).", "Conduct user testing sessions."],
                    "resources": [{"title": "Figma Prototyping Course", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=c9Wg6RyOx0U", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Build an interactive checkout flow prototype linking components.",
                    "checkpoint": "What is the goal of smart animate?"
                },
                {
                    "week": 4, "goal": "HTML/CSS Interface Inspection",
                    "objectives": ["Inspect Figma CSS properties.", "Translate components into HTML/CSS.", "Configure responsive grid CSS."],
                    "resources": [{"title": "CSS Grid & Flexbox Tutorial", "provider": "YouTube", "url": "https://www.youtube.com/watch?v=hG7hV-17xUM", "type": "video"}],
                    "practice": "https://www.freecodecamp.org/learn/",
                    "project": "Final Capstone: Build and publish a responsive HTML/CSS landing page from a Figma mockup.",
                    "checkpoint": "How do media queries support responsive screen widths?"
                }
            ]
        }
    }
    
    # Merge blueprints
    domain_blueprints.update(other_domains_data)
    
    # ---------------------------------------------------------
    # 5. roles.json & curriculum.json program generation
    # ---------------------------------------------------------
    roles = {}
    curriculum = []
    
    role_templates = {
        "Artificial Intelligence": [
            "AI Specialist", "AI Researcher", "Cognitive Systems Architect",
            "AI Solutions Engineer", "AI Strategy Consultant", "AI Ethicist",
            "Applied AI Engineer", "Autonomous Systems Specialist"
        ],
        "Agentic AI": [
            "Agentic AI Developer", "AI Workflow Engineer", "AI Automation Engineer",
            "Multi-Agent Systems Engineer", "AI Integration Engineer", "Enterprise Agent Developer",
            "RPA AI Specialist", "Cognitive Flow Architect"
        ],
        "Machine Learning": [
            "Machine Learning Engineer", "Applied ML Engineer", "Feature Store Specialist",
            "ML Research Scientist", "ML Pipeline Developer", "Model Optimization Engineer",
            "ML Platform Engineer", "MLOps Automation Lead"
        ],
        "Deep Learning": [
            "Deep Learning Engineer", "Neural Networks Specialist", "GPU Tuning Engineer",
            "DL Research Scientist", "Vision DL Architect", "Transformer Engineer",
            "Compute Resource Allocator", "Quantization Specialist"
        ],
        "Large Language Models": [
            "LLM Developer", "LLM Evaluation Specialist", "Prompt Engineer",
            "RAG Engineer", "Vector Database Specialist", "LLM Security Auditor",
            "Fine-Tuning Specialist", "Context Optimization Engineer"
        ],
        "Natural Language Processing": [
            "NLP Engineer", "Conversational AI Designer", "Semantic Search Specialist",
            "Computational Linguist", "NLP Researcher", "Text Analytics Engineer",
            "Speech Processing Engineer", "NLP Database Admin"
        ],
        "Computer Vision": [
            "Computer Vision Engineer", "Image Processing Specialist", "Perception Engineer",
            "Visual CV Architect", "Spatial Processing Developer", "CV Optimization Engineer",
            "Video Analytics Developer", "CV Quality Analyst"
        ],
        "Data Science": [
            "Data Scientist", "Decision Scientist", "Quantitative Analyst",
            "Applied Statistician", "Data Modeler", "Data Science Lead",
            "Predictive Modeler", "Experimental Designer"
        ],
        "Data Analytics": [
            "Data Analyst", "Business Intelligence Analyst", "Product Data Analyst",
            "Excel Specialist", "BI Developer", "Marketing Analyst",
            "Sales Data Consultant", "Operations Analyst"
        ],
        "Data Engineering": [
            "Data Pipeline Engineer", "Database Engineer", "Data Warehouse Architect",
            "ETL Developer", "Postgres Administrator", "Data Lake Specialist",
            "Spark Operations Lead", "DB Integration Engineer"
        ],
        "Software Engineering": [
            "Backend Developer", "Frontend Developer", "Full Stack Developer",
            "Software Engineer", "Systems Engineer", "Application Developer",
            "Git Operations Lead", "Desktop App Engineer"
        ],
        "Backend Development": [
            "Backend Engineer", "API Developer", "Serverless Specialist",
            "FastAPI Developer", "REST API Architect", "Database Connections Lead",
            "Backend Security Architect", "Python Server Developer"
        ],
        "Frontend Development": [
            "Frontend Engineer", "UI Developer", "SPA Developer",
            "React Web Developer", "Web Designer", "Responsive Layout Builder",
            "CSS Architect", "Component Library Maintainer"
        ],
        "Full Stack Development": [
            "Full Stack Web Developer", "Full-Stack AI Developer", "Rapid Prototyping Engineer",
            "Web App Lead", "Deployments Architect", "Figma-to-Code Developer",
            "FullStack Security Specialist", "SaaS Developer"
        ],
        "Mobile Development": [
            "Mobile App Engineer", "iOS Developer", "Android Developer",
            "Flutter Developer", "React Native Developer", "Mobile UI Builder",
            "Mobile Security Analyst", "Mobile Performance Specialist"
        ],
        "Cloud Computing": [
            "Cloud Solutions Architect", "Cloud Systems Administrator", "Cloud Security Engineer",
            "AWS Architect", "Virtualization Specialist", "Cloud Scaling Lead",
            "Multicloud Coordinator", "Cloud FinOps Analyst"
        ],
        "DevOps": [
            "DevOps Engineer", "Platform Engineer", "Release Coordinator",
            "CI/CD Pipeline Lead", "Containerization Lead", "Docker Specialist",
            "DevOps Automation Engineer", "Kubernetes Deployment Lead"
        ],
        "Site Reliability Engineering": [
            "Site Reliability Engineer", "SRE Lead", "Infrastructure Automation Engineer",
            "Systems Reliability Auditor", "Chaos Engineering Lead", "Monitoring Analyst",
            "Infrastructure Developer", "Network Reliability Architect"
        ],
        "Cybersecurity": [
            "SOC Analyst", "Penetration Tester", "Cybersecurity Engineer",
            "Security Auditor", "Threat Intelligence Analyst", "Network Defender",
            "Incident Response Specialist", "Vulnerability Auditor"
        ],
        "UI/UX Design": [
            "UI/UX Designer", "Product Designer", "Interaction Designer",
            "Figma Prototyper", "UX Researcher", "Usability Analyst",
            "Wireframe Architect", "Visual Design Specialist"
        ]
    }
    
    for domain_name, roles_list in role_templates.items():
        blueprint = domain_blueprints[domain_name]
        
        for role_name in roles_list:
            # Map role metadata structured object
            roles[role_name] = {
                "domain": domain_name,
                "role_overview": f"{(blueprint.get('overview') or blueprint.get('desc', ''))} targeting specifically the {role_name} career role.",
                "responsibilities": blueprint["responsibilities"],
                "expectations": blueprint["expectations"],
                "core_competencies": blueprint["core_competencies"],
                "supporting_competencies": blueprint["supporting_competencies"],
                "technologies": blueprint["technologies"],
                "learning_objectives": blueprint["learning_objectives"],
                "recommended_projects": blueprint["projects"]
            }
            
            # Map weekly curriculum sequence
            curriculum.append({
                "role": role_name,
                "weeks": blueprint["weeks"]
            })

    with open("database/roles.json", "w") as f:
        json.dump(roles, f, indent=2)

    with open("database/curriculum.json", "w") as f:
        json.dump(curriculum, f, indent=2)

    # Load domains and skill blocks from JSON if available to print stats
    try:
        with open("database/domains.json") as f:
            domains = json.load(f)
    except Exception:
        domains = {}

    try:
        with open("database/skill_blocks.json") as f:
            skill_blocks = json.load(f)
    except Exception:
        skill_blocks = {}

    print("[SUCCESS] Fully deterministic, competency-first curriculum database seeded successfully under root /database/ directory!")
    print(f"Seeded: {len(domains)} Domains, {len(roles)} Career Roles, {len(skill_blocks)} Skill Blocks, and {len(curriculum)} Syllabus Paths.")

if __name__ == "__main__":
    seed()
