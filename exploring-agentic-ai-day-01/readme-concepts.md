🧠 HIGH-LEVEL IDEA
Your system = AI Agent + Tools + Database
e.g: User → AI Brain → Tool → Database → Result → User


🔥 MAIN ARCHITECTURE DIAGRAM


                                    ┌──────────────────────┐
                                    │        USER          │
                                    │  "Add user Sunil"   │
                                    └─────────┬────────────┘
                                            │
                                            ▼
                                    ┌──────────────────────┐
                                    │   AI AGENT (LLM)     │
                                    │ ChatOpenAI (LLaMA)   │
                                    │                      │
                                    │ - Understand query   │
                                    │ - Decide tool        │
                                    └─────────┬────────────┘
                                            │
                                            ▼
                                    ┌──────────────────────┐
                                    │   SYSTEM PROMPT      │
                                    │ (Rules / Brain guide)│
                                    │                      │
                                    │ - Use ONLY tools     │
                                    │ - Call ONE tool      │
                                    │ - Return exact output│
                                    └─────────┬────────────┘
                                            │
                                            ▼
                                    ┌──────────────────────┐
                                    │      TOOLS           │
                                    │                      │
                                    │ 1. add_user()        │
                                    │ 2. list_users()      │
                                    └───────┬──────────────┘
                                            │
                            ┌───────────────┴───────────────┐
                            ▼                               ▼
                    ┌──────────────────────┐     ┌──────────────────────┐
                    │     add_user()       │     │     list_users()     │
                    │ Insert into DB       │     │ Fetch from DB        │
                    └─────────┬────────────┘     └─────────┬────────────┘
                            │                              │
                            ▼                              ▼
                        ┌────────────────────────────────────────┐
                        │          SQLITE DATABASE               │
                        │----------------------------------------│
                        │ ID     | Name   | Authenticated        │
                        │ ML001  | Raj    | 1                    │
                        │ ML002  | Ram    | 0                    │
                        │ ML003  | Sham   | 1                    │
                        └────────────────────────────────────────┘
                                            │
                                            ▼
                                    ┌──────────────────────┐
                                    │   TOOL OUTPUT        │
                                    │ (Final Answer)       │
                                    └─────────┬────────────┘
                                            │
                                            ▼
                                    ┌──────────────────────┐
                                    │        USER          │
                                    │ "User added..."      │
                                    └──────────────────────┘