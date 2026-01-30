FIELDS = [
    "embedded_systems_and_iot",
    "systems_and_hardware_programming",
    "computational_biology",
    "quantum_computing",
    "cybersecurity",
    "game_development",
    "entrepreneurship_and_startups",
    "research_and_academia",
    "education_and_teaching",
    "artificial_intelligence_and_machine_learning",
    "frontend_development",
    "backend_development",
    "full_stack_development",
    "mobile_development",
    "ui_ux_design_and_human_computer_interaction",
    "fintech",
    "data_science_and_analytics",
    "companies",
]

MODEL = "openai/gpt-oss-120b"

FIELD_WEIGHT = 0.9  # weight of numeric field similarity
COMPANY_WEIGHT = 0.1  # weight of company similarity (before cap)
CLASH_PENALTY = 0.15  # penalty per field where student and mentor clash
STRONG_MATCH_THRESHOLD = 0.6  # similarity >= this -> "strong"
WEAK_MATCH_THRESHOLD = 0.3  # similarity < this -> "weak"; between -> "ok"

EXPECTED_POS_THRESHOLD = 0.25  # positive interests should be at least 0.25
EXPECTED_NEG_THRESHOLD = -0.25  # negative interests should be at most -0.25
CONSISTENCY_RUNS = 3  # number of runs to test consistency
CONSISTENCY_THRESHOLD = 0.75  # consistency should be at least 0.75

USE_CSV_STUDENTS = False
N = 23

STUDENT_TEST_CASES = [
    {
        "input": {
            "interests": "AI/ML, DevOps, Systems Engineering, Network Engineering, Biotech, Firmware, Hardware",
            "disinterests": "Crypto",
            "ideal_mentor": "They would work at any company, whether Big Tech or a startup. They would be knowledgeable in many fields but hopefully at least full-stack. I don't care much about their background, just whether they are able to assist and connect with me.",
        },
        "expected_pos": [
            "artificial_intelligence_and_machine_learning",
            "systems_and_hardware_programming",
            "computational_biology",
        ],
        "expected_neg": ["fintech"],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Backend and infrastructure engineering, with a focus on scalable systems, APIs, and data pipelines. Interested in developer platforms, reliability, and performance critical services. Enjoy building tools that support large numbers of users and enable other engineers to move faster.",
            "disinterests": "N/A",
            "ideal_mentor": "I’m looking for mentorship on navigating the path to big tech roles, including technical interview preparation and long term career positioning. I’d also value guidance on planning coursework strategically and weighing the tradeoffs between industry experience and pursuing graduate school.",
        },
        "expected_pos": ["backend_development"],
        "expected_neg": [],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Mobile/iOS development, game development",
            "disinterests": "Operating systems, compilers, anything to do with hardware/memory",
            "ideal_mentor": "Someone from a game development company like Blizzard, etc., expert in developing games and increasing performance",
        },
        "expected_pos": ["mobile_development", "game_development"],
        "expected_neg": ["systems_and_hardware_programming"],
        "expected_companies": ["Blizzard"],
    },
    {
        "input": {
            "interests": "Frontend, Backend, Python, Java, Web Development, Cloud Computing, System Design, AI Engineering, Machine Learning, C++",
            "disinterests": "Cyber Security, Quantum Computing",
            "ideal_mentor": "My ideal mentor would work in Big Tech (Google, Meta, Amazon, Nvidia, etc), ML/AI companies like (Waymo, OpenAI, Anthropic), or work in FinTech like (Sofi, PayPal, JaneStreet, HRT, etc) as a software developer.",
        },
        "expected_pos": [
            "frontend_development",
            "backend_development",
            "full_stack_development",
            "artificial_intelligence_and_machine_learning",
            "fintech",
        ],
        "expected_neg": ["cybersecurity", "quantum_computing"],
        "expected_companies": [
            "Google",
            "Meta",
            "Amazon",
            "Nvidia",
            "Waymo",
            "OpenAI",
            "Anthropic",
            "Sofi",
            "PayPal",
            "JaneStreet",
            "HRT",
        ],
    },
    {
        "input": {
            "interests": "Backend systems, distributed systems, databases, performance optimization, infrastructure.",
            "disinterests": "Front-end heavy roles, UI/UX design.",
            "ideal_mentor": "Someone senior in distributed systems at a large-scale company like Google or Meta. Ideally they’ve worked on systems that serve millions of users and can explain tradeoffs clearly. A strong CS fundamentals background is a must.",
        },
        "expected_pos": ["backend_development"],
        "expected_neg": [
            "frontend_development",
            "ui_ux_design_and_human_computer_interaction",
        ],
        "expected_companies": ["Google", "Meta"],
    },
    {
        "input": {
            "interests": "AI/ML, data engineering, applied statistics, recommender systems.",
            "disinterests": "Low-level systems programming, hardware.",
            "ideal_mentor": "An applied ML engineer at a consumer tech company like Netflix or Spotify. They should be strong at turning messy data into useful models and be honest about what ML can’t solve.",
        },
        "expected_pos": ["artificial_intelligence_and_machine_learning"],
        "expected_neg": ["systems_and_hardware_programming"],
        "expected_companies": ["Netflix", "Spotify"],
    },
    {
        "input": {
            "interests": "Full-stack development, product engineering, developer tooling.",
            "disinterests": "Pure research roles.",
            "ideal_mentor": "A product-focused engineer at a fast-growing startup. Bonus points if they’ve shipped multiple products end-to-end and can talk about balancing code quality with real deadlines.",
        },
        "expected_pos": ["full_stack_development"],
        "expected_neg": ["research_and_academia"],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Security engineering, privacy, operating systems, networking.",
            "disinterests": "Game development.",
            "ideal_mentor": "A security engineer at a company like Cloudflare or a major cloud provider. Ideally someone with experience in both defensive security and systems-level programming.",
        },
        "expected_pos": ["cybersecurity", "systems_and_hardware_programming"],
        "expected_neg": ["game_development"],
        "expected_companies": ["Cloudflare"],
    },
    {
        "input": {
            "interests": "Mobile app development, UX-aware engineering, consumer products.",
            "disinterests": "Backend infrastructure work.",
            "ideal_mentor": "A mobile engineer at Apple or a well-known consumer startup. They should be opinionated about clean code, usability, and building polished user-facing features.",
        },
        "expected_pos": [
            "mobile_development",
            "ui_ux_design_and_human_computer_interaction",
        ],
        "expected_neg": ["backend_development"],
        "expected_companies": ["Apple"],
    },
    {
        "input": {
            "interests": "Game engines, graphics programming, C++, real-time systems.",
            "disinterests": "Web development.",
            "ideal_mentor": "An engineer working on game engines or graphics at a studio or company like NVIDIA. Strong math and low-level optimization background preferred.",
        },
        "expected_pos": ["game_development"],
        "expected_neg": ["full_stack_development"],
        "expected_companies": ["NVIDIA"],
    },
    {
        "input": {
            "interests": "Data science, analytics, dashboards, experimentation, SQL, Python",
            "disinterests": "Low-level C/C++, embedded systems",
            "ideal_mentor": "Someone doing data science or analytics at a consumer tech company who actually influences product decisions, not just builds charts no one looks at.",
        },
        "expected_pos": ["data_science_and_analytics"],
        "expected_neg": [
            "systems_and_hardware_programming",
            "embedded_systems_and_iot",
        ],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Embedded systems, microcontrollers, firmware, sensors, IoT",
            "disinterests": "Web development, UI work",
            "ideal_mentor": "An embedded engineer who has shipped real hardware products and understands the pain of debugging physical systems.",
        },
        "expected_pos": ["embedded_systems_and_iot"],
        "expected_neg": [
            "frontend_development",
            "ui_ux_design_and_human_computer_interaction",
        ],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Startups, product engineering, full-stack development, MVPs",
            "disinterests": "Pure research, academia",
            "ideal_mentor": "A startup founder or early engineer who’s built products from scratch and dealt with ambiguity, pivots, and limited resources.",
        },
        "expected_pos": ["entrepreneurship_and_startups", "full_stack_development"],
        "expected_neg": ["research_and_academia"],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Theoretical CS, algorithms, proofs, research",
            "disinterests": "Industry-focused software engineering roles",
            "ideal_mentor": "A professor or PhD researcher who can guide me on publishing, conferences, and deciding whether academia is the right long-term path.",
        },
        "expected_pos": ["research_and_academia"],
        "expected_neg": ["backend_development", "full_stack_development"],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Teaching computer science, curriculum design, mentoring beginners",
            "disinterests": "High-pressure production engineering roles",
            "ideal_mentor": "Someone who has taught CS at a university or bootcamp and can talk honestly about education as a career.",
        },
        "expected_pos": ["education_and_teaching"],
        "expected_neg": ["backend_development"],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Cybersecurity, threat modeling, network security, privacy",
            "disinterests": "Frontend/UI development",
            "ideal_mentor": "A security engineer at a company like Google or a cloud provider who has handled real-world incidents and can explain tradeoffs.",
        },
        "expected_pos": ["cybersecurity"],
        "expected_neg": ["frontend_development"],
        "expected_companies": ["Google"],
    },
    {
        "input": {
            "interests": "AI, deep learning, NLP, research papers, model training",
            "disinterests": "Frontend work, UI polish",
            "ideal_mentor": "An AI researcher or applied scientist at a place like OpenAI or DeepMind who understands both theory and production constraints.",
        },
        "expected_pos": ["artificial_intelligence_and_machine_learning"],
        "expected_neg": ["frontend_development"],
        "expected_companies": ["OpenAI", "DeepMind"],
    },
    {
        "input": {
            "interests": "Databases, backend APIs, scalable services",
            "disinterests": "Mobile development",
            "ideal_mentor": "A backend engineer at a fintech company like Stripe or Square who has worked on high-reliability systems handling money.",
        },
        "expected_pos": ["backend_development", "fintech"],
        "expected_neg": ["mobile_development"],
        "expected_companies": ["Stripe", "Square"],
    },
    {
        "input": {
            "interests": "UX engineering, accessibility, frontend architecture",
            "disinterests": "Backend infrastructure",
            "ideal_mentor": "A senior frontend or UX-focused engineer who deeply cares about usability and inclusive design.",
        },
        "expected_pos": [
            "frontend_development",
            "ui_ux_design_and_human_computer_interaction",
        ],
        "expected_neg": ["backend_development"],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Bioinformatics, genomics, ML for biology",
            "disinterests": "Game development, graphics",
            "ideal_mentor": "Someone working at the intersection of biology and computation, ideally in industry or a research lab translating science into tools.",
        },
        "expected_pos": [
            "computational_biology",
            "artificial_intelligence_and_machine_learning",
        ],
        "expected_neg": ["game_development"],
        "expected_companies": [],
    },
    {
        "input": {
            "interests": "Backend systems, APIs, distributed systems, performance",
            "disinterests": "Frontend/UI work",
            "ideal_mentor": "A senior backend engineer at Google, Meta, or Uber who has worked on large-scale distributed systems serving millions of users.",
        },
        "expected_pos": ["backend_development"],
        "expected_neg": [
            "frontend_development",
            "ui_ux_design_and_human_computer_interaction",
        ],
        "expected_companies": ["Google", "Meta", "Uber"],
    },
    {
        "input": {
            "interests": "Machine learning, recommendation systems, data engineering",
            "disinterests": "Low-level systems programming",
            "ideal_mentor": "An ML engineer at Netflix, YouTube, or TikTok working on large-scale recommender systems.",
        },
        "expected_pos": [
            "artificial_intelligence_and_machine_learning",
            "data_science_and_analytics",
        ],
        "expected_neg": ["systems_and_hardware_programming"],
        "expected_companies": ["Netflix", "YouTube", "TikTok"],
    },
    {
        "input": {
            "interests": "Full-stack development, product engineering, rapid iteration",
            "disinterests": "Pure research roles",
            "ideal_mentor": "A product engineer at Stripe, Airbnb, or Notion who has shipped multiple user-facing features end-to-end.",
        },
        "expected_pos": ["full_stack_development"],
        "expected_neg": ["research_and_academia"],
        "expected_companies": ["Stripe", "Airbnb", "Notion"],
    },
    {
        "input": {
            "interests": "iOS development, mobile UX, consumer apps",
            "disinterests": "Backend infrastructure",
            "ideal_mentor": "A mobile engineer at Apple, Instagram, or Snap focused on polished consumer experiences.",
        },
        "expected_pos": [
            "mobile_development",
            "ui_ux_design_and_human_computer_interaction",
        ],
        "expected_neg": ["backend_development"],
        "expected_companies": ["Apple", "Instagram", "Snap"],
    },
    {
        "input": {
            "interests": "Cybersecurity, cloud security, networking",
            "disinterests": "Game development",
            "ideal_mentor": "A security engineer at Cloudflare, AWS, or Microsoft Azure with experience securing large-scale cloud infrastructure.",
        },
        "expected_pos": ["cybersecurity"],
        "expected_neg": ["game_development"],
        "expected_companies": ["Cloudflare", "AWS", "Microsoft"],
    },
    {
        "input": {
            "interests": "Game engines, graphics programming, C++, real-time rendering",
            "disinterests": "Web development",
            "ideal_mentor": "An engineer at Epic Games, Unity, or NVIDIA working on game engines or graphics tooling.",
        },
        "expected_pos": ["game_development"],
        "expected_neg": ["full_stack_development"],
        "expected_companies": ["Epic Games", "Unity", "NVIDIA"],
    },
    {
        "input": {
            "interests": "Fintech systems, backend engineering, reliability",
            "disinterests": "UI/UX design",
            "ideal_mentor": "A backend engineer at Stripe, PayPal, or Square who works on payment infrastructure and financial systems.",
        },
        "expected_pos": ["backend_development", "fintech"],
        "expected_neg": ["ui_ux_design_and_human_computer_interaction"],
        "expected_companies": ["Stripe", "PayPal", "Square"],
    },
    {
        "input": {
            "interests": "Research-oriented machine learning, theory, experiments",
            "disinterests": "Product-focused engineering",
            "ideal_mentor": "A research scientist at DeepMind, OpenAI, or FAIR who can advise on transitioning from undergrad to research roles.",
        },
        "expected_pos": [
            "artificial_intelligence_and_machine_learning",
            "research_and_academia",
        ],
        "expected_neg": ["full_stack_development"],
        "expected_companies": ["DeepMind", "OpenAI", "FAIR"],
    },
    {
        "input": {
            "interests": "Embedded systems, firmware, hardware-software integration",
            "disinterests": "Frontend and web development",
            "ideal_mentor": "An embedded engineer at Tesla, SpaceX, or Apple working close to hardware.",
        },
        "expected_pos": [
            "embedded_systems_and_iot",
            "systems_and_hardware_programming",
        ],
        "expected_neg": ["frontend_development"],
        "expected_companies": ["Tesla", "SpaceX", "Apple"],
    },
    {
        "input": {
            "interests": "Startups, engineering leadership, building teams",
            "disinterests": "Large slow-moving organizations",
            "ideal_mentor": "A founder or early engineer from a YC-backed startup or companies like Dropbox or Airbnb in their early days.",
        },
        "expected_pos": ["entrepreneurship_and_startups"],
        "expected_neg": [],
        "expected_companies": ["Y Combinator", "Dropbox", "Airbnb"],
    },
]
